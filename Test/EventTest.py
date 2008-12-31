# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/EventTest.py,v 1.2 2008-12-31 00:13:32 steve Exp $
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
# vi:set ai sm nu ts=4 sw=4 expandtab:
import unittest
from Lumos.Event import Event

class DummyControllerUnit (object):
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return self.id == other.id

class EventTest(unittest.TestCase):
    def testCons(self):
        e = Event(unit=DummyControllerUnit(44), channel=3, level=31, delta=100)
        self.assertEqual(e.channel, 3)
        self.assertEqual(e.level, 31)
        self.assertEqual(e.unit.id, 44)
        self.assertEqual(e.delta, 100)

    def test_on(self):
        e = Event(unit=DummyControllerUnit(44), channel=0, level=100)
        self.assertEqual(e.channel, 0)
        self.assertEqual(e.level, 100)
        self.assertEqual(e.delta, 0)

    def test_off(self):
        e = Event(unit=DummyControllerUnit(44), channel=0, level=0)
        self.assertEqual(e.channel, 0)
        self.assertEqual(e.level, 0)
        self.assertEqual(e.delta, 0)

    def test_equality(self):
        e = Event(DummyControllerUnit(12), 'AA', 10, 100)
        f = Event(DummyControllerUnit(12), 'AA', 10, 100)
        g = Event(DummyControllerUnit(12), 'AB', 10, 100)
        h = Event(DummyControllerUnit(11), 'AA', 10, 100)
        i = Event(DummyControllerUnit(12), 'AA', 16, 100)
        j = Event(DummyControllerUnit(12), 'AA', 10, 0)

        self.assertEqual(e,f)
        self.assertNotEqual(e,g)
        self.assertNotEqual(e,h)
        self.assertNotEqual(e,i)
        self.assertNotEqual(e,j)
# 
# $Log: not supported by cvs2svn $
#
