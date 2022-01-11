#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/ControllerUnitTest.py,v 1.5 2008-12-31 00:13:32 steve Exp $
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
from Lumos.Channel                     import Channel
from Lumos.Device.Controllers          import controller_unit_factory
from Lumos.ControllerUnit              import ControllerUnit
from Lumos.Device.X10ControllerUnit    import X10ControllerUnit
from Lumos.Device.LynX10ControllerUnit import LynX10ControllerUnit
from Lumos.Device.LumosControllerUnit  import LumosControllerUnit
from Lumos.PowerSource                 import PowerSource

class ControllerUnitTest (unittest.TestCase):
    def test_subclass_cons(self):
        p = PowerSource('testpower', amps=1)
        lynx = controller_unit_factory(type='lynx10', id='lx10', power_source=p, network=None)
        self.assertTrue(isinstance(lynx, ControllerUnit))
        self.assertTrue(isinstance(lynx, X10ControllerUnit))
        self.assertTrue(isinstance(lynx, LynX10ControllerUnit))
        self.assertEqual(lynx.resolution, 16)

        ssr = controller_unit_factory(type='lumos', id='48', power_source=p, network=None, address=12, resolution=256)
        self.assertTrue(isinstance(ssr, ControllerUnit))
        self.assertTrue(isinstance(ssr, LumosControllerUnit))
        self.assertEqual(ssr.resolution, 256)
        self.assertEqual(ssr.id, '48')

    def test_add_channel_dict(self):
        p = PowerSource('testpower', amps=1)
        ssr = controller_unit_factory(type='lumos', id='48', power_source=p, network=None, address=12, resolution=128)
        ssr.add_channel(3,load=1)
        ssr.add_channel(14,load=1)
        self.assertTrue(isinstance(ssr.channels,dict))
        self.assertTrue(3 in ssr.channels)
        self.assertTrue(14 in ssr.channels)
        self.assertTrue(5 not in ssr.channels)

    def test_add_channel_list(self):
        p = PowerSource('testpower', amps=1)
        ssr = controller_unit_factory(type='renard', id='u', power_source=p, network=None, address=2, resolution=32, num_channels=12)
        self.assertTrue(isinstance(ssr.channels, list))
        self.assertEqual(len(ssr.channels), 12)
        self.assertTrue(ssr.channels[4] is None)
        ssr.add_channel(3,load=1)
        ssr.add_channel(11,load=1)
        self.assertTrue(ssr.channels[3] is not None)
        self.assertTrue(ssr.channels[11] is not None)
        self.assertTrue(ssr.channels[5] is None)
        self.assertTrue(isinstance(ssr.channels[3], Channel))
# 
# $Log: not supported by cvs2svn $
#
