# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/ControllersTest.py,v 1.3 2008-12-31 00:13:32 steve Exp $
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
import os
from Lumos.ControllerUnit import ControllerUnit
from Lumos.Device.Controllers import controller_unit_factory
from Lumos.Device.LynX10ControllerUnit import LynX10ControllerUnit
from Lumos.Device.LumosControllerUnit import LumosControllerUnit
from Lumos.Device.FirecrackerX10ControllerUnit import FirecrackerX10ControllerUnit

import Lumos.PowerSource
import TestNetwork

class ControllersTest (unittest.TestCase):
    def test_subclass_cons(self):
        ps = Lumos.PowerSource.PowerSource('test', 1)
        nw = TestNetwork.TestNetwork()

        u = controller_unit_factory(type='lynx10', id='lx', power_source=ps, network=nw)
        self.assert_(isinstance(u, LynX10ControllerUnit))
        self.assert_(isinstance(u, ControllerUnit))

        u = controller_unit_factory(type='cm17a', id='cm', power_source=ps, network=nw)
        self.assert_(isinstance(u, FirecrackerX10ControllerUnit))
        self.assert_(isinstance(u, ControllerUnit))

        u = controller_unit_factory(type='lumos', id='ss', power_source=ps, address=0, network=nw)
        self.assert_(isinstance(u, LumosControllerUnit))
        self.assert_(isinstance(u, ControllerUnit))

# 
# $Log: not supported by cvs2svn $
#
