# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/ChannelTest.py,v 1.3 2008-12-31 00:13:32 steve Exp $
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
import unittest
from Lumos.VirtualChannel          import VirtualChannel
from Lumos.VirtualChannels.Factory import virtual_channel_factory

class DummyChannelObject (object):
    def __init__(self, name):
        self.name = name

class VirtualChannelTest (unittest.TestCase):
    def setUp(self):
        self.c = DummyChannelObject('spam')

    def testCons(self):
        vc = VirtualChannel('id', self.c, 'name', '#ffffff')
        self.assertEqual(vc.id, 'id')
        self.assertEqual(vc.channel, self.c)
        self.assertEqual(vc.name, 'name')
        self.assertEqual(vc.color, '#ffffff')

        vc = VirtualChannel('id', self.c, color='#ffffff')
        self.assertEqual(vc.id, 'id')
        self.assertEqual(vc.channel, self.c)
        self.assertEqual(vc.name, 'spam')
        self.assertEqual(vc.color, '#ffffff')

        vc = VirtualChannel('id', self.c)
        self.assertEqual(vc.id, 'id')
        self.assertEqual(vc.channel, self.c)
        self.assertEqual(vc.name, 'spam')
        self.assertEqual(vc.color, '#ffffff')

        self.assertRaises(ValueError, VirtualChannel, 'id', (self.c, self.c))
        self.assertRaises(ValueError, VirtualChannel, 'id', self.c, color='13#57')

    def test_colors(self):
        for v, r, g, b in (
            (       13,  13,  13,  13),
            (     'on', 100, 100, 100),
            (    'off', 000, 000, 000),
            (        0,   0,   0,   0),
            (      0.5, 0.5, 0.5, 0.5),
            (      1.0, 1.0, 1.0, 1.0),
            (      100, 100, 100, 100),
            ('#000000',   0,   0,   0),
            ('#1257e2', 7.058823529411765, 34.11764705882353, 88.62745098039217),
            ('#DEADBE', 87.05882352941177, 67.84313725490196, 74.50980392156863),
        ):
            vc = VirtualChannel('id', self.c, color=v)
            self.assertEqual(vc.raw_color, (r, g, b), msg='in: {0}; out {1}; not {2}'.format(v, vc.raw_color, (r,g,b)))

        for v in (
            '#',
            'spam', 'spam.spam.spam.eggs.sausage',
            '#13#27',
            '$ffddee',
            'ffeedd',
            '#123',
            '#ddee4488',
        ):
            self.assertRaises(ValueError, VirtualChannel, 'id', self.c, color=v)

    def test_factory(self):
        self.assertRaises(ValueError, virtual_channel_factory, 'does-not-exist', id='thisOne')
