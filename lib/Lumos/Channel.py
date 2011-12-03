# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS CHANNEL CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Channel.py,v 1.4 2008-12-31 00:25:19 steve Exp $
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

class DimmerError (Exception):
    "Exception thrown for improper usage of dimmer settings."
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return str(self.value)

class Channel (object):
    """
    Class for power output channels.

    This just describes some behavior and attributes common to all kinds
    of channels.
    """

    def __init__(self, id, name=None, load=None, dimmer=True, warm=None, resolution=100, power=None):
        """
        Constructor for Channel objects:

        Channel(id, [name], load, [dimmer], [warm], [resolution], power)

        id:           unique (within a given controller) ID 
                      for this channel.
        name:         descriptive name for channel (optional).
        load:         amperage of load assigned to this channel.
        dimmer:       (bool) is channel capable of dimming?
        warm:         minimum dimmer level to maintain for this 
                      channel, as an integer percentage of full 
                      brightness.  If you set this to None, no 
                      minimum is set, and turning the channel off 
                      will turn it completely off.  Alternatively, 
                      if you set it to 0, then turning the channel 
                      off will dim it to 0%, which is an important 
                      distinction on some devices (e.g., X10).
                      [default=None]
        resolution:   number of discrete dimmer steps supported.  
                      [default=100]
        power:        PowerSource object supplying power to this channel
        """

        if name is None:
            self.name = 'Channel %s' % id
        else:
            self.name = name
        if load is None:
            raise ValueError("Channel %s load parameter is required" % id)
        if power is None:
            raise ValueError("Channel %s power parameter is required" % id)


        self.load = float(load)
        self.dimmer = bool(dimmer)
        self.resolution = int(resolution)
        self.level = None
        self.power_source = power
        if warm is not None:
            self.warm = self.raw_dimmer_value(warm)
            if not 0 <= self.warm < self.resolution:
                self.warm = None
                raise ValueError, "Channel %s warm percentage out of range (%d)" % (id, warm)

            if not self.dimmer:
                self.warm = None
                raise DimmerError, "Channel %s specifies warm value but is not dimmable." % id
        else:
            self.warm = None

    def raw_dimmer_value(self, n):
        '''Translate brightness percentage to device-specific "raw"
        dimmer level value.

        Note that this is for determining *dimmer* values; if you 
        give it a value of None (which normally indicates the "off"
        state), this function returns 0 (zero).'''

        if n is None: return 0
        return int(((self.resolution-1)/100.0) * n)

    def pct_dimmer_value(self, n):
        '''Translate device-specific "raw" dimmer value to percentage.
        
        The None value (i.e., "off") is returned as 0% as well.'''

        if n is None: return 0
        return int((100.0/(self.resolution-1)) * n)

    def normalized_value(self, n, override_warm=False):
        '''Normalize percentage brightness level to percentage 
        which matches dimmer resolution steps.  Takes into account 
        the "warm" attribute unless told to override that.
        
        An input value of None is considered to be a dimmer level 
        of 0 for this function.'''

        n = self.raw_dimmer_value(n)
        if self.warm is not None and not override_warm and n < self.warm: 
            n = self.warm
        return self.pct_dimmer_value(n)

    def set_level(self, level, override_warm=False):
        '''
        Set channel to a raw (device-specific) dimmer level.
        
        For convenience, you can set the level to None, which
        will turn the device off completely.  This is different
        than dimming it to 0%.  (More importantly different with
        some controllers than others.)

        Returns a tuple of raw (device-specific) level values for the
        channel.  The first is the original value before the change,
        and the second is the new value being set.  Either value could
        be None to indicate a completely "off" condition.
        '''
        previous = self.level
        #
        # if we are not capable of dimming, we make any level
        # less than 50% "off" and anything greater "on".
        #
        if not self.dimmer:
            self.level = None if level < self.resolution / 2.0 else self.resolution-1
            return (previous, self.level)
        #
        # otherwise, figure out proper dimmer handling.
        #
        if level is None:
            if override_warm or self.warm is None:
                self.level = None
                return (previous, None)
            else:
                level = 0

        level = int(level)
        if not override_warm and self.warm is not None:
            if level < self.warm: 
                level = self.warm
        elif level < 0:         
            level = 0

        if level >= self.resolution: 
            level = self.resolution-1

        self.level = level
        return (previous, self.level)

    def set_on(self):
        '''Turn channel fully on (full brightness).  
        Returns same values as setLevel()'''
        return self.set_level(self.resolution-1)

    def set_off(self):
        'Turn channel fully off.  Returns same values as setLevel()'
        return self.set_level(self.warm)

    def kill(self):
        '''Turn channel COMPLETELY off, disregarding "warm" setting.  
        Returns same values as setLevel()'''
        return self.set_level(None, override_warm=True)

    def current_drain(self):
        "Report current load in amps based on output level right now -> (amps, PowerSource)"
        if self.level is None:
            return (0, self.power_source)

        return ((float(self.level) / (self.resolution-1)) * self.load, self.power_source)

    def current_load(self):
        "Report the load assigned to this channel as a tuple (amps, PowerSource)"
        return (self.load, self.power_source)
#
# $Log: not supported by cvs2svn $
# Revision 1.3  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
