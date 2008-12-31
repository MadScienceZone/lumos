# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/PowerSourceTest.py,v 1.3 2008-12-31 00:13:32 steve Exp $
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
from Lumos.PowerSource import PowerSource

class PowerSourceTest (unittest.TestCase):
	def testCons(self):
		p1 = PowerSource('p1', amps=20, gfci=True)
		p2 = PowerSource('p2', amps=15, gfci=False)
		p3 = PowerSource('p3', amps=5)

		self.assertEquals(p1.amps, 20)
		self.assertEquals(p2.amps, 15)
		self.assertEquals(p3.amps, 5)
		self.assert_(p1.gfci)
		self.assert_(not p2.gfci)
		self.assert_(not p3.gfci)
		self.assertEquals(p1.id, 'p1')

	def testBadGFCI(self):
		self.assertRaises(ValueError, PowerSource, 'x', 20, 'yes')
		self.assertRaises(ValueError, PowerSource, 'x', 20, 'no')
		self.assertRaises(ValueError, PowerSource, 'x', 20, None)
# 
# $Log: not supported by cvs2svn $
#
