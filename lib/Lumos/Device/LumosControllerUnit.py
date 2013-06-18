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
import time

class DeviceProtocolError (Exception): pass
class InternalDeviceError (Exception): pass

class LumosControllerUnit (ControllerUnit):
    """
    ControllerUnit subclass for my custom 48-channel SSR boards.
    """
    def dumpstats(self, filename):
        f = open(filename, 'w')
        f.write('{0} flush calls():\n'.format(len(self.stats)))
        for time, count in self.stats:
            f.write('{0} {1}\n'.format(time, count))
        f.close()

    def __init__(self, id, power_source, network, address=0, resolution=256, num_channels=48):
        """
        Constructor for a Lumos SSR board object:
            LumosControllerUnit(id, power_source, [address,] [resolution,] [channel])

        Specify the correct PowerSource object for this unit and
        the unit address (0-15).  The resolution defaults to 256,
        which is correct for the 3.0 revision of the board firmware.

        Compatible with the 48-channel controller board (AC or DC) v.3.1
        and the 24-channel DC self-contained controller v.1.0.
        """

        ControllerUnit.__init__(self, id, power_source, network, resolution)
        self.address = int(address)
        self.num_channels = num_channels
        self.type = 'Lumos {0}-Channel SSR Controller'.format(self.num_channels)
        #self.iter_channels = self._iter_non_null_channel_list
        self._changed_channels = set()
        self._reset_queue()
        self.stats=[]

        if not 0 <= self.address <= 15:
            raise ValueError("Address {0} out of range for Lumos SSR Controller".format(self.address))

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
    # Completely re-written for the v3.0 ROM firmware.  Now that we
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
    #  Chan c to level v  1010aaaa 0vcccccc 0vvvvvvv
    #  Bulk @c for N to v 1011aaaa 00cccccc <N-1> <v> <v> ... <v> 01010101
    #  Disable admin cmds 1111aaaa 01110100

    def _reset_queue(self):
        self._min_change = self.resolution-1
        self._max_change = 0
        self._changed_channels.clear()

    def _queue_set_channel(self, id, old_level, new_level, force=False):
        if old_level != new_level or force:
            self._min_change, self._max_change = min(self._min_change, id), max(self._max_change, id)
            self._changed_channels.add(id)

    def _8_bit_decode_string(self, byte_string):
        return self._8_bit_decode_packet([ord(i) for i in byte_string])
    
    def _8_bit_decode_packet(self, byte_list):
        result = []
        next_MSB = False
        next_literal = False
        for byte in byte_list:
            if next_MSB:
                next_MSB = False
                result.append(byte | 0x80)
            elif next_literal:
                next_literal = False
                result.append(byte)
            elif byte == 0x7e:
                next_MSB = True
            elif byte == 0x7f:
                next_literal = True
            else:
                result.append(byte)
        return result
                
    def _8_bit_string(self, byte_list):
        return ''.join([chr(x) for x in self._8_bit_packet(byte_list)])

    def _8_bit_packet(self, byte_list):
        "Convert a list of bytes to a list of 8-bit-escaped bytes (may be longer)"
        result = []
        for byte in byte_list:
            if byte > 0x7f:
                result.extend([0x7e, (byte & 0x7f)])
            elif byte == 0x7e:
                result.extend([0x7f, 0x7e])
            elif byte == 0x7f:
                result.extend([0x7f, 0x7f])
            else:
                result.append(byte)
        return result

    def flush(self, force=False):
        #
        # send any pending channel level setting commands now.
        #
        if self._changed_channels or force:
            #
            # If we're updating 48 channels, this takes 52 bytes to update everything with a bulk
            # update command.  18 channel updates separately take 54 bytes total, so if we're
            # changing 18 or more channels we'll just punt and update them all.
            #
            # On a 24-channel board, it's 28 bytes to update the world, which is like 10 channel
            # updates (30 separately).
            #
            # More optimization may be obtained by sending a small bulk update for any contiguous
            # run of 3 or more channels.  However, for this version we're going to leave that out 
            # and see how it goes, to avoid adding even more bookkeeping and calculation overhead 
            # just to save a few bytes.  If it becomes necessary, though, we'll add it in the future.
            #

            #
            # If all the channels are at zero, then really we just need to send
            # a one-byte "all channels off" command.
            #
            byte_count=0
            if sum([i.level or 0 for i in self.channels.values()]) == 0:
                self.network.send(chr(0x80 | self.address))
                byte_count += 1
            else:
                if force:
                    n = self.num_channels
                    self._min_change = 0
                    self._max_change = self.num_channels - 1
                else:
                    n = len(self._changed_channels)

                if n >= (10 if self.num_channels <= 24 else 18):
                    # bulk transfer B0|a ch n-1 v*n 55
                    n_1 = self._max_change - self._min_change
                    packet = [
                        chr(0xb0 | self.address),
                        chr(self._min_change & 0x3f),
                        chr(n_1 & 0x3f)
                    ] + self._8_bit_packet([
                        ((self.channels[vi].level or 0) if vi in self.channels else 0)
                            for vi in range(self._min_change, self._max_change + 1)
                    ]) + [
                        chr(0x55)
                    ]
                    self.network.send(''.join(packet))
                    byte_count += len(packet)
                else:
                    # individual channel updates A0|a ch v
                    for i in self._changed_channels:
                        if not self.channels[i].level:  # covers None and 0
                            self.network.send(chr(0x90 | self.address) + chr(i & 0x3f))
                            byte_count += 2
                        elif self.channels[i].level >= self.resolution-1:
                            self.network.send(chr(0x90 | self.address) + self._8_bit_string([0x40 | (i & 0x3f)]))
                            byte_count += 2
                        else:
                            self.network.send(
                                chr(0xa0 | self.address) + self._8_bit_string([
                                    (i & 0x3f) | ((self.channels[i].level << 6) & 0x40),
                                    (self.channels[i].level >> 1) & 0x7f
                                ])
                            )
