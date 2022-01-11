#
# LUMOS NETWORK LIST
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Network/Networks.py,v 1.4 2008-12-31 00:25:19 steve Exp $
#
# Lumos Light Orchestration System
# Copyright (c) 2005, 2006, 2007, 2008, 2016 by Steven L. Willoughby, Aloha,
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
from Lumos.Network.SerialNetwork      import SerialNetwork
from Lumos.Network.SerialBitNetwork   import SerialBitNetwork
from Lumos.Network.ParallelNetwork    import ParallelNetwork
from Lumos.Network.ParallelBitNetwork import ParallelBitNetwork
from Lumos.Network.TestNetwork        import TestNetwork

#
# List of supported network drivers, mapping the name as used
# in the show.conf file (and other interfaces) to the actual
# class implementing the driver for that network.
#
supported_network_types = {
    'serial':    SerialNetwork,
    'serialbit': SerialBitNetwork,
    'parallel':  ParallelNetwork,
    'parbit':    ParallelBitNetwork,
    'test':      TestNetwork
}

def network_factory(type, **kwargs):
    """
	Create and return a network object of the requested type.
	Usage: network_factory(typename, [args...])
	where: typename is one of the defined keywords for a network
	       type (as usable in the show configuration file), and
		   [args] are whatever constructor arguments are applicable
		   to that type of network class.
	"""

    type = type.lower().strip()
    if type not in supported_network_types:
        raise ValueError("Invalid network/protocol type '%s'" % type)

    return supported_network_types[type](**kwargs)
#
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
