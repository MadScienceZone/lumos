# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS CONTROLLER UNIT BASE CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/ControllerUnit.py,v 1.6 2008-12-31 00:25:19 steve Exp $
#
# Lumos Light Orchestration System
# Copyright (c) 2005, 2006, 2007, 2008 by Steven L. Willoughby, Aloha,
# Oregon, USA.  All Rights Reserved.  Licensed under the Open Software
# License version 3.0.
#
# This product is provided for educational, experimental or personal
# interest use, in accordance with the terms and conditions of the
# aforementioned license agreement, ON AN "AS IS" BASIS AND WITHOUT
# WARRANTY, EITHER EXPRESS OR IMPLIED, INCLUDING, WITHOUT LIMITATION,
# THE WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY OR FITNESS FOR A
# PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY OF THE ORIGINAL
# WORK IS WITH YOU.  (See the license agreement for full details, 
# including disclaimer of warranty and limitation of liability.)
#
# Under no curcumstances is this product intended to be used where the
# safety of any person, animal, or property depends upon, or is at
# risk of any kind from, the correct operation of this software or
# the hardware devices which it controls.
#
# USE THIS PRODUCT AT YOUR OWN RISK.
# 
from Lumos.Channel import Channel

class ControllerUnit (object):
    """
    Generic controller unit virtual class.  Don't create these directly; 
    derive a subclass describing some real type of hardware device.  
    This class describes attributes and behaviors common to all controller 
    unit types.
    """
    def __init__(self, id, power, network, resolution=100):
        """
        Constructor for basic controller units.
        id:          the ID tag this unit instance is known by.
        power:       a PowerSource instance describing the power 
                     feed for this unit  This will be the default
                     source for all channels unless a channel 
                     explicitly overrides this.
        network:     a Network instance describing the communications
                     network and protocol connected to this unit.
        resolution:  default dimmer resolution for channels of this 
                     device. [def=100]
        """
        self.id = id
        self.power_source = power
        self.channels = {}
        self.resolution = resolution
        self.network = network

    def channel_id_from_string(self, channel):
        '''Given a string with a channel name, return the proper channel
        ID this device wants to see.  This may be, for example, an
        integer value instead of a character string with digits in it.'''

        raise NotImplementedError("Subclasses of ControllerUnit must define a channel_id_from_string() method.")

    def add_channel(self, id, name=None, load=None, dimmer=True, warm=None, resolution=None, power=None):
        """
        Add an active channel for this controller.
           add_channel(id, [name], [load], [dimmer], [warm], [resolution], [power])

        This constructs a channel object of the appropriate type and 
        adds it to this controller unit.  This may be of the the base 
        Channel class, or it may be something derived from that if the 
        controller has special channel features.  The parameters are 
        the same as for the Channel object constructor.

        The resolution parameter will default to the value specified to 
        the ControllerUnit constructor.
        """

        if resolution is None: resolution = self.resolution
        if power is None: power = self.power_source
        self.channels[id] = Channel(id, name, load, dimmer, warm, resolution, power)

    def set_channel(self, id, level, force=False):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own set_channel method.")

    def set_channel_on(self, id, force=False):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own set_channel_on method.")

    def set_channel_off(self, id, force=False):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own set_channel_off method.")

    def kill_channel(self, id, force=False):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own kill_channel method.")

    def kill_all_channels(self, force=False):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own kill_all_channels method.")

    def all_channels_off(self, force=False):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own all_channels_off method.")

    def initialize_device(self):
        raise NotImplementedError("Subclasses of ControllerUnit must define their own initialize_device method.")

    def flush(self, force=False):
        """
        Flush any pending device changes to the hardware.  The default action
        is to do nothing, which is appropriate for devices which will transmit
        their commands immediately.  Other devices may need to track commands
        internally and then send a controller-wide all-channel update sequence
        when flush() is called.
        """
        pass

    def iter_channels(self):
        "Iterate over the list of channel IDs, not necessarily in any order."
        return iter(self.channels)

    def _iter_non_null_channel_list(self):
        '''For units where the channel list is a linear list of objects,
        this method implements an generator function which will return the
        channel IDs which are actually initialized.  So, for example, if
        a unit had 48 physical channels but only 13 were set up in a show
        profile, only those 13 would be returned.'''

        for i in range(len(self.channels)):
            if self.channels[i] is not None:
                yield i

    def current_drain(self):
        '''Report on the current load drawn by this controller at this point in
        time, based on chanel output levels.  (This assumes any pending flush
        has happened and channels are already doing what they were last commanded
        to do.)  The return value is a dictionary mapping channel ID to a tuple
        of (amps, PowerSource) for each channel in this controller.'''
        return dict([
            (k,self.channels[k].current_drain()) 
                for k in self.iter_channels()
            ])

    def current_loads(self):
        '''Report on the loads assigned to this controller during the show.
        The return value is a dictionary mapping channel ID to a tuple of
        (amps, PowerSource) for each channel in this controller.'''
        return dict([
            (k,self.channels[k].current_load()) 
                for k in self.iter_channels()
            ])
#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
