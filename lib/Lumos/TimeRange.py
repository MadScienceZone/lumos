# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS TIME RANGE HANDLER CLASS
#
# Lumos Light Orchestration System
# Copyright (c) 2011 by Steven L. Willoughby, Aloha,
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

import re

class InvalidTimeRange (Exception):
    "An error was encountered in dealing with the time expression"

class TimeRange (object):
    def __init__(self, expression, last=59, first=0):
        "Create a time range from the user-supplied expression"
        self.list = []
        for v in expression.split(','):
#            m = re.match(r'(?P<range>\*|(?P<start>\d+)-(?P<end>\d+))(/(?P<skip>\d+))?', v)
            try:
                m = re.match(r'\s*(?P<range>\*|(?P<start>\d+)-(?P<end>\d+))(/(?P<skip>\d+))?\s*$', v)
                if m:
                    skip = 1 if m.group('skip') is None else int(m.group('skip'))
                    if m.group('range') == '*':
                        self.list.extend(range(first, last+1, skip))
                    else:
                        start = int(m.group('start'))
                        end = int(m.group('end'))

                        if not first <= start <= end <= last or not 0 <= skip <= last:
                            raise InvalidTimeRange("Start time can't be after end time in {0}.".format(v))
                        self.list.extend(range(start, end+1, skip))
                else:
                    if not first <= int(v) <= last:
                        raise InvalidTimeRange("Value {0} out of range {1}-{2}".format(v, first, last))
                    self.list.append(int(v))
            except InvalidTimeRange:
                raise
            except Exception as e:
                raise InvalidTimeRange("Unable to understand time expression {0}: {1}".format(v, e))





#            m = re.match(r'(\*|\d+)(-(\d+))?(/(\d+))?'
#            v = int(v)
#            if not first <= v <= last:
#                raise InvalidTimeRange("Value {0} out of range {1}-{2}.".format(
#                    v, first, last))
#            self.list.append(v)
