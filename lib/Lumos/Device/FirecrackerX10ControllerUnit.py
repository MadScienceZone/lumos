# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS DEVICE DRIVER: X-10 CM17A "FIRECRACKER"
# ***UNTESTED*** SPECULATIVE CODE.  NOT READY FOR USE!
#
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Device/FirecrackerX10ControllerUnit.py,v 1.5 2008-12-31 00:25:19 steve Exp $
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
from Lumos.Device.X10ControllerUnit import X10ControllerUnit

# **MUST** be plugged into a FirecrackerSerialNetwork device.

#
# Protocol:
#
# transmit MSB first in 40-bit packets per command:
#    D5       AA       xx       xx       AD
# 11010101 10101010 xxxx0x00 xxxxx000 10101101
# \____header_____/ \____command____/ \footer/
#
# commands:
# House Code A   0110xxxx xxxxxxxx 6000
# House Code B   0111xxxx xxxxxxxx 7000
# House Code C   0100xxxx xxxxxxxx 4000
# House Code D   0101xxxx xxxxxxxx 5000
# House Code E   1000xxxx xxxxxxxx 8000
# House Code F   1001xxxx xxxxxxxx 9000
# House Code G   1010xxxx xxxxxxxx A000
# House Code H   1011xxxx xxxxxxxx B000
# House Code I   1110xxxx xxxxxxxx E000
# House Code J   1111xxxx xxxxxxxx F000
# House Code K   1100xxxx xxxxxxxx C000
# House Code L   1101xxxx xxxxxxxx D000
# House Code M   0000xxxx xxxxxxxx 0000
# House Code N   0001xxxx xxxxxxxx 1000
# House Code O   0010xxxx xxxxxxxx 2000
# House Code P   0011xxxx xxxxxxxx 3000
# Unit Code  1   xxxxx0xx x0x00xxx 0000
# Unit Code  2   xxxxx0xx x0x10xxx 0010
# Unit Code  3   xxxxx0xx x0x01xxx 0008
# Unit Code  4   xxxxx0xx x0x11xxx 0018
# Unit Code  5   xxxxx0xx x1x00xxx 0040
# Unit Code  6   xxxxx0xx x1x10xxx 0050
# Unit Code  7   xxxxx0xx x1x01xxx 0048
# Unit Code  8   xxxxx0xx x1x11xxx 0058
# Unit Code  9   xxxxx1xx x0x00xxx 0400
# Unit Code 10   xxxxx1xx x0x10xxx 0410
# Unit Code 11   xxxxx1xx x0x01xxx 0408
# Unit Code 12   xxxxx1xx x0x11xxx 0418
# Unit Code 13   xxxxx1xx x1x00xxx 0440
# Unit Code 14   xxxxx1xx x1x10xxx 0450
# Unit Code 15   xxxxx1xx x1x01xxx 0448
# Unit Code 16   xxxxx1xx x1x11xxx 0458
# BRIGHT         hhhhxxxx 1x001xxx 0088 +5%; NO UNIT CODE
# DIM            hhhhxxxx 1x011xxx 0098 -5%; NO UNIT CODE
# ON             hhhhxuxx 0u0uuxxx 0000
# OFF            hhhhxuxx 0u1uuxxx 0020
#
# These are transmitted serially on the DTR and RTS lines.
# One of the lines MUST be asserted at all times to power the
# Firecracker unit.  The encodings are:
#
# RTS DTR
#  0   0   Reset (power off)
#  1   0   Transmit 1
#  0   1   Transmit 0
#  1   1   Idle
#
# Wait at least .5mS between each transition.
#

