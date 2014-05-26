# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/ParallelBitNetworkTest.py,v 1.2 2008-12-31 00:13:32 steve Exp $
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
from Lumos.Network                    import NullNetwork
from Lumos.Network.Networks           import network_factory
from Lumos.Network.ParallelBitNetwork import ParallelBitNetwork
from Test                             import warn_once

class ParallelBitNetworkTest (unittest.TestCase):

    def testCons(self):
        n = network_factory(type='parbit', description='desc', port=1, open_device=False)
        if isinstance(n, NullNetwork):
            warn_once('NOPARBIT', "Skipping tests of ParallelBit networks: this machine does not support them (install PyParallel?)")
        else:
            self.assertEqual(n.description, 'desc')

    def testDefaults(self):
        n = network_factory(type='parbit', open_device=False)
        if isinstance(n, NullNetwork):
            warn_once('NOPARBIT', "Skipping tests of ParallelBit networks: this machine does not support them (install PyParallel?)")
        else:
            self.assertEqual(n.description, None)
            self.assertEqual(str(n), 'ParallelBitNetwork (port 0)')
            self.assertEqual(n.port, 0)

    def test_no_open(self):
        n = network_factory(type='parbit', open_device=False)
        if isinstance(n, NullNetwork):
            warn_once('NOPARBIT', "Skipping tests of ParallelBit networks: this machine does not support them (install PyParallel?)")
        else:
            self.assertEqual(n.dev, None)
