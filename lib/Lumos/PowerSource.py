# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS POWER SOURCE CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/PowerSource.py,v 1.3 2008-12-30 22:58:02 steve Exp $
#
# Lumos Light Orchestration System
# Copyright © 2005, 2006, 2007, 2008 by Steven L. Willoughby, Aloha,
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

class PowerSource (object):
    """
    This class describes each power source from which we draw power to run the
    controller loads.  The main reason we define these is so we can keep track
    of the current load we're pulling at any given time.
    """
    
    def __init__(self, id, amps=0, gfci=False):
        """
        Constructor for the PowerSource class:
            PowerSource([amps], [gfci=False])
        
        amps: The current rating AVAILABLE TO US from this power source
        (i.e., if there is anything else on that circuit, subtract its
        load from the circuit capacity first, so this number reflects the
        total number of amps that we can pull at any given time.)

        gfci: Whether or not the circuit has GFCI protection.  The default
        is False (no GFCI protection).
        """
        self.id = id

        try:
            self.amps = float(amps)
        except:
            raise ValueError, "amps must be a numeric value"

        if isinstance(gfci, bool):
            self.gfci = gfci
        else:
            raise ValueError, "gfci value must be a boolean"
#
# $Log: not supported by cvs2svn $
#
