#!/usr/bin/env python3

import sys
import os
from subprocess import Popen,PIPE


# youtube-dl https://www.youtube.com/watch?v=fMt2yfRYEmw --exec "mv {} 01-{}"

class Youda:


	def about(self):
		print("youda.py - Youtube Downloader Automation - 2017.02.27")


	def help(self):
		print("""
How to setup:
  - download this script to your computer, then
    change download path and listen port, if you want
  - install youtube-dl 
    on a Mac: brew install youtube-dl
    on any OS: sudo pip install --upgrade youtube_dl
  - install a context-menu extension in your browser
    e.g. Context Menus for Chrome https://goo.gl/8hgwuB
  - add a custom action for links, which sends the URL to
    http://localhost:8012/q=%s
    where "%s" is the variable name for the selected URL

How to use:
  - start this script in a shell window
  - in your browser, right-click in a YouTube link and
    select custom context menu item you've added
  - this script will catch the URL and pass it to youtube-dl
  - do not abort the script until it finish
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


if __name__ == '__main__':
	(Youda()).main()