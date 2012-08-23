# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/SerialNetworkTest.py,v 1.2 2008-12-31 00:13:32 steve Exp $
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
from Lumos.Network               import NullNetwork
from Lumos.Network.Networks      import network_factory
from Lumos.Network.SerialNetwork import SerialNetwork

class SerialNetworkTest (unittest.TestCase):
    def testCons(self):
        n = network_factory(type='serial', description='desc', port=1,
                            baudrate=1200, bits=7, parity='even', stop=2,
                            xonxoff=True, rtscts=True, open_device=False)
        if isinstance(n, NullNetwork):
            warn_once('NOSERIAL', "Skipping tests of Serial networks: this machine does not support them (intall PySerial?)")
        else:
            self.assertEqual(n.description, 'desc')
            self.assertEqual(n.port, 1)
            self.assertEqual(n.baudrate, 1200)
            self.assertEqual(n.bits, 7)
            self.assertEqual(n.parity, 'even')
            self.assertEqual(n.stop, 2)
            self.assert_(n.xonxoff)
            self.assert_(n.rtscts)

    def testDefaults(self):
        n = network_factory(type='serial', open_device=False)
        if isinstance(n, NullNetwork):
            warn_once('NOSERIAL', "Skipping tests of Serial networks: this machine does not support them (intall PySerial?)")
        else:
            self.assertEqual(n.description, 'Unnamed Network')
            self.assertEqual(str(n), 'Unnamed Network')
            self.assertEqual(n.port, 0)
            self.assertEqual(n.baudrate, 9600)
            self.assertEqual(n.bits, 8)
            self.assertEqual(n.parity, 'none')
            self.assertEqual(n.stop, 1)
            self.assert_(not n.xonxoff)
            self.assert_(not n.rtscts)

    def test_no_open(self):
        n = network_factory(type='serial', open_device=False)
        if isinstance(n, NullNetwork):
            warn_once('NOSERIAL', "Skipping tests of Serial networks: this machine does not support them (intall PySerial?)")
        else:
            self.assertEqual(n.dev, None)
            #n = network_factory(type='serial', open_device=False)
            #self.assertNotEqual(n.dev, None)
