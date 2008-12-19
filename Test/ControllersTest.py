import unittest
import os
from Lumos.ControllerUnit import ControllerUnit
from Lumos.Device.Controllers import controller_unit_factory
from Lumos.Device.LynX10ControllerUnit import LynX10ControllerUnit
from Lumos.Device.SSR48ControllerUnit import SSR48ControllerUnit
from Lumos.Device.FirecrackerX10ControllerUnit import FirecrackerX10ControllerUnit

import Lumos.PowerSource
import TestNetwork

class ControllersTest (unittest.TestCase):
    def test_subclass_cons(self):
        ps = Lumos.PowerSource.PowerSource('test', 1)
        nw = TestNetwork.TestNetwork()

        u = controller_unit_factory(type='lynx10', id='lx', power=ps, network=nw)
        self.assert_(isinstance(u, LynX10ControllerUnit))
        self.assert_(isinstance(u, ControllerUnit))

        u = controller_unit_factory(type='cm17a', id='cm', power=ps, network=nw)
        self.assert_(isinstance(u, FirecrackerX10ControllerUnit))
        self.assert_(isinstance(u, ControllerUnit))

        u = controller_unit_factory(type='48ssr', id='ss', power=ps, address=0, network=nw)
        self.assert_(isinstance(u, SSR48ControllerUnit))
        self.assert_(isinstance(u, ControllerUnit))

