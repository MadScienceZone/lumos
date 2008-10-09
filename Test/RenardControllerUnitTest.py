# vi:set ts=4 sw=4 ai sm expandtab nu:
import unittest, quopri
from Lumos.Device.RenardControllerUnit import RenardControllerUnit
from Lumos.PowerSource                 import PowerSource
from TestNetwork                       import TestNetwork

class RenardControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=1)
        self.ssr = RenardControllerUnit(p, address=2, network=self.n, channels=8)
        self.ssr.add_channel(0, load=.3)
        self.ssr.add_channel(1, load=1)
        self.ssr.add_channel(2, load=.3, warm=10)
        self.ssr.add_channel(3, load=1, dimmer=False)

    def tearDown(self):
        self.ssr = None
        self.n = None

    def testInit(self):
        self.ssr.kill_all_channels()
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=00=00=00=00')

    def testBufferedIO(self):
        self.assertEqual(self.n.buffer, '')
        self.ssr.initialize_device()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=00=00=00=00')
        self.n.reset()
        self.ssr.add_channel(4, load=1)
        self.ssr.add_channel(5, load=1)
        self.ssr.add_channel(7, load=1)
        self.ssr.set_channel_on(7)
        self.ssr.set_channel_on(4)
        self.assertEqual(self.n.buffer, '')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF')
        self.ssr.set_channel_off(7)
        self.ssr.set_channel_on(0)
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF~=82=FF=00=19=00=FF=00=00=00')
        self.ssr.set_channel(5, 0x66)
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF~=82=FF=00=19=00=FF=00=00=00')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF~=82=FF=00=19=00=FF=00=00=00~=82=FF=00=19=00=FFf=00=00')
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=FF=00=00=FF~=82=FF=00=19=00=FF=00=00=00~=82=FF=00=19=00=FFf=00=00')
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
        self.assertEqual(self.n.buffer, '~=82=00=00=19=FF=00=00=00=00')

    def testDimmer(self):
        self.ssr.set_channel(0, None)
        self.ssr.set_channel(0, 15)
        self.ssr.set_channel(2, 15)
        self.ssr.set_channel(2, 0x31)
        self.ssr.set_channel(2, 0x30)
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=0F=000=00=00=00=00=00')
    
    def testWarm(self):
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '~=82=00=00=19=00=00=00=00=00')

        for i,j in (
            (0x01,'~=82=00=00=19=00=00=00=00=00'), 
            (0x00,'~=82=00=00=19=00=00=00=00=00'),
            (0x02,'~=82=00=00=19=00=00=00=00=00'),
            (0x05,'~=82=00=00=19=00=00=00=00=00'),
            (0x18,'~=82=00=00=19=00=00=00=00=00'),
            (0x19,'~=82=00=00=19=00=00=00=00=00'),
            (0x20,'~=82=00=00=20=00=00=00=00=00'),
            (0x02,'~=82=00=00=19=00=00=00=00=00'),
            (0x30,'~=82=00=000=00=00=00=00=00'),
            (0x50,'~=82=00=00P=00=00=00=00=00'),
            (0x80,'~=82=00=00=80=00=00=00=00=00'),
            (0xa0,'~=82=00=00=A0=00=00=00=00=00'),
            (0xff,'~=82=00=00=FF=00=00=00=00=00'),
            (0x00,'~=82=00=00=19=00=00=00=00=00'),
            (0x50,'~=82=00=00P=00=00=00=00=00'),
        ):
            self.n.reset()
            self.ssr.set_channel(2, i)
            self.ssr.flush()
            self.assertEqual(self.n.buffer, j, "set_channel(2, %d) -> %s, expected %s" % (i,self.n.buffer,j) )

    def testEscapeCodes(self):
        self.ssr.all_channels_off()

        for i,j in (
            (0x01,'~=82=00=00=19=00=00=00=00=00'), 
            (0x7c,'~=82=00=00|=00=00=00=00=00'), 
            (0x7d,'~=82=00=00=7F/=00=00=00=00=00'), 
            (0x7e,'~=82=00=00=7F0=00=00=00=00=00'), 
            (0x7f,'~=82=00=00=7F1=00=00=00=00=00'), 
            (0x80,'~=82=00=00=80=00=00=00=00=00'), 
        ):
            self.n.reset()
            self.ssr.set_channel(2, i)
            self.ssr.flush()
            self.assertEqual(self.n.buffer, j, "set_channel(2, %d) -> %s, expected %s" % (i,self.n.buffer,j) )

    def testFirstInit(self):
        self.ssr.initialize_device()
        self.assertEqual(self.n.buffer, "~=82=00=00=19=00=00=00=00=00")

    # test that it doesn't send redundant changes
    def test_iterator(self):
        self.assertEquals(sorted(self.ssr.iter_channels()), range(8))
