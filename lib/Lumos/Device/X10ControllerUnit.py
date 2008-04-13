from ControllerUnit import ControllerUnit

class X10ControllerUnit (ControllerUnit):
	def __init__(self, power, resolution=16):
		ControllerUnit.__init__(self, power)
		self.type = 'X-10 Controller'
		self.resolution = resolution

	def __str__(self):
		return self.type

	def add_channel(self, id, name=None, load=None, dimmer=True, warm=None, resolution=None):
		try:
			id = id.upper().strip()
			assert('A' <= id[0] <= 'P')
			assert(1 <= int(id[1:]) <= 16)
		except:
			raise ValueError, "X-10 channels must be 'A1'..'P16'"

		if resolution is not None:
			resolution = int(resolution)
		else:
			resolution = self.resolution

		ControllerUnit.add_channel(self, id, name, load, dimmer, warm, resolution)
