import ConfigParser
from PowerSource import PowerSource
from Network     import Network
from Controllers import controller_unit_factory

def get_config_dict(conf, section, typemap, objlist=None):
	dict = {}
	for k in conf.options(section):
		if k in typemap:
			if   typemap[k] == 'int':     dict[k] = conf.getint(section, k)
			elif typemap[k] == 'float':   dict[k] = conf.getfloat(section, k)
			elif typemap[k] == 'bool':    dict[k] = conf.getboolean(section, k)
			elif typemap[k] == 'objlist': dict[k] = objlist[conf.get(section, k)]
			elif typemap[k] == 'ignore':  pass
			else:
				raise ValueError, "Invalid typemap value for %s" % section
		else:
			dict[k] = conf.get(section, k)
	return dict

class Show (object):
	'''
	This object describes and orchestrates the show.  It holds descriptions
	of the various hardware plugged in to the host computer. 

	After creating an instance of this class, call the load method to load
	a show configuration into it.  After that, the following attributes
	will be available:

		power_sources:   A dictionary of PowerSource objects, indexed by 
		                 circuit identifier as given in the show config file.

		networks:        A dictionary of Network objects, indexed by network
		                 identifier as given in the show config file.  These
						 networks will contain controller units.

		title:           The show title.
		description:     The show's descriptive text.
	'''
	def __init__(self):
		self._clear()

	def _clear(self):
		self.power_sources = {}
		self.networks = {}
		self.title = None
		self.description = None

	def load(self, file):
		'''Load up a show configuration file.  This will instantiate and
		initialize a set of power sources, networks and controllers, ready
		to begin running show sequences.  Pass in a file-like object holding
		the configuration data for the show.
		'''
		self._clear()

		show = ConfigParser.SafeConfigParser()
		show.readfp(file)
		self.title = show.get('show', 'title')
		self.description = show.get('show', 'description')
		#
		# POWER SOURCES
		#
		for source_ID in show.get('show', 'powersources').split():
			self.power_sources[source_ID] = PowerSource(source_ID, 
				**get_config_dict(show, 'power '+source_ID, {
					'amps': 'float',
					'gfci': 'bool'
				}))
		#
		# NETWORKS
		#
		for net_ID in show.get('show', 'networks').split():
			self.networks[net_ID] = Network(net_ID, **get_config_dict(show, 'net '+net_ID, {
				'baudrate': 'int',
				'bits':     'int',
				'stop':     'int',
				'xonxoff':  'bool',
				'rtscts':   'bool',
				'units':    'ignore'
			}))
			#
			# CONTROLLER UNITS
			#
			for unit_ID in show.get('net '+net_ID, 'units').split():
				unit_type = show.get('unit '+unit_ID, 'type')
				unit_args = get_config_dict(show, 'unit '+unit_ID, {
					'power': 'objlist',
					'type':  'ignore'
				}, self.power_sources)
				self.networks[net_ID].add_unit(unit_ID, controller_unit_factory(
					unit_type, **unit_args))
				#
				# CHANNELS IN CONTROLLER UNIT
				#
				for channel_ID in show.sections():
					if channel_ID.startswith('chan '+unit_ID+'.'):
						c_ID = channel_ID[len(unit_ID)+6:]
						self.networks[net_ID].units[unit_ID].add_channel(c_ID, 
							**get_config_dict(show, channel_ID, {
								'load':   'float',
								'dimmer': 'bool',
								'warm':   'int'
							}))

# XXX call initializeDevice on all controllers
# XXX startup all the comm network drivers
