import unittest
import subprocess
import os

runenv = os.environ
runenv['PYTHONPATH'] = ':'.join(['../lib'] + os.environ.get('PYTHONPATH', '').split(':'))

def runAfcheck(arglist, srcfile, compfile):
	try:
		proc = subprocess.Popen(('../bin/lcheck', srcfile) + arglist, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=runenv)
	except:
		# no ../bin directory?  Looks like we're not in our development environment.
		# must have unpacked from a source distribution tarball.  Look for our scripts
		# in ../dist_bin instead, and better make sure they are executable.
		os.chmod('../dist_bin/lcheck', 0755)
		proc = subprocess.Popen(('../dist_bin/lcheck', srcfile) + arglist, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=runenv)
		
	output = proc.communicate()[0]
	cmpout = open(compfile).read()
	return (proc.returncode, output, cmpout)

class AfcheckTest (unittest.TestCase):
	def testRunV(self):
		(c, a, b) = runAfcheck(('-v',), 'lcheck.conf', 'lcheck.v.out')
		self.assertEqual(c, 0)
		self.assertEqual(a, b)

	def testRun(self):
		(c, a, b) = runAfcheck((), 'lcheck.conf', 'lcheck.out')
		self.assertEqual(c, 0)
		self.assertEqual(a, b)

	def testDuplicates(self):
		(c, a, b) = runAfcheck((), 'duptest.conf', 'lcheck.dup.out')
		self.assertEqual(c, 1)
		#self.assertEqual(a, b)
		self.assert_("ValueError: Unit 'a' is not unique!" in a)
