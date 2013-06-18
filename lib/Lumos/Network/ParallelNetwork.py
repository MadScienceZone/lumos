# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS NETWORK DRIVER: PARALLEL PORT
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Network/ParallelNetwork.py,v 1.3 2008-12-31 00:25:19 steve Exp $
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
    import parallel
except ImportError:
    class ParallelNetwork (NullNetwork):
        def __init__(self, description=None, port=0, open_device=True):
            NullNetwork.__init__(self, description, nulltype="Parallel")
            self.port=port

else:
    class ParallelNetwork (Network):
        """
        This class describes each parallel-port network of controllers.  
        Typically this will be a parallel port on the host computer, 
        and attached to that parallel port will be one or more 
        controller devices.  Commands are sent as a sequence of
        bytes using the standard control bits (STROBE, etc).
        """
        
        def __init__(self, description=None, port=0, open_device=True):
            """
            Constructor for the ParallelNetwork class.

            description: A short description of what this network is 
                         responsible for.

            port:        The system designation for the parallel device 
                         connecting the host computer to the network.  
                         Can be system-specific like "LPT1" or 
                         "/dev/lp0", or can be a simple integer--0 
                         should be the "first" parallel port on your 
                         system, 1 the next, etc.  [0]

            open_device: Boolean: whether to actually open the parallel 
                         device upon construction.  If you don't let it
                         open here, you'll need to call the open()
                         method later.  [True]
            """
            
            Network.__init__(self, description)
            
            self.port = port
            self.diversion = None

            # If the port can be a simple integer, make it so.
            try:
                self.port = int(self.port)
            except:
                pass

            self.dev = None
            if open_device:
                self.open()

        def divert_output(self):
            if self.diversion is None:
                self.diversion = []

        def end_divert_output(self):
            if self.diversion is not None:
                data = ''.join(self.diversion)
                self.diversion = None
                return data
            else:
                return ''

        def open(self):
            self.dev = parallel.Parallel(port=self.port)
            self.dev.setDataDir(1)
            self.dev.setDataStrobe(0)

        def send(self, cmd):
            if self.diversion is not None:
                self.diversion.append(cmd)
            elif self.dev is not None:
                self.dev.setData(cmd)
                self.dev.setDataStrobe(1)
                self.dev.setDataStrobe(0)

        def close(self):
            if self.dev is not None:
                self.dev.setDataDir(0)
                self.dev.close()
            self.dev = None

        def __str__(self):
            if self.description is not None: return self.description
            return "ParallelNetwork (port %s)" % self.port
