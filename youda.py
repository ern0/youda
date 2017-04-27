#!/usr/bin/env python3

import sys
import os
import time
from subprocess import Popen,PIPE
from http.server import BaseHTTPRequestHandler,HTTPServer
from urllib import parse
from threading import *
import queue


class Youda(Thread):
	

	def about(self):
		print("youda.py - Youtube Downloader Automation - 2017.04.25")


	def help(self):

		self.about()

		text = ("""
## How to setup ##
  - download this script to your computer
  - install youtube-dl <br />
    on a Mac: brew install youtube-dl <br />
    on any OS: sudo pip install --upgrade youtube_dl
  - install a context-menu extension in your browser <br />
    e.g. Context Menus for Chrome https://goo.gl/8hgwuB
  - add a custom action for links, which sends the URL to <br />
    http://localhost:8009/q=%s <br />
    where "%s" is the variable name for the selected URL

## How to use ##
  - start this script in a shell window: <br />
      youda.py <port> [<download-dir> [<check-dir> [<check-dir>...]]] <br />
    example:
      youda.py 8009 ~/Downloads/youtube /media/nexus7/storage/sdcard0/Podcasts/ <br />
    If you specify download-dirs, duplications will be also <br />
    checked in these directories
  - in your browser, right-click in a YouTube link and <br />
    select custom context menu item you've added
  - this script will catch the URL and call youtube-dl with it

## Under the hood ##
  - when you add a file, the web server thread creates a placeholder file
  - the processing thread scans the directory, picks first placeholder file, 
    then replaces it with the downloaded file
  - because the queue is stored in files, script can be restarted
			"""
		)

		text = text.replace("##","")
		text = text.replace("<br />","")
		print(text)
		sys.exit(0)

	
	def __init__(self):
		
		Thread.__init__(self)

		self.dir = "."
		self.checkDirs = []
		self.rescanLock = Lock()
		self.change = False


	def fatal(self,msg):
		print(msg)
		sys.exit(2)


	def checkYoutubeDl(self):

		line = ""
		try:
			with Popen(["which","youtube-dl"],stdout=PIPE,bufsize=1,universal_newlines=True) as p:
				for line in p.stdout: break
		except:
			self.fatal("your operating system is not supported")

		if line != "": return
		self.fatal("you need to install youtube-dl")


	def setupPort(self):
		try: self.port = int(sys.argv[1])
		except: self.help()
		if self.port == 0: self.help()


	def setupDir(self):
		try: self.dir = sys.argv[2]
		except: self.discoverDownloadDirectory()


	def discoverDownloadDirectory(self):

		for self.dir in ["~/Downloads","~/Download","~/downloads","~/download","~"]:
			if not os.path.isdir(self.dir): continue
			self.dir += "/youtube"
			os.makedirs(self.dir)
			if not os.path.isdir(self.dir): continue
			return

		fatal("Can't create download directory")


	def setupCheck(self):

		arg = 4
		while True:
			try: checkDir = sys.argv[arg]
			except: break
			self.addCheckDir(checkDir)
			arg += 1


	def addCheckDir(self,checkDir):
		
		for dir in self.checkDirs:
			if checkDir == dir: return

		self.checkDirs.append(checkDir)


	def restore(self):
		
		remnants = {}
		
		# collect remnants
		for fnam in os.listdir(self.dir):
			if fnam[-17:] != "-processing.youda": continue
			remnants[fnam[0:3]] = fnam
			
		# process remnants	
		for fnam in os.listdir(self.dir):
			if fnam[-17:] == "-processing.youda": continue
			if fnam[0:3] not in remnants: continue
			
			# remove remnant
			os.remove(self.dir + "/" + fnam)
			
			# rename "~processing" back to "~queued"
			pnam = remnants[fnam[0:3]]
			qnam = pnam.replace("-processing.youda","-queued.youda")
			os.rename(self.dir + "/" + pnam,self.dir + "/" + qnam)


	def rescan(self):

		self.rescanLock.acquire()

		self.queue = []
		self.check = {}

		for fnam in os.listdir(self.dir):
			item = (Item()).buildFromName(fnam)
			if item.isInvalid(): continue
			if item.getId() in self.check: continue
			self.queue.append(item)
			self.check[item.getId()] = item

		try:
			for dir in self.checkDirs:
				if os.path.isfile(dir): continue
				for fnam in os.listdir(dir):
					item = (Item()).buildFromName(fnam)
					if item.isInvalid(): continue
					self.check[item.getId()] = item
		except FileNotFoundError:
			pass
			
		lowNumero = 0
		highNumero = 0
		for id in self.check:
			item = self.check[id]
			num = item.getNumero()
			if num < 500:
				if num > lowNumero: lowNumero = num
			else:
				if num > highNumero: highNumero = num

		if lowNumero == 0:
			self.numero = 1 + highNumero
		else:
			self.numero = 1 + lowNumero
		if self.numero == 1000: self.numero = 1 + lowNumero

		self.rescanLock.release()


	def getNumero(self):
		return self.numero		


	def findItem(self,id):
		
		try: return self.check[id]
		except: pass
		
		return None
		

	def enqueue(self,item):

		item.setNumero(self.numero)
		self.numero += 1

		fnam = self.dir
		fnam += "/"
		fnam += item.getNumeroFmtd()
		fnam += "-"
		fnam += item.getId()
		fnam += "-queued."

		f = open(fnam + "tmp","w")
		f.write("youda\n")
		f.close()
		
		# make semaphore file creation atomic
		os.rename(fnam + "tmp",fnam + "youda")
		
		self.change = True
		

	def run(self):
		while True:

			# wait for next queued item
			while True:
				found = False
				
				# scan dir at startup and every ~10s
				for fnam in os.listdir(self.dir):
					if fnam[-13:] == "-queued.youda":
						found = True
						break

				if found: break

				# check for change in every 1 s
				for i in range(0,9):
					if self.change:
						found = True
						break

				if found: break

				time.sleep(1)
				
			# create item
			item = None
			for fnam in os.listdir(self.dir):
				if fnam[-13:] != "-queued.youda": continue
				item = (Item()).buildFromName(fnam)
				break
			if item is None: continue

			# download item
			self.downloadItem(item)
			time.sleep(1)


	def downloadItem(self,item):

		print("----[ " + item.getNumeroFmtd() + " ]----")

		basenam = self.dir 
		basenam += "/" 
		basenam += item.getNumeroFmtd()
		basenam += "-" 
		basenam += item.getId()
		basenam += "-"
			
		pnam = basenam + "processing.youda"
		qnam = basenam + "queued.youda"
				
		url = "http://www.youtube.com/watch?v=" + item.getId()
		
		cmd = "youtube-dl \"<url>\""
		cmd += " -o \"<path>/<num>-%(title)s-%(id)s.%(ext)s\""
		cmd = cmd.replace("<path>",self.dir)
		cmd = cmd.replace("<url>",url)
		cmd = cmd.replace("<num>",item.getNumeroFmtd())

		os.rename(qnam,pnam)
		os.system(cmd)
		os.remove(pnam)

		print("===============")
		

	def status(self):
		
		print("  port: " + str(self.port))
		print("   dir: " + self.dir)
		
		i = 0
		for check in self.checkDirs:
			if check == self.dir: continue
			if os.path.isfile(check): continue

			if i == 0: print(" check: " + check,end="")
			else: print("        " + check,end="")

			if not os.path.isdir(check): 
				print(" - not exists",end="")

			print()
			i += 1

		print(" start: " + str(self.numero).zfill(3))


	def renderWebPage(self,item,message):
		
		page = (
			"<pre style='font-size:1.5em'>"
			+ "<b>" 
			+ message 
			+ ", numero=" 
			+ str( item.getNumero() ) 
			+ "</b>"
			+ "\n----\n"
		)
		
		hilite = item.getId()

		for item in self.queue:
			id = item.getId()
			
			title = item.getTitle()

			if id == hilite: page += "<span style='color: #fff; background: #000'>"

			page += " "
			page += item.getNumeroFmtd()
			page += " "
			
			if title is None:
				page += "<i>"
				page += "(queued, ID="
				page += item.getId()
				page += ")"
				page += "</i>"
			else:
				page += title
				
			if id == hilite: page += " </span>"
			page += "\n"
		
		return page
		

	def main(self):

		self.setupPort()
		self.checkYoutubeDl()
		self.setupDir()
		self.setupCheck()
		self.restore()
		self.rescan()
		self.about()
		self.status()

		self.setDaemon(True)		
		self.start()

		httpd = HTTPServer(("0.0.0.0",self.port),YoudaRequestHandler)
		httpd.theServer = self
		httpd.serve_forever()


