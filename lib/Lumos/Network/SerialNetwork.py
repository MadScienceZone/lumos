# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS NETWORK DRIVER: SERIAL PORT
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Network/SerialNetwork.py,v 1.5 2008-12-31 00:25:19 steve Exp $
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
import serial
from Lumos.Network import Network

class SerialNetwork (Network):
    """
    This class describes each serial network of controllers.  
    Typically this will be a serial port on the host computer, 
    and attached to that serial port will be one or more 
    controller devices.  Commands are sent as a sequence of
    bytes sent at a particular baud rate and flow control.
    """
    
    def __init__(self, description=None, port=0, baudrate=9600, bits=8, parity='none', stop=1, xonxoff=False, rtscts=False, open_device=True):
        """
        Constructor for the SerialNetwork class.

        description: A short description of what this network is 
                     responsible for.

        port:        The system designation for the serial device 
                     connecting the host computer to the network.  
                     Can be system-specific like "COM1" or 
                     "/dev/ttyS1", or can be a simple integer--0 
                     should be the "first" serial port on your 
                     system, 1 the next, etc.  [0]

        baudrate:    The integer number of bits/sec this network 
                     needs to run at.  [9600]

        bits:        7 or 8; the number of data bits per byte 
                     transmitted.  [8]

        parity:      One of: 'none', 'even', 'odd'.  ['none']

        stop:        1 or 2; the number of stop bits.  [1]

        xonxoff:     Boolean; whether to use XON/XOFF flow control.
                     [False]

        rtscts:      Boolean; whether to use RTS/CTS flow control.
                     [False]

        open_device: Boolean: whether to actually open the serial 
                     device upon construction.  If you don't let it
                     open here, you'll need to call the open()
                     method later.  [True]
        """
        
        Network.__init__(self, description)
        
        self.port = port
        self.baudrate = int(baudrate)
        self.bits = int(bits)
        self.parity = parity
        self.stop = int(stop)
        self.xonxoff = bool(xonxoff)
        self.rtscts = bool(rtscts)

        if self.parity not in ('none', 'even', 'odd'):
            raise ValueError, "'%s' is not a valid parity type" % parity
        # conform to PySerial values
        self._parity = self.parity.upper()[0]

        if self._parity not in serial.Serial.PARITIES:
            raise ValueError, "IMPLEMENTATION BUG: parity %s (%s) does not match to serial parity label" % (parity, self._parity)

        if self.bits not in serial.Serial.BYTESIZES:
            raise ValueError, "%d is not a valid number of bits per byte" % self.bits

        if self.stop not in serial.Serial.STOPBITS:
            raise ValueError, "%d is not a valid number of stop bits" % self.stop

        if self.baudrate not in serial.Serial.BAUDRATES:
            raise ValueError, "%d is not a valid baud rate" % self.baudrate

        # If the port can be a simple integer, make it so.
        try:
            self.port = int(self.port)
        except:
            pass

        self.dev = None
        if open_device:
            self.open()

    def open(self):
        self.dev = serial.Serial(
            port=self.port, 
            baudrate=self.baudrate, 
            bytesize=self.bits, 
            parity=self._parity, 
            stopbits=self.stop, 
            xonxoff=self.xonxoff, 
            rtscts=self.rtscts)

    def send(self, cmd):
        if self.dev is None:
            return None
        return self.dev.write(cmd)

    def close(self):
        if self.dev is not None:
            self.dev.close()
        self.dev = None

    def __str__(self):
        if self.description is not None: return self.description
        return "SerialNetwork (port %s)" % self.port
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
