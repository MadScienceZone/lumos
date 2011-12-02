# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS DEVICE DRIVER: FIREGOD DIY SSR CONTROLLER
# ***UNTESTED*** SPECULATIVE CODE.  NOT READY FOR USE!
#
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Device/FireGodControllerUnit.py,v 1.5 2008-12-31 00:25:19 steve Exp $
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
from Lumos.ControllerUnit import ControllerUnit

#
# The FireGod is a classic DIY SSR controller.  This driver is 
# an experimental design based on the protocol description posted
# on doityourselfchristmas.com.  The author does not have the hardware
# available to verify that this works.  Hopefully someone with a FireGod
# can verify this and give feedback about it to the author.
#
# The serial protocol used by this device updates all channels at one
# time, in packets which look like this:
#    <0x55><address><level0><level1>...<level31>
#
# The <address> byte may be 0x01-0x04, to address the 32-channel module
# being updated.
#
# <level> bytes are in the range <0x64> (fully off) to <0xc8> (fully on).
# there are 101 levels, so you get 0%-100% inclusive.
#

class FireGodControllerUnit (ControllerUnit):
    """
    ControllerUnit subclass for the Renard DIY SSR unit.

    ***THE STATUS OF THIS DRIVER IS EXPERIMENTAL***
    THIS HAS NOT YET BEEN VERIFIED TO WORK WITH ACTUAL HARDWARE

    If you have a FireGod or compatible controller, we would
    appreciate any feedback you'd like to offer about this driver,
    if you're willing to try it and help us test/debug this code.
    """
    def __init__(self, id, power, network, address, resolution=101, channels=32):
        """
        Constructor for a FireGod dimmable 128-channel SSR board object:
            FireGodControllerUnit(power, id, network, address, [resolution], [channels])

        Specify the correct PowerSource object for this unit and
        the module address (1-4).  The number of channels defaults to 32, but this
        can be changed if you have a controller which implements a different number
        of channels per module.  This will change the number of levels transmitted
        in the command packets.  

        The resolution probably won't ever need to be changed.  The FireGod units
        use 101 dimmer levels (0%-100%), so that's the default for that parameter.
        """

        ControllerUnit.__init__(self, id, power, network, resolution)
        self.address = int(address)
        self.type = 'FireGod SSR Controller (%d channels)' % channels
        self.channels = [None] * channels
        self.update_pending = False
        self.iter_channels = self._iter_non_null_channel_list

        if not 1 <= self.address <= 4:
            raise ValueError("Address %d out of range for a FireGod SSR Controller Module" % self.address)

    def __str__(self):
        return "%s, module #%d (%d channels)" % (self.type, self.address, len(self.channels))

    def channel_id_from_string(self, channel):
        return int(channel)

    #def iter_channels(self):
        #return range(len(self.channels))

    def add_channel(self, id, name=None, load=None, dimmer=True, warm=None, resolution=None, power=None):
        try:
            id = int(id)
            assert 0 <= id < len(self.channels)
        except:
            raise ValueError("%d-channel FireGod channel IDs must be integers from 0-%d"
                % (len(self.channels), len(self.channels)-1))
                
        if resolution is not None:
            resolution = int(resolution)
        else:
            resolution=self.resolution

        ControllerUnit.add_channel(self, id, name, load, dimmer, warm, resolution, power)
    
    def set_channel(self, id, level, force=False):
        self.channels[id].set_level(level)
        self.update_pending = True

    def set_channel_on(self, id, force=False):
        self.channels[id].set_on()
        self.update_pending = True

    def set_channel_off(self, id, force=False):
        self.channels[id].set_off()
        self.update_pending = True

    def kill_channel(self, id, force=False):
        self.channels[id].kill()
        self.update_pending = True

    def kill_all_channels(self, force=False):
        for ch in self.channels:
            if ch is not None:
                ch.kill()
        self.update_pending = True

    def all_channels_off(self, force=False):
        for ch in self.channels:
            if ch is not None:
                ch.set_off()
        self.update_pending = True

    def initialize_device(self):
        self.all_channels_off(True)
        self.flush(True)

    def flush(self, force=False):
        if self.update_pending or force:
            self.network.send('U%c' % self.address)
            for channel in self.channels:
                if channel is None:
                    self.network.send(chr(0x64))
                elif channel.level is None:
                    self.network.send(chr(0x64))
                else:
                    self.network.send(chr(0x64 + channel.level))
            self.update_pending = False
