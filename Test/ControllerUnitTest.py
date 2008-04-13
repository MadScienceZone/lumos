import unittest
from Controllers          import controller_unit_factory
from ControllerUnit       import ControllerUnit
from X10ControllerUnit    import X10ControllerUnit
from LynX10ControllerUnit import LynX10ControllerUnit
from SSR48ControllerUnit  import SSR48ControllerUnit
from PowerSource          import PowerSource

class ControllerUnitTest (unittest.TestCase):
	def test_subclass_cons(self):
		p = PowerSource('testpower', amps=1)
		lynx = controller_unit_factory(type='lynx10', power=p)
		self.assert_(isinstance(lynx, ControllerUnit))
		self.assert_(isinstance(lynx, X10ControllerUnit))
		self.assert_(isinstance(lynx, LynX10ControllerUnit))
		self.assertEqual(lynx.resolution, 16)

		ssr = controller_unit_factory(type='48ssr', power=p, address=12, resolution=20)
		self.assert_(isinstance(ssr, ControllerUnit))
		self.assert_(isinstance(ssr, SSR48ControllerUnit))
		self.assertEqual(ssr.resolution, 20)
