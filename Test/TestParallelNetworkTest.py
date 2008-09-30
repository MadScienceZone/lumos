# vi:set ai sm nu ts=4 sw=4 expandtab:
import unittest
import os
from TestNetwork   import TestParallelNetwork
from Lumos.Network import Network

class TestParallelNetworkTest (unittest.TestCase):
    def test_cons(self):
        tn = TestParallelNetwork()
        self.assert_(isinstance(tn, Network))
        self.assertEqual(tn.buffer, '')

    def test_simple_data(self):
        tn = TestParallelNetwork()
        tn.send(0)
        tn.send(1)
        tn.send(1)
        tn.send(0)
        self.assertEqual(tn.buffer, '0110')

    def test_latch(self):
        tn = TestParallelNetwork()
        tn.send(0)
        tn.send(1)
        tn.send(0)
        tn.send(1)
        tn.latch()
        self.assertEqual(tn.buffer, '0101X')
