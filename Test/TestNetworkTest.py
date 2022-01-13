#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/TestNetworkTest.py,v 1.2 2008-12-31 00:13:32 steve Exp $
#
# Lumos Light Orchestration System
# Copyright (c) 2005, 2006, 2007, 2008 by Steven L. Willoughby, Aloha,
# Oregon, USA.  All Rights Reserved.  Licensed under the Open Software
# License version 3.0.
#
# This product is provided for educational, experimental or personal
# interest use, in accordance with the terms and conditions of the
# aforementioned license agreement, ON AN "AS IS" BASIS AND WITHOUT
# WARRANTY, EITHER EXPRESS OR IMPLIED, INCLUDING, WITHOUT LIMITATION,
# THE WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A
# PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY OF THE ORIGINAL
# WORK IS WITH YOU.  (See the license agreement for full details, 
# including disclaimer of warranty and limitation of liability.)
#
# Under no curcumstances is this product intended to be used where the
# safety of any person, animal, or property depends upon, or is at
# risk of any kind from, the correct operation of this software or
# the hardware devices which it controls.
#
# USE THIS PRODUCT AT YOUR OWN RISK.
# 
# vi:set ai sm nu ts=4 sw=4 expandtab:
import unittest
import os
from TestNetwork   import TestNetwork
from Lumos.Network import Network

class TestNetworkTest (unittest.TestCase):
    def test_cons(self):
        tn = TestNetwork()
        self.assertTrue(isinstance(tn, Network))
        self.assertEqual(tn.buffer, b'')

    def test_simple_data(self):
        tn = TestNetwork()
        tn.send(b'ABCD')
        tn.send(b'EEEF')
        self.assertEqual(tn.buffer, b'ABCDEEEF')

    def test_binary_data(self):
        tn = TestNetwork()
        tn.send(b'\33[Hello\5\5\0')
        self.assertEqual(tn.buffer, b'=1B[Hello=05=05=00')


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
# 
# $Log: not supported by cvs2svn $
#
