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
		print("youda.py - Youtube Downloader Automation - 2017.02.27")


	def help(self):
		print("""
How to setup:
  - download this script to your computer
  - install youtube-dl 
    on a Mac: brew install youtube-dl
    on any OS: sudo pip install --upgrade youtube_dl
  - install a context-menu extension in your browser
    e.g. Context Menus for Chrome https://goo.gl/8hgwuB
  - add a custom action for links, which sends the URL to
    http://localhost:8012/q=%s
    where "%s" is the variable name for the selected URL

How to use:
  - start this script in a shell window:
    youda.py 8009 ~/Downloads/youtube
  - in your browser, right-click in a YouTube link and
    select custom context menu item you've added
  - this script will catch the URL and call youtube-dl with it
  - do not abort the script until it finishes
			"""
		)
		sys.exit(0)


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


	def discoverNumero(self):

		self.number = 0
		for fnam in os.listdir(self.dir):
			try:
				if fnam[3] != "-": continue
				n = int(fnam.split("-")[0])
			except: 
				continue
			if n > self.number: self.number = n
		self.number += 1


	def run(self):
		while True:
			
			(numero,url) = self.queue.get(block=True)

			cmd = "youtube-dl \"<url>\" --exec \"mv {} <path>/<num>-{}\"" 
			cmd = cmd.replace("<path>",self.dir)
			cmd = cmd.replace("<url>",url)
			cmd = cmd.replace("<num>",str(numero).zfill(3))

			os.system(cmd)


	def enqueue(self,url):
		num = self.number

		if url in self.dupe: return (True,self.dupe[url])

		self.dupe[url] = num
		self.queue.put((num,url))

		self.number += 1
		return (False,num)


	def main(self):

		try: self.port = int(sys.argv[1])
		except: self.help()
		if self.port == 0: self.help()

		self.checkYoutubeDl()
		try: self.dir = sys.argv[2]
		except: self.discoverDownloadDirectory()
		self.discoverNumero()

		self.about()
		print("  port: " + str(self.port))
		print("   dir: " + self.dir)
		print(" start: " + str(self.number).zfill(3))

		self.queue = queue.Queue()
		self.dupe = {}
		self.setDaemon(True)		
		self.start()

		httpd = HTTPServer(("0.0.0.0",self.port),YoudaRequestHandler)
		httpd.theServer = self
		httpd.serve_forever()


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

