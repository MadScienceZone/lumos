# vi:set ts=4 sw=4 ai sm expandtab nu:
import unittest, quopri
from Lumos.Device.Olsen595ControllerUnit import Olsen595ControllerUnit
from Lumos.PowerSource                   import PowerSource
from TestNetwork                         import TestParallelNetwork

class Olsen595ControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestParallelNetwork()
        p = PowerSource('testpower', amps=1)
        self.ssr = Olsen595ControllerUnit('o595', p, network=self.n, channels=8)
        self.ssr.add_channel(0, load=.3)
        self.ssr.add_channel(1, load=1)
        self.ssr.add_channel(2, load=.3)
        self.ssr.add_channel(3, load=1)

    def tearDown(self):
        self.ssr = None
        self.n = None

    def testFirstInit(self):
        self.ssr.initialize_device()
        self.assertEqual(self.n.buffer, "00000000X")

    def test_unit_id(self):
        self.assertEqual(self.ssr.id, 'o595')

    def testInit(self):
        self.ssr.kill_all_channels()
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '00000000X')

    def testBufferedIO(self):
        self.assertEqual(self.n.buffer, '')
        self.ssr.initialize_device()
        self.assertEqual(self.n.buffer, '00000000X')
        self.n.reset()
        self.ssr.add_channel(4, load=1)
        self.ssr.add_channel(5, load=1)
        self.ssr.add_channel(7, load=1)
        self.ssr.set_channel_on(7)
        self.ssr.set_channel_on(4)
        self.assertEqual(self.n.buffer, '')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '00001001X')
        self.ssr.set_channel_off(7)
        self.ssr.set_channel_on(0)
        self.assertEqual(self.n.buffer, '00001001X')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '00001001X10001000X')
        self.ssr.set_channel(5, 0x66)
        self.assertEqual(self.n.buffer, '00001001X10001000X')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '00001001X10001000X10001100X')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '00001001X10001000X10001100X')
        self.n.reset()
        self.assertEqual(self.n.buffer, '')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '')

    def testOnOff(self):
        self.ssr.set_channel_on(2)
        self.ssr.set_channel_on(3)
        self.ssr.set_channel_off(0)
        self.ssr.set_channel_off(2)
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '00010000X')

    def testDimmer(self):
        self.ssr.set_channel(0, None)
        self.ssr.set_channel(0, 15)
        self.ssr.set_channel(2, 15)
        self.ssr.set_channel(2, 0x31)
        self.ssr.set_channel(2, 0x30)
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '10100000X')
    
    # test that it doesn't send redundant changes
    def test_iterator(self):
        self.assertEquals(sorted(self.ssr.iter_channels()), range(8))
