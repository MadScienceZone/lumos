import unittest
from SSR48ControllerUnit  import SSR48ControllerUnit
from PowerSource          import PowerSource

class SSR48ControllerUnitTest (unittest.TestCase):
	def setUp(self):
		p = PowerSource('testpower', amps=1)
		self.ssr = SSR48ControllerUnit(p, address=12)
		self.ssr.add_channel(0, load=.3)
		self.ssr.add_channel(1, load=1)
		self.ssr.add_channel(2, load=.3, warm=10)
		self.ssr.add_channel(3, load=1, dimmer=False)

	def tearDown(self):
		self.ssr = None

	def testInit(self):
		self.assertEqual(self.ssr.kill_all_channels(), "\x8c")
		self.assertEqual(self.ssr.all_channels_off(),  "\xac\x02\x03")

	def testOnOff(self):
		self.assertEqual(self.ssr.set_channel_on(2), "\x9c\x42")
		self.assertEqual(self.ssr.set_channel_on(3), "\x9c\x43")
		self.assertEqual(self.ssr.set_channel_off(0), "")
		self.assertEqual(self.ssr.set_channel_off(2), "\xac\x02\x03")
	
	def testDimmer(self):
		self.assertEqual(self.ssr.set_channel(0, None),"")
		self.assertEqual(self.ssr.set_channel(0, 15),  "\xac\x00\x0f")
		self.assertEqual(self.ssr.set_channel(2, 15),  "\xac\x02\x0f")
		self.assertEqual(self.ssr.set_channel(2, 31),  "\x9c\x42")
		self.assertEqual(self.ssr.set_channel(2, 30),  "\xac\x02\x1e")
	
	def testWarm(self):
		self.assertEqual(self.ssr.all_channels_off(),  "\xac\x02\x03")
		for i,j in ((1,''), (0,''), (2,''), (3,''), (4,4), (0,3), (5,5),(2,3),
			(6,6),(7,7),(3,3),(8,8),(10,10),(20,20),(30,30)):
			result = self.ssr.set_channel(2, i)
			if j == '':
				self.assertEqual(result, "", "set_channel(2, %d) -> %s, expected nothing" % (i,`result`) )
			else:
				self.assertEqual(result, "\xac\x02%c" % chr(j), "set_channel(2, %d) -> %s, expected %x" % (i,`result`,j) )

	def testFirstInit(self):
		self.assertEqual(self.ssr.initialize_device(), "\xfc\x61\x8c\xac\x02\x03")
