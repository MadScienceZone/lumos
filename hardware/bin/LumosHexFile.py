# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS Hex File Class
# For Lumos Hardware Project revision @@RELEASE@@
#
# Copyright (c) 2013 by Steven L. Willoughby, Aloha,
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
class LumosHexFile (object):
    def sequence_header(self, sequence_id):
        if not 0 <= sequence_id < 128:
            raise ValueError("sequence_id {0} out of range 0-127".format(sequence_id))
        self.current_address = 0
        return self._record(type=4, data=[00,sequence_id])

    def eof(self):
        return self._record(type=1)

    def data_record(self, data=[]):
        a = self.current_address
        self.current_address += len(data)
        return self._record(address=a, data=data)

    def _record(self, type=0, address=0, data=[]):
        if not 0 <= type <= 0xff:
            raise ValueError("type 0x{0:X} out of 8-bit range".format(type))
            
        if not 0 <= address <= 0xffff:
            raise ValueError("address 0x{0:X} out of 16-bit range".format(address))

        return ":{0:02X}{1:04X}{2:02X}{3}{4:02X}".format(
            len(data), address, type, ''.join("{0:02X}".format(d) for d in data),
            ((~(len(data) + ((address >> 8) & 0xff) + (address & 0xff) + type + sum(data))) + 1) & 0xff)
