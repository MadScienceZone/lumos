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
