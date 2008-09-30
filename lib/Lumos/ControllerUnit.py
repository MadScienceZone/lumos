# vi:set ai sm nu ts=4 sw=4 expandtab:
from Lumos.Channel import Channel

class ControllerUnit (object):
    """
    Generic controller unit virtual class.  Don't create these directly; 
    derive a subclass describing some real type of hardware device.  
    This class describes attributes and behaviors common to all controller 
    unit types.
    """
    def __init__(self, power, network, resolution=100):
        """
        Constructor for basic controller units.
        power:       a PowerSource instance describing the power 
                     feed for this unit.
        network:     a Network instance describing the communications
                     network and protocol connected to this unit.
        resolution:  default dimmer resolution for channels of this 
                     device. [def=100]
        """
        self.power_source = power
        self.channels = {}
        self.resolution = resolution
        self.network = network

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
        raise NotImplementedError("Subclasses of ControllerUnit must define their own set_channel method.")

    def set_channel_on(self, id):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own set_channel_on method.")

    def set_channel_off(self, id):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own set_channel_off method.")

    def kill_channel(self, id):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own kill_channel method.")

    def kill_all_channels(self):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own kill_all_channels method.")

    def all_channels_off(self):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own all_channels_off method.")

    def initialize_device(self):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own initialize_device method.")

    def flush(self):
        """
        Flush any pending device changes to the hardware.  The default action
        is to do nothing, which is appropriate for devices which will transmit
        their commands immediately.  Other devices may need to track commands
        internally and then send a controller-wide all-channel update sequence
        when flush() is called.
        """
        pass
