# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS NETWORK BASE CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Network/__init__.py,v 1.3 2008-12-31 00:25:19 steve Exp $
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
class Network (object):
    """
    This class describes each network of controllers.  Each network
    driver class derived from this base class describes a type of
    communications interface and protocol for communicating with a
    set of controllers.

    This is a virtual base class from which all actual network drivers
    are derived.
    """
    
    def __init__(self, description=None):
        """
        Constructor for the Network class
        description: A short description of what this network is 
                     responsible for.

        Derived classes will have additional keyword arguments
        appropriate for the specific kind of hardware they will
        communicate with.
        """
        self.description = description
        self.units = {}

    def add_unit(self, id, unit):
        "Add a new controller unit to the network."
        self.units[id] = unit

    def send(self, cmd):
        "Send a command string to the hardware device."
        raise NotImplementedError, "You MUST redefine this method in each Network class."

    def close(self):
        """Close the network device; no further operations are
        possible for it."""
        raise NotImplementedError, "You MUST redefine this method in each Network class."
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