bits = {
#   HOUSE CODES  UNIT CODES     H/U COMMANDS      HOUSE COMMANDS
    'A': 0x6000,  '1': 0x0000,  'on':   0x0000,   'up': 0x0088,
    'B': 0x7000,  '2': 0x0010,  'off':  0x0020,   'dn': 0x0098,
    'C': 0x4000,  '3': 0x0008,
    'D': 0x5000,  '4': 0x0018,
    'E': 0x8000,  '5': 0x0040,
    'F': 0x9000,  '6': 0x0050,
    'G': 0xa000,  '7': 0x0048,
    'H': 0xb000,  '8': 0x0058,
    'I': 0xe000,  '9': 0x0400,
    'J': 0xf000, '10': 0x0410,
    'K': 0xc000, '11': 0x0408,
    'L': 0xd000, '12': 0x0418,
    'M': 0x0000, '13': 0x0440,
    'N': 0x1000, '14': 0x0450,
    'O': 0x2000, '15': 0x0448,
    'P': 0x3000, '16': 0x0458,
}

def packet(id, op):
    if op in ('up','dn'):
        b = bits[id[0]] | bits[op]
    else:
        b = bits[id[0]] | bits[id[1:]] | bits[op]
        
    return chr(0xd5)+chr(0xaa)+chr((b>>8)&0xff)+chr(b&0xff)+chr(0xad)

class FirecrackerX10ControllerUnit (X10ControllerUnit):
    def __init__(self, id, power, network, resolution=21):
        '''
        Constructor for a CM17a X10 object:
            FirecrackerX10ControllerUnit(power, [resolution])

        Specify the correct PowerSource object for this unit.
        The resolution defaults to 21, which matches the 5%
        delta mentioned in the CM17a protocol spec from X-10.
        '''
        X10ControllerUnit.__init__(self, id, power, network, resolution)
        self.type = 'X-10 CM17a "Firecracker" Controller'

    def _proto_set_channel(self, id, old_level, new_level, force=False):
        if new_level == old_level and not force: return ''
        #
        # We only turn fully off when we are told to,
        # since if we dim to zero we keep the ability to
        # fade back up, too.
        #
        # Going from anything to OFF is easy, just send
        # the OFF code.  However, this means our only
        # next option is fully ON.  You can't fade up
        # from off, at least not on all X10 dimmers.
        #
        if new_level is None:
            return packet(id, 'off')
        #
        # Any other change in level is going to require
        # starting off by getting the unit's attention by
        # sending it an ON command.  If the unit used to
        # be OFF, that will turn it fully on (see below);
        # but otherwise it won't affect the brightness but
        # will make it listen to subsequent DIM or BRIGHT
        # commands.
        #
        response = packet(id, 'on')
        if old_level is None:
            #
            # Going from OFF to ON is easy.  And since going
            # from OFF to anything else involves first turning
            # on the unit, we'll start by turning it fully on.
            #
            # If we wanted a dimmer level less than that, we'll
            # have to dim down to it.  (So if we're going from
            # "OFF" to "dimmer level zero" we still have to turn
            # fully on, then fade to black.  It's just how the 
            # X10 dimmers are designed.  But THEN we can fade
            # the dimmer back up from zero at will as long as
            # it doesn't get turned OFF again.)
            #
            if new_level < self.resolution-1:
                response += (self.resolution-1-new_level) * packet(id, 'dn')
        elif new_level > old_level:
            #
            # If we're going UP from an old dimmer level to a new
            # dimmer level, we send ON + some number of BRIGHT 
            # commands.
            #
            response += (new_level-old_level) * packet(id, 'up')
        else:
            #
            # Going DOWN from an old dimmer level to a new
            # level.
            #
            response += (old_level-new_level) * packet(id, 'dn')

        return response


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
            self.kill_channel(ch, force)

    def all_channels_off(self, force=False):
        for ch in self.channels:
            self.set_channel_off(ch, force)

    def initialize_device(self):
        self.kill_all_channels(True)
        # Force OFF commands to be transmitted out
        # we need to do this because kill_all_channels() won't
        # send anything to change channels it thinks are already
        # off.
        #for ch in self.channels:
        #    self.network.send(self._proto_set_channel(ch, 0, None))
        # Then adjust dimmer levels for warmed devices
        self.all_channels_off()
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
