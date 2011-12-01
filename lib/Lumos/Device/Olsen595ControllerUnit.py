# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS DEVICE DRIVER: OLSEN 595 DIY SSR CONTROLLER
# ***UNTESTED*** SPECULATIVE CODE.  NOT READY FOR USE!
#
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Device/Olsen595ControllerUnit.py,v 1.5 2008-12-31 00:25:19 steve Exp $
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
# The Olsen 595 is a classic DIY SSR controller.  This driver is 
# an experimental design based on the protocol description posted
# on computerchristmas.com.  The author does not have the hardware
# available to verify that this works.  Hopefully someone with a '595
# can verify this and give feedback about it to the author.
#
# This driver should also drive a Grinch board.
#
# This is a parallel protocol (well, actually it's "serial" but we
# use the PC's parallel port, manipulating three of the output pins
# to implement a synchronous serial bitstream).  These bits are 
# ultimately shifted out to the output SSR channels.
#
# For each bit you wish to send, set up the bit in D0 and set the
# /STROBE line high to clock it out.  Repeat until all bits have 
# been sent to the hardware.
# 
# When they've all been transmitted, clock the /AUTO_FEED line high 
# to have the controller latch all those bits out to the output lines 
# driving the SSRs.
# 
# This does not use Channel objects since all we're doing is changing
# them from on to off.  This may change in the future, though.
#

class Olsen595ControllerUnit (ControllerUnit):
    """
    ControllerUnit subclass for the classic "Olsen 595" and
    "Grinch" DIY SSR controllers.  

    ***THE STATUS OF THIS DRIVER IS EXPERIMENTAL***
    THIS HAS NOT YET BEEN VERIFIED TO WORK WITH ACTUAL HARDWARE

    If you have an Olsen 595 and/or a Grinch controller, we would
    appreciate any feedback you'd like to offer about this driver,
    if you're willing to try it and help us test/debug this code.
    """

    def __init__(self, id, power, network, channels=64):
        """
        Constructor for an Olsen 595/Grinch controller object:
            Olsen595ControllerUnit(power, network, [channels])

        Specify the correct PowerSource object for this unit,
        the network this board (or chained set of boards) talks
        through.  Also specify the number of channels implemented
        on this (set of) controller(s).  The default is 64.  Lumos
        will transmit that many bits on each update.
        """

        ControllerUnit.__init__(self, id, power, network)
        self.type = 'Olsen595 Controller'
        self.channels = [0] * channels
        self.needs_update = False

    def __str__(self):
        return "%s (%d channels)" % (self.type, len(self.channels))

    def channel_id_from_string(self, channel):
        return int(channel)

    def add_channel(self, id, name=None, load=None):
        try:
            id = int(id)
            assert 0 <= id < len(self.channels)
        except:
            raise ValueError("This Olsen595's channel IDs must be integers from 0-%d" % self.max_bits)

    def set_channel(self, id, level, force=False):
        if level == 0:
            self.set_channel_off(id, force)
        else:
            self.set_channel_on(id, force)

    def set_channel_on(self, id, force=False):
        self.channels[int(id)] = 1
        self.needs_update = True

    def set_channel_off(self, id, force=False):
        self.channels[int(id)] = 0
        self.needs_update = True

    def kill_channel(self, id, force=False):
        self.set_channel_off(id, force)

    def kill_all_channels(self, force=False):
        self.channels = [0] * len(self.channels)
        self.needs_update = True

    def all_channels_off(self, force=False):
        self.kill_all_channels(force)

    def initialize_device(self):
        self.all_channels_off(True)
        self.flush(True)

    def flush(self, force=False):
        if self.needs_update or force:
            for bit in self.channels:
                self.network.send(bit)
            self.network.latch()
            self.needs_update = False

    def iter_channels(self):
        return range(len(self.channels))

#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
