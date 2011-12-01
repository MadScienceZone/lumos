# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS DEVICE DRIVER: X-10 TW523 + LynX10
# ***UNTESTED*** SPECULATIVE CODE.  NOT READY FOR USE!
#
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Device/LynX10ControllerUnit.py,v 1.5 2008-12-31 00:25:19 steve Exp $
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

# XXX How do we pause waiting for the unit to be reset/ready? XXX
# XXX We can refactor some of this, including recognizing and XXX
# XXX batching up dimmer changes on the same house code which XXX
# XXX can be done simultaneously.                             XXX
#
# The LynX10 X-10 controller product accepts serial commands
# (described below) and manipulates a TW523 line interface
# module to send and receive X-10 command codes on the AC
# power lines.
#
# For Lumos, we don't presently handle error codes from our
# devices, in the interest of keeping the real-time show
# output flowing out.  This means we may run into dropped
# events, particularly with X-10 devices where a collision
# may occur or other transmission issues.  X-10 technology
# reliability being what it is, we could still have signals
# not reach their destination and not be aware of that fact
# anyway.  We'll say it again... X-10 is useful for many
# things, and we'll certainly talk to those devices from
# Lumos; however it's not really the recommended type of
# controller device for Lumos.
#
# Commands are sent as a sequence of printable ASCII
# characters followed by a carriage return ('\r').
# Responses are ASCII strings terminated by a return
# as well.  For successful commands, this will be a
# star ("*").  For errors, one of the error codes 
# listed below may appear.  Note that error codes or
# other inputs may appear on their own in some 
# cases.  For example, if an input is received on
# an I/O port, the LynX10 will transmit the string:
#
#  I<pp>=<vv>\r     
# where:
#  <pp>=port (00..FF); <vv>=byte (00..FF)
#
# The I/O ports are for experimental use (I built
# a quiz show control circuit on my LynX10 board,
# for example).  The are NOT used for normal X-10
# control purposes, and are not referenced in this
# driver.
#
# Commands may be "batched" by concatenating them
# before the return.  For example, a command XX
# and a command YY may be sent separately as:
#   XX\r
#   YY\r
# or may be sent together as:
#   XXYY\r
#
# X-10 units sharing a common power circuit are
# addressed individually.  Up to 256 devices may
# be addressed, but these units are grouped into
# 16 groups (called "house codes") of 16 units
# per group.  The house code is a letter "A".."P"
# while the unit code is a number 1..16.  For
# example, a device may be addressed as "A1",
# "C10", or "P16".
#
# The LynX10 controller uses hexadecimal codes to
# specify these device addresses, which works well
# since a single hex digit represents the house 
# code, and the other digit is for the unit
# code.  However, by expressing these as hexadecimal
# values, some translation between standard X-10 
# address nomenclature (which Lumos presents to the
# user) and the codes sent to the device, is necessary.
#
# In the descriptions which follos, <h> represents the
# house code as a single hex character:
#   <h> is the house code 0-F (=A-P)
#         0=A 1=B 2=C 3=D 4=E 5=F 6=G 7=H 
#         8=I 9=J A=K B=L C=M D=N E=O F=P
# while <u> is the unit code as a hex character:
#   <u> is the unit code  0-F (=1-16)
# (Note that the value of <u> has a zero origin rather
# than the one-origin used by X-10, so these are always
# one less than the X-10 unit code number.)
#
# F0<h><u>         turn off unit
# F1<h>            turn off all lights
# F2<h>            turn off all units
# F3               turn off all lights, all house codes
# F4               turn off all units, all house codes
# N0<h><u>         turn on unit
# N1<h>            turn on all lights
# N2               turn on all lights, all house codes
# D<n><h><u>       MODE 0:  Set unit to brightness level <n> (0-F)
# D0<h><n>         MODE 1:  Send <n> dims to house code (n: 1-F, 0=1)
# D1<h><n>         MODE 1:  Send <n> brights to house code (n: 1-F, 0=1)
# S0<h>            Send OFF STATUS to last unit in house code <h>
# S1<h>            Send ON STATUS to last unit in house code <h>
# S2<h><u>         Request status of unit
# S3               Get LynX-10 status as "S=xx\r":
#                       7  6  5   4    3     2     1    0
#                       RESERVED XON XOFF EEPROM FREQ TW523
#                       X  X  X  NO  NO   BAD    60Hz OK           <-- 0
#                       X  X  X  YES YES  OK     50Hz No Power     <-- 1
# X0<h><u>         Raw X10 code: address unit for next command
#                   Multiple X0<h><u>'s will address a set of units to respond
# X1<h>0           Raw X10 code: Send ALL UNITS OFF to house <h>
# X1<h>1           Raw X10 code: Send ALL LIGHTS ON to house <h>
# X1<h>2           Raw X10 code: Send ON to house <h>
# X1<h>3           Raw X10 code: Send OFF to house <h>
# X1<h>4           Raw X10 code: Send one DIM to house <h>
# X1<h>5           Raw X10 code: Send one BRIGHT to house <h>
# X1<h>6           Raw X10 code: Send ALL LIGHTS OFF to house <h>
# X1<h>7           Raw X10 code: Send EXTENDED CODE to house <h>
# X1<h>8           Raw X10 code: Send HAIL REQUEST to house <h>
# X1<h>9           Raw X10 code: Send HAIL ACK to house <h>
# X1<x>A           Raw X10 code: Send PRESET DIM 0x0<x>
# X1<x>B           Raw X10 code: Send PRESET DIM 0x1<x>
# X1<h>C           Raw X10 code: Send EXTENDED DATA to house <h>
# X1<h>D           Raw X10 code: Send STATUS ON to house <h>
# X1<h>E           Raw X10 code: Send STATUS OFF to house <h>
# X1<h>F           Raw X10 code: Send STATUS REQUEST to house <h>
# H<h>             Hail house code (get HAIL ACK, X1<h>9, if a controller seen)
# R                Reset LynX-10; clear timer; reset EEPROM
# T                Get time since power restored/reset as "dd:hh:mm:ss\r"
# V0               Get LynX-10 version number string
# V1               Get LynX-10 copyright string
# V\r              Get both version number and copyright strings
# C0<e>\r          Get count of E<e> errors as "C0<t>=xxxx\r" (xxxx in hex)
# C0<e>=0          Reset counter
# M00\r            Get MODE register as "M00=xx\r":
#                       7  6  5  4     3        2      1    0
#                       LINE  RESRV REPEATER XON/XOFF DIM DEBUG
#                       TERM  X  X    NO        OFF    0    OFF        <-- 0
#                        *    X  X    YES       ON     1    ON         <-- 1
#                    *00=\r 01=\n 10=\r\n 11=none
# M00=<xx>         Set MODE register
# M01\r            SIO FIFO threshold
# M01=<xx>         Set FIFO threshold (0x10 is good) (01-1C)
# M02\r            Host retransmit attempts after collision
# M02=<xx>         Set retransmits (00-FE; FF=infinite--DONT USE FF)
# M03\r            Command receive timeout in seconds
# M03=<xx>         Set timeout (00-FF; 00=disable)
# O<pp>=<xx>       Output byte <xx> to port <pp>.  FF is front panel lights.
# I<pp>            Input byte from port <pp> as "I<pp>=<xx>\r"
# W0               Save current settings to EEPROM.
# WF               Restore factory defaults; clear all counters and timers.
#
#
# Return codes:
# E0\r             X10 reception error
# E1\r             invalid command
# E2\r             invalid data for command
# E3\r             X10 collision detected
# E4\r             X10 transmission timed out (failed)
# E5\r             X10 lost reception
# E6\r             SIO RX FIFO overrun
# E7\r             Carrier lost
# X<n><h><m>\r     Raw X10 command received (out of band)
#
#
# Diagnostic LEDS:
# ERROR            Bad accumulator
# ERROR+RX         Bad register
# ERROR+TX         Bad memory location
#
# Communications:
#   1200bps, no parity, 8 bits, 1 stop
#   rts/cts handshaking, also xon/xoff if enabled in M00 register
#   
#
# Dimming:
#   X10 dimmers have a peculiarity where they can be 
#   incrementally bumped up or down in brightness, but
#   only if it's "on".  If the unit is "off", then the
#   only option is to turn it fully "on".  For devices
#   which are just being switched on and off, this isn't
#   a problem.  If they're being dimmed, though, we'll 
#   need to keep them "on" but dimmed to 0% output if
#   they're going to later be gradually brightened.
#
#   We handle this by assuming that the channel level of
#   None means fully off, while 0-100 indicates some 
#   dimmer level.  We'll apply the appropriate logic to
#   adjust them.  This will use the flush function

