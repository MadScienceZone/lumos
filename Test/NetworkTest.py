import unittest
import os
from Lumos.Network               import Network
from Lumos.Network.Networks      import network_factory
from Lumos.Network.SerialNetwork import SerialNetwork

class NetworkTest (unittest.TestCase):
	def test_subclass_cons(self):
		serial = network_factory(type='serial')
		self.assert_(isinstance(serial, Network))
		self.assert_(isinstance(serial, SerialNetwork))
		#self.assertEqual(serial.id, 'test_network')

		# XXX add more types here when more exist

