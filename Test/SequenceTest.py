# vi:set ai sm nu ts=4 sw=4 expandtab:
import unittest
from Lumos.Event    import Event
from Lumos.Sequence import Sequence, InvalidFileFormat, InvalidTimestamp, InvalidUnitDefinition
from Lumos.Sequence import InvalidEvent

class DummyController(object):
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return self.id == other.id

class SqeuenceTest(unittest.TestCase):
    def setUp(self):
        self.controllers = {
            'floods': DummyController('floods'),
            'tree':   DummyController('tree')
        }

    def build_seq(self):
        s = Sequence()
        s.load_file('data/test.lseq', self.controllers)
        return s

    def test_load(self):
        s = self.build_seq()
        self.assertEqual(s.total_time, 11000)

    def test_save(self):
        self.build_seq().save_file('data/test-out.lseq')
        orig = file('data/test-cmp.lseq', 'rb').read()
        newf = file('data/test-out.lseq', 'rb').read()
        self.assertEqual(orig, newf)

    def test_version(self):
        s = Sequence()
        self.assertRaises(InvalidFileFormat, s.load_file, 'data/testv1.lseq', {})
        self.assertRaises(InvalidFileFormat, s.load_file, 'data/testv3.lseq', {})
        self.assertRaises(InvalidFileFormat, s.load_file, 'data/testvq.lseq', {})
        self.assertRaises(InvalidFileFormat, s.load_file, 'data/testnov.lseq', {})

    def test_timestamps(self):
        s = Sequence()
        self.assertRaises(InvalidTimestamp, s.load_file, 'data/notime.lseq', {})
        self.assertRaises(InvalidTimestamp, s.load_file, 'data/badtime.lseq', {})
        self.assertRaises(InvalidTimestamp, s.load_file, 'data/badtime2.lseq', {})

    def test_unitmap(self):
        s = self.build_seq()
        self.assertEqual(len(s._controllers), 2)
        self.assertEqual(s._controllers[0]['obj'].id, 'floods')
        self.assertEqual(s._controllers[1]['obj'].id, 'tree')

    def test_badunit(self):
        s = Sequence()
        self.assertRaises(InvalidUnitDefinition, s.load_file, 'data/badunit.lseq', {})
        self.assertRaises(InvalidUnitDefinition, s.load_file, 'data/badunit2.lseq', {})
        self.assertRaises(InvalidUnitDefinition, s.load_file, 'data/badunit3.lseq', {})

    def test_badevents(self):
        s = Sequence()
        self.assertRaises(InvalidEvent, s.load_file, 'data/badev.lseq', {'flood': DummyController('flood')})

    def test_events(self):
        expected_events = {
            0:     [
                Event(None,None,0,0)
            ],
            1000:  [
                Event(self.controllers['floods'],'C7',100,2000), 
                Event(self.controllers['tree'],'0',100,0)
            ],
            2000:  [
                Event(self.controllers['tree'],'0',0,0), 
                Event(self.controllers['tree'],'1',100,0)
            ],
            3000:  [
                Event(self.controllers['tree'],'1',0,0), 
                Event(self.controllers['tree'],'2',100,0)
            ],
            4000:  [
                Event(self.controllers['tree'],'2',0,0), 
                Event(self.controllers['tree'],'3',100,0)
            ],
            5000:  [
                Event(self.controllers['tree'],'0',100,1000), 
            ],
            6000:  [
                Event(self.controllers['tree'],'1',100,1000), 
            ],
            7000:  [
                Event(self.controllers['tree'],'2',100,1000), 
                Event(self.controllers['floods'],'C7',50,0), 
            ],
            8000:  [
                Event(self.controllers['tree'],'3',100,1000), 
            ],
            10000:  [
                Event(None,None,0,1000)
            ],
        }
        s = self.build_seq()
        self.assertEquals(len(s.intervals), 10)
        self.assertEquals([i for i in s.intervals], [0,1000,2000,3000,4000,5000,6000,7000,8000,10000])
        for time in s.intervals:
            e_list = s.events_at(time)
            self.assertEqual(e_list, expected_events[time])


