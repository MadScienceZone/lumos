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

class DeviceProtocolError (Exception): pass

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

    def raw_sensor_trigger(self, sens_id, i_seq, p_seq, t_seq, inverse=False, mode='while'):
        # inverse is "active high"
        self.network.send(chr(0xF0 | self.address) + chr(0x06) + chr(
            (0x40 if mode=='once' else (0x20 if mode == 'while' else 0x00)) | 
            (0x00 if inverse else 0x10) |
            {'A': 0, 'B': 1, 'C': 2, 'D': 3}[sens_id]) + 
            chr(i_seq & 0x7f) + chr(p_seq & 0x7f) + chr(t_seq & 0x7f) + '<')

    def raw_configure_device(self, conf_obj):
        self.network.send(chr(0xF0 | self.address) + chr(0x71) + chr(
            reduce((lambda x,y: x|y), 
                [{'A': 0x40, 'B': 0x20, 'C': 0x10, 'D': 0x08}[s] 
                    for s in conf_obj.configured_sensors], 0)
            | (0x04 if conf_obj.dmx_start else 0x00)
            | (0 if not conf_obj.dmx_start else ((conf_obj.dmx_start - 1) >> 7) & 0x03)
            ) + chr(0 if not conf_obj.dmx_start else ((conf_obj.dmx_start - 1) & 0x7f)) +
            chr(0x3a | (0x40 if conf_obj.resolution == 256 else 0x00)) + chr(0x3D))
            
    # 1111aaaa 00011111 <data> 00110011
    # <data>::=
    #   0ABCDdcc 0ccccccc 0ABCDqsf 0ABCDrpp 0ppppppp 0eeeeee 0eeeeeee 0mmmmmmm 0mmmmmmm 0X0000ii 0xxxxxxx
    #    \__/|\_________/  \__/|||  \__/|\_________/ \______________/  \______________/  |    \/ \______/
    #    |   |     |         | |||    | |       |             |                 |        |     |     |
    # sens   |     |         | |||    | |       |             |                 |        |     |     |
    # DMX----+     |         | |||    | |       |             |                 |        |     |     |
    # DMX channel--+         | |||    | |       |             |                 |        |     |     |
    # sensor masks (1=en)----+ |||    | |       |             |                 |        |     |     |
    # in admin/config mode now-+||    | |       |             |                 |        |     |     |
    # sleep mode (s=1)----------+|    | |       |             |                 |        |     |     |
    # last seq overfilled--------+    | |       |             |                 |        |     |     |
    # Current sensor input states-----+ |       |             |                 |        |     |     |
    # Resolution (1=high, 0=low)--------+       |             |                 |        |     |     |
    # phase offset value------------------------+             |                 |        |     |     |
    # EEPROM bytes free for sequences-------------------------+                 |        |     |     |
    # RAM bytes free for sequences----------------------------------------------+        |     |     |
    # A sequence is currently executing (1)----------------------------------------------+     |     |
    # Device Model ID (00=48SSR, 01=24SSR-DC)--------------------------------------------------+     |
    # Currently running sequence---------------------------------------------------------------------+
    #    0owmxx00 0iiiiiii 0ppppppp 0ttttttt 	sensor config for A
    #    0owmxx01 0iiiiiii 0ppppppp 0ttttttt 	sensor config for B
    #    0owmxx10 0iiiiiii 0ppppppp 0ttttttt 	sensor config for C
    #    0owmxx11 0iiiiiii 0ppppppp 0ttttttt 	sensor config for D

    def raw_query_device_status(self):
        self.network.send(chr(0xf0 | self.address) + "\3$T")

        def find_command_byte(d, start=0):
            if d is None:
                return -1

            for i in range(start, len(d)):
                if ord(d[i]) & 0x80:
                    return i
            return -1

        def packet_scanner(d):
            start=0
            while True:
                cb = find_command_byte(d, start)
                start = cb+1
                if cb < 0:
                    return 30
                if ord(d[cb]) == (0xf0 | self.address):
                    if len(d) - cb <= 1:
                        return 29
                    if ord(d[cb+1]) == 0x1f:
                        return max(0, 30 - (len(d) - cb))


                        # 0  1  2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9
                        # cc                                          1
                        # x  x  x c                                   1
                        # cc 1f 1 2 3                                 5-0    9
                        # x  x  x c f 1 2 3 4                         9-3    8
                        # x  x  c f 1 2 3 4 5 6 7 8 9 0 1 2           16-2   0
                        # x  x  c f 1 2 3 4 5 6 7 8 9 0 1 2 x x x x   20-2  -4
            
        reply = self.network.input(packet_scanner)
        if len(reply) != 30:
            raise DeviceProtocolError("Query packet response malformed (len={0})".format(len(reply)))
        if ord(reply[29]) != 0x33:
            raise DeviceProtocolError("Query packet response malformed (end={0:02X})".format(ord(reply[29])))
        if any([ord(x) & 0x80 for x in reply[1:]]):
            raise DeviceProtocolError("Query packet response malformed (high bit in data area: {0})".format(
                ' '.join(['{0:02X}'.format(ord(x)) for x in reply])))

        reply = [ord(i) for i in reply]

        status = LumosControllerStatus()
        for sensor_id, bitmask in ('A', 0x40), ('B', 0x20), ('C', 0x10), ('D', 0x08):
            if reply[2] & bitmask:
                status.config.configured_sensors.append(sensor_id)
                status.sensors[sensor_id].configured = True

            if reply[4] & bitmask:
                status.sensors[sensor_id].enabled = True

            if reply[5] & bitmask:
                status.sensors[sensor_id].on = True

        if reply[2] & 0x04:
            status.config.dmx_start = ((reply[2] & 0x03) << 7) | (reply[3] & 0x7f)
        else:
            status.config.dmx_start = None

        status.in_config_mode = bool(reply[4] & 0x04)
        status.in_sleep_mode = bool(reply[4] & 0x02)
        status.err_memory_full = bool(reply[4] & 0x01)
        status.config.resolution = 256 if reply[5] & 0x04 else 128 
        status.phase_offset = ((reply[5] & 0x03) << 7) | (reply[6] & 0x7f)
        status.eeprom_memory_free = ((reply[7] & 0x7f) << 7) | (reply[8] & 0x7f)
        status.ram_memory_free = ((reply[9] & 0x7f) << 7) | (reply[10] & 0x7f)
        if reply[11] & 0x40:
            status.current_sequence = reply[12] & 0x7f
        else:
            status.current_sequence = None
        if reply[11] & 0x03 == 0:
            status.hardware_type = 'lumos48ctl'
            status.channels = 48
        elif reply[11] & 0x03 == 1:
            status.hardware_type = 'lumos24dc'
            status.channels = 24
        else:
            status.hardware_type = 'unknown'
            status.channels = 0

        for group, sensor_id in enumerate(['A', 'B', 'C', 'D']):
            flags = reply[group * 4 + 13]
            if flags & 0x03 != group:
                raise DeviceProtocolError("Query packet response malformed (sensor group {0} ID as {1} ({2:02X}))".format(
                    group, flags & 0x03, flags))
            status.sensors[sensor_id].trigger_mode = ('once' if flags & 0x40 else 
                                                        ('while' if flags & 0x20 else 'repeat'))
            status.sensors[sensor_id].active_low = bool(flags & 0x01)
            status.sensors[sensor_id].pre_trigger = reply[group * 4 + 14]
            status.sensors[sensor_id].trigger = reply[group * 4 + 15]
            status.sensors[sensor_id].post_trigger = reply[group * 4 + 16]

        return status

