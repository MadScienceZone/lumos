# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/RenardControllerUnitTest.py,v 1.4 2008-12-31 00:13:32 steve Exp $
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
from Lumos.Device.RenardControllerUnit import RenardControllerUnit
from Lumos.PowerSource                 import PowerSource
from TestNetwork                       import TestNetwork

class RenardControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=1)
        self.ssr = RenardControllerUnit('ren', p, address=2, network=self.n, num_channels=8)
        self.ssr.add_channel(0, load=.3)
        self.ssr.add_channel(1, load=1)
        self.ssr.add_channel(2, load=.3, warm=10)
        self.ssr.add_channel(3, load=1, dimmer=False)

    def tearDown(self):
        self.ssr = None
        self.n = None

    def test_unit_id(self):
        self.assertEqual(self.ssr.id, 'ren')

    def testInit(self):
        self.ssr.kill_all_channels()
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=00=00=00=00')

    def testBufferedIO(self):
        self.assertEqual(self.n.buffer, '')
        self.ssr.initialize_device()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=00=00=00=00')
        self.n.reset()
        self.ssr.add_channel(4, load=1)
        self.ssr.add_channel(5, load=1)
        self.ssr.add_channel(7, load=1)
        self.ssr.set_channel_on(7)
        self.ssr.set_channel_on(4)
        self.assertEqual(self.n.buffer, '')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF')
        self.ssr.set_channel_off(7)
        self.ssr.set_channel_on(0)
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF~=82=FF=00=19=00=FF=00=00=00')
        self.ssr.set_channel(5, 0x66)
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF~=82=FF=00=19=00=FF=00=00=00')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF~=82=FF=00=19=00=FF=00=00=00~=82=FF=00=19=00=FFf=00=00')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF~=82=FF=00=19=00=FF=00=00=00~=82=FF=00=19=00=FFf=00=00')
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
        self.assertEqual(self.n.buffer, '~=82=00=00=19=FF=00=00=00=00')

    def testDimmer(self):
        self.ssr.set_channel(0, None)
        self.ssr.set_channel(0, 15)
        self.ssr.set_channel(2, 15)
        self.ssr.set_channel(2, 0x31)
        self.ssr.set_channel(2, 0x30)
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=0F=000=00=00=00=00=00')
    
    def testWarm(self):
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=00=00=00=00')

        for i,j in (
            (0x01,'~=82=00=00=19=00=00=00=00=00'), 
            (0x00,'~=82=00=00=19=00=00=00=00=00'),
            (0x02,'~=82=00=00=19=00=00=00=00=00'),
            (0x05,'~=82=00=00=19=00=00=00=00=00'),
            (0x18,'~=82=00=00=19=00=00=00=00=00'),
            (0x19,'~=82=00=00=19=00=00=00=00=00'),
            (0x20,'~=82=00=00=20=00=00=00=00=00'),
            (0x02,'~=82=00=00=19=00=00=00=00=00'),
            (0x30,'~=82=00=000=00=00=00=00=00'),
            (0x50,'~=82=00=00P=00=00=00=00=00'),
            (0x80,'~=82=00=00=80=00=00=00=00=00'),
            (0xa0,'~=82=00=00=A0=00=00=00=00=00'),
            (0xff,'~=82=00=00=FF=00=00=00=00=00'),
            (0x00,'~=82=00=00=19=00=00=00=00=00'),
            (0x50,'~=82=00=00P=00=00=00=00=00'),
        ):
            self.n.reset()
            self.ssr.set_channel(2, i)
            self.ssr.flush()
            self.assertEqual(self.n.buffer, j, "set_channel(2, %d) -> %s, expected %s" % (i,self.n.buffer,j) )

    def testEscapeCodes(self):
        self.ssr.all_channels_off()

        for i,j in (
            (0x01,'~=82=00=00=19=00=00=00=00=00'), 
            (0x7c,'~=82=00=00|=00=00=00=00=00'), 
            (0x7d,'~=82=00=00=7F/=00=00=00=00=00'), 
            (0x7e,'~=82=00=00=7F0=00=00=00=00=00'), 
            (0x7f,'~=82=00=00=7F1=00=00=00=00=00'), 
            (0x80,'~=82=00=00=80=00=00=00=00=00'), 
        ):
            self.n.reset()
            self.ssr.set_channel(2, i)
            self.ssr.flush()
            self.assertEqual(self.n.buffer, j, "set_channel(2, %d) -> %s, expected %s" % (i,self.n.buffer,j) )

    def testFirstInit(self):
        self.ssr.initialize_device()
        self.assertEqual(self.n.buffer, "~=82=00=00=19=00=00=00=00=00")

    # test that it doesn't send redundant changes
    def test_iterator(self):
        self.assertEquals(sorted(self.ssr.iter_channels()), [0, 1, 2, 3])
# 
# $Log: not supported by cvs2svn $
#
