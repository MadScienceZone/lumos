# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS VIRTUAL CHANNEL CLASS FACTORY
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

from Lumos.VirtualChannels.ToggleVirtualChannel import ToggleVirtualChannel
from Lumos.VirtualChannels.DimmerVirtualChannel import DimmerVirtualChannel
from Lumos.VirtualChannels.RGBVirtualChannel    import RGBVirtualChannel

supported_virtual_channel_types = {
    'toggle':   ToggleVirtualChannel,
    'dimmer':   DimmerVirtualChannel,
    'rgb':      RGBVirtualChannel,
}

def virtual_channel_factory(type='dimmer', **kwargs):
    type = type.lower().strip()

    if type not in supported_virtual_channel_types:
        raise ValueError('{0} is not a supported virtual channel type'.format(type))

    return supported_virtual_channel_types[type](**kwargs)
