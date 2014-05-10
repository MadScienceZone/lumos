# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/ChannelTest.py,v 1.3 2008-12-31 00:13:32 steve Exp $
#
# Lumos Light Orchestration System
# Copyright (c) 2005, 2006, 2007, 2008, 2014 by Steven L. Willoughby, Aloha,
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
import unittest
from Lumos.VirtualChannels.RGBVirtualChannel import RGBVirtualChannel
from Lumos.VirtualChannels.Factory           import virtual_channel_factory

class DummyChannelObject (object):
    def __init__(self, name):
        self.name = name

class RGBVirtualChannelTest (unittest.TestCase):
    def setUp(self):
        self.c = DummyChannelObject('spam')
        self.r = DummyChannelObject('red')
        self.g = DummyChannelObject('green')
        self.b = DummyChannelObject('blue')
        self.rgb = (self.r, self.g, self.b)


    def testCons(self):
        vc = RGBVirtualChannel('id', self.rgb, 'name', '#ffffff')
        self.assertEqual(vc.id, 'id')
        self.assertEqual(vc.channel, self.rgb)
        self.assertEqual(vc.name, 'name')
        self.assertEqual(vc.color, '#ffffff')
        self.assertEqual(vc.type, 'rgb')

        vc = RGBVirtualChannel('id', self.rgb, color='#ffffff')
        self.assertEqual(vc.id, 'id')
        self.assertEqual(vc.channel, self.rgb)
        self.assertEqual(vc.name, None)
        self.assertEqual(vc.color, '#ffffff')
        self.assertEqual(vc.type, 'rgb')

        vc = RGBVirtualChannel('id', self.rgb)
        self.assertEqual(vc.id, 'id')
        self.assertEqual(vc.channel, self.rgb)
        self.assertEqual(vc.name, None)
        self.assertEqual(vc.color, '#ffffff')
        self.assertEqual(vc.type, 'rgb')

        self.assertRaises(ValueError, RGBVirtualChannel, 'id', (self.c, self.c))
        self.assertRaises(ValueError, RGBVirtualChannel, 'id', self.rgb, color='13#57')

    def test_levels(self):
        vc = RGBVirtualChannel('id', self.rgb)
        for i, o, p in (
            ('on', (100,100,100), False),
            ('off', (0,0,0), False),
            (None, (0,0,0), False),
            (1, (1,1,1), True),
            (0, (0,0,0), True),
            ('1', (1,1,1), False), 
            ('0', (0,0,0), False),
            ("#161616", (8.627450980392158, 8.627450980392158, 8.627450980392158), False),
            (127, (100,100,100), False),
            (-1, (0,0,0), False),
        ):
            self.assertEqual(vc.normalize_level_value(i, permissive=p), o, msg="{0} should have normalized to {1} but was {2}".format(i, o, vc.normalize_level_value(i, permissive=p)))

        for i, p in (
            ("#-1", False),
        ):
            self.assertRaises(ValueError, vc.normalize_level_value, i, permissive=p)

    def test_factory(self):
        vc = virtual_channel_factory('rgb', id='thisOne', channel=self.rgb, name='This One', color='#123456')
        self.assertEqual(vc.type, 'rgb')
        self.assertEqual(vc.id, 'thisOne')
        self.assertEqual(vc.name, 'This One')
        self.assertEqual(vc.color, '#123456')
