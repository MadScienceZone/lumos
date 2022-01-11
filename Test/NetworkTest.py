#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/NetworkTest.py,v 1.3 2008-12-31 00:13:32 steve Exp $
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
from Lumos.Network               import Network, NullNetwork
from Lumos.Network.Networks      import network_factory
from Lumos.Network.SerialNetwork import SerialNetwork
from Test                        import warn_once

class NetworkTest (unittest.TestCase):
    def test_subclass_cons(self):
        serial = network_factory(type='serial', open_device=False)
        if isinstance(serial, NullNetwork):
            warn_once('NOSERIAL', 'Not checking serial networks: this system does not support them (install PySerial?)')
        else:
            self.assertTrue(isinstance(serial, Network))
            self.assertTrue(isinstance(serial, SerialNetwork))

    # XXX add more types here when more exist

# 
# $Log: not supported by cvs2svn $
#
