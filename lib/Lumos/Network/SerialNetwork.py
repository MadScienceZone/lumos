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
from Lumos.Network import Network, NullNetwork
import time
class DeviceNotReadyError (Exception): pass
class IOError (Exception): pass
class APIUsageError (Exception): pass

try:
    import serial
except ImportError:
    class SerialNetwork (NullNetwork):
        def __init__(self, description=None, port=0, baudrate=9600, bits=8, parity='none', stop=1, xonxoff=False, rtscts=False, duplex='full', txmode='dtr', txlevel=1, txdelay=2, open_device=True):
            NullNetwork.__init__(self, description, nulltype="Serial")
            self.port=port
            self.baudrate=self._int(baudrate)
            self.bits=self._int(bits)
            self.parity=self._str(parity)
            self.stop=self._int(stop)
            self.xonxoff=self._bool(xonxoff)
            self.rtscts=self._bool(rtscts)
            self.duplex=duplex
            self.txmode=txmode
            self.txlevel=self._bool(txlevel)
            self.txdelay=self._int(txdelay)
else:
    class SerialNetwork (Network):
        """
        This class describes each serial network of controllers.  
        Typically this will be a serial port on the host computer, 
        and attached to that serial port will be one or more 
        controller devices.  Commands are sent as a sequence of
        bytes sent at a particular baud rate and flow control.
        """
        
        def __init__(self, description=None, port=0, baudrate=9600, bits=8, parity='none', stop=1, xonxoff=False, rtscts=False, duplex='full', txmode='rts', txlevel=1, txdelay=2, open_device=True):
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

            duplex:      One of: 'full', 'half'.  Determines whether the
                         (usually RS-485) serial interface is full- or 
                         half-duplex.  If half-duplex, we will assert* a
                         control line (DTR or RTS) to put the interface
                         in transmit mode, and deassert* that line when
                         we need to turn off the transmitter and wait for
                         another device to send data (*but see txlevel
                         parameter). ['full']

            txmode:      One of: 'dtr', 'rts'.  Specifies which control
                         line controls the RS-485 transmit mode.  ['dtr']

            txlevel:     Boolean; if True, the DTR or RTS line is asserted
                         (logic 1) to activate the transmitter.  Otherwise,
                         the line is deasserted (logic 0) to activate it.
                         [True]

            txdelay:     Integer; number of milliseconds to delay before and
                         after switching txmode on or off.  Note that we will
                         wait until the output buffer drains before starting
                         the mode change cycle in any event.  [2]

            open_device: Boolean: whether to actually open the serial 
                         device upon construction.  If you don't let it
                         open here, you'll need to call the open()
                         method later.  [True]
            """
            
            Network.__init__(self, description)
            
            self.port = port
            self.baudrate = self._int(baudrate)
            self.bits = self._int(bits)
            self.parity = self._str(parity)
            self.stop = self._int(stop)
            self.xonxoff = self._bool(xonxoff)
            self.rtscts = self._bool(rtscts)
            self.txmode = txmode
            self.txlevel = self._bool(txlevel)
            self.txdelay = self._int(txdelay)

            if txmode not in ('dtr', 'rts'):
                raise ValueError('{0} is not a valid transmit mode line name'.format(txmode))

            if txdelay < 0:
                raise ValueError("Negative values for txdelay don't make sense")

            if self.parity not in ('none', 'even', 'odd'):
                raise ValueError, "'%s' is not a valid parity type" % parity
            # conform to PySerial values
            self._parity = self.parity.upper()[0]

            if self._parity not in serial.Serial.PARITIES:
                raise ValueError, "IMPLEMENTATION BUG: parity %s (%s) does not match serial parity label" % (parity, self._parity)

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

        def input_waiting(self):
            "Report if input was received and is waiting to be read.  Returns number of bytes waiting."
            if self.dev is None:
                return 0

            return self.dev.inWaiting()

        def receive_mode(self):
            """Low-level function to switch to receive mode.  Waits for the output
            buffer to drain, then delays, switches mode, delays, and returns."""

            if self.dev is None:
                raise DeviceNotReadyError('There is no serial device active.')

            for max_wait in xrange(1000):
                if self.dev.outWaiting():
                    break
                time.sleep(0.001)
            else:
                raise IOError('{0} bytes stuck in output buffer!  Can\'t change to receive mode yet.'.format(self.dev.outWaiting()))

            self._change_mode(0 if self.txlevel else 1)

        def transmit_mode(self)
            """Low-level function to switch to transmit mode.  Abandons any unread
            input.  This also delays before and after the mode switch."""

            if self.dev is None:
                raise DeviceNotReadyError('There is no serial device active.')

            self.dev.flushInput()
            self._change_mode(1 if self.txlevel else 0)

        def _change_mode(self, newlevel):
            if self.dev is None:
                raise DeviceNotReadyError('There is no serial device active.')

            if self.txdelay > 0:
                time.sleep(self.txdelay / 1000.0)

            if self.txmode == 'dtr':
                self.dev.setDTR(newlevel)
            elif self.txmode == 'rts':
                self.dev.setRTS(newlevel)
            else:
                raise ValueError('{0} is not a valid serial control line'.format(self.txmode))

            if self.txdelay > 0:
                time.sleep(self.txdelay / 1000.0)

        def input(self, remaining_f=None, bytes=None, mode_switch=True):
            """Input data from the serial interface.

            If in half-duplex mode, first switch to receive mode (unless
            the mode_switch parameter is False), then read and return
            an input packet received from the serial port.  Before returning,
            switch back to transmit mode if we switched out of it.

            If the bytes parameter is specified, read that much data
            and stop.

            If the remaining_f parameter is given, it should be a function
            reference which will provide guidance to know how much data needs
            to be read before a full packet is accepted.  If <bytes> is also
            specified, that many bytes is read unconditionally first.  Then
            remaining_f() is called with a single parameter holding the input
            buffer read so far.  It returns the number of additional bytes
            we need to receive before getting a complete packet.  There is no
            guarantee that we will actually read that many before calling
            remaining_f() to check again.  When remaining_f() returns zero,
            the input operation stops.

            N.B.:  In a half-duplex network, we assume that we can only get
            data we ask for, and nobody is speaking out of turn, so any extra
            data that may be in the serial buffer is discarded after our
            packet is dealt with (iff switching modes back to transmit mode
            when we're done).  If not switching modes (as with a full-duplex
            network), no data are discarded and will still be there for a 
            subsequent call to input().
            
            This will block the main program's execution until the input 
            is complete."""

            if self.dev is None:
                raise DeviceNotReadyError("There is no active serial device to read from.")

            if mode_switch and self.txmode == 'half':
                self.receive_mode()

            buffer = ''

            if remaining_f:
                if not bytes:
                    bytes = remaining_f(None)
            elif bytes:
                buffer = self.dev.read(bytes)
                bytes = 0
            else:
                raise APIUsageError("You must specify either bytes or remaining_f (or both) to input")

            while bytes > 0:
                buffer += self.dev.read(bytes)
                bytes = remaining_f(buffer)

            if mode_switch and self.txmode == 'half':
                self.transmit_mode()

            return buffer

        def __str__(self):
            if self.description is not None: return self.description
            return "SerialNetwork (port %s)" % self.port
