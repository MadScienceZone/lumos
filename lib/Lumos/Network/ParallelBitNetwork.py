# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS NETWORK DRIVER: BIT-AT-A-TIME OVER PARALLEL PORT
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Network/ParallelBitNetwork.py,v 1.3 2008-12-31 00:25:19 steve Exp $
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
import parallel
from Lumos.Network import Network

class ParallelBitNetwork (Network):
    """
    This class describes each parallel-port network of controllers.  
	Unlike ParallelNetwork, though, the interface is designed for
	bit-at-a-time devices such as the Olsen 595, Grinch, etc.

	There are two event methods provided.  send() transmits a
	single bit on pin D0, strobed via the /STROBE pin.  When
	all the bits are sent, call the latch() method to assert
	the /AUTOFEED and /STROBE lines once.  This signals the
	device to latch the shifted bits out to the output channels.
    """
    
    def __init__(self, description=None, port=0, open_device=True):
        """
        Constructor for the ParallelBitNetwork class.

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

        # If the port can be a simple integer, make it so.
        try:
            self.port = int(self.port)
        except:
            pass

        self.dev = None
        if open_device:
            self.open()

    def open(self):
        self.dev = parallel.Parallel(port=self.port)
        self.dev.setDataDir(1)
        self.dev.setDataStrobe(0)

    def send(self, bit):
        if self.dev is not None:
            self.dev.setData(bit)
            self.dev.setDataStrobe(1)
            self.dev.setDataStrobe(0)

	def latch(self):
		raise NotImplementedError("LATCH")

    def close(self):
        if self.dev is not None:
            self.dev.setDataDir(0)
            self.dev.close()
        self.dev = None

    def __str__(self):
        if self.description is not None: return self.description
        return "ParallelBitNetwork (port %s)" % self.port
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
