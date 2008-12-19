#
# vi:set ai sm nu ts=4 sw=4 expandtab:
#
import unittest, quopri
from Lumos.Device.X10ControllerUnit  import X10ControllerUnit
from Lumos.ControllerUnit            import ControllerUnit
from Lumos.PowerSource               import PowerSource
from TestNetwork                     import TestNetwork

class X10ControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=12)
        self.x10 = X10ControllerUnit('myx10', p, network=self.n)

    def tearDown(self):
        self.x10 = None
        self.n = None

    def test_unit_id(self):
        self.assertEquals(self.x10.id, 'myx10')

    def testCons(self):
        self.assertEqual(self.x10.type, 'X-10 Controller')
        self.assertEqual(str(self.x10), 'X-10 Controller')
        self.assertEqual(self.x10.resolution, 16)
        self.assert_(isinstance(self.x10, X10ControllerUnit))
        self.assert_(isinstance(self.x10, ControllerUnit))

    def test_add_channel_noload(self):
        self.assertRaises(ValueError, self.x10.add_channel, ('a1',))

    def test_add_channel(self):
        self.x10.add_channel(' a1  ', load=1.11)
        self.assertEqual(self.x10.channels['A1'].name, 'Channel A1')
        self.assertEqual(self.x10.channels['A1'].load, 1.11)
        self.assertEqual(self.x10.channels['A1'].dimmer, True)
        self.assertEqual(self.x10.channels['A1'].resolution, 16)
        self.assertEqual(self.x10.channels['A1'].level, None)
        self.assertEqual(self.x10.channels['A1'].warm, None)

    def test_add_channel_bad_id(self):
        self.assertRaises(ValueError, self.x10.add_channel, ('123',), {'load':12})
        self.assertRaises(ValueError, self.x10.add_channel, ('P17',), {'load':12})
        self.assertRaises(ValueError, self.x10.add_channel, ('Q7',), {'load':12})

    def test_iterator(self):
        self.x10.add_channel('b7', load=1)
        self.x10.add_channel('c8', load=1)
        self.x10.add_channel('f7', load=1)
        self.x10.add_channel('m10', load=1)
        self.assertEquals(sorted(self.x10.iter_channels()), ['B7','C8','F7','M10'])
