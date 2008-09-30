# vi:set ai sm nu ts=4 sw=4 expandtab:
import unittest
import os
from Lumos.Network.Networks         import network_factory
from Lumos.Network.SerialBitNetwork import SerialBitNetwork

class SerialBitNetworkTest (unittest.TestCase):
    def testCons(self):
        n = network_factory(type='serialbit', description='desc', port=1)
        self.assertEqual(n.description, 'desc')

    def testDefaults(self):
        n = network_factory(type='serialbit')
        self.assertEqual(n.description, None)
        self.assertEqual(str(n), 'SerialBitNetwork (port 0)')
        self.assertEqual(n.port, 0)

    def test_no_open(self):
        n = network_factory(type='serialbit', open_device=False)
        self.assertEqual(n.dev, None)
        n = network_factory(type='serialbit')
        self.assertNotEqual(n.dev, None)
