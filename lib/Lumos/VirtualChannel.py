# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS VIRTUAL CHANNEL CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/VirtualChannel.py,v 1.4 2008-12-31 00:25:19 steve Exp $
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

class VirtualChannel (object):
    """
    Device-independent abstraction of a Channel object.  This
    provides a conceptual model of a channel as seen by the sequence
    editor and compiler.  This is tied to an actual Channel object which
    describes some hardware, which is eventually called upon to perform
    actual real-world effects.

    At this abstract level, however, all channels are things that can be
    turned on/off or dimmed over a range of values from 0-100 (percentages).
    """

    def __init__(self, id, channel, name=None, color=None):
        self.channel = channel
        self.is_dimmable = True
        if isinstance(channel, (list, tuple)):
            if len(channel) != 1:
                raise ValueError('virtual channel {0} only takes a single hardware channel object'.format(id))
            self.channel = channel[0]

        self.name = name or (channel.name if channel is not None else id)
        self.color = '#ffffff' if color is None else color
        self.raw_color = self._to_raw_color(self.color)
        self.id = id
        self.type = None

    def set_raw_value(self, value, subidx=0):
        if subidx != 0:
            raise ValueError('Virtual channel "{0}" ("{1}") does not have a sub-channel "{2}".'.format(
                self.id, self.name, subidx))

        # this will throw an exception if value is out of bounds for this type of virtual channel
        self.current_raw_value = self.normalize_level_value(self.denormalize_level_value(value))

    def normalize_level_value(self, value, permissive=False):
        raise NotImplementedError("VirtualChanel is an abstract base class.  Derived sub-classes must implement their own normalize_level_value() method.")

    def denormalize_level_value(self, value):
        raise NotImplementedError("VirtualChanel is an abstract base class.  Derived sub-classes must implement their own denormalize_level_value() method.")

    def compile_level_change(self, base_timestamp, base_priority, new_raw_level, time_delta, force=False):
        raise NotImplementedError("VirtualChanel is an abstract base class.  Derived sub-classes must implement their own compile_level_change() method.")

    def display_level_change(self, new_raw_level):
        """
        For GUI tools which work with channel level changes, change the virtual
        channel's current value as it's being tracked here.  Emits a pair of
        color values representing the display color before and after the change.
        """

        old_value = self.current_raw_value
        self.current_raw_value = new_raw_level

        return (
            self._to_rgb_color(self.denormalize_level_value(old_value), base_color=self.color), 
            self._to_rgb_color(self.denormalize_level_value(self.current_raw_value), base_color=self.color)
        )
        
    def all_hardware_channels(self):
        "Returns a list of all hardware channels associated with this virtual channel."
        return [self.channel]
        
    #
    # Internal-use (private) methods
    #
    def _base_level_change(self, base_timestamp, starting_raw_level, new_raw_level, time_delta, force=False):
        """
        Given a starting level and desired new level, this 
        generates a set of level-change increments over a given 
        number of milliseconds.

        Returns a list of tuples (<timestamp>, <raw level value>)
        REMEMBER THAT IF YOU INJECT MORE EVENT TIMES DUE TO
        TRANSITIONS, YOU MUST INSERT MORE FLUSH EVENTS TOO
        """
        
        if time_delta == 0:
            if starting_raw_level != new_raw_level or force:
                return [(base_timestamp, new_raw_level)]
            else:
                return []
        else:
            fade_steps = abs(starting_raw_level - new_raw_level)
            fade_incr = 1 if starting_raw_level < new_raw_level else -1

            if fade_steps == 1:
                return [(base_timestamp, new_raw_level)]
            elif fade_steps > 1:
                return [(
                    (base_timestamp + (time_delta * i) / (fade_steps - 1)),
                    starting_raw_level + (fade_incr * (i + 1))
                ) for i in range(fade_steps)]
            elif force:
                return [(base_timestamp, new_raw_level)]

        return []

    def _to_raw_color(self, color_code):
        """
        Resolve standard color representations which may be
        used by different virtual channels and GUI elements.

        Accepts a single integer or float value (or string
        containing such) as a percentage of white intensity 
        from 0 to 100; or the strings "on" and "off"; or
        a string of the form "#rrggbb".  Also accepts the
        None value as a synonym for 0.

        Returns a tuple of (red,green,blue) values each
        in the floating-point range 0-100.
        """

        if color_code is None:
            return (0,0,0)

        try:
            #v = int((float(color_code) / 100.0) * 255)
            v = float(color_code)
            if v < 0:   v = 0
            if v > 100: v = 100
            return (v,v,v)
        except ValueError:
            if not isinstance(color_code, str):
                raise ValueError("Color code {0} not understood".format(color_code))

        v = color_code.lower().strip()
        if v == 'on':   return (100,100,100)
        if v == 'off':  return (0,0,0)
        if v.startswith('#') and len(v)==7:
            try:
                return (int(v[1:3], 16)/2.55, int(v[3:5], 16)/2.55, int(v[5:7], 16)/2.55)
            except ValueError:
                raise ValueError("Color value {0} not understood (invalid hex bytes)".format(color_code))
        raise ValueError("Color value {0} not understood (bad string format)".format(color_code))

    def _to_rgb_color(self, color_code, base_color=None):
        """
        Resolve standard color representations which may be
        used by different virtual channels and GUI elements.

        Accepts a single integer or float value (or string
        containing such) as a percentage of white intensity 
        from 0 to 100; or the strings "on" and "off"; or
        a string of the form "#rrggbb".  Also accepts the
        None value as a synonym for 0.

        Returns a string of the form "#rrggbb".
        """

        if color_code is None:
            return '#000000'

        if base_color is not None:
            base_rgb = self._to_raw_color(base_color)
        else:
            base_rgb = self._to_raw_color("#ffffff")

        try:
            #v = int((float(color_code) / 100.0) * 255)
            v = float(color_code)
            if v < 0:   v = 0
            if v > 100: v = 100
            return '#{0:02x}{1:02x}{2:02x}'.format(
                int(base_rgb[0] * v *  0.0255) & 0xff, 
                int(base_rgb[1] * v * 0.0255) & 0xff, 
                int(base_rgb[2] * v * 0.0255) & 0xff)
        except ValueError:
            if not isinstance(color_code, str):
                raise ValueError("Color code {0} not understood".format(color_code))

        v = color_code.lower().strip()
        if v == 'on':   return '#{0[0]:02x}{0[1]:02x}{0[2]:02x}'.format([int(i*2.55)&0xff for i in base_rgb])
        if v == 'off':  return '#000000'
        if v.startswith('#') and len(v)==7:
            try:
                rgb = (int(v[1:3], 16)/2.55, int(v[3:5], 16)/2.55, int(v[5:7], 16)/2.55)
                return v
            except ValueError:
                raise ValueError("Color value {0} not understood (invalid hex bytes)".format(color_code))
        raise ValueError("Color value {0} not understood (bad string format)".format(color_code))
