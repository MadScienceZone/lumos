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

class DeviceTimeoutError (Exception):
    def __init__(self, read_so_far, *args, **kw):
        Exception.__init__(self, *args, **kw)
        self.read_so_far = read_so_far

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
            self.verbose = None
            self._protocol_debug = None

        def set_baud_rate(self, new_speed):
            self.baudrate = self._int(new_speed)
else:
    class SerialNetwork (Network):
        """
        This class describes each serial network of controllers.  
        Typically this will be a serial port on the host computer, 
        and attached to that serial port will be one or more 
        controller devices.  Commands are sent as a sequence of
        bytes sent at a particular baud rate and flow control.
        """
        
        def __init__(self, description=None, port=0, baudrate=9600, bits=8, parity='none', stop=1, xonxoff=False, rtscts=False, duplex='full', txmode='dtr', txlevel=1, txdelay=2, open_device=True):
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
            self.duplex = duplex
            self.txmode = txmode
            self.txlevel = self._bool(txlevel)
            self.txdelay = self._int(txdelay)
            self.verbose = None
            self.diversion = None
            self._protocol_debug = None

            if txmode not in ('dtr', 'rts'):
                raise ValueError('{0} is not a valid transmit mode line name'.format(txmode))

            if txdelay < 0:
                raise ValueError("Negative values for txdelay don't make sense unless you have a time machine.")

            if self.parity not in ('none', 'even', 'odd'):
                raise ValueError("'{0}' is not a valid parity type".format(parity))
            # conform to PySerial values
            self._parity = self.parity.upper()[0]

            if self._parity not in serial.Serial.PARITIES:
                raise ValueError("IMPLEMENTATION BUG: parity %s (%s) does not match serial parity label" % (parity, self._parity))

            if self.bits not in serial.Serial.BYTESIZES:
                raise ValueError("%d is not a valid number of bits per byte" % self.bits)

            if self.stop not in serial.Serial.STOPBITS:
                raise ValueError("%d is not a valid number of stop bits" % self.stop)

            if self.baudrate not in serial.Serial.BAUDRATES:
                raise ValueError("{0} is not a valid baud rate (must be one of {1})".format(self.baudrate, serial.Serial.BAUDRATES))

            # If the port can be a simple integer, make it so.
            try:
                self.port = int(self.port)
            except:
                pass

            self.dev = None
            if open_device:
                self.open()

        def set_verbose(self, device):
            self.verbose = device

        def divert_output(self):
            """Start diverting output.  Anything sent will be collected instead of being
            transmitting anything.  Harmless to call if output is already diverted."""
            if self.diversion is None:
                self.diversion = []

        def end_divert_output(self):
            "End diversion.  Returns the bytes collected as a single string value."
            if self.diversion is not None:
                data = ''.join(self.diversion)
                self.diversion = None
                return data

        def open(self):
            print `self.port`, `self.baudrate`, `self.bits`, `self._parity`, `self.stop`, `self.xonxoff`, `self.rtscts`
            self.dev = serial.Serial(
                port=self.port, 
                baudrate=self.baudrate, 
                bytesize=self.bits, 
                parity=self._parity, 
                stopbits=self.stop, 
                xonxoff=self.xonxoff, 
                rtscts=self.rtscts)

            if self.verbose:
                self.verbose.write(time.ctime()+" Opened serial port {0} for {8} ({1} baud, {2} bits, {3}, {4} stop, xonxoff {5}, rtscts {6}) -> {7}\n".format(
                    self.port, self.baudrate, self.bits, self._parity, self.stop, self.xonxoff, self.rtscts, self.dev, self.description))

        def diagnostic_output(self, message):
            if self.verbose:
                self.verbose.write(time.ctime()+" "+message+"\n")
                
        def set_baud_rate(self, new_speed):
            "Change the baud rate of an operating device."
            if self.dev:
                self.dev.flushInput()
                self.dev.flushOutput()
                self.dev.baudrate = new_speed
                self.dev.flushOutput()
                self.dev.flushInput()

        def hexdump(self, data, addr=0, outdev=None):
            if outdev is None:
                outdev = self.verbose

            if outdev:
                # --------------------------------------------------------------------------------
                # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|
                # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|
                # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|

                for idx in range(0, len(data), 16):
                    outdev.write('{0:04X}:'.format(addr+idx))
                    for byte in range(16):
                        if idx+byte < len(data):
                            outdev.write(' {0:02X}'.format(ord(data[idx+byte])))
                        else:
                            outdev.write('   ')
                        if byte == 7:
                            outdev.write('   ')
                    outdev.write('   |')
                    for byte in range(16):
                        if idx+byte < len(data):
                            outdev.write(data[idx+byte] if ' ' <= data[idx+byte] <= '~' else '.')
                        else:
                            outdev.write(' ')

                        if byte == 7:
                            outdev.write(' ')
                    outdev.write('|\n')

        def send(self, cmd):
            if self.dev is None:
                return None
                
            if self.verbose:
                self.verbose.write(time.ctime()+" Sending to {0} (port {1}):\n".format(self.description, self.port))
                self.hexdump(cmd)
                if self._protocol_debug is not None:
                    self._protocol_debug(cmd, self.verbose)

            if self.diversion is not None:
                self.diversion.append(cmd)
            else:
                return self.dev.write(cmd)

        def close(self):
            if self.dev is not None:
                self.dev.close()
            self.dev = None

            if self.verbose:
                self.verbose.write(time.ctime()+" Closed port {1} for {0}.\n".format(self.description, self.port))

        def input_waiting(self):
            "Report if input was received and is waiting to be read.  Returns number of bytes waiting."

            if self.verbose:
                self.verbose.write(time.ctime()+" {0}: check input_waiting() -> {1}\n".format(self.description, 0 if self.dev is None else self.dev.inWaiting()))

            if self.dev is None:
                return 0

            return self.dev.inWaiting()

        def receive_mode(self):
            """Low-level function to switch to receive mode.  Waits for the output
            buffer to drain, then delays, switches mode, delays, and returns."""

            if self.dev is None:
                raise DeviceNotReadyError('There is no serial device active.')

            if self.verbose:
                ow = self.dev.outWaiting()
                self.verbose.write(time.ctime()+" {0}: switching to receive mode ({1} byte{2} waiting to drain from output queue)\n".format(
                    self.description, ow, '' if ow==1 else 's'))

            for max_wait in xrange(1000):
                if self.dev.outWaiting() == 0:
                    break
                time.sleep(0.01)
            else:
                ow = self.dev.outWaiting()
                raise IOError('{0} byte{1} stuck in output buffer!  Can\'t change to receive mode yet.'.format(ow, '' if ow==1 else 's'))

            self._change_mode(0 if self.txlevel else 1)

        def transmit_mode(self):
            """Low-level function to switch to transmit mode.  Abandons any unread
            input.  This also delays before and after the mode switch."""

            if self.dev is None:
                raise DeviceNotReadyError('There is no serial device active.')

            if self.verbose:
                self.verbose.write(time.ctime()+" {0}: switching to transmit mode (discarding pending input)\n".format(self.description))

            self.dev.flushInput()
            self._change_mode(1 if self.txlevel else 0)

        def _change_mode(self, newlevel):
            if self.dev is None:
                raise DeviceNotReadyError('There is no serial device active.')

            if self.verbose:
                self.verbose.write(time.ctime()+" {0}: changing TX mode to {1}\n".format(self.description, 'ON' if newlevel else 'OFF'))

            if self.txdelay > 0:
                if self.verbose:
                    self.verbose.write(time.ctime()+" {0}: delaying {1} milliseconds before switching...\n".format(self.description, self.txdelay))

                time.sleep(self.txdelay / 1000.0)

            if self.txmode == 'dtr':
                self.dev.setDTR(newlevel)
                if self.verbose:
                    self.verbose.write(time.ctime()+" {0}: DTR->{1}\n".format(self.description, newlevel))
            elif self.txmode == 'rts':
                self.dev.setRTS(newlevel)
                if self.verbose:
                    self.verbose.write(time.ctime()+" {0}: RTS->{1}\n".format(self.description, newlevel))
            else:
                raise ValueError('{0} is not a valid serial control line'.format(self.txmode))

            if self.txdelay > 0:
                if self.verbose:
                    self.verbose.write(time.ctime()+" {0}: delaying {1} milliseconds after switching...\n".format(self.description, self.txdelay))

                time.sleep(self.txdelay / 1000.0)

        def input(self, remaining_f=None, bytes=None, mode_switch=True, timeout=1):
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

            If a timeout value is given, we will allow that many seconds
            (which may be a real number) before abandoning the input.  Note
            that if some data arrive during that time, we may keep reading.
            If the input timed out, a DeviceTimeoutError exception is thrown.
            This exception object has a read_so_far attribute containing
            the data read before the timeout occurred.

            N.B.:  In a half-duplex network, we assume that we can only get
            data we ask for, and nobody is speaking out of turn, so any extra
            data that may be in the serial buffer is discarded after our
            packet is dealt with (iff switching modes back to transmit mode
            when we're done).  If not switching modes (as with a full-duplex
            network), no data are discarded and will still be there for a 
            subsequent call to input().
            
            This will block the main program's execution until the input 
            is complete or the operation times out."""

            if self.dev is None:
                raise DeviceNotReadyError("There is no active serial device to read from.")

            if self.verbose:
                self.verbose.write(time.ctime()+" {0}: getting input (bytes={1}, mode_switch={2}, timeout={3}):\n".format(self.description, bytes, `mode_switch`, timeout))

            #self.dev.setTimeout(timeout)
            self.dev.timeout=timeout
            if mode_switch and self.txmode == 'half':
                self.receive_mode()

            buffer = ''

            if remaining_f:
                if not bytes:
                    bytes = remaining_f(None)
                    if self.verbose:
                        self.verbose.write(time.ctime()+" Trying initial read of {0} (computed)\n".format(bytes))
            elif bytes:
                if self.verbose:
                    self.verbose.write(time.ctime()+" Trying initial read of {0} (specified)\n".format(bytes))
                buffer = self.dev.read(bytes)
                if not buffer:
                    raise DeviceTimeoutError(buffer, 'Timeout ({0} sec) waiting for device to respond.'.format(timeout))
                bytes = 0
                if self.verbose:
                    self.verbose.write(time.ctime()+" Read {0} byte{1}.\n".format(len(buffer), '' if len(buffer)==1 else 's'))
            else:
                raise APIUsageError("You must specify either bytes or remaining_f (or both) to input()")

            while bytes > 0:
                if self.verbose:
                    self.verbose.write(time.ctime()+" Reading {0} byte{1}...\n".format(bytes, '' if bytes == 1 else 's'))

                r = self.dev.read(bytes)
                if not r:
                    if self.verbose:
                        self.verbose.write(time.ctime()+" ERROR: short read of {0} (expected {1}):\n".format(len(buffer), bytes))
                        self.hexdump(buffer)

                    raise DeviceTimeoutError(buffer, 'Timeout ({0} sec) waiting for device to respond after receiving only {1} byte{2}.'.format(
                        timeout, len(buffer), '' if len(buffer) == 1 else 's'))
                buffer += r
                bytes = remaining_f(buffer)
                if self.verbose:
                    self.verbose.write(time.ctime()+" Read {0}, looking for {1} more...\n".format(len(buffer), bytes))

            if self.verbose:
                self.verbose.write(time.ctime()+" Input data received:\n")
                self.hexdump(buffer)
                if self._protocol_debug is not None:
                    self._protocol_debug(buffer, self.verbose)

            if mode_switch and self.txmode == 'half':
                self.transmit_mode()

            return buffer

        def __str__(self):
            if self.description is not None: return self.description
            return "SerialNetwork (port %s)" % self.port