#    def testCons(self):
#        s = Sequence()
#        self.assertEqual(s.event_list(), [])
#
#    def testSeq1(self):
#        s = Sequence()
#        s.add_event(Event(time=0, unit=0, channel=0, level=0))
#        self.assertEqual(s.event_list(), [(0,0,0,0)])
#
#    def testSeq2(self):
#        s = Sequence()
#        s.add_event(Event(time=100, unit=2, channel=12, level=32))
#        s.add_event(Event(time=200, unit=2, channel=12, level=64))
#        s.add_event(Event(time=200, unit=3, channel=14, level=12))
#        self.assertEqual(s.event_list(), [
#            (100, 2, 12, 32),
#            (200, 2, 12, 64),
#            (200, 3, 14, 12)
#        ])
#
#    def testSeq3(self):
#        s = Sequence()
#        s.add_event(Event(time=200, unit=4, channel=12, level=64))
#        s.add_event(Event(time=100, unit=5, channel=12, level=32))
#        s.add_event(Event(time=200, unit=0, channel=14, level=12))
#        self.assertEqual(s.event_list(), [
#            (100, 5, 12, 32),
#            (200, 4, 12, 64),
#            (200, 0, 14, 12)
#        ])
#
##    def testLoaderConstructor(self):
##        s = Sequence("test-1.csv")
##        self.checkLoadedFile(s)
##
##    def testLoaderMethod(self):
##        s = Sequence()
##        s.load("test-1.csv")
##        self.checkLoadedFile(s)
##
##    def testPlayList(self):
##        s = Sequence("test-2.csv")
##        self.assertEqual(s.eventList(), [
##            (    0L, 0, 0,   0),
##            (    0L, 0, 1,   0),
##            (    0L, 0, 2,   0),
##            (    0L, 0, 3,   0),
##            ( 5000L, 0, 0, 127),
##            ( 5000L, 0, 1,  64),
##            ( 5833L, 0, 1,  65),
##            ( 6666L, 0, 1,  66),
##            ( 7499L, 0, 1,  67),
##            ( 8332L, 0, 1,  68),
##            ( 9165L, 0, 1,  69),
##            ( 9998L, 0, 1,  70),
##            (10000L, 0, 0,  64),
##            (10000L, 0, 2,  50),
##            (15000L, 0, 0,  32),
##            (15000L, 0, 1,   0),
##            (15000L, 0, 2,   7),
##            (15000L, 0, 3,  42),
##            (15714L, 0, 2,   6),
##            (16428L, 0, 2,   5),
##            (17142L, 0, 2,   4),
##            (17856L, 0, 2,   3),
##            (18570L, 0, 2,   2),
##            (19284L, 0, 2,   1),
##            (19998L, 0, 2,   0),
##            (20000L, 0, 0,   0),
##            (20000L, 0, 3, 127),
##            (25000L, 0, 0, 127),
##            (25000L, 0, 3,   0),
##        ])
##
##    def checkLoadedFile(self, seq):
##        self.assertEqual(seq.eventList(), [
##            (    0L, 0, 0,   0),
##            (    0L, 0, 1,   0),
##            (    0L, 0, 2,   0),
##            (    0L, 0, 3,   0),
##            ( 5000L, 0, 0, 127),
##            ( 5000L, 0, 1,  64),
##            (10000L, 0, 0,  64),
##            (10000L, 0, 1,  64),
##            (10000L, 0, 2,  50),
##            (15000L, 0, 0,  32),
##            (15000L, 0, 1,   0),
##            (15000L, 0, 2,   7),
##            (15000L, 0, 3,  42),
##            (20000L, 0, 0,   0),
##            (20000L, 0, 2,   0),
##            (20000L, 0, 3, 127),
##            (25000L, 0, 0, 127),
##            (25000L, 0, 3,   0),
##        ])
