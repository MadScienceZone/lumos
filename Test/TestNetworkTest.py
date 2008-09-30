# vi:set ai sm nu ts=4 sw=4 expandtab:
import unittest
import os
from TestNetwork   import TestNetwork
from Lumos.Network import Network

class TestNetworkTest (unittest.TestCase):
    def test_cons(self):
        tn = TestNetwork()
        self.assert_(isinstance(tn, Network))
        self.assertEqual(tn.buffer, '')

    def test_simple_data(self):
        tn = TestNetwork()
        tn.send('ABCD')
        tn.send('EEEF')
        self.assertEqual(tn.buffer, 'ABCDEEEF')

    def test_binary_data(self):
        tn = TestNetwork()
        tn.send('\33[Hello\5\5\0')
        self.assertEqual(tn.buffer, '=1B[Hello=05=05=00')


    # removed with the flush() functionality
#    def test_flush(self):
#        tn = TestNetwork()
#        self.assertEqual(tn.buffer, '')
#        self.assertEqual(tn.flushed, '')
#        tn.send('AABB')
#        self.assertEqual(tn.buffer, 'AABB')
#        self.assertEqual(tn.flushed, '')
#        tn.flush()
#        self.assertEqual(tn.buffer, '')
#        self.assertEqual(tn.flushed, 'AABB')
#        tn.send('ZYZZY')
#        self.assertEqual(tn.buffer, 'ZYZZY')
#        self.assertEqual(tn.flushed, 'AABB')
#        tn.flush()
#        self.assertEqual(tn.buffer, '')
#        self.assertEqual(tn.flushed, 'AABBZYZZY')