#<<<<<<< .mine
#                            byte_count += 3
#                #else:
#                #    if n >= (10 if self.num_channels <= 24 else 18):
#                        # low-res bulk transfer B0|a ch n v*n 55
#                #        n_1 = self._max_change - self._min_change
#                #        self.network.send(''.join([
#                #            chr(0xb0 | self.address),
#                #            chr(self._min_change & 0x3f),
#                #            chr((n_1) & 0x3f)
#                #        ] + [
#                #            chr((((self.channels[vi].level or 0)) & 0x7f) if vi in self.channels else 0) for vi in range(self._min_change, self._max_change + 1)
#                #        ] + [
#                #            chr(0x55)
#                #        ]))
#                #    else:
#                #        # low-res individual channel updates A0|a ch v
#                #        for i in self._changed_channels:
#                #            if not self.channels[i].level:
#                #                self.network.send(chr(0x90 | self.address) + chr(i & 0x3f))
#                #            elif self.channels[i].level >= self.resolution-1:
#                #                self.network.send(chr(0x90 | self.address) + chr(0x40 | (i & 0x3f)))
#                #            else:
#                #                self.network.send(
#                #                    chr(0xa0 | self.address) + 
#                #                    chr(i & 0x3f) +
#                #                    chr(self.channels[i].level & 0x7f)
#                #                )
#=======
#>>>>>>> .r91
            self._reset_queue()
            self.stats.append((time.time(), byte_count))
            

    def set_channel(self, id, level, force=False):
        self._queue_set_channel(id, *self.channels[id].set_level(level), force=force)

    def set_channel_on(self, id, force=False):
        self._queue_set_channel(id, *self.channels[id].set_on(), force=force)

    def set_channel_off(self, id, force=False):
        self._queue_set_channel(id, *self.channels[id].set_off(), force=force)

    def kill_channel(self, id, force=False):
        self._queue_set_channel(id, *self.channels[id].kill(), force=force)

    def kill_all_channels(self, force=False):
        for ch in self.channels:
            self.channels[ch].kill()
        self.network.send(chr(0x80 | self.address))

    def all_channels_off(self, force=False):
        for ch in self.channels:
            self.set_channel_off(ch, force)
        self.flush(force)

    def initialize_device(self):
        self.network.send(chr(0xf0 | self.address) + chr(0x74))     # turn off config mode
        self.kill_all_channels(False)
        self.all_channels_off(False)

    def raw_ramp_up(self, channel, steps, delay):
        self.flush()
        self.channels[channel].set_level(self.resolution - 1)
        self.network.send(chr(0xC0 | self.address) + self._8_bit_string([
            0x40 | (channel & 0x3f),
            steps - 1,
            delay - 1
        ]))

    def raw_ramp_down(self, channel, steps, delay):
        self.flush()
        self.channels[channel].set_level(0)
        self.network.send(chr(0xC0 | self.address) + self._8_bit_string([
            channel & 0x3f,
            steps - 1,
            delay - 1
        ]))


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
            self.network.send(chr(0xF0 | self.address) + self._8_bit_string(
                self._device_commands[command].format(
                ''.join([chr(i & 0x7f) for i in args if isinstance(i, int)]),
                chr(0x7f & reduce((lambda x,y: x|y), [self._dev_bitmasks.get(k, 0) for k in args], 0)),
            )))
        else:
            raise ValueError("Unknown raw control command \"{0}\" for Lumos board {1}".format(command, self.address))

    def raw_set_phase(self, value):
        self.network.send(chr(0xF0 | self.address) + self._8_bit_string([
            0x40 | ((value >> 7) & 0x03),
            value & 0x7f
            ]) + "PO")

    def raw_set_address(self, value):
        if 0 <= value <= 15:
            self.network.send(chr(0xF0 | self.address) + self._8_bit_string([
                0x60 | (value & 0x0f),
            ]) + 'IAD')
            self.address = value
        else:
            raise ValueError('New device address {0} out of range [0,15]'.format(value))

    def raw_download_sequence(self, id, bits):
        "Download a compiled sequence <id> consisting of <bits> (a sequence of integers)"

        self.network.send(chr(0xF0 | self.address) + self._8_bit_string([0x04, id, len(bits)-1] 
            + bits) + 'Ds')

    def raw_sensor_trigger(self, sens_id, seq_id, inverse=False, execf=False):
        # inverse is "active high"
        self.network.send(chr(0xF0 | self.address) + self._8_bit_string([
            0x06, 
            (0x00 if inverse else 0x10) | (0x20 if execf else 0x00) | 
                {'A':0, 'B':1, 'C':2, 'D':3}[sens_id],
            seq_id
        ]) + '<')

    def raw_configure_device(self, conf_obj):
        self.network.send(chr(0xF0 | self.address) + self._8_bit_string([
            0x71,
            reduce((lambda x,y: x|y), 
                [{'A': 0x40, 'B': 0x20, 'C': 0x10, 'D': 0x08}[s] 
                    for s in conf_obj.configured_sensors], 0)
            | (0x04 if conf_obj.dmx_start else 0x00)
            | (0 if not conf_obj.dmx_start else ((conf_obj.dmx_start - 1) >> 7) & 0x03),
            (0 if not conf_obj.dmx_start else ((conf_obj.dmx_start - 1) & 0x7f)),
            0x3A,
            0x3D
        ]))
            

