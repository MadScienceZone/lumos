# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/TestParallelNetworkTest.py,v 1.2 2008-12-31 00:13:32 steve Exp $
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
# 
# $Log: not supported by cvs2svn $
#
