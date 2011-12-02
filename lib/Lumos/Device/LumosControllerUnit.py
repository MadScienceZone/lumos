# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS DEVICE DRIVER: LUMOS DIY SSR CONTROLLER
#
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Device/LumosControllerUnit.py,v 1.6 2008-12-31 00:25:19 steve Exp $
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

class LumosControllerUnit (ControllerUnit):
    """
    ControllerUnit subclass for my custom 48-channel SSR boards.
    """
    def __init__(self, id, power, network, address, resolution=32):
        """
        Constructor for a 48-Channel SSR board object:
            LumosControllerUnit(id, power, address, [resolution])

        Specify the correct PowerSource object for this unit and
        the unit address (0-15).  The resolution defaults to 32,
        which is correct for the 3.1 revision of the boards.
        """

        ControllerUnit.__init__(self, id, power, network, resolution)
        self.address = int(address)
        self.type = 'Lumos 48-Channel SSR Controller'
        self.iter_channels = self._iter_non_null_channel_list
        if not 0 <= self.address <= 15:
            raise ValueError, "Address %d out of range for Lumos 48-Channel SSR Controller" % self.address

    def __str__(self):
        return "%s, address=%d" % (self.type, self.address)

    def channel_id_from_string(self, channel):
        return int(channel)

    #def iter_channels(self):
    #    return range(48)

    def add_channel(self, id, name=None, load=None, dimmer=True, warm=None, resolution=None, power=None):
        try:
            id = int(id)
            assert 0 <= id <= 47
        except:
            raise ValueError, "Lumos 48SSR channel IDs must be integers from 0-47"

        if resolution is not None:
            resolution = int(resolution)
        else:
            resolution=self.resolution

        ControllerUnit.add_channel(self, id, name, load, dimmer, warm, resolution, power)

    #
    # hardware protocol, for a unit with address <a>
    #  Kill all channels  1000aaaa
    #  Chan c off         1001aaaa 00cccccc
    #  Chan c on          1001aaaa 01cccccc
    #  Chan c to level v  1010aaaa 00cccccc 000vvvvv
    #  Disable admin cmds 1111aaaa 01100001

    def _proto_set_channel(self, id, old_level, new_level, force=False):
        if old_level == new_level and not force: return ''
        if new_level is None or new_level <= 0:
            return chr(0x90 | self.address) + chr(id & 0x3f)
        elif new_level >= self.resolution-1: 
            return chr(0x90 | self.address) + chr(0x40 | (id & 0x3f))
        else:                               
            return chr(0xa0 | self.address) + chr(id & 0x3f) + chr(new_level & 0x1f)

    def set_channel(self, id, level, force=False):
        self.network.send(self._proto_set_channel(id, *self.channels[id].set_level(level), force=force))

    def set_channel_on(self, id, force=False):
        self.network.send(self._proto_set_channel(id, *self.channels[id].set_on(), force=force))

    def set_channel_off(self, id, force=False):
        self.network.send(self._proto_set_channel(id, *self.channels[id].set_off(), force=force))

    def kill_channel(self, id, force=False):
        self.network.send(self._proto_set_channel(id, *self.channels[id].kill(), force=force))

    def kill_all_channels(self, force=False):
        for ch in self.channels:
            self.channels[ch].kill()
        self.network.send(chr(0x80 | self.address))

    def all_channels_off(self, force=False):
        for ch in self.channels:
            self.set_channel_off(ch, force)

    def initialize_device(self):
        self.network.send(chr(0xf0 | self.address) + chr(0x61))   # go to normal run mode
        self.kill_all_channels(True)
        self.all_channels_off(True)
#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
#
# LUMOS CHANNEL MAP HANDLER CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Device/SSR48ControllerUnit.py,v 1.6 2008-12-31 00:25:19 steve Exp $
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
