# vi:set ai sm nu ts=4 sw=4 expandtab:
import unittest, quopri
from Lumos.Device.SSR48ControllerUnit  import SSR48ControllerUnit
from Lumos.PowerSource                 import PowerSource
from TestNetwork                       import TestNetwork

class SSR48ControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=1)
        self.ssr = SSR48ControllerUnit('ssr1', p, address=12, network=self.n)
        self.ssr.add_channel(0, load=.3)
        self.ssr.add_channel(1, load=1)
        self.ssr.add_channel(2, load=.3, warm=10)
        self.ssr.add_channel(3, load=1, dimmer=False)


    def test_unit_id(self):
        self.assertEqual(self.ssr.id, 'ssr1')

    def tearDown(self):
        self.ssr = None
        self.n = None

    def testInit(self):
        self.ssr.kill_all_channels()
        self.ssr.all_channels_off()
        self.assertEqual(self.n.buffer, '=8C=AC=02=03')

    def testOnOff(self):
        self.ssr.set_channel_on(2)
        self.ssr.set_channel_on(3)
        self.ssr.set_channel_off(0)
        self.ssr.set_channel_off(2)
        self.assertEqual(self.n.buffer, '''=9CB=9CC=AC=02=03''')

    def testDimmer(self):
        self.ssr.set_channel(0, None)
        self.ssr.set_channel(0, 15)
        self.ssr.set_channel(2, 15)
        self.ssr.set_channel(2, 31)
        self.ssr.set_channel(2, 30)
        self.assertEqual(self.n.buffer, '=AC=00=0F=AC=02=0F=9CB=AC=02=1E')
    
    def testWarm(self):
        self.ssr.all_channels_off()
        self.assertEqual(self.n.buffer, '=AC=02=03')

        for i,j in ((1,''), (0,''), (2,''), (3,''), (4,4), (0,3), (5,5),(2,3),
            (6,6),(7,7),(3,3),(8,8),(10,10),(20,20),(30,30)):
            self.n.reset()
            self.ssr.set_channel(2, i)
            if j == '':
                self.assertEqual(self.n.buffer, "", "set_channel(2, %d) -> %s, expected nothing" % (i,self.n.buffer) )
            else:
                self.assertEqual(self.n.buffer, "=AC=02%s" % quopri.encodestring(chr(j)), 
                    "set_channel(2, %d) -> %s, expected %x" % (i,self.n.buffer,j) )

    def testFirstInit(self):
        self.ssr.initialize_device()
        self.assertEqual(self.n.buffer, "=FCa=8C=AC=02=03")

    def test_iterator(self):
        self.assertEquals(sorted(self.ssr.iter_channels()), [0, 1, 2, 3])
