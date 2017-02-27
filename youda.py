#!/usr/bin/env python3

import sys
import os
from subprocess import Popen,PIPE


class Youda:

	def help(self):
		print("""youda.py - Youtube Downloader Automation - 2017.02.27

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


	def main(self):

		try: 
			if sys.argv[1] == "-h":
				self.help()
				sys.exit(0)
		except:
			pass

		self.checkYoutubeDl()



if __name__ == '__main__':
	(Youda()).main()