# Response packet from QUERY command (35 bytes):
# note the rom version byte also serves to indicate the format of the response
# bytes which follow.  If the query packet format changes, the ROM version byte
# MUST also change.
#        0       1         2        3        4        5        6        7
#    1111aaaa 00011111 VVVVvvvv 0ABCDd0c cccccccc 0ABCDqsf 0ABCDX0p pppppppp 
#        \__/           \_/\__/  \__/|\_________/  \__/|||  \__/|\_________/  
#          |             maj |     | |   |           | |||   |  |      `--phase
#          `--reporting    minor   | |   `--DMX      | |||   |  `--config locked?
#              unit addr  rom      | |      channel  | |||   `--active
#                         vers.    | |               | ||`--mem full?
#                                  | `--DMX mode?    | |`--sleeping?
#                                  `--configured     | `--config mode?
#                                                    `--masks
#        8        9       10       11       12       13
#    eeeeeeee eeeeeeee MMMMMMMM MMMMMMMM 0Q0iiiii 0xxxxxxx 
#     \______________/  \______________/  | \___/  \_____/
#        `--EEPROM free    `--RAM free    |   |       `--executing seq.
#                                         |   `--device model
#                                         `--seq running?
#       14        15       
#    00eE0000 0IIIIIII                  	Sensor trigger info for A
#    0owE0001 0IIIIIII                  	Sensor trigger info for B
#    0owE0010 0IIIIIII                  	Sensor trigger info for C
#    0owE0011 0IIIIIII                  	Sensor trigger info for D
#       22       23       24       25       26       27       28
#    ffffffff ffffffff 0000000p pppppppp ssssssss ssssssss 00110011
#    \______/ \______/       \_________/ \_______________/
#        |        |               |              `--serial number
#        |        |               `--phase (channels 24-47)
#        |        `--fault code (channels 24-47)
#        `--fault code (channels 0-23)
#
# XXX need to recode for new query packet

    def raw_query_device_status(self, timeout=0):
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
                    return 35
                if ord(d[cb]) == (0xf0 | self.address):
                    if len(d) - cb <= 1:
                        return 34
                    if ord(d[cb+1]) == 0x1f:
                        return max(0, 35 - (len(d) - cb))
            
        reply = self.network.input(packet_scanner, timeout=timeout)
        reply = [ord(i) for i in reply]

        if len(reply) != 35:
            raise DeviceProtocolError("Query packet response malformed (len={0})".format(len(reply)))
        if reply[34] != 0x33:
            raise DeviceProtocolError("Query packet response malformed (end={0:02X})".format(reply[34]))
        if reply[2] != 0x30:
            raise DeviceProtocolError("Query packet version unsupported ({0}.{1})".format((reply[2] >> 4) & 0x07, (reply[2] & 0x0f)))

        if any([x & 0x80 for x in reply[1:]]):
            raise DeviceProtocolError("Query packet response malformed (high bit in data area: {0})".format(
                ' '.join(['{0:02X}'.format(x) for x in reply])))


        status = LumosControllerStatus()
        for sensor_id, bitmask in ('A', 0x40), ('B', 0x20), ('C', 0x10), ('D', 0x08):
            if reply[3] & bitmask:
                status.config.configured_sensors.append(sensor_id)
                status.sensors[sensor_id].configured = True

            if reply[5] & bitmask:
                status.sensors[sensor_id].enabled = True

            if reply[6] & bitmask:
                status.sensors[sensor_id].on = True

        if reply[3] & 0x04:
            status.config.dmx_start = ((reply[3] & 0x03) << 7) | (reply[4] & 0x7f)
        else:
            status.config.dmx_start = None

        status.rom_version = ((reply[2] >> 4) & 0x07, reply[2] & 0x0f)
        status.in_config_mode = bool(reply[5] & 0x04)
        status.config_mode_locked = bool(reply[6] & 0x04)
        status.in_sleep_mode = bool(reply[5] & 0x02)
        status.err_memory_full = bool(reply[5] & 0x01)
        status.phase_offset = ((reply[6] & 0x03) << 7) | (reply[7] & 0x7f)
        status.eeprom_memory_free = ((reply[8] & 0x7f) << 7) | (reply[9] & 0x7f)
        status.ram_memory_free = ((reply[10] & 0x7f) << 7) | (reply[11] & 0x7f)
        if reply[12] & 0x40:
            status.current_sequence = reply[13] & 0x7f
        else:
            status.current_sequence = None
        if reply[12] & 0x03 == 0:
            status.hardware_type = 'lumos48ctl'
            status.channels = 48
        elif reply[12] & 0x03 == 1:
            status.hardware_type = 'lumos24dc'
            status.channels = 24
        else:
            status.hardware_type = 'unknown'
            status.channels = 0

        for group, sensor_id in enumerate(['A', 'B', 'C', 'D']):
            flags = reply[group * 4 + 14]
            if flags & 0x03 != group:
                raise DeviceProtocolError("Query packet response malformed (sensor group {0} ID as {1} ({2:02X}))".format(
                    group, flags & 0x03, flags))
            status.sensors[sensor_id].trigger_mode = ('once' if flags & 0x40 else 
                                                        ('while' if flags & 0x20 else 'repeat'))
            status.sensors[sensor_id].active_low = bool(flags & 0x01)
            status.sensors[sensor_id].pre_trigger = reply[group * 4 + 15]
            status.sensors[sensor_id].trigger = reply[group * 4 + 16]
            status.sensors[sensor_id].post_trigger = reply[group * 4 + 17]

        status.last_error = reply[30]
        status.last_error2 = reply[31]
        status.phase_offset2 = ((reply[32] & 0x03) << 7) | (reply[33] & 0x7f)

        if status.channels <= 24:
            if status.last_error2 != 0 or status.phase_offset2 != 0:
                raise InternalDeviceError('Query reply packet incorrect for device of this type (LE2=0x{0:02X}, PO2={1})'.format(
                    status.last_error2, status.phase_offset2))
            status.last_error2 = None       # no status at all since the corresponding hardware doesn't exist
            status.phase_offset2 = None
        elif status.phase_offset != status.phase_offset2:
            raise InternalDeviceError('Inconsistent phase offset between CPUs (#0={0}, #1={1})'.format(status.phase_offset, status.phase_offset2))

        return status

class LumosControllerConfiguration (object):
    def __init__(self):
        self.configured_sensors = []    # list of 'A'..'D'
        self.dmx_start = None           # None or 1..512

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
        self.config_mode_locked = False
        self.in_sleep_mode = False
        self.err_memory_full = False
        self.phase_offset = 2
        self.phase_offset2 = 2
        self.last_error = 0
        self.last_error2 = 0
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
