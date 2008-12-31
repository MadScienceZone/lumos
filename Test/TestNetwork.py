# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/TestNetwork.py,v 1.3 2008-12-31 00:13:32 steve Exp $
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
# vi:set ai sm nu ts=4 sw=4 expandtab:
from Lumos.Network import Network
from quopri        import encodestring
import sys

class TestNetwork (Network):
    """
    This is a network type for debugging purposes.  Instead of talking
    to an external device, it simply prints its commands to stdout.
    """
    def __init__(self, description='test network', **kwargs):
        self.units = {}
        self.description = description
        self.buffer = ''
        self.closed = False
        self.args = kwargs
        for key in 'port', 'baudrate', 'bits':
            if key in self.args:
                try:
                    self.args[key] = int(self.args[key])
                except:
                    pass

    def send(self, cmd):
        "Send a command string to the hardware device."
        if self.closed: raise ValueError, "Device already closed!"
        if cmd:
            self.buffer += encodestring(cmd)

    def close(self):
        """Close the network device; no further operations are
        possible for it."""
        if self.closed: raise ValueError, "Device already closed!"
        self.closed = True

    def reset(self):
        "Reset output buffer for easier testing (of isolated events)"
        self.buffer = ''

class TestParallelNetwork (TestNetwork):
    def send(self, bit):
        if   bit == 0: self.buffer += '0'
        elif bit == 1: self.buffer += '1'
        else:
            raise ValueError('Parallel Network given bogus value %s' % bit)

    def latch(self):
        self.buffer += 'X'
# 
# $Log: not supported by cvs2svn $
#
