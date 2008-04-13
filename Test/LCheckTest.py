import unittest
import subprocess

def runAfcheck(arglist, srcfile, compfile):
	proc = subprocess.Popen(('./lcheck', srcfile) + arglist, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	output = proc.communicate()[0]
	cmpout = open(compfile).read()
	return (proc.returncode, output, cmpout)

class AfcheckTest (unittest.TestCase):
	def testRunV(self):
		(c, a, b) = runAfcheck(('-v',), 'show.conf', 'Test/lcheck.v.out')
		self.assertEqual(c, 0)
		self.assertEqual(a, b)

	def testRun(self):
		(c, a, b) = runAfcheck((), 'show.conf', 'Test/lcheck.out')
		self.assertEqual(c, 0)
		self.assertEqual(a, b)

	def testDuplicates(self):
		(c, a, b) = runAfcheck((), 'Test/duptest.conf', 'Test/lcheck.dup.out')
		self.assertEqual(c, 1)
		self.assertEqual(a, b)
