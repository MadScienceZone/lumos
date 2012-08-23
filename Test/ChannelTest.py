# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/ChannelTest.py,v 1.3 2008-12-31 00:13:32 steve Exp $
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
from Lumos.Channel import Channel, DimmerError

class ChannelTest (unittest.TestCase):
    def SetUp(self):
        self.power = PowerSource('ps')

	def testCons(self):
		ch = Channel('id', name='ch', load=3, dimmer=True, warm=20, power=self.power)
		self.assertEqual(ch.name, 'ch')
		self.assertEqual(ch.load, 3)
		self.assert_(ch.dimmer)
		self.assertEqual(ch.warm, 19)
		self.assertEqual(ch.resolution, 100)
		self.assertEqual(ch.level, None)
		self.assertEqual(ch.set_off(), (None, 19))
		self.assertEqual(ch.level, 19)

		ch = Channel('id', name='ch', load=3, dimmer=False, power=self.power)
		self.assertEqual(ch.name, 'ch')
		self.assertEqual(ch.load, 3)
		self.assert_(not ch.dimmer)
		self.assertEqual(ch.warm, None)
		self.assertEqual(ch.level, None)

		ch2 = Channel('id2', load=2.3, power=self.power)
		self.assertEqual(ch2.name, 'Channel id2')
		self.assertEqual(ch2.load, 2.3)
		self.assert_(ch2.dimmer)
		self.assertEqual(ch2.warm, None)
		self.assertEqual(ch.level, None)

		self.assertRaises(ValueError, Channel, 'id3')

	def testInvalidDimmer(self):
		self.assertRaises(DimmerError, Channel, 'id', load=2, dimmer=False, warm=20, power=self.power)

	def testResolution(self):
		ch = Channel('ch', load=1, dimmer=True, resolution=32, power=self.power)
		self.assertEqual(ch.raw_dimmer_value(0), 0)
		self.assertEqual(ch.raw_dimmer_value(100), 31)
		self.assertEqual(ch.raw_dimmer_value(50), 15)

		self.assertEqual(ch.pct_dimmer_value(0), 0)
		self.assertEqual(ch.pct_dimmer_value(31), 100)
		self.assertEqual(ch.pct_dimmer_value(15), 48)

	def testLevel(self):
		ch = Channel('ch', load=1, dimmer=True, warm=10, resolution=100, power=self.power)
		self.assertEqual(ch.level, None)
		ch.set_off()
		self.assertEqual(ch.level, 9)
		for i,o in (-5,9), (0,9), (5,9), (10,10), (50,50), (75,75), (80,80), (100,99), (101,99):
			ch.set_level(i)
			self.assertEqual(ch.level, o)
	

	def testLevel2(self):
		ch = Channel('ch', load=1, dimmer=True, warm=10, resolution=48, power=self.power)
		ch.kill()
		self.assertEqual(ch.level, None)
		ch.set_off()
		self.assertEqual(ch.level, 4)
		ch.set_on()
		self.assertEqual(ch.level, 47)
		ch.set_level(36)
		self.assertEqual(ch.level, 36)

	def testLevelChange(self):
		ch = Channel('ch', load=1, dimmer=True, warm=10, resolution=48, power=self.power)
		ch.kill()
		self.assertEqual(ch.set_level(0), (None,4))
		self.assertEqual(ch.set_level(0), (4,4))
		self.assertEqual(ch.set_level(47), (4,47))
		self.assertEqual(ch.set_level(15), (47,15))
		self.assertEqual(ch.set_on(), (15,47))
		self.assertEqual(ch.set_off(), (47,4))
		self.assertEqual(ch.set_on(), (4,47))
		self.assertEqual(ch.set_level(0, override_warm=True), (47,0))
		self.assertEqual(ch.kill(), (0,None))
# 
# $Log: not supported by cvs2svn $
#
