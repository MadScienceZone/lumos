# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS VALUE EVENT CLASS
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
class ValueEvent:
    """A ValueEvent object describes a single event in the sequence
    being played out.  It essentially represents a specific point in time,
    at which a given channel is moved to a given output level, during a
    transition period of delta time."""

    def __init__(self, vchannel, level=None, delta=0):
        """
        ev = ValueEvent(<vchannel>, [<level>], [<delta>])

        Creates an event that changes the value of a particular virtual
        channel.  The <level> is any value that has meaning to the device
        associated with <vchannel>  The default <level> is None, which
        usually means to turn the device fully off.  If <delta> is specified,
        the level change effect transitions from the channel's current value
        over a period of <delta> milliseconds.

        If <vchannel> is None, this event is NOT associated with a channel,
        but will be applied to ALL known channels.  In this case, the
        attribute ev.level will remain in the high-level form given here as
        <level>, and will wait to be interpreted by every channel when the
        event is actually compiled.  This value therefore must be something that
        every virtual channel can understand.  (ev.raw_level will be None)

        Otherwise, <level> is immediately interpreted by <vchannel> and converted
        to a normalized value appropriate to <vchannel>.  This normalized value will
        be stored in ev.raw_level.
        """
        self.vchannel = vchannel
        self.change_level(level, delta)

    def copy(self):
        "Return a new copy of this ValueEvent object."

        return  ValueEvent(self.vchannel, self.level, self.delta)

    def change_level(self, level, delta, permissive=False):
        self.level    = level
        self.delta    = delta

        # normalize the value a bit
        if isinstance(level, str):
            try:
                self.level = int(level)
            except ValueError:
                try:
                    self.level = float(level)
                except ValueError:
                    self.level = level.strip().lower()
        else:
            self.level = level

        if self.vchannel is None:
            self.raw_level = None
        else:
            self.raw_level= self.vchannel.normalize_level_value(level, permissive)
            if not self.vchannel.is_dimmable:
                self.delta = 0

    def change_channel(self, new_vchannel, permissive=False):
        self.vchannel = new_vchannel
        self.change_level(self.level, self.delta, permissive)

    def compile(self, base_timestamp, base_priority=1, force=False, for_vchannel=None):
        """
        event.compile(base_timestamp, [base_priority], [force], [for_channel])

        Compile the results of this value-change event into a discrete
        sequence of hardware changes to be made.

        base_timestamp: time of the beginning of this event
        base_priority:  base priority for this event's actions
        force:          true if we should output level change events
                        even if we think the device is already at
                        the desired level
        for_vchannel:   a virtual channel for which to compile the event
                        [defaults to the one associated with this event.]
                        NOTE: this should only be used for global events
                        (where this event's vchannel is None), since the
                        event level will be normalized for <for_vchannel>
                        at compile-time.

        Returns a pair of values: (affected_controllers, events).
        
        <affected_controllers> is a list of ControllerUnit objects
        which are involved in this event's activities.  You may
        need to (eventually) call the flush() method on those
        controllers.

        <events> is a list of low-level scheduled events.  Each
        element of this list is a tuple:
            (timestamp, bound_method, arg_list, priority)
        where:
            <timestamp>     is the milliseconds at which the method
                            is to be invoked,
            <bound_method>  is a bound method to be called to effect
                            the change in hardware state,
            <arg_list>      is a sequence of arguments to be passed
                            to <bound_method>, and
            <priority>      is the scheduling priority for this call.
        """
        if for_vchannel is None:
            if self.vchannel is None:
                raise ValueError("ValueEvent missing virtual channel to act upon.")
            return self.vchannel.compile_level_change(base_timestamp, base_priority, 
                self.raw_level, self.delta, force=force)

        return for_vchannel.compile_level_change(base_timestamp, base_priority, 
            for_vchannel.normalize_level_value(self.level), self.delta, force=force)

    def __eq__(self, other):
        return (
            (other.vchannel is None if self.vchannel is None else self.vchannel is other.vchannel)
               and self.raw_level == other.raw_level 
               and self.level == other.level 
               and self.delta == other.delta
        )

    def __repr__(self):
        return "<ValueEvent %s(%s)->%s(%s) (%dmS)>" % (
            '*' if self.vchannel is None else self.vchannel.id,
            '*' if self.vchannel is None else id(self.vchannel),
            `self.level`, `self.raw_level`,
            self.delta
        )
