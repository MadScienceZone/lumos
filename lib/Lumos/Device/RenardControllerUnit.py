# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS DEVICE DRIVER: RENARD DIY SSR CONTROLLER
# ***UNTESTED*** SPECULATIVE CODE.  NOT READY FOR USE!
#
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Device/RenardControllerUnit.py,v 1.5 2008-12-31 00:25:19 steve Exp $
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
# The Renard is a classic DIY SSR controller.  This driver is 
# an experimental design based on the protocol description posted
# on computerchristmas.com.  The author does not have the hardware
# available to verify that this works.  Hopefully someone with a Renard
# can verify this and give feedback about it to the author.
#
# The serial protocol used by this device updates all channels at one
# time, in packets which look like this:
#    <0x7e><address><level0><level1>...<leveln>
#
# literal 0x7d, 0x7e and 0x7f bytes are sent using an escape mechanism:
#    <0x7f><0x2f> == <0x7d>
#    <0x7f><0x30> == <0x7e>
#    <0x7f><0x31> == <0x7f>
#
# The <address> byte always has MSB set (so the address of the first unit
# is really 0x80, the second is 0x81, etc.).
#
# <level> bytes are in the range <0x00> (fully off) to <0xff> (fully on).
#

class RenardControllerUnit (ControllerUnit):
    """
    ControllerUnit subclass for the Renard DIY SSR unit.

    ***THE STATUS OF THIS DRIVER IS EXPERIMENTAL***
    THIS HAS NOT YET BEEN VERIFIED TO WORK WITH ACTUAL HARDWARE

    If you have a Renard or compatible controller, we would
    appreciate any feedback you'd like to offer about this driver,
    if you're willing to try it and help us test/debug this code.
    """
    def __init__(self, id, power_source, network, address=0, resolution=256, num_channels=64):
        """
        Constructor for a Renard SSR board object:
            RenardControllerUnit(id, power_source, network, [address], [resolution], [num_channels])

        Specify the correct PowerSource object for this unit and
        the unit address (0-127).  (We will call the first unit address 0,
        even though behind the scenes the address byte's MSB will be sent
        when transmitted (so unit address 0 transmits as 0x80, address 1
        transmits as 0x81, etc.)  The number of channels defaults to 64, but there
        are known Renard implementations with 8, 16, 24, 32 and 64 channels and
        probably others.  This sets the upper bound for channel IDs on this
        controller unit, and also the packet size which will always be sent
        when pending changes are flushed out to the hardware.

        The resolution probably won't ever need to be changed.  The Renards
        use 256 dimmer levels, so that's the default for that parameter.
        """

        ControllerUnit.__init__(self, id, power_source, network, resolution)
        self.address = int(address)
        self.num_channels = int(num_channels)
        self.type = 'Renard SSR Controller (%d channels)' % self.num_channels
        self.channels = [None] * self.num_channels
        self.update_pending = False
        self.iter_channels = self._iter_non_null_channel_list

        if not 0 <= self.address < 127:
            raise ValueError("Address %d out of range for a Renard SSR Controller" % self.address)

    def channel_id_from_string(self, channel):
        return int(channel)

    def __str__(self):
        return "%s, address=%d (%d channels)" % (self.type, self.address, len(self.channels))

    def add_channel(self, id, name=None, load=None, dimmer=True, warm=None, resolution=None, power_source=None):
        try:
            id = int(id)
            assert 0 <= id < len(self.channels)
        except:
            raise ValueError("%d-channel Renard channel IDs must be integers from 0-%d"
                % (len(self.channels), len(self.channels)-1))
                
        if resolution is not None:
            resolution = int(resolution)
        else:
            resolution=self.resolution

        ControllerUnit.add_channel(self, id, name, load, dimmer, warm, resolution, power_source)
    
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
            self.network.send('~%c' % (0x80 | self.address))
            for channel in self.channels:
                if channel is None:
                    self.network.send(chr(0))
                else:
                    self.send_escaped_int(channel.level)
            self.update_pending = False

    #def iter_channels(self):
        #return range(len(self.channels))

    def send_escaped_int(self, i):
        if i is None: i = 0
        if   i == 0x7d: self.network.send('\x7f/')
        elif i == 0x7e: self.network.send('\x7f0')
        elif i == 0x7f: self.network.send('\x7f1')
        else:           self.network.send(chr(i))
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
