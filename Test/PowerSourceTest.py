import unittest
from PowerSource import PowerSource

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
