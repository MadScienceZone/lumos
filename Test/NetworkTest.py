import unittest
import os
from Network import Network

class NetworkTest (unittest.TestCase):
	def testCons(self):
		n = Network('x', description='desc', port=1, baudrate=1200, bits=7, parity='even',
			stop=2, xonxoff=True, rtscts=True)

		self.assertEqual(n.id, 'x')
		self.assertEqual(n.description, 'desc')
		self.assertEqual(n.port, 1)
		self.assertEqual(n.baudrate, 1200)
		self.assertEqual(n.bits, 7)
		self.assertEqual(n.parity, 'even')
		self.assertEqual(n.stop, 2)
		self.assert_(n.xonxoff)
		self.assert_(n.rtscts)

	def testDefaults(self):
		n = Network('y')
		self.assertEqual(n.id, 'y')
		self.assertEqual(n.description, 'Network "y"')
		self.assertEqual(n.port, 0)
		self.assertEqual(n.baudrate, 9600)
		self.assertEqual(n.bits, 8)
		self.assertEqual(n.parity, 'none')
		self.assertEqual(n.stop, 1)
		self.assert_(not n.xonxoff)
		self.assert_(not n.rtscts)

	def testOpenTest(self):
		n = Network('t')
		fd = open('Test/network.out', 'w')
		try:
			n.openfd(fd)
			self.assertEqual(n.fd, fd)
			self.assert_(os.path.exists('Test/network.out'))
		finally:
			fd.close()
			os.unlink('Test/network.out')
