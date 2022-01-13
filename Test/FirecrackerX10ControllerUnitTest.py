#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/FirecrackerX10ControllerUnitTest.py,v 1.5 2008-12-31 00:13:32 steve Exp $
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
import unittest
from Lumos.Device.FirecrackerX10ControllerUnit \
                                    import FirecrackerX10ControllerUnit
from Lumos.Device.X10ControllerUnit import X10ControllerUnit
from Lumos.ControllerUnit           import ControllerUnit
from Lumos.PowerSource              import PowerSource
from TestNetwork                    import TestNetwork

def P(data):
    stream = b''
#    print(f"P({data})")
    for i in data:
#        print(f" i={i}")
        stream += b"=D5=AA" + i + b"=AD"
#    print(f"->{stream}")
    return stream

def PP(data):
#    print(f"PP({data})")
#    print("->", data.replace(b'=\n', b''))
    return data.replace(b'=\n', b'')

class FirecrackerX10ControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=1)
        self.fc = FirecrackerX10ControllerUnit('testFC', p, network=self.n)
        self.fc.add_channel('A1', load=.3)
        self.fc.add_channel('A2', load=1)
        self.fc.add_channel('B7', load=.3, warm=10)
        self.fc.add_channel('M16', load=1, dimmer=False)

    def tearDown(self):
        self.fc = None
        self.n = None

    def testCons(self):
        self.assertEqual(self.fc.type, 'X-10 CM17a "Firecracker" Controller')
        self.assertEqual(str(self.fc), 'X-10 CM17a "Firecracker" Controller')
        self.assertEqual(self.fc.resolution, 21)
        self.assertTrue(isinstance(self.fc, FirecrackerX10ControllerUnit))
        self.assertTrue(isinstance(self.fc, X10ControllerUnit))
        self.assertTrue(isinstance(self.fc, ControllerUnit))

    def test_unit_id(self):
        "In response to a design change (controller units should track their own ID)."
        self.assertEqual(self.fc.id, 'testFC')

    def testFirstInit(self):
        self.fc.initialize_device()
        # kill all channels + level-set dimmers
        # a1   a2   b7   m16 off, b7 on, b7->10%
        # 6020 6030 7068 0478     7048 (18x) 7098
        #  `sp  ` 0  p h    x      p H (18x)  p 
        print(f"buf={self.n.buffer}")

        self.assertEqual(PP(self.n.buffer), 
           P([
               b'` ',
               b'`0',
               b'ph',
               b'=04x',
               b'pH'
           ] + (18 * [b'p=98'])))

    def testInit(self):
        self.fc.kill_all_channels()
        self.assertEqual(PP(self.n.buffer), b'')
        self.fc.set_channel_on('A1')
        self.fc.set_channel_on('B7')
        # 6000 7048
        #  `    p H
        self.assertEqual(PP(self.n.buffer), P((b'`=00',b'pH')))
        self.n.reset()
        self.fc.kill_all_channels()
        self.assertEqual(PP(self.n.buffer), P([b'` ',b'ph']))

    def testOnOff(self):
        self.fc.set_channel_on('A2')
        self.fc.set_channel_on('M16')
        self.fc.set_channel_off('M16')
        self.fc.set_channel_off('A2')
        # on a2 m16     off m16 a2
        # 6010 0458        0478 6030
        #  `      X           x  ` 0
        self.assertEqual(PP(self.n.buffer), P([b'`=10',b'=04X',b'=04x',b'`0']))

    def test_iterator(self):
        self.assertEqual(sorted(self.fc.iter_channels()), ['A1','A2','B7','M16'])
# 
# $Log: not supported by cvs2svn $
#
