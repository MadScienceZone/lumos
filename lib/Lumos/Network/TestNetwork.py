#
# LUMOS NETWORK DRIVER: TEST NETWORK
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Network/SerialNetwork.py,v 1.5 2008-12-31 00:25:19 steve Exp $
#
# Lumos Light Orchestration System
# Copyright (c) 2016 by Steven L. Willoughby, Aloha, Oregon, USA.
# All Rights Reserved.  Licensed under the Open Software License version
# 3.0.  
# Based on earlier code
# copyright (c) 2005, 2006, 2007, 2008 by Steven L. Willoughby, Aloha,
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
from Lumos.Network import Network, DeviceTimeoutError
import time, os

class DeviceNotReadyError (Exception): pass
class IOError (Exception): pass
class APIUsageError (Exception): pass


class TestNetwork (Network):
    """
    This class describes a special "test" network of controllers.  
    This is not mapped to any actual hardware; rather it simply
    records to a file the output sent, for debugging purposes.
    """
        
    def __init__(self, description=None, output=None, input=None, open_device=True):
            """
            Constructor for the SerialNetwork class.

            description: A short description of what this network is 
                         responsible for.

            output:      A file while will be written to with all the
                         output data sent to this network.

            input:       A file containing binary input stimulus data
                         which will be read as input bytes are expected.

            open_device: Whether or not to actually open the device I/O
                         files [True]
            """
            
            Network.__init__(self, description)
            self.description = description
            self.output_name=output
            self.input_name=input
            self.output_file = None
            self.input_file =None
            self._protocol_debug = None
            
            if open_device:
                self.open()

    def open(self):
            self.output_file = open(self.output_name, "ab")
            self.input_file = open(self.input_name, "rb")

            self.output_file.write("\n\n"+(79 * "=")+"\n")
            self.output_file.write("[{0}] Opened TestNetwork port {1}\n".format(time.ctime(), self.description))
            self.output_file.flush()

    def hexdump(self, data, addr=0, outdev=None):
            if isinstance(data, str):
                data = data.encode()

            if outdev:
                # --------------------------------------------------------------------------------
                # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|
                # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|
                # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|

                for idx in range(0, len(data), 16):
                    outdev.write('{0:04X}:'.format(addr+idx))
                    for byte in range(16):
                        if idx+byte < len(data):
                            outdev.write(' {0:02X}'.format(data[idx+byte]))
                        else:
                            outdev.write('   ')
                        if byte == 7:
                            outdev.write('   ')
                    outdev.write('   |')
                    for byte in range(16):
                        if idx+byte < len(data):
                            outdev.write(chr(data[idx+byte]) if 32 <= data[idx+byte] <= 126 else '.')
                        else:
                            outdev.write(' ')

                        if byte == 7:
                            outdev.write(' ')
                    outdev.write('|\n')
                self.output_file.flush()

    def send(self, cmd: bytes):
            if self.output_file:
                self.output_file.write('[{0}] Transmitted data\n'.format(time.ctime()))
                self.hexdump(cmd, outdev=self.output_file)
                self.output_file.flush()
                if self._protocol_debug is not None:
                    self._protocol_debug(cmd, self.output_file)

    def close(self):
            if self.output_file:
                self.output_file.write('[{0}] Closed file\n'.format(time.ctime()))
                self.output_file.close()
            if self.input_file:
                self.input_file.close()
            self.input_file = self.output_file = None

    def input_waiting(self):
            "Report if input was received and is waiting to be read.  Returns number of bytes waiting."
            return self.input_file.tell() != os.stat(self.input_name).st_size

    def input(self, remaining_f=None, nbytes=None, mode_switch=True, timeout=1):
            if self.input_file is None:
                raise DeviceNotReadyError("There is no active input file to read from.")

            buffer = b''

            if remaining_f:
                if not nbytes:
                    nbytes = remaining_f(None)
            elif nbytes:
                buffer = self.input_file.read(nbytes)
                if not buffer:
                    raise DeviceTimeoutError(buffer, 'Timeout ({0} sec) waiting for device to respond.'.format(timeout))
                nbytes = 0
            else:
                raise APIUsageError("You must specify either bytes or remaining_f (or both) to input()")

            while nbytes > 0:
                r = self.input_file.read(nbytes)
                if not r:
                    raise DeviceTimeoutError(buffer, 'Timeout ({0} sec) waiting for device to respond after receiving only {1} byte{2}.'.format(
                        timeout, len(buffer), '' if len(buffer) == 1 else 's'))
                buffer += r
                nbytes = remaining_f(buffer)

            if self._protocol_debug is not None:
                self.output_file.write('[{0}] Received data\n'.format(time.ctime()))
                self.hexdump(buffer, outdev=self.output_file)
                self._protocol_debug(buffer, self.output_file)

            return buffer

    def __str__(self):
            if self.description is not None: return self.description
            return "TestNetwork (input {0}, output {1})".format(self.input_name, self.output_name)
