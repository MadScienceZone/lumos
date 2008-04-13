from X10ControllerUnit import X10ControllerUnit

class LynX10ControllerUnit (X10ControllerUnit):
	def __init__(self, power, resolution=16):
		X10ControllerUnit.__init__(self, power, resolution)
		self.type = 'LynX-10/TW523 Controller'
