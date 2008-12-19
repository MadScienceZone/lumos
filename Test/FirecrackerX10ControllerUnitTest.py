#
# vi:set ai sm nu ts=4 sw=4 expandtab:
#
import unittest
from Lumos.Device.FirecrackerX10ControllerUnit \
                                    import FirecrackerX10ControllerUnit
from Lumos.Device.X10ControllerUnit import X10ControllerUnit
from Lumos.ControllerUnit           import ControllerUnit
from Lumos.PowerSource              import PowerSource
from TestNetwork                    import TestNetwork

def P(data):
    stream = ''
    for i in data:
        stream += "=D5=AA" + i + "=AD"
    return stream

def PP(data):
    return data.replace('=\n', '')

class FirecrackerX10ControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=1)
        self.fc = FirecrackerX10ControllerUnit('testFC', p, network=self.n)
        self.fc.add_channel('A1', load=.3)
        self.fc.add_channel('A2', load=1)
        self.fc.add_channel('B7', load=.3, warm=10)
        self.fc.add_channel('M16', load=1, dimmer=False)

    def tearDown(self):
        self.fc = None
        self.n = None

    def testCons(self):
        self.assertEqual(self.fc.type, 'X-10 CM17a "Firecracker" Controller')
        self.assertEqual(str(self.fc), 'X-10 CM17a "Firecracker" Controller')
        self.assertEqual(self.fc.resolution, 21)
        self.assert_(isinstance(self.fc, FirecrackerX10ControllerUnit))
        self.assert_(isinstance(self.fc, X10ControllerUnit))
        self.assert_(isinstance(self.fc, ControllerUnit))

    def test_unit_id(self):
        "In response to a design change (controller units should track their on ID)."
        self.assertEqual(self.fc.id, 'testFC')

    def testFirstInit(self):
        self.fc.initialize_device()
        # kill all channels + level-set dimmers
        # a1   a2   b7   m16 off, b7 on, b7->10%
        # 6020 6030 7068 0478     7048 (18x) 7098
        #  `sp  ` 0  p h    x      p H (18x)  p 
        self.assertEqual(PP(self.n.buffer), 
           P(['` ','=04x','`0','ph','pH'] + (18 * ['p=98'])))

    def testInit(self):
        self.fc.kill_all_channels()
        self.assertEqual(PP(self.n.buffer), '')
        self.fc.set_channel_on('A1')
        self.fc.set_channel_on('B7')
        # 6000 7048
        #  `    p H
        self.assertEqual(PP(self.n.buffer), P(('`=00','pH')))
        self.n.reset()
        self.fc.kill_all_channels()
        self.assertEqual(PP(self.n.buffer), P(['` ','ph']))

    def testOnOff(self):
        self.fc.set_channel_on('A2')
        self.fc.set_channel_on('M16')
        self.fc.set_channel_off('M16')
        self.fc.set_channel_off('A2')
        # on a2 m16     off m16 a2
        # 6010 0458        0478 6030
        #  `      X           x  ` 0
        self.assertEqual(PP(self.n.buffer), P(['`=10','=04X','=04x','`0']))

    def test_iterator(self):
        self.assertEquals(sorted(self.fc.iter_channels()), ['A1','A2','B7','M16'])
