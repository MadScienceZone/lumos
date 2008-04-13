from ControllerUnit import ControllerUnit

class SSR48ControllerUnit (ControllerUnit):
	"""
	ControllerUnit subclass for my custom 48-channel SSR boards.
	"""
	def __init__(self, power, address, resolution=32):
		"""
		Constructor for a 48-Channel SSR board object:
			SSR48ControllerUnit(power, address, [resolution])

		Specify the correct PowerSource object for this unit and
		the unit address (0-15).  The resolution defaults to 32,
		which is correct for the 3.1 revision of the boards.
		"""

		ControllerUnit.__init__(self, power, resolution)
		self.address = int(address)
		self.type = '48-Channel SSR Controller'
		if not 0 <= self.address <= 15:
			raise ValueError, "Address %d out of range for 48-Channel SSR Controller" % self.address

	def __str__(self):
		return "%s, address=%d" % (self.type, self.address)

	def add_channel(self, id, name=None, load=None, dimmer=True, warm=None, resolution=None):
		try:
			id = int(id)
			assert 0 <= id <= 47
		except:
			raise ValueError, "48SSR channel IDs must be integers from 0-47"

		if resolution is not None:
			resolution = int(resolution)
		else:
			resolution=self.resolution

		ControllerUnit.add_channel(self, id, name, load, dimmer, warm, resolution)

    #
    # hardware protocol, for a unit with address <a>
	#  Kill all channels  1000aaaa
    #  Chan c off         1001aaaa 00cccccc
	#  Chan c on          1001aaaa 01cccccc
	#  Chan c to level v  1010aaaa 00cccccc 000vvvvv
	#  Disable admin cmds 1111aaaa 01100001

	def _proto_set_channel(self, id, old_level, new_level):
		if old_level == new_level: return ''
		if new_level is None or new_level <= 0:
			return chr(0x90 | self.address) + chr(id & 0x3f)
		elif new_level >= self.resolution-1: 
			return chr(0x90 | self.address) + chr(0x40 | (id & 0x3f))
		else:                               
			return chr(0xa0 | self.address) + chr(id & 0x3f) + chr(new_level & 0x1f)

	def set_channel(self, id, level):
		self.network.send(self._proto_set_channel(id, *self.channels[id].set_level(level)))

	def set_channel_on(self, id):
		self.network.send(self._proto_set_channel(id, *self.channels[id].set_on()))

	def set_channel_off(self, id):
		self.network.send(self._proto_set_channel(id, *self.channels[id].set_off()))

	def kill_channel(self, id):
		self.network.send(self._proto_set_channel(id, *self.channels[id].kill()))

	def kill_all_channels(self):
		for ch in self.channels:
			self.channels[ch].kill()
		self.network.send(chr(0x80 | self.address))

	def all_channels_off(self):
		for ch in self.channels:
			self.set_channel_off(ch)

	def initialize_device(self):
		self.network.send(chr(0xf0 | self.address) + chr(0x61))   # go to normal run mode
		self.kill_all_channels()
		self.all_channels_off()