class Item:


	def __init__(self):

		self.name = None
		self.title = None
		self.numero = None
		self.id = None
		self.queued = False


	def getId(self):
		return self.id
		
	
	def setNumero(self,num):
		self.numero = num
		
		
	def getNumero(self):
		return self.numero
	
	
	def getNumeroFmtd(self):
		return str(self.numero).zfill(3)
		
	
	def getTitle(self):
		return self.title
		
	
	def buildFromId(self,id):
		self.id = id
		return self
		
	
	def buildFromName(self,name):

		if os.path.isfile(name): return self

		self.name = name

		try:

			if name[3] == "-":
				self.numero = int(name[0:3])
				name = name[4:]

			length = len(name)
			if name[-13:] == "-queued.youda": 
				self.queued = True
				self.id = name[:-13]
				
			else:

				dot = None
				for pos in [3,4,5]:
					if name[length - pos] == ".": dot = length - pos
				if dot is not None: name = name[:dot]

				length = len(name)
				id = None
				for pos in [11,12]:
					if name[length - pos] == "-": id = length - pos
				if id is not None: 
					self.id = name[id + 1:]
					self.title = name[:id]
				else:
					self.title = name

		except IndexError: pass
		
		return self
		
		
	def isInvalid(self):
		if self.numero is None: return True
		if self.id is None: return True
		return False


	def dump(self):

		print("numero=",end="")
		if self.numero is None: print("n.a.",end="")
		else:	print(str(self.numero).zfill(3),end="")

		print(" ",end="")

		print("id=",end="")
		if self.id is None: print("n.a.",end="")
		else:	print(self.id,end="")

		print(" ",end="")

		print(self.name,end="")

		print()



class YoudaRequestHandler(BaseHTTPRequestHandler):


	def log_message(self,format,*args):
		pass


	def send(self,txt):
		self.wfile.write(bytes(txt,"utf8"))


	def parseUrl(self):

		url = self.path.replace("?","&")
		if url.find("&q=") == -1: return None
		url = url.split("&q=")[1]
		url = parse.unquote(url)

		url = url.replace("?","&")
		if url.find("&v=") == -1: return None
		url = url.split("&v=")[1]
		url = url.split("&")[0]

		return url


	def do_GET(self):

		self.send_response(200)

		self.send_header("Content-type","text/html; charset=utf-8")
		self.end_headers()

		id = self.parseUrl()
		if id is None: 
			self.send("hallo")
			return

		item = self.server.theServer.findItem(id)

		if item is None:
			item = (Item()).buildFromId(id)
			self.server.theServer.enqueue(item)
			self.server.theServer.rescan()
			message = "added to download queue"

		else:
			message = "already added"

		self.send( self.server.theServer.renderWebPage(item,message) );


if __name__ == '__main__':
	(Youda()).main()
