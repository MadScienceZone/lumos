# XXX What is "force" for in the flush() method?
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
from functools import reduce

class DeviceProtocolError (Exception): pass
class InternalDeviceError (Exception): pass
class InternalError (Exception): pass

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
        self.channels = 0
        self.serial_number = None
        self.sensors = {
            'A': LumosControllerSensor('A'),
            'B': LumosControllerSensor('B'),
            'C': LumosControllerSensor('C'),
            'D': LumosControllerSensor('D'),
        }
        self.model_specific_data = None
        self.protocol = 0
        self.revision = [0,0,0]

    def describe_model_specific_data(self):
        return ''

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
        self.num_channels = int(num_channels)
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

    def _8_bit_encode(self, byte_list: bytes) -> bytes:
        "Encode raw binary sequence into 7-bit-clean version for sending in a Lumos command stream."
        result = []
        for b in byte_list:
            if b > 0x7f:
                result.extend([0x7e, (b & 0x7f)])
            elif b == 0x7e:
                result.extend([0x7f, 0x7e])
            elif b == 0x7f:
                result.extend([0x7f, 0x7f])
            else:
                result.append(b)
        return bytes(result)

    def _8_bit_decode(self, byte_list: bytes) -> bytes:
        "Decode 7-bit-clean data stream to raw binary."
        result = []
        next_MSB = False
        next_literal = False

        for b in byte_list:
            if next_MSB:
                next_MSB = False
                result.append(b | 0x80)
            elif next_literal:
                next_literal = False
                result.append(b)
            elif b == 0x7e:
                next_MSB = True
            elif b == 0x7f:
                next_literal = True
            else:
                result.append(b)
        return bytes(result)