class LumosControllerConfiguration (object):
    def __init__(self):
        self.configured_sensors = []    # list of 'A'..'D'
        self.dmx_start = None           # None or 1..512
        self.resolution = 256           # 128 or 256

class LumosControllerSensor (object):
    def __init__(self, id):
        self.id = id
        self.active_low = True
        self.enabled = False
        self.configured = False
        self.on = False
        self.pre_trigger = 0
        self.trigger = 0
        self.post_trigger = 0
        self.trigger_mode = 'once'

    def copy(self):
        new = LumosControllerSensor(self.id)
        new.active_low = self.active_low
        new.enabled = self.enabled
        new.configured = self.configured
        new.on = self.on
        new.pre_trigger = self.pre_trigger
        new.trigger = self.trigger
        new.post_trigger = self.post_trigger
        new.trigger_mode = self.trigger_mode
        return new


class LumosControllerStatus (object):
    def __init__(self):
        self.config = LumosControllerConfiguration()
        self.in_config_mode = False
        self.in_sleep_mode = False
        self.err_memory_full = False
        self.phase_offset = 2
        self.eeprom_memory_free = 0
        self.ram_memory_free = 0
        self.current_sequence = None
        self.hardware_type = None
        self.sensors = {
            'A': LumosControllerSensor('A'),
            'B': LumosControllerSensor('B'),
            'C': LumosControllerSensor('C'),
            'D': LumosControllerSensor('D'),
        }

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
