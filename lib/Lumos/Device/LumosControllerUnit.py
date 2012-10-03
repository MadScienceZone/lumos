# XXX What is "force" for in the flush() method?
# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS DEVICE DRIVER: LUMOS DIY SSR CONTROLLER
#
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Device/LumosControllerUnit.py,v 1.6 2008-12-31 00:25:19 steve Exp $
#
# Lumos Light Orchestration System
# Copyright (c) 2005, 2006, 2007, 2008, 2012 by Steven L. Willoughby, Aloha,
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
    def __init__(self, id, power_source, network, address=0, resolution=256, num_channels=48):
        """
        Constructor for a Lumos SSR board object:
            LumosControllerUnit(id, power_source, [address,] [resolution,] [channel])

        Specify the correct PowerSource object for this unit and
        the unit address (0-15).  The resolution defaults to 256,
        which is correct for the 2.0 revision of the board firmware.

        Compatible with the 48-channel controller board (AC or DC) v.3.1
        and the 24-channel DC self-contained controller v.1.0.
        """

        ControllerUnit.__init__(self, id, power_source, network, resolution)
        self.address = int(address)
        self.num_channels = num_channels
        self.type = 'Lumos {0}-Channel SSR Controller'.format(self.num_channels)
        self.iter_channels = self._iter_non_null_channel_list
        self._changed_channels = set()
        self._reset_queue()

        if not 0 <= self.address <= 15:
            raise ValueError("Address {0} out of range for Lumos SSR Controller".format(self.address))

        if self.resolution == 256:
            self._high_resolution = True
        elif self.resolution == 128:
            self._high_resolution = False
        else:
            raise ValueError("Lumos controller resolution value {0} out of range (should be 128 or 256).".format(self.resolution))

    def __str__(self):
        return "{0}, address={1}".format(self.type, self.address)

    def channel_id_from_string(self, channel):
        return int(channel)

    def add_channel(self, id, name=None, load=None, dimmer=True, warm=None, resolution=None, power_source=None):
        try:
            id = int(id)
            assert 0 <= id < self.num_channels
        except:
            raise ValueError("This Lumos SSR's channel IDs must be integers from 0-{0}".format(self.num_channels - 1))

        if resolution is not None:
            resolution = int(resolution)
        else:
            resolution=self.resolution

        ControllerUnit.add_channel(self, id, name, load, dimmer, warm, resolution, power_source)

    #
    # Completely re-written for the v2.0 ROM firmware.  Now that we
    # have optimized bulk updates, we need to buffer up changes and
    # wait until we get a flush() to send them out.
    #
    # We used to send each update as it was requested.
    #
    #
    # hardware protocol, for a unit with address <a>
    #  Kill all channels  1000aaaa
    #  Chan c off         1001aaaa 00cccccc
    #  Chan c on          1001aaaa 01cccccc
    #  Chan c to level v  1010aaaa 00cccccc 000vvvvv
    #  Disable admin cmds 1111aaaa 01100001

    def _reset_queue(self):
        self._min_change = self.resolution-1
        self._max_change = 0
        self._changed_channels.clear()

    def _queue_set_channel(self, id, old_level, new_level, force=False):
        if old_level != new_level or force:
            self._min_change, self._max_change = min(self._min_change, id), max(self._max_change, id)
            self._changed_channels.add(id)


