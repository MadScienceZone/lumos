# vi:set ai sm nu ts=4 sw=4 expandtab:
from Lumos.Network.SerialNetwork      import SerialNetwork
from Lumos.Network.SerialBitNetwork   import SerialBitNetwork
from Lumos.Network.ParallelBitNetwork import ParallelBitNetwork

#
# List of supported network drivers, mapping the name as used
# in the show.conf file (and other interfaces) to the actual
# class implementing the driver for that network.
#
supported_network_types = {
    'serial':    SerialNetwork,
    'serialbit': SerialBitNetwork,
    'parbit':    ParallelBitNetwork
}

def network_factory(type, **kwargs):
    """
	Create and return a network object of the requested type.
	Usage: network_factory(typename, [args...])
	where: typename is one of the defined keywords for a network
	       type (as usable in the show configuration file), and
		   [args] are whatever constructor arguments are applicable
		   to that type of network class.
	"""

    type = type.lower().strip()
    if type not in supported_network_types:
        raise ValueError, "Invalid network/protocol type '%s'" % type

    return supported_network_types[type](**kwargs)
