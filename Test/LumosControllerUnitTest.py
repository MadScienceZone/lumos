# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/SSR48ControllerUnitTest.py,v 1.5 2008-12-31 00:13:32 steve Exp $
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
import unittest, quopri
from Lumos.Device.LumosControllerUnit  import LumosControllerUnit
from Lumos.PowerSource                 import PowerSource
from TestNetwork                       import TestNetwork

class LumosControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=1)
        self.ssr = LumosControllerUnit('ssr1', p, address=12, network=self.n)
        self.ssr.add_channel(0, load=.3)
        self.ssr.add_channel(1, load=1)
        self.ssr.add_channel(2, load=.3, warm=10)
        self.ssr.add_channel(3, load=1, dimmer=False)


    def test_unit_id(self):
        self.assertEqual(self.ssr.id, 'ssr1')

    def tearDown(self):
        self.ssr = None
        self.n = None

    def testInit(self):
        self.ssr.kill_all_channels()
        self.ssr.all_channels_off()
        self.assertEqual(self.n.buffer, '=8C=AC=02=03')

    def testOnOff(self):
        self.ssr.set_channel_on(2)
        self.ssr.set_channel_on(3)
        self.ssr.set_channel_off(0)
        self.ssr.set_channel_off(2)
        self.assertEqual(self.n.buffer, '''=9CB=9CC=AC=02=03''')

    def testDimmer(self):
        self.ssr.set_channel(0, None)
        self.ssr.set_channel(0, 15)
        self.ssr.set_channel(2, 15)
        self.ssr.set_channel(2, 31)
        self.ssr.set_channel(2, 30)
        self.assertEqual(self.n.buffer, '=AC=00=0F=AC=02=0F=9CB=AC=02=1E')
    
    def testWarm(self):
        self.ssr.all_channels_off()
        self.assertEqual(self.n.buffer, '=AC=02=03')

        for i,j in ((1,''), (0,''), (2,''), (3,''), (4,4), (0,3), (5,5),(2,3),
            (6,6),(7,7),(3,3),(8,8),(10,10),(20,20),(30,30)):
            self.n.reset()
            self.ssr.set_channel(2, i)
            if j == '':
                self.assertEqual(self.n.buffer, "", "set_channel(2, %d) -> %s, expected nothing" % (i,self.n.buffer) )
            else:
                self.assertEqual(self.n.buffer, "=AC=02%s" % quopri.encodestring(chr(j)), 
                    "set_channel(2, %d) -> %s, expected %x" % (i,self.n.buffer,j) )

    def testFirstInit(self):
        self.ssr.initialize_device()
        self.assertEqual(self.n.buffer, "=FCa=8C=AC=02=03")

    def test_iterator(self):
        self.assertEquals(sorted(self.ssr.iter_channels()), [0, 1, 2, 3])
# 
# $Log: not supported by cvs2svn $
#
