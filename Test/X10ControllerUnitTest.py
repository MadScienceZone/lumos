#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/X10ControllerUnitTest.py,v 1.4 2008-12-31 00:13:32 steve Exp $
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
#
# vi:set ai sm nu ts=4 sw=4 expandtab:
#
import unittest, quopri
from Lumos.Device.X10ControllerUnit  import X10ControllerUnit
from Lumos.ControllerUnit            import ControllerUnit
from Lumos.PowerSource               import PowerSource
from TestNetwork                     import TestNetwork

class X10ControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=12)
        self.x10 = X10ControllerUnit('myx10', p, network=self.n)

    def tearDown(self):
        self.x10 = None
        self.n = None

    def test_unit_id(self):
        self.assertEqual(self.x10.id, 'myx10')

    def testCons(self):
        self.assertEqual(self.x10.type, 'X-10 Controller')
        self.assertEqual(str(self.x10), 'X-10 Controller')
        self.assertEqual(self.x10.resolution, 16)
        self.assertTrue(isinstance(self.x10, X10ControllerUnit))
        self.assertTrue(isinstance(self.x10, ControllerUnit))

    def test_add_channel_noload(self):
        self.assertRaises(ValueError, self.x10.add_channel, ('a1',))

    def test_add_channel(self):
        self.x10.add_channel(' a1  ', load=1.11)
        self.assertEqual(self.x10.channels['A1'].name, 'Channel A1')
        self.assertEqual(self.x10.channels['A1'].load, 1.11)
        self.assertEqual(self.x10.channels['A1'].dimmer, True)
        self.assertEqual(self.x10.channels['A1'].resolution, 16)
        self.assertEqual(self.x10.channels['A1'].level, None)
        self.assertEqual(self.x10.channels['A1'].warm, None)

    def test_add_channel_bad_id(self):
        self.assertRaises(ValueError, self.x10.add_channel, ('123',), {'load':12})
        self.assertRaises(ValueError, self.x10.add_channel, ('P17',), {'load':12})
        self.assertRaises(ValueError, self.x10.add_channel, ('Q7',), {'load':12})

    def test_iterator(self):
        self.x10.add_channel('b7', load=1)
        self.x10.add_channel('c8', load=1)
        self.x10.add_channel('f7', load=1)
        self.x10.add_channel('m10', load=1)
        self.assertEqual(sorted(self.x10.iter_channels()), ['B7','C8','F7','M10'])
# 
# $Log: not supported by cvs2svn $
#
