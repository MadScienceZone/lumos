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
		p1 = PowerSource('p1', amps=20)
		p2 = PowerSource('p2', amps=15)
		p3 = PowerSource('p3', amps=5)

		self.assertEqual(p1.amps, 20)
		self.assertEqual(p2.amps, 15)
		self.assertEqual(p3.amps, 5)
		self.assertEqual(p1.id, 'p1')

# 
# $Log: not supported by cvs2svn $
#
