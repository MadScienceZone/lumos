# vi:set ai sm nu ts=4 sw=4 expandtab:

import ConfigParser

class ChannelMap (object):
	def __init__(self):
		self.mapping = {}

	def __len__(self):
		return len(self.mapping)

	def load_file(self, filename):
		pass
