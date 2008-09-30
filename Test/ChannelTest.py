import unittest
from Lumos.Channel import Channel, DimmerError

class ChannelTest (unittest.TestCase):
	def testCons(self):
		ch = Channel('id', name='ch', load=3, dimmer=True, warm=20)
		self.assertEqual(ch.name, 'ch')
		self.assertEqual(ch.load, 3)
		self.assert_(ch.dimmer)
		self.assertEqual(ch.warm, 19)
		self.assertEqual(ch.resolution, 100)
		self.assertEqual(ch.level, None)
		self.assertEqual(ch.set_off(), (None, 19))
		self.assertEqual(ch.level, 19)

		ch = Channel('id', name='ch', load=3, dimmer=False)
		self.assertEqual(ch.name, 'ch')
		self.assertEqual(ch.load, 3)
		self.assert_(not ch.dimmer)
		self.assertEqual(ch.warm, None)
		self.assertEqual(ch.level, None)

		ch2 = Channel('id2', load=2.3)
		self.assertEqual(ch2.name, 'Channel id2')
		self.assertEqual(ch2.load, 2.3)
		self.assert_(ch2.dimmer)
		self.assertEqual(ch2.warm, None)
		self.assertEqual(ch.level, None)

		self.assertRaises(ValueError, Channel, 'id3')

	def testInvalidDimmer(self):
		self.assertRaises(DimmerError, Channel, 'id', load=2, dimmer=False, warm=20)

	def testResolution(self):
		ch = Channel('ch', load=1, dimmer=True, resolution=32)
		self.assertEqual(ch.raw_dimmer_value(0), 0)
		self.assertEqual(ch.raw_dimmer_value(100), 31)
		self.assertEqual(ch.raw_dimmer_value(50), 15)

		self.assertEqual(ch.pct_dimmer_value(0), 0)
		self.assertEqual(ch.pct_dimmer_value(31), 100)
		self.assertEqual(ch.pct_dimmer_value(15), 48)

	def testLevel(self):
		ch = Channel('ch', load=1, dimmer=True, warm=10, resolution=100)
		self.assertEqual(ch.level, None)
		ch.set_off()
		self.assertEqual(ch.level, 9)
		for i,o in (-5,9), (0,9), (5,9), (10,10), (50,50), (75,75), (80,80), (100,99), (101,99):
			ch.set_level(i)
			self.assertEqual(ch.level, o)
	

	def testLevel2(self):
		ch = Channel('ch', load=1, dimmer=True, warm=10, resolution=48)
		ch.kill()
		self.assertEqual(ch.level, None)
		ch.set_off()
		self.assertEqual(ch.level, 4)
		ch.set_on()
		self.assertEqual(ch.level, 47)
		ch.set_level(36)
		self.assertEqual(ch.level, 36)

	def testLevelChange(self):
		ch = Channel('ch', load=1, dimmer=True, warm=10, resolution=48)
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
