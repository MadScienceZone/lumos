# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS DEVICE DRIVER: X-10 BASE CLASS
#
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Device/X10ControllerUnit.py,v 1.5 2008-12-31 00:25:19 steve Exp $
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
from Lumos.ControllerUnit import ControllerUnit

class X10ControllerUnit (ControllerUnit):
    def __init__(self, id, power, network, resolution=16):
        ControllerUnit.__init__(self, id, power, network, resolution)
        self.type = 'X-10 Controller'

    def __str__(self):
        return self.type

    def channel_id_from_string(self, channel):
        return str(channel).upper().strip()

    def add_channel(self, id, name=None, load=None, dimmer=True, warm=None, resolution=None, power=None):
        try:
            id = self.channel_id_from_string(id)
            assert('A' <= id[0] <= 'P')
            assert(1 <= int(id[1:]) <= 16)
        except:
            raise ValueError, "X-10 channels must be 'A1'..'P16'"

        if resolution is not None:
            resolution = int(resolution)
        else:
            resolution = self.resolution

        ControllerUnit.add_channel(self, id, name, load, dimmer, warm, resolution, power)
#
# $Log: not supported by cvs2svn $
# Revision 1.4  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
