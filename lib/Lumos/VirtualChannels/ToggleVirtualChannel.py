# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS VIRTUAL CHANNEL CLASS :: TOGGLE
#
# Lumos Light Orchestration System
# Copyright (c) 2005, 2006, 2007, 2008, 2014 by Steven L. Willoughby, Aloha,
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

from Lumos.VirtualChannel import VirtualChannel

class ToggleVirtualChannel (VirtualChannel):
    """
    Device-independent abstraction of a toggle Channel object.  This
    provides a conceptual model of a channel as seen by the sequence
    editor and compiler.  This is tied to an actual Channel object which
    describes some hardware, which is eventually called upon to perform
    actual real-world effects.

    Toggles can be turned on or off.
    """

    def __init__(self, id, channel, name=None, color=None):
        VirtualChannel.__init__(self, id, channel, name, color)
        self.type = 'toggle'
        self.current_raw_value = 0
        self.is_dimmable = False

    def denormalize_level_value(self, value):
        return 'on' if value else 'off'
            
    def normalize_level_value(self, value, permissive=False):
        """
        Levels for toggles can be 'on' or 'off'.  To normalize that, 
        we will accept numeric values as well, with 0=off, !0=on.
        Internally we use integers 0 and 1.
        """
        if value is None:
            return 0
        #
        # Try a vew things to clean up v (not fatal if any of them don't work)
        #
        try:
            v = value.lower().strip()
        except AttributeError:
            pass

        try:
            v = int(value)
        except ValueError:
            try:
                v = int(float(value))
            except ValueError:
                pass

        if v == 'on': return 1
        if v == 'off': return 0

        if not permissive or not isinstance(v, int):
            raise ValueError('{1}: toggle channels must be set to "on" or "off", not "{0}"'.format(value, id))

        return 1 if v else 0

    def compile_level_change(self, base_timestamp, base_priority, new_raw_level, time_delta, force=False):
        """
        Compile a desired change into a set of hardware device controller
        method calls which we'll schedule to be invoked at the proper
        time in the future.  This updates the virtual channel's current
        idea of what level it's set to.  Returns an event list as
        documented for ValueEvent.compile().
        """
        if self.current_raw_value != new_raw_level or force:
            self.current_raw_value = new_raw_level
            return (self.channel.controller,), [(base_timestamp, 
                self.channel.controller.set_channel_on if new_raw_level else self.channel.controller.set_channel_off, 
                (self.channel.id, force), 
                base_priority)]
        return ((), ())  
