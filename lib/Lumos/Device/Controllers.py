# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS CONTROLLER LIST
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Device/Controllers.py,v 1.5 2008-12-31 00:25:19 steve Exp $
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
#
from Lumos.Device.LynX10ControllerUnit import LynX10ControllerUnit
from Lumos.Device.LumosControllerUnit  import LumosControllerUnit
from Lumos.Device.FirecrackerX10ControllerUnit import FirecrackerX10ControllerUnit
from Lumos.Device.RenardControllerUnit import RenardControllerUnit
from Lumos.Device.Olsen595ControllerUnit import Olsen595ControllerUnit
from Lumos.Device.FireGodControllerUnit import FireGodControllerUnit
#
# List of supported controller device drivers, mapping the name as used
# in the show.conf file (and other interfaces) to the actual class
# implementing the driver for that device.
#
supported_controller_types = {
    'lynx10':   LynX10ControllerUnit,
    '48ssr':    LumosControllerUnit,
    'lumos':    LumosControllerUnit,
    'cm17a':    FirecrackerX10ControllerUnit,
    'renard':   RenardControllerUnit,
    'olsen595': Olsen595ControllerUnit,
    'firegod':  FireGodControllerUnit,
}

def controller_unit_factory(type, **kwargs):
    """
    Create and return a controller object of the requested type.
    Usage: controller_unit_factory(typename, [args...])
    where: typename is one of the defined keywords for a device
           type (as usable in the show configuration file), and
           [args] are whatever constructor arguments are applicable
           to that type of device class.
    """

    type = type.lower().strip()
    if type not in supported_controller_types:
        raise ValueError, "Invalid controller unit type '%s'" % type

    return supported_controller_types[type](**kwargs)
