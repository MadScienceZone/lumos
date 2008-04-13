import unittest
from FirecrackerX10ControllerUnit  import FirecrackerX10ControllerUnit
from PowerSource                   import PowerSource

def P(data):
	stream = ''
	for i in data:
		stream += "\xd5\xaa" + i + "\xad"
	return stream

class FirecrackerX10ControllerUnitTest (unittest.TestCase):
	def setUp(self):
		p = PowerSource('testpower', amps=1)
		self.fc = FirecrackerX10ControllerUnit(p)
		self.fc.add_channel('A1', load=.3)
		self.fc.add_channel('A2', load=1)
		self.fc.add_channel('B1', load=.3, warm=10)
		self.fc.add_channel('B2', load=1, dimmer=False)

	def tearDown(self):
		self.fc = None

	def testInit(self):
		self.assertEqual(self.fc.kill_all_channels(), '')
		self.assertEqual(self.fc.all_channels_off(),  P(('\x70\x00',)) + (18 * P(('\x70\x98',))))

	def testInitDev(self):
		self.assertEqual(self.fc.initialize_device(), P(('\x60\x20','\x60\x30','\x70\x20','\x70\x30','\x70\x00')) + (18 * P(('\x70\x98',))))

#	def testOnOff(self):
#		self.assertEqual(self.ssr.setChannelOn(2), "\x9c\x42")Error: testInit (FirecrackerX10ControllerUnitTest.FirecrackerX10ControllerUnitTest)
#		self.assertEqual(self.ssr.setChannelOn(3), "\x9c\x43")
#		self.assertEqual(self.ssr.setChannelOff(0), "\x9c\x00")
#		self.assertEqual(self.ssr.setChannelOff(2), "\xac\x02\x03")
#	
#	def testDimmer(self):
#		self.assertEqual(self.ssr.setChannel(0, 0),   "\x9c\x00")
#		self.assertEqual(self.ssr.setChannel(0, 15),  "\xac\x00\x0f")
#		self.assertEqual(self.ssr.setChannel(2, 15),  "\xac\x02\x0f")
#		self.assertEqual(self.ssr.setChannel(2, 31),  "\x9c\x42")
#		self.assertEqual(self.ssr.setChannel(2, 30),  "\xac\x02\x1e")
#	
#	def testWarm(self):
#		self.assertEqual(self.ssr.allChannelsOff(),  "\x9c\x00\x9c\x01\xac\x02\x03\x9c\x03")
#		for i,j in ((0,3), (1,3), (2,3), (3,3), (4,4), (5,5),
#			(6,6),(7,7),(8,8),(10,10),(20,20),(30,30)):
#			self.assertEqual(self.ssr.setChannel(2, i), "\xac\x02%c" % chr(j), "setChannel(2, %d)" % i)
