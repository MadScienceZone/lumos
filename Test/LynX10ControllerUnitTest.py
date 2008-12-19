# vi:set ai sm nu ts=4 sw=4 expandtab:
import unittest, quopri
from Lumos.Device.LynX10ControllerUnit import LynX10ControllerUnit
from Lumos.Device.X10ControllerUnit    import X10ControllerUnit
from Lumos.ControllerUnit              import ControllerUnit
from Lumos.PowerSource                 import PowerSource
from TestNetwork                       import TestNetwork

class LynX10ControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=12)
        self.x10 = LynX10ControllerUnit('LX', p, network=self.n)
        self.x10.add_channel('A1', load=.3)
        self.x10.add_channel('A2', load=1)
        self.x10.add_channel('B7', load=.3, warm=20)
        self.x10.add_channel('M16', load=1, dimmer=False)

    def tearDown(self):
        self.x10 = None
        self.n = None

    def test_unit_id(self):
        self.assertEqual(self.x10.id, 'LX')

    def testCons(self):
        self.assertEqual(self.x10.type, 'LynX-10/TW523 Controller')
        self.assertEqual(str(self.x10), 'LynX-10/TW523 Controller')
        self.assertEqual(self.x10.resolution, 16)
        self.assert_(isinstance(self.x10, LynX10ControllerUnit))
        self.assert_(isinstance(self.x10, X10ControllerUnit))
        self.assert_(isinstance(self.x10, ControllerUnit))

    def testFirstInit(self):
        self.x10.initialize_device()
        # reset + all off + level-set dimmers
        self.assertEqual(self.n.buffer, "R\rM00=3D02\rF4\rN016\rD01C\r")

    def textIdTranslation(self):
        self.assertEqual(self.x10._x10_to_lynx_id('A1'), '00')
        self.assertEqual(self.x10._x10_to_lynx_id('B1'), '10')
        self.assertEqual(self.x10._x10_to_lynx_id('P1'), 'F0')
        self.assertEqual(self.x10._x10_to_lynx_id('P16'),'FF')

    def testInit(self):
        self.x10.kill_all_channels()
        self.x10.all_channels_off()
        self.assertEqual(self.n.buffer, 'F4\rN016\rD01C\r')

    def testOnOff(self):
        self.x10.set_channel_on('A1')
        self.x10.set_channel_on('A2')
        self.x10.set_channel_off('A2')
        self.x10.set_channel_off('B7')
        self.assertEqual(self.n.buffer, 'N000\rN001\rF001\rN016\rD01C\r')
 
    def testDimmer(self):
        self.x10.set_channel('A1', None)
        self.x10.set_channel('A1', 8)
        self.x10.set_channel('A2', 8)
        self.x10.set_channel('A2', 15)
        self.x10.set_channel('A2', 14)
        self.assertEqual(self.n.buffer, 'N000\rD007\rN001\rD007\rN001\rD107\rN001\rD001\r')
   
    def testWarm(self):
        self.x10.all_channels_off()
        self.assertEqual(self.n.buffer, 'N016\rD01C\r')
 
        for i,j in ((1,''), (0,''), (2,''), (3,''), (4,'111'), (0,'011'), (5,'112'),(2,'012'),
            (6,'113'),(7,'111'),(3,'014'),(8,'115'),(10,'112'),(14,'114'),(15,'111')):
            self.n.reset()
            self.x10.set_channel('B7', i)
            if j == '':
                self.assertEqual(self.n.buffer, "", "set_channel('B7', %d) -> %s, expected nothing" % (i,self.n.buffer) )
            else:
                self.assertEqual(self.n.buffer, "N016\rD%s\r" % j, 
                    "set_channel('B7', %d) -> %s, expected ...D%s" % (i,self.n.buffer,j) )

    def test_iterator(self):
        self.assertEquals(sorted(self.x10.iter_channels()), ['A1','A2','B7','M16'])
