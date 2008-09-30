import unittest
import os
from Lumos.Network.Networks           import network_factory
from Lumos.Network.ParallelBitNetwork import ParallelBitNetwork

class ParallelBitNetworkTest (unittest.TestCase):
    def testCons(self):
        n = network_factory(type='parbit', description='desc', port=1, open_device=False)
        self.assertEqual(n.description, 'desc')

    def testDefaults(self):
        n = network_factory(type='parbit', open_device=False)
        self.assertEqual(n.description, None)
        self.assertEqual(str(n), 'ParallelBitNetwork (port 0)')
        self.assertEqual(n.port, 0)

    def test_no_open(self):
        n = network_factory(type='parbit', open_device=False)
        self.assertEqual(n.dev, None)
		# XXX 
        #n = network_factory(type='parbit')
        #self.assertNotEqual(n.dev, None)
