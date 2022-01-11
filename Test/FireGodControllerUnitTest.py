#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/FireGodControllerUnitTest.py,v 1.4 2008-12-31 00:13:32 steve Exp $
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
# vi:set ts=4 sw=4 ai sm expandtab nu:
import unittest, quopri
from Lumos.Device.FireGodControllerUnit import FireGodControllerUnit
from Lumos.PowerSource                  import PowerSource
from TestNetwork                        import TestNetwork

class FireGodControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=1)
        self.ssr = FireGodControllerUnit('fg', p, address=2, network=self.n)
        self.ssr.add_channel(0, load=.3)
        self.ssr.add_channel(1, load=1)
        self.ssr.add_channel(2, load=.3, warm=10)
        self.ssr.add_channel(3, load=1, dimmer=False)

    def tearDown(self):
        self.ssr = None
        self.n = None

    def test_unit_id(self):
        self.assertEqual(self.ssr.id, 'fg')

    def testInit(self):
        self.ssr.kill_all_channels()
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.assertEqual(self.n.buffer, 'U=02ddnddddddddddddddddddddddddddddd')

    def testBufferedIO(self):
        self.assertEqual(self.n.buffer, '')
        self.ssr.initialize_device()
        self.assertEqual(self.n.buffer, 'U=02ddnddddddddddddddddddddddddddddd')
        self.n.reset()
        self.ssr.add_channel(4, load=1)
        self.ssr.add_channel(5, load=1)
        self.ssr.add_channel(7, load=1)
        self.ssr.set_channel_on(7)
        self.ssr.set_channel_on(4)
        self.assertEqual(self.n.buffer, '')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, 'U=02ddnd=C8dd=C8dddddddddddddddddddddddd')
        self.ssr.set_channel_off(7)
        self.ssr.set_channel_on(0)
        self.assertEqual(self.n.buffer, 'U=02ddnd=C8dd=C8dddddddddddddddddddddddd')
        self.n.reset()
        self.ssr.flush()
        self.assertEqual(self.n.buffer, 'U=02=C8dnd=C8ddddddddddddddddddddddddddd')
        self.ssr.set_channel(5, 75)
        self.assertEqual(self.n.buffer, 'U=02=C8dnd=C8ddddddddddddddddddddddddddd')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, 'U=02=C8dnd=C8dddddddddddddddddddddddddddU=02=C8dnd=C8=AFdddddddddddddddddddddddddd')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, 'U=02=C8dnd=C8dddddddddddddddddddddddddddU=02=C8dnd=C8=AFdddddddddddddddddddddddddd')
        self.n.reset()
        self.assertEqual(self.n.buffer, '')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '')
        

    def testOnOff(self):
        self.ssr.set_channel_on(2)
        self.ssr.set_channel_on(3)
        self.ssr.set_channel_off(0)
        self.ssr.set_channel_off(2)
        self.ssr.flush()
        self.assertEqual(self.n.buffer, 'U=02ddn=C8dddddddddddddddddddddddddddd')

    def testDimmer(self):
        self.ssr.set_channel(0, None)
        self.ssr.set_channel(0, 15)
        self.ssr.set_channel(2, 15)
        self.ssr.set_channel(2, 31)
        self.ssr.set_channel(2, 30)
        self.ssr.flush()
        self.assertEqual(self.n.buffer, 'U=02sd=82ddddddddddddddddddddddddddddd')
    
    def testWarm(self):
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.assertEqual(self.n.buffer, 'U=02ddnddddddddddddddddddddddddddddd')

        for i,j in (
            (  1, 'U=02ddnddddddddddddddddddddddddddddd'),
            (  2, 'U=02ddnddddddddddddddddddddddddddddd'),
            (  5, 'U=02ddnddddddddddddddddddddddddddddd'),
            (  9, 'U=02ddnddddddddddddddddddddddddddddd'),
            ( 10, 'U=02ddnddddddddddddddddddddddddddddd'),
            ( 11, 'U=02ddoddddddddddddddddddddddddddddd'),
            (  2, 'U=02ddnddddddddddddddddddddddddddddd'),
            ( 30, 'U=02dd=82ddddddddddddddddddddddddddddd'),
            ( 50, 'U=02dd=96ddddddddddddddddddddddddddddd'),
            ( 80, 'U=02dd=B4ddddddddddddddddddddddddddddd'),
            ( 99, 'U=02dd=C7ddddddddddddddddddddddddddddd'),
            (100, 'U=02dd=C8ddddddddddddddddddddddddddddd'),
            (  0, 'U=02ddnddddddddddddddddddddddddddddd'),
            ( 50, 'U=02dd=96ddddddddddddddddddddddddddddd')
        ):
            self.n.reset()
            self.ssr.set_channel(2, i)
            self.ssr.flush()
            self.assertEqual(self.n.buffer, j, "set_channel(2, %d) -> %s, expected %s" % (i,self.n.buffer,j) )

    def testFirstInit(self):
        self.ssr.initialize_device()
        self.assertEqual(self.n.buffer, 'U=02ddnddddddddddddddddddddddddddddd')

    # test that it doesn't send redundant changes
    def test_iterator(self):
        self.assertEqual(sorted(self.ssr.iter_channels()), [0, 1, 2, 3])
# 
# $Log: not supported by cvs2svn $
#
