# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS VIRTUAL CHANNEL CLASS :: DIMMER
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

class DimmerVirtualChannel (VirtualChannel):
    """
    Device-independent abstraction of a dimmer Channel object.  This
    provides a conceptual model of a channel as seen by the sequence
    editor and compiler.  This is tied to an actual Channel object which
    describes some hardware, which is eventually called upon to perform
    actual real-world effects.

    Dimmers can be set to arbitrary intensity levels.
    """

    def __init__(self, id, channel, name=None, color=None):
        VirtualChannel.__init__(self, id, channel, name, color)
        self.type = 'dimmer'
        self.current_raw_value = 0

    def denormalize_level_value(self, value):
        v = float(value)
        if v.is_integer():
            return int(v)

        if not 0 < v < 100:
            raise ValueError("Dimmer values of {0} are out of range (0-100%)".format(v))

        return v

    def normalize_level_value(self, value, permissive=False):
        """
        Levels for dimmers can be a floating-point value from 0 to 100,
        or "on" or "off".
        """
        if value is None:
            return 0.0

        try:
            v = float(value)
        except ValueError:
            try:
                v = value.lower().strip()
                if v == 'on':  
                    v = 100.0
                elif v == 'off': 
                    v = 0.0
                else:
                    raise ValueError("Value {0} not understood for dimmer channel".format(value))
            except AttributeError:
                raise ValueError("Value {0} not understood for dimmer channel".format(value))

        if not 0.0 <= v <= 100.0:
            raise ValueError("Value {0} ({1}%) out of range for dimmer channel".format(value, v))
                
        return v

    def compile_level_change(self, base_timestamp, base_priority, new_raw_level, time_delta, force=False):
        """
        Compile a desired change into a set of hardware device controller
        method calls which we'll schedule to be invoked at the proper
        time in the future.  This updates the virtual channel's current
        idea of what level it's set to.  Returns an event list as
        documented for ValueEvent.compile().
        """

    # _base_level_change(t, start, end, dt, force) -> [(t0, v), ...]

        hw_channel        = self.channel
        hw_starting_level = hw_channel.normalized_value(self.current_raw_value)
        hw_ending_level   = hw_channel.normalized_value(new_raw_level)

        if hw_starting_level != hw_ending_level or force:
            self.current_raw_value = new_raw_level
            hw_channel_id = hw_channel.id
            hw_controller = hw_channel.controller
            ev_list = []

            for event_time, next_level in self._base_level_change(base_timestamp, hw_starting_level, hw_ending_level, time_delta, force):
                ev_list.append((event_time, hw_controller.set_channel, (hw_channel_id, next_level, force), base_priority))
                if event_time != base_timestamp:
                    ev_list.append((event_time, hw_controller.flush, (), base_priority+1))

            return ((hw_controller,), ev_list)
        return ((), ())
