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
		print("youda.py - Youtube Downloader Automation - 2017.02.28")


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
  - do not abort the script until it finishes
			"""
		)

		text = text.replace("##","")
		text = text.replace("<br />","")
		print(text)
		sys.exit(0)


	def __init__(self):
		Thread.__init__(self)
		self.queue = queue.Queue()


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


	def discoverDownloadDirectory(self):

		for self.dir in ["~/Downloads","~/Download","~/downloads","~/download","~"]:
			if not os.path.isdir(self.dir): continue
			self.dir += "/youtube"
			os.makedirs(self.dir)
			if not os.path.isdir(self.dir): continue
			print("Download directory: " + self.dir)
			return

		fatal("Can't create download directory")


	def run(self):
		while True:
			
			(numero,url) = self.queue.get(block=True)

			cmd = "youtube-dl \"<url>\" --exec \"mv {} <path>/<num>-{}\"" 
			cmd = cmd.replace("<path>",self.dir)
			cmd = cmd.replace("<url>",url)
			cmd = cmd.replace("<num>",str(numero).zfill(3))

			os.system(cmd)


	def enqueue(self,url):
		num = self.numero

		if url in self.dupe: return (True,self.dupe[url])

		self.dupe[url] = num
		self.queue.put((num,url))

		self.numero += 1
		return (False,num)


	def setupPort(self):
		try: self.port = int(sys.argv[1])
		except: self.help()
		if self.port == 0: self.help()


	def setupDir(self):
		try: self.dir = sys.argv[2]
		except: self.discoverDownloadDirectory()


	def setupDupe(self):

		self.dupeDirs = []
		self.addDupe(self.dir)

		arg = 3
		while True:
			try: dupeDir = sys.argv[arg]
			except: break
			self.addDupe(dupeDir)
			arg += 1

		self.rebuildDupe()


	def addDupe(self,dir):
		for dupe in self.dupeDirs:
			if dir == dupe: return
		self.dupeDirs.append(dir)


	def discoverNumero(self):
		self.numero = 0
		self.scanDirs("numero")
		self.numero += 1


	def rebuildDupe(self):
		self.dupe = {}
		self.scanDirs("dupe")


	def scanDirs(self,action):

		for dir in self.dupeDirs:
			for fnam in os.listdir(self.dir):
				(name,ext) = os.path.splitext(fnam)
				if name == "": continue
				if ext == "": continue
				if action == "dupe": 
					item = Item()
					item.setName(fnam,True)
					self.addDupeItem(item)
				if action == "numero": 
					self.checkNumeroItem(fnam)


	def checkNumeroItem(self,fnam):

		try:
			if fnam[3] != "-": return
			n = int(fnam.split("-")[0])
		except: 
			return

		if n > self.numero: self.numero = n


	def addDupeItem(self,item):
		pass
		#todo


	def status(self):
		print("  port: " + str(self.port))
		print("   dir: " + self.dir)
		i = 0
		for dupe in self.dupeDirs:
			if dupe == self.dir: continue
			if i == 0: print("  dupe: " + dupe)
			else: print("        " + dupe)
			i += 1
		print(" start: " + str(self.numero).zfill(3))


	def main(self):

		self.setupPort()
		self.checkYoutubeDl()
		self.setupDir()
		self.setupDupe()
		self.discoverNumero()
		self.about()
		self.status()

		sys.exit(0)

		self.setDaemon(True)		
		self.start()

		httpd = HTTPServer(("0.0.0.0",self.port),YoudaRequestHandler)
		httpd.theServer = self
		httpd.serve_forever()


class Item:


	def __item__(self):

		self.name = None
		self.title = None
		self.numero = None
		self.id = None


	def setName(self,name,parseId = False):

		self.name = name

		if name[3] == "-":
			self.numero = int(name[0:3])
			name = name[4:]

		length = len(name)
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

		if name.find("mesterl") == -1: return
		self.dump()

		if not parseId: return


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


	def do_GET(self):

		self.send_response(200)

		self.send_header("Content-type","text/html")
		self.end_headers()

		url = self.path.replace("?","&")
		if url.find("&q=") == -1: return
		url = url.split("&q=")[1]
		url = parse.unquote(url)

		(already,numero) = self.server.theServer.enqueue(url)

		if already:
			message = "<h3>Already added, numero=" + str(numero) + "</h3>\n"
		else:
			message = "<h3>Added to download queue, numero=" + str(numero) + "</h3>\n"
		self.wfile.write(bytes(message,"utf8"))


if __name__ == '__main__':
	(Youda()).main()

