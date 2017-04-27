#!/usr/bin/env python3

import unittest
import sys
import os
import tempfile
sys.path.append(".")
sys.path.append("..")
import youda


class TestStringMethods(unittest.TestCase):


	def rescan(self,fileList):

		dir = tempfile.mkdtemp()
		for num in fileList: 
			nam = str(num).zfill(3) + "-test-" + str(num).zfill(11) + ".mpg"
			fnam = dir + "/" + nam
			open(fnam,"a").close()

		y = youda.Youda()
		y.addCheckDir(dir)
		y.rescan()

		for file in os.listdir(dir):
			full = os.path.join(dir,file)
			try: os.unlink(full)
			except: pass
		os.removedirs(dir)

		return y.getNumero()


	def test_empty(self):

		self.assertEqual(self.rescan([]),1)


	def test_low(self):

		self.assertEqual(self.rescan([1,2,3,4]),5)
		self.assertEqual(self.rescan([1,2,3,11]),12)


	def test_high(self):

		self.assertEqual(self.rescan([501,502,503]),504)
		self.assertEqual(self.rescan([501,502,540]),541)


	def test_overflowhi(self):

		self.assertEqual(self.rescan([933,999]),1)
		self.assertEqual(self.rescan([999,1]),2)
		self.assertEqual(self.rescan([999,1,4]),5)
		self.assertEqual(self.rescan([600,999,1,4]),5)
		self.assertEqual(self.rescan([600,999,1,4]),5)
		self.assertEqual(self.rescan([300,999,1,4]),301)


	def test_overflowlo(self):

		self.assertEqual(self.rescan([264,499,500,501,567]),568)


if __name__ == '__main__':
	unittest.main()