class LynX10ControllerUnit (X10ControllerUnit):
    def __init__(self, id, power, network, resolution=16):
        X10ControllerUnit.__init__(self, id, power, network, resolution)
        self.type = 'LynX-10/TW523 Controller'

    def _x10_to_lynx_id(self, x10_id):
        return self._x10_housecode_to_lynx(x10_id[0]) \
             + self._x10_unitcode_to_lynx(x10_id[1:])

    def _x10_housecode_to_lynx(self, x10_id):
        return str("ABCDEFGHIJKLMNOP".index(x10_id.upper()))

    def _x10_unitcode_to_lynx(self, x10_id):
        return '%X' % (int(x10_id)-1)

    def _proto_set_channel(self, id, old_level, new_level, force=False):
        #
        # Implement logic for what commands we output to move
        # channels from one dimmer level to another.  These are
        # already translated (via the Channel object) to device
        # specific dimmer values, and warm limits or undimmable
        # channels already taken into account.
        #
        if new_level == old_level and not force:
            # The level didn't end up changing on the actual
            # device, so don't send anything.
            return ''

        if new_level is None:
            # We're going to a fully off state, so just turn off
            # the device and be done with it.
            return 'F0' + self._x10_to_lynx_id(id) + '\r'

        # ...so we're changing to an ON state.  We know then 
        # no matter what we'll start off with an ON code.
        # We might add more, depending on what else is going on...
        command = 'N0' + self._x10_to_lynx_id(id) + '\r'

        if old_level is None:
            # We're going from a fully OFF position.  If we're
            # going to something less that fully ON, we'll have
            # to turn it all the way on, then dim DOWN to the
            # desired level.  Sorry, that's just how (some?)
            # X10 dimmer modules work...
            # Or, we can just send some number of dim UP or DOWN
            # commands...
            if new_level < self.resolution - 1:
                command += 'D0%s%X\r' % (
                    self._x10_housecode_to_lynx(id[0]),
                    self.resolution - 1 - new_level
                )
        elif new_level > old_level:
            command += 'D1%s%X\r' % (
                self._x10_housecode_to_lynx(id[0]),
                new_level - old_level
            )
        else:
            command += 'D0%s%X\r' % (
                self._x10_housecode_to_lynx(id[0]),
                old_level - new_level
            )

        return command


    def set_channel(self, id, level, force=False):
        self.network.send(self._proto_set_channel(id, *self.channels[id].set_level(level), force=force))

    def set_channel_on(self, id, force=False):
        self.network.send(self._proto_set_channel(id, *self.channels[id].set_on(), force=force))

    def set_channel_off(self, id, force=False):
        self.network.send(self._proto_set_channel(id, *self.channels[id].set_off(), force=force))

    def kill_channel(self, id, force=False):
        self.network.send(self._proto_set_channel(id, *self.channels[id].kill(), force=force))

    def kill_all_channels(self, force=False):
        self.network.send("F4\r")
        for ch in self.channels:
            self.channels[ch].kill()

    def all_channels_off(self, force=False):
        for ch in self.channels:
            self.set_channel_off(ch, force)

    def initialize_device(self):
        "Reset device state to reasonable default settings."
        self.network.send("R\r")
        self.network.send("M00=02\r")
        self.kill_all_channels(True)
        self.all_channels_off(True)
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
