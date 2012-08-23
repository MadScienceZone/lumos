# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS NETWORK DRIVER: BIT-AT-A-TIME OVER SERIAL PORT
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Network/SerialBitNetwork.py,v 1.3 2008-12-31 00:25:19 steve Exp $
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
try:
    import serial
except ImportError:
    class SerialBitNetwork (NullNetwork):
        def __init__(self, description=None, port=0, open_device=True):
            NullNetwork.__init__(self, description, nulltype='SerialBit')
            self.port=port

else:
    class SerialBitNetwork (Network):
        """
        This class describes each serial network of controllers.  
        As opposed to the SerialNetwork class, this is for bit-
        at-a-time interfaces such as the X-10 CM17A "Firecracker"
        interface. 

        With an open port, sending bytes is accomplished by toggling
        the states of the serial port control lines XXX and XXX.
        """
        
        def __init__(self, description=None, port=0, open_device=True):
            """
            Constructor for the SerialBitNetwork class.

            description: A short description of what this network is 
                         responsible for.

            port:        The system designation for the serial device 
                         connecting the host computer to the network.  
                         Can be system-specific like "COM1" or 
                         "/dev/ttyS1", or can be a simple integer--0 
                         should be the "first" serial port on your 
                         system, 1 the next, etc.  [0]

            open_device: Boolean: whether to actually open the serial 
                         device upon construction.  If you don't let it
                         open here, you'll need to call the open()
                         method later.  [True]
            """
            
            Network.__init__(self, description)
            
            self.port = port

            # If the port can be a simple integer, make it so.
            try:
                self.port = int(self.port)
            except:
                pass

            self.dev = None
            if open_device:
                self.open()

        def open(self):
            self.dev = serial.Serial(port=self.port)

        def send(self, cmd):
            raise NotImplementedError("SEND")

        def close(self):
            if self.dev is not None:
                self.dev.close()
            self.dev = None

        def __str__(self):
            if self.description is not None: return self.description
            return "SerialBitNetwork (port %s)" % self.port
