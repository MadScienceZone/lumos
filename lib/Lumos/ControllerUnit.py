from Channel import Channel

class ControllerUnit (object):
	"""
	Generic controller unit virtual class.  Don't create these directly; 
	derive a subclass describing some real type of hardware device.  
	This class describes attributes and behaviors common to all controller 
	unit types.
	"""
	def __init__(self, power, resolution=100):
		"""
		Constructor for basic controller units.

		ControllerUnit(power, [resolution])

		power:       a PowerSource instance describing the power 
		             feed for this unit.
		resolution:  default dimmer resolution for channels of this 
		             device. [def=100]
		"""
		self.powerSource = power
		self.channels = {}
		self.resolution = resolution

	def add_channel(self, id, name=None, load=None, dimmer=True, warm=None, resolution=None):
		"""
		Add an active channel for this controller.
		   add_channel(id, [name], [load], [dimmer], [warm], [resolution])

		This constructs a channel object of the appropriate type and 
		adds it to this controller unit.  This may be of the the base 
		Channel class, or it may be something derived from that if the 
		controller has special channel features.  The parameters are 
		the same as for the Channel object constructor.

		The resolution parameter will default to the value specified to 
		the ControllerUnit constructor.
		"""

		if resolution is None: resolution = self.resolution
		self.channels[id] = Channel(id, name, load, dimmer, warm, resolution)

	def set_channel(self, id, level):
		raise NotImplementedError, "Subclasses of ControllerUnit must define their own set_channel method."

	def set_channel_on(self, id):
		raise NotImplementedError, "Subclasses of ControllerUnit must define their own set_channel_on method."

	def set_channel_off(self, id):
		raise NotImplementedError, "Subclasses of ControllerUnit must define their own set_channel_off method."

	def kill_channel(self, id):
		raise NotImplementedError, "Subclasses of ControllerUnit must define their own kill_channel method."

	def kill_all_channels(self):
		raise NotImplementedError, "Subclasses of ControllerUnit must define their own kill_all_channels method."

	def all_channels_off(self):
		raise NotImplementedError, "Subclasses of ControllerUnit must define their own all_channels_off method."

	def initialize_device(self):
		raise NotImplementedError, "Subclasses of ControllerUnit must define their own initialize_device method."
