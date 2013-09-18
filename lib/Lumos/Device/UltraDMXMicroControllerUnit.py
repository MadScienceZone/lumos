# 
# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS DEVICE DRIVER: ULTRA DMX MICRO (ENTTEC PROTOCOL)
#
# Lumos Light Orchestration System
# Copyright (c) 2005, 2006, 2007, 2008, 2012, 2013 by Steven L. Willoughby, Aloha,
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

class UltraDMXMicroControllerStatus (object):
    "Internal state of device"

    def __init__(self):
        self.serial_number = None
        self.revision = 0
        self.user_data = ''
        self.break_us = 0
        self.mab_us = 0
        self.packet_speed = 0

class UltraDMXMicroControllerUnit (ControllerUnit):
    """
    Driver for the Ultra DMX Micro USB DMX interface from
    DMX King, based on ENT TEC DMX protocol documentation
    obtained from public sources.
    """
    def __init__(self, id, power_source, network, num_channels=512):
        """
        Constructor for an Ultra DMX Micro device object:
            UltraDMXMicroControllerUnit(id, power_source, [num_channels])

        Specify the correct PowerSource object for this unit, the serial
        (or virtual serial) device into which it's plugged, and optionally
        a number of DMX slots it'll transmit.

	Compatible with DMX interfaces based on the ENT TEC serial protocol.
	(Not guaranteed; tested successfully with the Ultra DMX Micro.)
        """

        ControllerUnit.__init__(self, id, power_source, network, 256)
        self.num_channels = num_channels
        self.type = 'Ultra DMX Micro ({0} channels)'.format(self.num_channels)
        self._changed_channels = False
        self.status = None
        self.channels = [None] * (num_channels+1)

    def iter_channels(self):
        return range(1, self.num_channels+1)

    def __str__(self):
        return self.type

    def channel_id_from_string(self, channel):
        return int(channel)

    def add_channel(self, id, name=None, load=None, dimmer=True, warm=None, resolution=None, power_source=None):
        try:
            id = int(id)
            assert 1 <= id <= self.num_channels
        except:
            raise ValueError("This DMX interface's IDs must be integers from 1-{0}".format(self.num_channels))

        if resolution is not None:
            resolution = int(resolution)
        else:
            resolution=self.resolution

        ControllerUnit.add_channel(self, id, name, load, dimmer, warm, resolution, power_source)

    def flush(self, force=False):
        #
        # send any pending channel level setting commands now.
        #
        if self._changed_channels or force:
            self._send_packet(6, [0] + [
                self.channels[i].level or 0 if self.channels[i] is not None else 0 
                    for i in range(1,self.num_channels+1)
            ])
            self._changed_channels = False
            
    def _set_channel(self, id, old_level, new_level, force=False):
        if old_level != new_level or force:
            self._changed_channels = True

    def set_channel(self, id, level, force=False):
        self._set_channel(id, *self.channels[id].set_level(level), force=force)

    def set_channel_on(self, id, force=False):
        self._set_channel(id, *self.channels[id].set_on(), force=force)

    def set_channel_off(self, id, force=False):
        self._set_channel(id, *self.channels[id].set_off(), force=force)

    def kill_channel(self, id, force=False):
        self._set_channel(id, *self.channels[id].kill(), force=force)

    def kill_all_channels(self, force=False):
        for ch in self.iter_channels():
            self.channels[ch].kill()
        self.flush(force=True)

    def all_channels_off(self, force=False):
        for ch in self.iter_channels():
            self.set_channel_off(ch, force)
        self.flush(force)

    def initialize_device(self):
        self.kill_all_channels(False)
        self.all_channels_off(False)
        self.update_status()

    def _packetlen(self, buf):
        if not buf or len(buf) < 5:
            return 5
        return max(0, (
            ((ord(buf[3]) << 8) & 0xff00) |
            ((ord(buf[2])     ) & 0x00ff)
        ) + 5 - len(buf))

    def _send_packet(self, label, byte_list):
        self.network.send(''.join([chr(i) for i in [
            0x7e,
            label,
            (len(byte_list)     ) & 0xff,
            (len(byte_list) >> 8) & 0xff] + byte_list + 
            [0xe7]
        ]))

    def update_status(self, timeout=10):
        self.status = self.raw_query_device_status(timeout=timeout)

    def commit_status(self):
        self.raw_set_parameters(
            self.status.break_us,
            self.status.mab_us,
            self.status.packet_speed,
            self.status.user_data
        )

    def raw_query_device_status(self, user_size=0, timeout=10):
        status = UltraDMXMicroControllerStatus()
        status.serial_number = self.raw_get_serial_number(timeout)
        status.revision, status.break_us, status.mab_us, status.packet_speed, status.user_data = self.raw_get_parameters(user_size, timeout)

        return status
            
    def raw_get_parameters(self, user_size=0, timeout=10):
        self._send_packet(3, [user_size & 0xff, (user_size >> 8) & 0xff])
        reply = self.network.input(self._packetlen, timeout=timeout)
        if reply[0:2] != '\x7e\x03' or reply[-1] != '\xe7' or len(reply) < 10:
            raise DeviceProtocolError("Get param packet response malformed.")

        return [
            ((ord(reply[5]) >> 8) & 0xff) | (ord(reply[4]) & 0xff), # firmware rev
            ord(reply[6]) * 10.6,   # break time (uS)
            ord(reply[7]) * 10.6,   # MAB time (uS)
            ord(reply[8]),          # DMX packets/sec
            reply[9:-1],            # user data
        ]

    def raw_set_parameters(self, break_us=116.6, mab_us=31.8, packet_speed=40, user_data=None):
        self._send_packet(4, [
            len(user_data) & 0xff,
            (len(user_data) >> 8) & 0xff,
            int(break_us / 10.6),
            int(mab_us / 10.6),
            packet_speed
        ] + list(user_data or ''))

    def raw_get_serial_number(self, timeout=10):
        self._send_packet(10,[])
        reply = self.network.input(self._packetlen, timeout=timeout)
        if len(reply) != 9 or reply[0:4] != '\x7e\x0a\x04\x00' or reply[8] != '\xe7':
            raise DeviceProtocolError("Get S/N packet response malformed.")
        return (
            (ord(reply[4])      & 0x0f)            +
            (ord(reply[4]) >> 4 & 0x0f) * 10       +
            (ord(reply[5])      & 0x0f) * 100      +
            (ord(reply[5]) >> 4 & 0x0f) * 1000     +
            (ord(reply[6])      & 0x0f) * 10000    +
            (ord(reply[6]) >> 4 & 0x0f) * 100000   +
            (ord(reply[7])      & 0x0f) * 1000000  +
            (ord(reply[7]) >> 4 & 0x0f) * 10000000
        )