#            return chr(0x90 | self.address) + chr(id & 0x3f)
#        elif new_level >= self.resolution-1: 
#            return chr(0x90 | self.address) + chr(0x40 | (id & 0x3f))
#        else:                               
#            return chr(0xa0 | self.address) + chr(id & 0x3f) + chr(new_level & 0x1f)

    def flush(self, force=False):
        # send any pending channel level setting commands now.
        # 
        # 1001aaaa 0scccccc                                                                  on/off only
        # 1010aaaa 0hcccccc 0vvvvvvv                                                         set to level 0-255
        # 1011aaaa 00cccccc 00nnnnnn {0vvvvvvv}*n+1 01010101                                 set c to c+n+1 to level 0-127
        # 1011aaaa 01cccccc 00nnnnnn {0vvvvvvv}*n+1 01010110 {0hhhhhhh}*[(n+7)/7] 01010101   set c to c+n+1 to level 0-255
        #
        if self._changed_channels or force:
            #
            # If we're updating 48 channels at low res, this is 52 bytes, so we are updating 18 or more, we might as well do them all.
            # If we're updating 3 or more contiguous channels, we might as well do them as a unit.
            # Similarly for the other kinds of boards, so it boils down to:
            #   48-channel board: low-res: 18+  high-res: 20+
            #   24-channel board           10+            12+
            # If you update more than that number of channels, you save bytes by just bulk-updating
            # the entire board.
            #
            # More optimization may be obtained by sending a small bulk update for any contiguous
            # run of 3 or more channels (4 or more in high-res).  However, for this version we're
            # going to leave that out and see how it goes, to avoid adding even more bookkeeping
            # and calculation overhead just to save a few bytes.  If it becomes necessary, though,
            # we'll add it in the future.
            #

            #
            # If all the channels are at zero, then really we just need to send
            # a one-byte "all channels off" command.
            #
            if sum([i.level or 0 for i in self.channels.values()]) == 0:
                self.network.send(chr(0x80 | self.address))
            else:
                if force:
                    n = self.num_channels
                    self._min_change = 0
                    self._max_change = self.num_channels - 1
                else:
                    n = len(self._changed_channels)

                if self._high_resolution:
                    if n >= (12 if self.num_channels <= 24 else 20):
                        # high-res bulk transfer B0|a 40|ch n v*n 56 h*(n/7) 55
                        n_1 = self._max_change - self._min_change
                        packet = [
                            chr(0xb0 | self.address),
                            chr(0x40 | (self._min_change & 0x3f)),
                            chr((n_1) & 0x3f)
                        ] + [
                            chr((((self.channels[vi].level or 0) >> 1) & 0x7f) if vi in self.channels else 0) 
                                for vi in range(self._min_change, self._max_change + 1)
                        ] + [
                            chr(0x56)
                        ]

                        bit = 0x40
                        byte = 0
                        for vi in range(self._min_change, self._max_change + 1):
                            if vi in self.channels and (self.channels[vi].level or 0) & 1:
                                byte |= bit
                            bit >>= 1
                            if not bit:
                                packet.append(chr(byte))
                                bit = 0x40
                                byte = 0
                        if bit != 0x40:
                            packet.append(chr(byte))
                        packet.append(chr(0x55))
                        self.network.send(''.join(packet))
                    else:
                        # high-res individual channel updates A0|a ch v
                        for i in self._changed_channels:
                            if not self.channels[i].level:  # covers None and 0
                                self.network.send(chr(0x90 | self.address) + chr(i & 0x3f))
                            elif self.channels[i].level >= self.resolution-1:
                                self.network.send(chr(0x90 | self.address) + chr(0x40 | (i & 0x3f)))
                            else:
                                self.network.send(
                                    chr(0xa0 | self.address) + 
                                    chr((i & 0x3f) | ((self.channels[i].level << 6) & 0x40)) +
                                    chr((self.channels[i].level >> 1) & 0x7f)
                                )
                else:
                    if n >= (10 if self.num_channels <= 24 else 18):
                        # low-res bulk transfer B0|a ch n v*n 55
                        n_1 = self._max_change - self._min_change
                        self.network.send(''.join([
                            chr(0xb0 | self.address),
                            chr(self._min_change & 0x3f),
                            chr((n_1) & 0x3f)
                        ] + [
                            chr((((self.channels[vi].level or 0)) & 0x7f) if vi in self.channels else 0) for vi in range(self._min_change, self._max_change + 1)
                        ] + [
                            chr(0x55)
                        ]))
                    else:
                        # low-res individual channel updates A0|a ch v
                        for i in self._changed_channels:
                            if not self.channels[i].level:
                                self.network.send(chr(0x90 | self.address) + chr(i & 0x3f))
                            elif self.channels[i].level >= self.resolution-1:
                                self.network.send(chr(0x90 | self.address) + chr(0x40 | (i & 0x3f)))
                            else:
                                self.network.send(
                                    chr(0xa0 | self.address) + 
                                    chr(i & 0x3f) +
                                    chr(self.channels[i].level & 0x7f)
                                )
            self._reset_queue()
            

    def set_channel(self, id, level, force=False):
        #self.network.send(self._proto_set_channel(id, *self.channels[id].set_level(level), force=force))
        self._queue_set_channel(id, *self.channels[id].set_level(level), force=force)

    def set_channel_on(self, id, force=False):
        #self.network.send(self._proto_set_channel(id, *self.channels[id].set_on(), force=force))
        self._queue_set_channel(id, *self.channels[id].set_on(), force=force)

    def set_channel_off(self, id, force=False):
        #self.network.send(self._proto_set_channel(id, *self.channels[id].set_off(), force=force))
        self._queue_set_channel(id, *self.channels[id].set_off(), force=force)

    def kill_channel(self, id, force=False):
        #self.network.send(self._proto_set_channel(id, *self.channels[id].kill(), force=force))
        self._queue_set_channel(id, *self.channels[id].kill(), force=force)

    def kill_all_channels(self, force=False):
        for ch in self.channels:
            self.channels[ch].kill()
        #self.flush(force)
        self.network.send(chr(0x80 | self.address))

    def all_channels_off(self, force=False):
        for ch in self.channels:
            self.set_channel_off(ch, force)
        self.flush(force)

    def initialize_device(self):
        self.network.send(chr(0xf0 | self.address) + chr(0x70))     # turn off config mode
        #self.network.send(chr(0xf0 | self.address) + chr(0x61))   # go to normal run mode
        self.kill_all_channels(False)
        self.all_channels_off(False)

    def raw_ramp_up(self, channel, steps, delay):
        self.flush()
        self.channels[channel].set_level(self.resolution - 1)
        self.network.send(chr(0xC0 | self.address) + chr(0x40 | (channel & 0x3f)) + chr((steps - 1) & 0x7f) + chr((delay - 1) & 0x7f))

    def raw_ramp_down(self, channel, steps, delay):
        self.flush()
        self.channels[channel].set_level(0)
        self.network.send(chr(0xC0 | self.address) + chr(channel & 0x3f) + chr((steps - 1) & 0x7f) + chr((delay - 1) & 0x7f))


    _device_commands = {
        'sleep':    '\x00ZZ',
        'wake':     '\x01ZZ',
        'shutdown': '\x02XY',
        'execute':  '\x05{0}',
        'masksens': '\x07{1}',
        'clearmem': '\x08CA',
        'noconfig': '\x70',
        '__reset__':'\x71$r',
        '__baud__': '\x72{0}&',
    }
    _dev_bitmasks = {
        'A':        0x08,
        'B':        0x04,
        'C':        0x02,
        'D':        0x01,
    }
    def raw_control(self, command, *args):
        # A collection of device-level operations which Lumos ordinarily doesn't use
        if command in self._device_commands:
            self.network.send(chr(0xF0 | self.address) + self._device_commands[command].format(
                ''.join([chr(i & 0x7f) for i in args if isinstance(i, int)]),
                chr(0x7f & reduce((lambda x,y: x|y), [self._dev_bitmasks.get(k, 0) for k in args], 0)),
            ))
        else:
            raise ValueError("Unknown raw control command \"{0}\" for Lumos board {1}".format(command, self.address))

    def raw_set_phase(self, value):
        self.network.send(chr(0xF0 | self.address) + chr(0x40 | ((value >> 7) & 0x03)) + chr(value & 0x7f) + "PO")

    def raw_set_address(self, value):
        if 0 <= value <= 15:
            self.network.send(chr(0xF0 | self.address) + chr(0x60 | (value & 0x0f)) + 'IAD')
            self.address = value
        else:
            raise ValueError('New device address {0} out of range [0,15]'.format(value))

    def raw_download_sequence(self, id, bits):
        "Download a compiled sequence <id> consisting of <bits> (a sequence of integers)"

        self.network.send(chr(0xF0 | self.address) + chr(0x04) + chr(id & 0x7f) + chr(len(bits) & 0x7f) +
            ''.join([chr(i & 0x7f) for i in bits]) + 'Ds')


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
