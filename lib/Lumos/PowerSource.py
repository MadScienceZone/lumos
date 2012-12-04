# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS POWER SOURCE CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/PowerSource.py,v 1.4 2008-12-31 00:25:19 steve Exp $
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

class IncompatibleGFIC (Exception): pass
class PowerSourceStackError (Exception): pass

class PowerSource (object):
    """
    This class describes each power source from which we draw power to run the
    controller loads.  The main reason we define these is so we can keep track
    of the current load we're pulling at any given time.
    """
    
    def __init__(self, id, amps=0, volts=120):
        """
        Constructor for the PowerSource class:
            PowerSource([amps], [volts])
        
        amps: The current rating AVAILABLE TO US from this power source
        (i.e., if there is anything else on that circuit, subtract its
        load from the circuit capacity first, so this number reflects the
        total number of amps that we can pull at any given time.)

        volts: The number of volts supplied here.  The amount of power
        will be adjusted based on this voltage.
        """
        self.id = id
        self.subordinates = []
        self.parent_source = None

        try:
            self.amps = float(amps)
        except:
            raise ValueError, "amps must be a numeric value"

        try:
            self.volts = float(volts)
        except:
            raise ValueError, "volts must be a numeric value"

    def add_subordinate_source(self, child_obj):
        "Add a child PowerSource to this one."

        if child_obj.parent_source is not None:
            raise PowerSourceStackError("Power source %s already has %s as a parent; can't add %s" % (
                child_obj.id, child_obj.parent_source.id, self.id
            ))

        self.subordinates.append(child_obj)
        child_obj.parent_source = self

    def orphan(self, child_obj):
        "Remove a child source."
        if self.subordinates and child_obj in self.subordinates:
            self.subordinates.remove(child_obj)
            if len(self.subordinates) == 0:
                self.subordinates = None


#
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
