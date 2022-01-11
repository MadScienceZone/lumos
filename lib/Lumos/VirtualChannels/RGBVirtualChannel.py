# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS VIRTUAL CHANNEL CLASS :: RGB
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

class RGBVirtualChannel (VirtualChannel):
    """
    Device-independent abstraction of a multi-color Channel object.  This
    provides a conceptual model of a channel as seen by the sequence
    editor and compiler.  This is tied to an actual Channel object which
    describes some hardware, which is eventually called upon to perform
    actual real-world effects.

    RGB channels can be set to arbitrary colors.
    """

    def __init__(self, id, channel, name=None, color=None):
        VirtualChannel.__init__(self, id, None, name, color)
        if channel is not None and (not isinstance(channel, (list, tuple)) or len(channel) != 3):
            raise ValueError('RGB virtual channel requires three underlying hardware channel objects (red, green, blue)')
        self.channel = channel
        self.type = 'rgb'
        self.current_raw_value = [0,0,0]

    def all_hardware_channels(self):
        return self.channel

    def set_raw_value(self, value, subidx=0):
        if not 0 <= subidx <= 2:
            raise ValueError('subidx "{1}" for RGB virtual channel "{0}" out of range'.format(
                self.id, subidx))
        newvalue = self.current_raw_value[:]
        newvalue[subidx] = value
        self.current_raw_value = self.normalize_level_value(self.denormalize_level_value(newvalue))
        
    def denormalize_level_value(self, value):
        return "#{0[0]:02x}{0[1]:02x}{0[2]:02x}".format(
            [max(min(int((x/100.0)*255),255),0) for x in value])

    def normalize_level_value(self, value, permissive=False):
        """
        Levels for RGB devices are a string in the form #rrggbb,
        a floating-point level value, 'on', or 'off'.
        Internally, this is an (r,g,b) tuple.
        """

        return self._to_raw_color(value)

    def compile_level_change(self, base_timestamp, base_priority, new_raw_level, time_delta, force=False):
        """
        Compile a desired change into a set of hardware device controller
        method calls which we'll schedule to be invoked at the proper
        time in the future.  This updates the virtual channel's current
        idea of what level it's set to.  Returns an event list as
        documented for ValueEvent.compile().
        """

        affected_controllers = set()
        ev_list = []
        new_color_values = self.current_raw_value[:]

        for color_idx, color_name in enumerate(('red', 'green', 'blue')):
            hw_channel        = self.channel[color_idx]
            hw_starting_level = hw_channel.normalized_value(self.current_raw_value[color_idx])
            hw_ending_level   = hw_channel.normalized_value(new_raw_level[color_idx])

            if hw_starting_level != hw_ending_level or force:
                new_color_values[color_idx] = new_raw_level[color_idx]
                hw_channel_id = hw_channel.id
                hw_controller = hw_channel.controller
                affected_controllers.add(hw_controller)

                for event_time, next_level in self._base_level_change(base_timestamp, hw_starting_level, hw_ending_level, time_delta, force):
                    ev_list.append((event_time, hw_controller.set_channel, (hw_channel_id, next_level, force), base_priority))
                    if event_time != base_timestamp:
                        ev_list.append((event_time, hw_controller.flush, (), base_priority+1))

        if self.current_raw_value != new_color_values:
            self.current_raw_value = new_color_values[:]

        return (affected_controllers, ev_list)