#    def _8_bit_decode_string(self, byte_string: str) -> bytes:
#        return self._8_bit_decode_packet([ord(i) for i in byte_string])
#    
#    def _8_bit_decode_packet(self, byte_list: bytes) -> bytes:
#        result = []
#        next_MSB = False
#        next_literal = False
#        for byte in byte_list:
#            if next_MSB:
#                next_MSB = False
#                result.append(byte | 0x80)
#            elif next_literal:
#                next_literal = False
#                result.append(byte)
#            elif byte == 0x7e:
#                next_MSB = True
#            elif byte == 0x7f:
#                next_literal = True
#            else:
#                result.append(byte)
#        return result
#                
#    def _8_bit_string(self, byte_list):
#        return ''.join([chr(x) for x in self._8_bit_packet(byte_list)])
#
#    def _8_bit_packet(self, byte_list):
#        "Convert a list of bytes to a list of 8-bit-escaped bytes (may be longer)"
#        result = []
#        for byte in byte_list:
#            if byte > 0x7f:
#                result.extend([0x7e, (byte & 0x7f)])
#            elif byte == 0x7e:
#                result.extend([0x7f, 0x7e])
#            elif byte == 0x7f:
#                result.extend([0x7f, 0x7f])
#            else:
#                result.append(byte)
#        return result

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
            if sum([i.level or 0 for i in list(self.channels.values())]) == 0:
                self.network.send(bytes([0x80 | self.address]))
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
                    # 1011aaaa
                    # 00<chan>
                    # < n-1  >
                    # < level>
                    #    :
                    # < level>
                    # 01010101
                    n_1 = self._max_change - self._min_change
                    packet = bytes([0xb0 | self.address, self._min_change & 0x3f]) + self._8_bit_encode(
                            bytes([n_1 & 0xff] + [
                                ((self.channels[vi].level or 0) if vi in self.channels else 0)
                                for vi in range(self._min_change, self._max_change+1)])) + b'\x55'
                    self.network.send(packet)
                    byte_count += len(packet)
                else:
                    # individual channel updates A0|a ch v
                    for i in self._changed_channels:
                        if not self.channels[i].level:  # covers None and 0
                            # off:
                            # 1001aaaa
                            # 00<chan>
                            self.network.send(bytes([0x90 | self.address, i & 0x3f]))
                            byte_count += 2
                        elif self.channels[i].level >= self.resolution-1:
                            # on:
                            # 1001aaaa
                            # 01<chan>
                            self.network.send(bytes([0x90 | self.address, 0x40 | (i & 0x3f)]))
                            byte_count += 2
                        else:
                            # set:
                            # 1010aaaa
                            # 0l<chan>     dimmer value = hhhhhhhl  
                            # 0hhhhhhh
                            self.network.send(bytes([0xa0 | self.address]) + self._8_bit_encode(bytes([
                                (i & 0x3f) | ((self.channels[i].level << 6) & 0x40),
                                (self.channels[i].level >> 1) & 0x7f,
                            ])))
                            byte_count += 3
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
        self.network.send(bytes([0x80 | self.address]))

    def all_channels_off(self, force=False):
        for ch in self.channels:
            self.set_channel_off(ch, force)
        self.flush(force)

    def initialize_device(self):
        self.network.send(bytes([0xf0 | self.address, 0x09]))     # turn off config mode
        self.kill_all_channels(False)
        self.all_channels_off(False)

    def raw_ramp_up(self, channel, steps, delay, cycle=False):
        # 1100aaaa
        # CDcccccc  C=cycle, D=dir, c=chan
        # (steps-1)
        # (time-1)
        self.flush()
        self.channels[channel].set_level(self.resolution - 1)
        self.network.send(bytes([0xC0 | self.address]) + self._8_bit_encode(bytes([
            (0x80 if cycle else 0x00) | 0x40 | (channel & 0x3f),
            steps - 1,
            delay - 1,
        ])))

    def raw_ramp_down(self, channel, steps, delay, cycle=False):
        self.flush()
        self.channels[channel].set_level(0)
        self.network.send(bytes([0xC0 | self.address]) + self._8_bit_encode(bytes([
            (0x80 if cycle else 0x00) | (channel & 0x3f),
            steps - 1,
            delay - 1,
        ])))

    _device_commands = {
        'sleep':    b'\x00ZZ',  # 1111aaaa 00000000 01011010 01011010
        'wake':     b'\x01ZZ',  # 1111aaaa 00000001 01011010 01011010
        'shutdown': b'\x02XY',  # 1111aaaa 00000010 01011000 01011001
        'execute':  (lambda a: bytes([0x05, a[0]&0x7f])), # 1111aaaa 00000101 0xxxxxxx
        'masksens': (lambda a: bytes([0x07, 0x7f & reduce((lambda x,y: x|y), [LumosControllerUnit._dev_bitmasks.get(k, 0) for k in a], 0)])), # 1111aaaa 00000111 0000ABCD
        'clearmem': b'\x08CA',  # 1111aaaa 00001000 01000011 01000001
        'noconfig': b'\x70',    # 1111aaaa 01110000 
        'xconfig':  b'\x74',    # 1111aaaa 01111001 DEPRECATED
        'config':   b'\x0eY&\\',# 1111aaaa 00001110 01011001 00100110 01011100
        'forbid':   b'\x09',    # 1111aaaa 00001001
        '__reset__':b'\x73$r',  # 1111aaaa 01110011 00100100 01110010
        '__baud__': (lambda a: bytes([0x72, a[0]&0x7f, 0x26])), # 1111aaaa 01110010 0xxxxxxx 00100110
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
            f = self._device_commands[command]
            if callable(f):
                pkt = f(args)
            else:
                pkt = f
            self.network.send(bytes([0xf0 | self.address]) + self._8_bit_encode(pkt))
        else:
            raise ValueError("Unknown raw control command \"{0}\" for Lumos board {1}".format(command, self.address))

    def raw_begin_rom_download(self, *args):
        if args != ('CONFIRM','ROM','DOWNLOAD','YES','REALLY','I','MEAN','IT'):
            raise ValueError("Invalid arguments to raw_begin_rom_download() method: {0}".format(args))

        self.network.send(bytes([0xF0 | self.address, 0x75, 0x33, 0x4C, 0x1C]))

    def raw_set_phase(self, value):
        # 1111aaaa 010000PP 0ppppppp 01010000 01001111  (phase is PPppppppp)
        self.network.send(bytes([0xF0 | self.address]) + self._8_bit_encode(bytes([ 
            0x40 | ((value >> 7) & 0x03),
            value & 0x7f,
            0x50, 0x4f])))

    def raw_set_address(self, value):
        # 1111aaaa 0110AAAA 01001001 01000001 01000100  (address a -> A)
        if 0 <= value <= 15:
            self.network.send(bytes([0xF0 | self.address,
                0x60 | (value & 0x0f),
                0x49,
                0x41,
                0x44,
            ]))
            self.address = value
        else:
            raise ValueError('New device address {0} out of range [0,15]'.format(value))

    def raw_download_sequence(self, id, bits: bytes):
        "Download a compiled sequence <id> consisting of <bits> (a bytearray)"
        # 1111aaaa 00000100 0iiiiiii (N-1) (data....)*N 01000100 01110011

        if bits:
            self.network.send(bytes([0xf0 | self.address, 0x04]) + self._8_bit_encode(bytes([id&0x7f,
                len(bits)-1]) + bits) +
                bytes([0x44, 0x73]))

    def raw_sensor_trigger(self, sens_id, pre_seq_id, seq_id, post_seq_id, inverse=False, execf=False):
        # inverse is "active high"
        # 1111aaaa 00000110 0owe00ii 0(pre) 0(exec) 0(post) 00111100
        self.network.send(bytes([0xf0 | self.address]) + self._8_bit_encode(bytes([0x06, 
            (0x00 if inverse else 0x10) |
            (0x20 if execf   else 0x00) |
            {'A':0, 'B':1, 'C':2, 'D':3}[sens_id.upper()],
            pre_seq_id & 0x7f,
            seq_id & 0x7f,
            post_seq_id & 0x7f,
            0x3c])))

    def raw_configure_device(self, conf_obj):
        # 1111aaaa 01110001 0ABCDdcc 0CCCCCCC 00111010 00111101
        self.network.send(bytes([0xf0 | self.address]) + self._8_bit_encode(bytes([
            0x71,
            reduce((lambda x,y: x|y), 
                [{'A': 0x40, 'B': 0x20, 'C': 0x10, 'D': 0x08}[s.upper()] 
                    for s in conf_obj.configured_sensors], 0)
            | (0x04 if conf_obj.dmx_start else 0x00)
            | (0 if not conf_obj.dmx_start else ((conf_obj.dmx_start - 1) >> 7) & 0x03),
            (0 if not conf_obj.dmx_start else ((conf_obj.dmx_start - 1) & 0x7f)),
            0x3A,
            0x3D])))

# Response packet from QUERY command (37 or 42+ bytes):
# DEPRECATED:
#   note the ROM version byte also serves to indicate the format of the response
#   bytes which follow.  If the query packet format changes, the ROM version byte
#   MUST also change.
# NOW:
#   The ROM version byte is obsolete. Legacy boards are now called "protocol 0"
#   and send a 37-byte response, where the old ROM version byte is still valid.
#   Current firmware instead sets bit $20 in byte #12 (specified as 0 in the 
#   original protocol). With this bet set to 1, additional bytes are added to
#   the end which give the full revision number protocol number (which determines
#   the format of the response packet), and device model-specific configuration
#   information for specific fields not standard across all Lumos-compatible
#   devices.
#
#    1111aaaa 00011111 00110000 0ABCDdcc 0ccccccc 0ABCDqsf 0ABCDXpp 0ppppppp 
#        \__/           \_/\__/  \__/|\_________/  \__/|||  \__/|\_________/  
#          |             maj |     | |   |           | |||   |  |      `--phase
#          `--reporting    minor   | |   `--DMX      | |||   |  `--config locked?
#              unit addr  rom      | |      channel  | |||   `--active
#                         vers.    | |               | ||`--mem full?
#                       DEPRECATED | `--DMX mode?    | |`--sleeping?
#                                  `--configured     | `--config mode?
#                                                    `--masks
#
#    0eeeeeee 0eeeeeee 0MMMMMMM 0MMMMMMM 0QPiiiii 0xxxxxxx 
#     \______________/  \______________/  ||\___/  \_____/
#        `--EEPROM free    `--RAM free    ||  |       `--executing seq.
#                                         ||  `--device model
#                                         |`--0=legacy protocol 0; 1=protocol 1+
#                                         `--seq running?
#
#    0owE0000 0IIIIIII 0iiiiiii 0PPPPPPP	Sensor trigger info for A
#    0owE0001 0IIIIIII 0iiiiiii 0PPPPPPP	Sensor trigger info for B
#    0owE0010 0IIIIIII 0iiiiiii 0PPPPPPP	Sensor trigger info for C
#    0owE0011 0IIIIIII 0iiiiiii 0PPPPPPP	Sensor trigger info for D
#
#    0fffffff 0fffffff 000000pp 0ppppppp ssssssss ssssssss 
#    \______/ \______/       \_________/ \______S/N______/
#        |        |               `--phase (channels 24-47)
#        |        `--fault code (channels 24-47)
#        `--fault code (channels 0-23)
#
#  IF protocol > 0:
#    pppppppp RRRRRRRR rrrrrrrr PPPPPPPP nnnnnnnn |<------n bytes------->|
#    \______/ \______/ \______/ \______/          \______________________/
#        |        |        |        |                        |
#        protocol major    minor    patch                    model-specific data
#
#
#    00110011
#
# Note that the number of bytes actually received may be greater due to the
# encoding used to guard 8-bit values.
    def _find_command_byte(self, d: bytes, start=0):
        if d is None:
            return -1

        for i in range(start, len(d)):
            if d[i] & 0x80:
                return i
        return -1

    def raw_query_device_status(self, timeout=0):
        # 1111aaaa 00000011 00100100 01010100
        # response: 1111aaaa 00011111 ...
        self.network.send(bytes([0xf0 | self.address, 0x03, 0x24, 0x54]))

        def packet_scanner(d: bytes):
            start=0
            while True:
                cb = self._find_command_byte(d, start)
                start = cb+1
                if cb < 0:
                    return 37
                if d[cb] == 0xf0 | self.address:
                    # len(d) - cb  == number of bytes in our packet so far
                    if len(d) - cb <= 1:
                        return 36
                    if d[cb+1] == 0x1f:
                        # reply to this unit's query command
                        # watch for 0x7e, 0x7f
                        extra_bytes = 0
                        skip_next = False
                        msb_next = False
                        target_length = 35
                        model_specific_length = 0
                        protocol = 0
                        for pos, ch in enumerate(d[cb+2:]):
                            # pos is our position AFTER the leading two bytes (so just in the payload itself)
                            # this needs to be exactly 35 bytes (37 total) for protocol 0, or 42+d[cb+40] for protocol 1+
                            # ... plus extra_bytes in either case (to account for escapes)
                            if msb_next:
                                ch |= 0x80
                                msb_next = False
                            if not skip_next:
                                if ch == 0x7e:
                                    extra_bytes += 1
                                    msb_next = True
                                    continue
                                if ch == 0x7f:
                                    extra_bytes += 1
                                    skip_next = True
                                    continue
                            else:
                                skip_next = False

                            if pos == 10+extra_bytes:
                                # we're at [cb+12]; determine our protocol number
                                if ch & 0x20:
                                    # protocol 1+
                                    target_length = 40
                                    protocol = 1
                            elif protocol > 0 and pos == 38+extra_bytes:
                                # we're at [cb+40], where our data length is found
                                model_specific_length = ch
                            
                            if pos >= target_length+extra_bytes+model_specific_length: break

                        return max(0, (target_length + 2) - (len(d) - cb) + extra_bytes + model_specific_length)
            
        reply_buf = self.network.input(packet_scanner, timeout=timeout)
        reply = []
        set_msb = False
        literal_next = False
        #
        # skip over possible junk ahead of our reply packet
        #
        skipped_data = []
        state=0
        for i in reply_buf:
            if state == 0:      # wait for command byte addressed to us
                if i == (0xf0 | self.address):
                    state=1
                else:
                    skipped_data.append(i)

            elif state == 1:    # this byte must be 0x1f
                if i == 0x1f:
                    state=2
                    reply=[0xf0|self.address, 0x1f]
                    if skipped_data:
                        self.network.diagnostic_output('LumosControllerUnit.raw_query_device_status: Skipped over {0} superfluous byte{1} before finding reply packet: {2}'.format(
                            len(skipped_data),
                            's' if len(skipped_data)==1 else '',
                            ' '.join(['{0:02X}'.format(c) for c in skipped_data])
                        ))
                else:
                    skipped_data.extend([0xf0 | self.address, i])
                    state=0

            elif state == 2:    # we're in the response packet, interpret it!
                if i > 0x7f: 
                    raise DeviceProtocolError("Query packet response malformed (high bit in data area: {0})".format(
                        ' '.join(['{0:02X}'.format(x) for x in reply])))

                if set_msb:
                    set_msb = False
                    reply.append(i | 0x80)
                elif literal_next:
                    literal_next = False
                    reply.append(i)
                elif i == 0x7e:
                    set_msb = True
                elif i == 0x7f:
                    literal_next = True
                else:
                    reply.append(i)
            else:
                raise InternalError('Undefined state {0} in packet scanner'.format(state))

        if len(reply) < 37:
            raise DeviceProtocolError("Query packet response malformed (len={0})".format(len(reply)))

        status = LumosControllerStatus()
        self.update_status_from_packet(status, reply)
        return status


    def update_status_from_packet(self, status: LumosControllerStatus, reply: bytes):
        if reply[12] & 0x20:
            # protocol > 0
            if len(reply) < 42:
                raise DeviceProtocolError("Query packet response malformed (len={0}), protocol>0".format(len(reply)))
            status.protocol = reply[36]
            status.revision = reply[37:40]
            msd_length = reply[40]
            if len(reply) < 42+msd_length:
                raise DeviceProtocolError("Query packet response malformed (len={0}), protocol>0".format(len(reply)))
            if msd_length > 0:
                status.model_specific_data = reply[41:41+msd_length]
            if reply[41+msd_length] != 0x33:
                raise DeviceProtocolError("Query packet response malformed (end@{1}={0:02X})".format(reply[41+msg_length], 41+msg_length))
        else:
            # protocol 0
            if reply[36] != 0x33:
                raise DeviceProtocolError("Query packet response malformed (end={0:02X})".format(reply[34]))
            status.protocol = 0
            status.revision = [(reply[2] >> 4) & 0x07, (reply[2] & 0x0f), 0]
            status.model_specific_data = None

#        if reply[2] != 0x30 and reply[2] != 0x31:
#            # We support ROM version 3.0 and 3.1
#            raise DeviceProtocolError("Query packet version unsupported ({0}.{1})".format((reply[2] >> 4) & 0x07, (reply[2] & 0x0f)))

        for sensor_id, bitmask in ('A', 0x40), ('B', 0x20), ('C', 0x10), ('D', 0x08):
            if reply[3] & bitmask:
                status.config.configured_sensors.append(sensor_id)
                status.sensors[sensor_id].configured = True

            if reply[5] & bitmask:
                status.sensors[sensor_id].enabled = False
            else:
                status.sensors[sensor_id].enabled = True

            if reply[6] & bitmask:
                status.sensors[sensor_id].on = True

        if reply[3] & 0x04:
            status.config.dmx_start = (((reply[3] & 0x03) << 7) | (reply[4] & 0x7f)) + 1
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
        if reply[12] & 0x1F == 0:
            status.hardware_type = 'lumos48ctl'
            status.channels = 48
        elif reply[12] & 0x1F == 1:
            status.hardware_type = 'lumos24dc'
            status.channels = 24
        elif reply[12] & 0x1F == 2:
            status.hardware_type = 'lumos4dc'
            status.channels = 4
        else:
            status.hardware_type, status.channels = self._unknown_device_type(reply[12] & 0x1F);

        for group, sensor_id in enumerate(['A', 'B', 'C', 'D']):
            flags = reply[group * 4 + 14]
            if flags & 0x03 != group:
                #raise DeviceProtocolError("Query packet response malformed (sensor group {0} ID as {1} ({2:02X}))".format(
                #    group, flags & 0x03, flags))
                pass
            status.sensors[sensor_id].trigger_mode = ('once' if flags & 0x40 else 
                                                        ('while' if flags & 0x20 else 'repeat'))
            status.sensors[sensor_id].active_low = bool(flags & 0x01)
            status.sensors[sensor_id].pre_trigger = reply[group * 4 + 15]
            status.sensors[sensor_id].trigger = reply[group * 4 + 16]
            status.sensors[sensor_id].post_trigger = reply[group * 4 + 17]

        status.last_error = reply[30]
        status.last_error2 = reply[31]
        status.phase_offset2 = ((reply[32] & 0x03) << 7) | (reply[33] & 0x7f)
        status.serial_number = ((reply[34] << 8) | reply[35])
        #print "33={0:02X} 34={1:02X}".format(reply[34], reply[35])
        if status.serial_number == 0 or status.serial_number == 0xffff:
            status.serial_number = None

        self._receive_model_specific_data(status, reply)
#        if status.channels <= 24:
#            if status.last_error2 != 0 or status.phase_offset2 != 0:
#                raise InternalDeviceError('Query reply packet incorrect for device of this type (LE2=0x{0:02X}, PO2={1})'.format(
#                    status.last_error2, status.phase_offset2))
#            status.last_error2 = None       # no status at all since the corresponding hardware doesn't exist
#            status.phase_offset2 = None
#        elif status.phase_offset != status.phase_offset2:
#            raise InternalDeviceError('Inconsistent phase offset between CPUs (#0={0}, #1={1})'.format(status.phase_offset, status.phase_offset2))
#

    def _receive_model_specific_data(self, status, reply):
        pass

    def _unknown_device_type(self, code):
        return 'unknown', 0

class LumosControllerConfiguration (object):
    def __init__(self):
        self.configured_sensors = []    # list of 'A'..'D'
        self.dmx_start = None           # None or 1..512

    def __str__(self):
        return "LumosControllerConfiguration<configured_sensors={0},dmx_start={1}>".format(
            self.configured_sensors,
            self.dmx_start
        )

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


