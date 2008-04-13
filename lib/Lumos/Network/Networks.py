from SerialNetwork         import SerialNetwork

#
# List of supported network drivers, mapping the name as used
# in the show.conf file (and other interfaces) to the actual
# class implementing the driver for that network.
#
supported_network_types = {
    'serial': SerialNetwork,
}

def network_factory(type, **kwargs):
    "Create and return a network object of the requested type."

    type = type.lower().strip()
    if type not in supported_network_types:
        raise ValueError, "Invalid network/protocol type '%s'" % type

    return supported_network_types[type](**kwargs)
