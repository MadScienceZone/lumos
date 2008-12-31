# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS EVENT CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Event.py,v 1.3 2008-12-31 00:25:19 steve Exp $
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
class Event:
    """An Event object describes a single event in the sequence
    being played out.  It essentially represents a specific point in time,
    at which a given channel is moved to a given output level, during a
    transition period of delta time."""

    def __init__(self, unit, channel, level=0, delta=0):
        self.unit    = unit
        self.channel = channel
        self.level   = level
        self.delta   = delta

    def __eq__(self, other):
        #if not isinstance(other, Event):
            #return False

        return self.unit == other.unit \
           and self.channel == other.channel \
           and self.level == other.level \
           and self.delta == other.delta

#   def __ne__(self, other):
#       return not self.__eq__(other)

    def __repr__(self):
        return "<Event %s.%s->%.2f%% (%dmS)>" % (
            '*' if self.unit is None else self.unit.id,
            '*' if self.channel is None else self.channel,
            self.level,
            self.delta
        )
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
