#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/EventTest.py,v 1.2 2008-12-31 00:13:32 steve Exp $
#
# Lumos Light Orchestration System
# Copyright (c) 2014 by Steven L. Willoughby, Aloha,
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
import unittest
from Lumos.ValueEvent import ValueEvent

class DummyVirtualChannel (object):
    def __init__(self, id):
        self.id = id
        self.is_dimmable = True

    def normalize_level_value(self, i, permissive=False):
        return int(i)

    def __eq__(self, other):
        return self.id == other.id

class ValueEventTest(unittest.TestCase):
    def testCons(self):
        e = ValueEvent(DummyVirtualChannel(44), level='31', delta=100)
        self.assertEqual(e.vchannel.id, 44)
        self.assertEqual(e.level, 31)
        self.assertEqual(e.delta, 100)
        self.assertEqual(e.raw_level, 31)

    def test_on(self):
        e = ValueEvent(DummyVirtualChannel(44), level='100')
        self.assertEqual(e.vchannel.id, 44)
        self.assertEqual(e.level, 100)
        self.assertEqual(e.raw_level, 100)
        self.assertEqual(e.delta, 0)

    def test_off(self):
        e = ValueEvent(DummyVirtualChannel(44), level=0)
        self.assertEqual(e.level, 0)
        self.assertEqual(e.raw_level, 0)
        self.assertEqual(e.delta, 0)

    def test_equality(self):
        eo= DummyVirtualChannel(12)
        e = ValueEvent(eo, 10, 100)
        f = ValueEvent(DummyVirtualChannel(12), 10, 100)
        g = ValueEvent(DummyVirtualChannel(13), 10, 100)
        h = ValueEvent(DummyVirtualChannel('13'), 10, 100)
        i = ValueEvent(DummyVirtualChannel(14), 16, 100)
        j = ValueEvent(DummyVirtualChannel(12), 10, 0)
        k = ValueEvent(eo, 10, 100)

        self.assertEqual(e,k)
        self.assertNotEqual(e,f)
        self.assertNotEqual(e,g)
        self.assertNotEqual(e,h)
        self.assertNotEqual(g,h)
        self.assertNotEqual(e,i)
        self.assertNotEqual(e,j)
