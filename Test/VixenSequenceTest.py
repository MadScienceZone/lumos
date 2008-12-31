# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/VixenSequenceTest.py,v 1.2 2008-12-31 00:13:32 steve Exp $
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
from Lumos.Extras.VixenSequence import VixenSequence, VixenChannel
#from Lumos.ChannelMap  import ChannelMap

# test for warning if EngineType != Standard?
# test for enabled/disabled channels
# test for scaling if min/max level not 0/255

class VixenSequenceTest(unittest.TestCase):
    def test_read(self):
        x = VixenSequence("data/test.vix")
        self.assertEqual(len(x.channels), 5)
        for i,n,c,e,o in (
            (0, 'A', (255,0,0), True, '0'),
            (1, 'Two', (0,255,0), True, '1'),
            (2, 'Channel 3', (0,0,255), True, '2'),
            (3, 'Di Si', (255,255,255), True, '3'),
            (4, 'Channel V', (255,0,0), True, '4')
        ):
            self.assertEqual(x.channels[i].name, n)
            self.assertEqual(x.channels[i].color, c)
            self.assertEqual(x.channels[i].enabled, e)
            self.assertEqual(x.channels[i].output, o)

        self.assertEqual(x.total_time, 25208)
        self.assertEqual(x.audio_filename, 'v_clip.mp3')
        self.assertEqual(x.min_val, 0)
        self.assertEqual(x.max_val, 255)
        self.assertEqual(x.events, [
            # channel 0
            (0,0,0),
            (2250,0,255),
            (2500,0,0),
            (7250,0,255),
            (7500,0,0),
            (9250,0,255),
            (9500,0,0),
            (11000,0,255),
            (11250,0,0),
            (12750,0,255),
            (13000,0,0),
            (14750,0,255),
            (15000,0,0),
            (15500,0,255),
            (15750,0,0),
            (16000,0,255),
            (16250,0,0),
            (17250,0,255),
            (17500,0,0),
            # channel 1
            (0,1,0),
            (250,1,23),
            (500,1,46),
            (750,1,69),
            (1000,1,92),
            (1250,1,115),
            (1500,1,139),
            (1750,1,162),
            (2000,1,185),
            (2250,1,208),
            (2500,1,231),
            (2750,1,255),
            (3250,1,218),
            (3500,1,182),
            (3750,1,145),
            (4000,1,109),
            (4250,1,72),
            (4500,1,36),
            (4750,1,0),
            # channel 2
            (0,2,0),
            # channel 3
            (0,3,0),
            (750,3,255),
            (1000,3,0),
            (2250,3,255),
            (2500,3,0),
            (4500,3,255),
            (5000,3,0),
            (9500,3,255),
            (9750,3,0),
            (11750,3,255),
            (12000,3,0),
            (13500,3,255),
            (14500,3,0),
            # channel 4
            (0,4,0),
            (1000,4,255),
            (1250,4,0),
            (5250,4,255),
            (5500,4,0),
            (15500,4,255),
            (15750,4,0),
        ])

    def test_cons(self):
        c = VixenChannel('foo', (1,2,3), True, '0')
        d = VixenChannel('bar', -1, "True", '2')
        e = VixenChannel('baz', -65536, 'False', '3')

        self.assertEqual(c.name, 'foo')
        self.assertEqual(d.name, 'bar')
        self.assertEqual(e.name, 'baz')

        self.assertEqual(c.color, (1,2,3))
        self.assertEqual(d.color, (255,255,255))
        self.assertEqual(e.color, (255,0,0))

        self.assert_(c.enabled)
        self.assert_(d.enabled)
        self.assert_(not e.enabled)

        self.assertEqual(c.output, '0')
        self.assertEqual(d.output, '2')
        self.assertEqual(e.output, '3')
# 
# $Log: not supported by cvs2svn $
#
