#
# vi:set ai sm nu ts=4 sw=4 expandtab:
#
import unittest
from Lumos.Channel                     import Channel
from Lumos.Device.Controllers          import controller_unit_factory
from Lumos.ControllerUnit              import ControllerUnit
from Lumos.Device.X10ControllerUnit    import X10ControllerUnit
from Lumos.Device.LynX10ControllerUnit import LynX10ControllerUnit
from Lumos.Device.SSR48ControllerUnit  import SSR48ControllerUnit
from Lumos.PowerSource                 import PowerSource

class ControllerUnitTest (unittest.TestCase):
    def test_subclass_cons(self):
        p = PowerSource('testpower', amps=1)
        lynx = controller_unit_factory(type='lynx10', id='lx10', power=p, network=None)
        self.assert_(isinstance(lynx, ControllerUnit))
        self.assert_(isinstance(lynx, X10ControllerUnit))
        self.assert_(isinstance(lynx, LynX10ControllerUnit))
        self.assertEqual(lynx.resolution, 16)

        ssr = controller_unit_factory(type='48ssr', id='48', power=p, network=None, address=12, resolution=20)
        self.assert_(isinstance(ssr, ControllerUnit))
        self.assert_(isinstance(ssr, SSR48ControllerUnit))
        self.assertEqual(ssr.resolution, 20)
        self.assertEqual(ssr.id, '48')

    def test_add_channel_dict(self):
        p = PowerSource('testpower', amps=1)
        ssr = controller_unit_factory(type='48ssr', id='48', power=p, network=None, address=12, resolution=20)
        ssr.add_channel(3,load=1)
        ssr.add_channel(14,load=1)
        self.assert_(isinstance(ssr.channels,dict))
        self.assert_(3 in ssr.channels)
        self.assert_(14 in ssr.channels)
        self.assert_(5 not in ssr.channels)

    def test_add_channel_list(self):
        p = PowerSource('testpower', amps=1)
        ssr = controller_unit_factory(type='renard', id='u', power=p, network=None, address=2, resolution=32, channels=12)
        self.assert_(isinstance(ssr.channels, list))
        self.assertEqual(len(ssr.channels), 12)
        self.assert_(ssr.channels[4] is None)
        ssr.add_channel(3,load=1)
        ssr.add_channel(11,load=1)
        self.assert_(ssr.channels[3] is not None)
        self.assert_(ssr.channels[11] is not None)
        self.assert_(ssr.channels[5] is None)
        self.assert_(isinstance(ssr.channels[3], Channel))
