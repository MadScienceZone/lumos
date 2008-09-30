# vi:set ai sm nu ts=4 sw=4 expandtab:
import unittest
import os
from Lumos.Network.Networks      import network_factory
from Lumos.Network.SerialNetwork import SerialNetwork

class SerialNetworkTest (unittest.TestCase):
    def testCons(self):
        n = network_factory(type='serial', description='desc', port=1,
                            baudrate=1200, bits=7, parity='even', stop=2,
                            xonxoff=True, rtscts=True)
        self.assertEqual(n.description, 'desc')
        self.assertEqual(n.port, 1)
        self.assertEqual(n.baudrate, 1200)
        self.assertEqual(n.bits, 7)
        self.assertEqual(n.parity, 'even')
        self.assertEqual(n.stop, 2)
        self.assert_(n.xonxoff)
        self.assert_(n.rtscts)

    def testDefaults(self):
        n = network_factory(type='serial')
        self.assertEqual(n.description, None)
        self.assertEqual(str(n), 'SerialNetwork (port 0)')
        self.assertEqual(n.port, 0)
        self.assertEqual(n.baudrate, 9600)
        self.assertEqual(n.bits, 8)
        self.assertEqual(n.parity, 'none')
        self.assertEqual(n.stop, 1)
        self.assert_(not n.xonxoff)
        self.assert_(not n.rtscts)

    def test_no_open(self):
        n = network_factory(type='serial', open_device=False)
        self.assertEqual(n.dev, None)
        n = network_factory(type='serial')
        self.assertNotEqual(n.dev, None)
