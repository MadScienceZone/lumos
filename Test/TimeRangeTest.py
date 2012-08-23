# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
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
# vi:set nu ai sm ts=4 sw=4 expandtab:

import unittest #, os
from Lumos.TimeRange import TimeRange, InvalidTimeRange

class TimeRangeTest (unittest.TestCase):
    def test_identity(self):
        self.assertEquals(TimeRange('0').list, [0])
        self.assertEquals(TimeRange('15').list, [15])

    def test_range(self):
        self.assertRaises(InvalidTimeRange, TimeRange, '999')

    def test_list(self):
        self.assertEquals(TimeRange('0,1,5,6,9').list, [0,1,5,6,9])

    def test_range(self):
        self.assertEquals(TimeRange('5-9').list, [5,6,7,8,9])
        self.assertEquals(TimeRange('5-9,1-3').list, [5,6,7,8,9,1,2,3])

    def test_bad_range(self):
        self.assertRaises(InvalidTimeRange, TimeRange, '17-4')
        self.assertRaises(InvalidTimeRange, TimeRange, '-17')
        self.assertRaises(InvalidTimeRange, TimeRange, '3920')
        self.assertRaises(InvalidTimeRange, TimeRange, '-12-4')
        self.assertRaises(InvalidTimeRange, TimeRange, '12-4004')
        self.assertRaises(InvalidTimeRange, TimeRange, '*-4004')
        self.assertRaises(InvalidTimeRange, TimeRange, '*-*')
        self.assertRaises(InvalidTimeRange, TimeRange, '5-*')

    def test_star(self):
        self.assertEquals(TimeRange('*', 10).list, [0,1,2,3,4,5,6,7,8,9,10])

    def test_skip(self):
        self.assertEquals(TimeRange('0-30/5').list, [0, 5, 10, 15, 20, 25, 30])
        self.assertEquals(TimeRange('*/10').list, [0, 10, 20, 30, 40, 50])

#    def test_time_until(self):
#        self.assertEquals(TimeRange('15').time_until(20), 5)
#        self.assertEquals(TimeRange('15').time_until(10), 5)
