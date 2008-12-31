# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/SequenceTest.py,v 1.4 2008-12-31 00:13:32 steve Exp $
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
from Lumos.Event       import Event
from Lumos.Sequence    import Sequence, InvalidFileFormat, InvalidTimestamp, InvalidUnitDefinition
from Lumos.Sequence    import InvalidEvent
from TestNetwork       import TestNetwork
from Lumos.PowerSource import PowerSource

from Lumos.Device.FireGodControllerUnit import FireGodControllerUnit
from Lumos.Device.LynX10ControllerUnit  import LynX10ControllerUnit

class DummyController(object):
    def __init__(self, id):
        self.id = id

    def __eq__(self, other):
        return self.id == other.id

    def channel_id_from_string(self, ch):
        return ch

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

    def test_add_events(self):
        s = Sequence()
        s.add(1234, Event(self.controllers['floods'], 'A3', 50, 0))
        s.add(5543, Event(self.controllers['tree'],   '3', 100, 12))
        s.add(5543, Event(self.controllers['floods'], 'A3', 66, 0))
        s.add(1234, Event(self.controllers['floods'], 'X1', 22, 0))

        expected_events = {
            1234: [
                 Event(self.controllers['floods'], 'A3', 50, 0),
                 Event(self.controllers['floods'], 'X1', 22, 0)
            ],
            5543: [
                 Event(self.controllers['tree'],   '3', 100, 12),
                 Event(self.controllers['floods'], 'A3', 66, 0)
            ],
        }
        self.assertEquals(len(s.intervals), 2)
        self.assertEquals([i for i in s.intervals], [1234, 5543])
        for time in s.intervals:
            e_list = s.events_at(time)
            self.assertEqual(e_list, expected_events[time])

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

    def test_compilation(self):
        tree_controller = FireGodControllerUnit(
            'fg', PowerSource('ps1'), TestNetwork(),
            address=1, resolution=101, channels=32)
        tree_controller.add_channel(0, load=1)
        tree_controller.add_channel(1, load=1)
        tree_controller.add_channel(2, load=1)
        tree_controller.add_channel(3, load=1)

        floods_controller = LynX10ControllerUnit(
            'lx', PowerSource('ps2'), TestNetwork(), resolution=16)
        floods_controller.add_channel('C7', load=1, warm=10, resolution=16)

        s = Sequence()
        s.load_file('data/test.lseq', { 'floods': floods_controller, 'tree': tree_controller })
        # set_channel(id,lvl)
        # set_channel_on(id)
        # set_channel_off(id)
        # kill_channel(id)
        # kill_all_channels()
        # all_channels_off()
        # initialize_device()

        self.assert_(self.compare_timeline_lists(s.compile(), [
            (    0, tree_controller.all_channels_off, ()),       # == 0000 == all off
            (    0, floods_controller.all_channels_off, ()),
            ( 1000, tree_controller.set_channel, (0, 100)),      # == 1000 == 0=100
            ( 1000, floods_controller.set_channel, ('C7', 1)),   # C7 0->100% over 2000
            ( 1142, floods_controller.set_channel, ('C7', 2)),   #  (0-15, 15 steps, 1/133.33ms)
            ( 1285, floods_controller.set_channel, ('C7', 3)),
            ( 1428, floods_controller.set_channel, ('C7', 4)),
            ( 1571, floods_controller.set_channel, ('C7', 5)),
            ( 1714, floods_controller.set_channel, ('C7', 6)),
            ( 1857, floods_controller.set_channel, ('C7', 7)),
            ( 2000, tree_controller.set_channel, (0, 0)),        # == 2000 == 0=0
            ( 2000, tree_controller.set_channel, (1, 100)),      #            1=100
            ( 2000, floods_controller.set_channel, ('C7', 8)),
            ( 2142, floods_controller.set_channel, ('C7', 9)),
            ( 2285, floods_controller.set_channel, ('C7',10)),
            ( 2428, floods_controller.set_channel, ('C7',11)),
            ( 2571, floods_controller.set_channel, ('C7',12)),
            ( 2714, floods_controller.set_channel, ('C7',13)),
            ( 2857, floods_controller.set_channel, ('C7',14)),
            ( 3000, floods_controller.set_channel, ('C7',15)),
            ( 3000, tree_controller.set_channel, (1, 0)),        # == 3000 == 1=0, 2=100
            ( 3000, tree_controller.set_channel, (2, 100)),
            ( 4000, tree_controller.set_channel, (2, 0)),        # == 4000 == 2=0, 3=100
            ( 4000, tree_controller.set_channel, (3, 100)),
            ( 5000, tree_controller.set_channel, (0,   1)),      # == 5000 == 0=0->100 over 1000
            ( 5010, tree_controller.set_channel, (0,   2)),      # (100 steps, 1/10ms)
            ( 5020, tree_controller.set_channel, (0,   3)),
            ( 5030, tree_controller.set_channel, (0,   4)),
            ( 5040, tree_controller.set_channel, (0,   5)),
            ( 5050, tree_controller.set_channel, (0,   6)),
            ( 5060, tree_controller.set_channel, (0,   7)),
            ( 5070, tree_controller.set_channel, (0,   8)),
            ( 5080, tree_controller.set_channel, (0,   9)),
            ( 5090, tree_controller.set_channel, (0,  10)),
            ( 5101, tree_controller.set_channel, (0,  11)),
            ( 5111, tree_controller.set_channel, (0,  12)),
            ( 5121, tree_controller.set_channel, (0,  13)),
            ( 5131, tree_controller.set_channel, (0,  14)),
            ( 5141, tree_controller.set_channel, (0,  15)),
            ( 5151, tree_controller.set_channel, (0,  16)),
            ( 5161, tree_controller.set_channel, (0,  17)),
            ( 5171, tree_controller.set_channel, (0,  18)),
            ( 5181, tree_controller.set_channel, (0,  19)),
            ( 5191, tree_controller.set_channel, (0,  20)),
            ( 5202, tree_controller.set_channel, (0,  21)),
            ( 5212, tree_controller.set_channel, (0,  22)),
            ( 5222, tree_controller.set_channel, (0,  23)),
            ( 5232, tree_controller.set_channel, (0,  24)),
            ( 5242, tree_controller.set_channel, (0,  25)),
            ( 5252, tree_controller.set_channel, (0,  26)),
            ( 5262, tree_controller.set_channel, (0,  27)),
            ( 5272, tree_controller.set_channel, (0,  28)),
            ( 5282, tree_controller.set_channel, (0,  29)),
            ( 5292, tree_controller.set_channel, (0,  30)),
            ( 5303, tree_controller.set_channel, (0,  31)),
            ( 5313, tree_controller.set_channel, (0,  32)),
            ( 5323, tree_controller.set_channel, (0,  33)),
            ( 5333, tree_controller.set_channel, (0,  34)),
            ( 5343, tree_controller.set_channel, (0,  35)),
            ( 5353, tree_controller.set_channel, (0,  36)),
            ( 5363, tree_controller.set_channel, (0,  37)),
            ( 5373, tree_controller.set_channel, (0,  38)),
            ( 5383, tree_controller.set_channel, (0,  39)),
            ( 5393, tree_controller.set_channel, (0,  40)),
            ( 5404, tree_controller.set_channel, (0,  41)),
            ( 5414, tree_controller.set_channel, (0,  42)),
            ( 5424, tree_controller.set_channel, (0,  43)),
            ( 5434, tree_controller.set_channel, (0,  44)),
            ( 5444, tree_controller.set_channel, (0,  45)),
            ( 5454, tree_controller.set_channel, (0,  46)),
            ( 5464, tree_controller.set_channel, (0,  47)),
            ( 5474, tree_controller.set_channel, (0,  48)),
            ( 5484, tree_controller.set_channel, (0,  49)),
            ( 5494, tree_controller.set_channel, (0,  50)),
            ( 5505, tree_controller.set_channel, (0,  51)),
            ( 5515, tree_controller.set_channel, (0,  52)),
            ( 5525, tree_controller.set_channel, (0,  53)),
            ( 5535, tree_controller.set_channel, (0,  54)),
            ( 5545, tree_controller.set_channel, (0,  55)),
            ( 5555, tree_controller.set_channel, (0,  56)),
            ( 5565, tree_controller.set_channel, (0,  57)),
            ( 5575, tree_controller.set_channel, (0,  58)),
            ( 5585, tree_controller.set_channel, (0,  59)),
            ( 5595, tree_controller.set_channel, (0,  60)),
            ( 5606, tree_controller.set_channel, (0,  61)),
            ( 5616, tree_controller.set_channel, (0,  62)),
            ( 5626, tree_controller.set_channel, (0,  63)),
            ( 5636, tree_controller.set_channel, (0,  64)),
            ( 5646, tree_controller.set_channel, (0,  65)),
            ( 5656, tree_controller.set_channel, (0,  66)),
            ( 5666, tree_controller.set_channel, (0,  67)),
            ( 5676, tree_controller.set_channel, (0,  68)),
            ( 5686, tree_controller.set_channel, (0,  69)),
            ( 5696, tree_controller.set_channel, (0,  70)),
            ( 5707, tree_controller.set_channel, (0,  71)),
            ( 5717, tree_controller.set_channel, (0,  72)),
            ( 5727, tree_controller.set_channel, (0,  73)),
            ( 5737, tree_controller.set_channel, (0,  74)),
            ( 5747, tree_controller.set_channel, (0,  75)),
            ( 5757, tree_controller.set_channel, (0,  76)),
            ( 5767, tree_controller.set_channel, (0,  77)),
            ( 5777, tree_controller.set_channel, (0,  78)),
            ( 5787, tree_controller.set_channel, (0,  79)),
            ( 5797, tree_controller.set_channel, (0,  80)),
            ( 5808, tree_controller.set_channel, (0,  81)),
            ( 5818, tree_controller.set_channel, (0,  82)),
            ( 5828, tree_controller.set_channel, (0,  83)),
            ( 5838, tree_controller.set_channel, (0,  84)),
            ( 5848, tree_controller.set_channel, (0,  85)),
            ( 5858, tree_controller.set_channel, (0,  86)),
            ( 5868, tree_controller.set_channel, (0,  87)),
            ( 5878, tree_controller.set_channel, (0,  88)),
            ( 5888, tree_controller.set_channel, (0,  89)),
            ( 5898, tree_controller.set_channel, (0,  90)),
            ( 5909, tree_controller.set_channel, (0,  91)),
            ( 5919, tree_controller.set_channel, (0,  92)),
            ( 5929, tree_controller.set_channel, (0,  93)),
            ( 5939, tree_controller.set_channel, (0,  94)),
            ( 5949, tree_controller.set_channel, (0,  95)),
            ( 5959, tree_controller.set_channel, (0,  96)),
            ( 5969, tree_controller.set_channel, (0,  97)),
            ( 5979, tree_controller.set_channel, (0,  98)),
            ( 5989, tree_controller.set_channel, (0,  99)),
            ( 6000, tree_controller.set_channel, (0, 100)),
            ( 6000, tree_controller.set_channel, (1,   1)),      # == 6000 == 1=0->100 over 1000
            ( 6010, tree_controller.set_channel, (1,   2)),      # (100 steps, 1/10ms)
            ( 6020, tree_controller.set_channel, (1,   3)),
            ( 6030, tree_controller.set_channel, (1,   4)),
            ( 6040, tree_controller.set_channel, (1,   5)),
            ( 6050, tree_controller.set_channel, (1,   6)),
            ( 6060, tree_controller.set_channel, (1,   7)),
            ( 6070, tree_controller.set_channel, (1,   8)),
            ( 6080, tree_controller.set_channel, (1,   9)),
            ( 6090, tree_controller.set_channel, (1,  10)),
            ( 6101, tree_controller.set_channel, (1,  11)),
            ( 6111, tree_controller.set_channel, (1,  12)),
            ( 6121, tree_controller.set_channel, (1,  13)),
            ( 6131, tree_controller.set_channel, (1,  14)),
            ( 6141, tree_controller.set_channel, (1,  15)),
            ( 6151, tree_controller.set_channel, (1,  16)),
            ( 6161, tree_controller.set_channel, (1,  17)),
            ( 6171, tree_controller.set_channel, (1,  18)),
            ( 6181, tree_controller.set_channel, (1,  19)),
            ( 6191, tree_controller.set_channel, (1,  20)),
            ( 6202, tree_controller.set_channel, (1,  21)),
            ( 6212, tree_controller.set_channel, (1,  22)),
            ( 6222, tree_controller.set_channel, (1,  23)),
            ( 6232, tree_controller.set_channel, (1,  24)),
            ( 6242, tree_controller.set_channel, (1,  25)),
            ( 6252, tree_controller.set_channel, (1,  26)),
            ( 6262, tree_controller.set_channel, (1,  27)),
            ( 6272, tree_controller.set_channel, (1,  28)),
            ( 6282, tree_controller.set_channel, (1,  29)),
            ( 6292, tree_controller.set_channel, (1,  30)),
            ( 6303, tree_controller.set_channel, (1,  31)),
            ( 6313, tree_controller.set_channel, (1,  32)),
            ( 6323, tree_controller.set_channel, (1,  33)),
            ( 6333, tree_controller.set_channel, (1,  34)),
            ( 6343, tree_controller.set_channel, (1,  35)),
            ( 6353, tree_controller.set_channel, (1,  36)),
            ( 6363, tree_controller.set_channel, (1,  37)),
            ( 6373, tree_controller.set_channel, (1,  38)),
            ( 6383, tree_controller.set_channel, (1,  39)),
            ( 6393, tree_controller.set_channel, (1,  40)),
            ( 6404, tree_controller.set_channel, (1,  41)),
            ( 6414, tree_controller.set_channel, (1,  42)),
            ( 6424, tree_controller.set_channel, (1,  43)),
            ( 6434, tree_controller.set_channel, (1,  44)),
            ( 6444, tree_controller.set_channel, (1,  45)),
            ( 6454, tree_controller.set_channel, (1,  46)),
            ( 6464, tree_controller.set_channel, (1,  47)),
            ( 6474, tree_controller.set_channel, (1,  48)),
            ( 6484, tree_controller.set_channel, (1,  49)),
            ( 6494, tree_controller.set_channel, (1,  50)),
            ( 6505, tree_controller.set_channel, (1,  51)),
            ( 6515, tree_controller.set_channel, (1,  52)),
            ( 6525, tree_controller.set_channel, (1,  53)),
            ( 6535, tree_controller.set_channel, (1,  54)),
            ( 6545, tree_controller.set_channel, (1,  55)),
            ( 6555, tree_controller.set_channel, (1,  56)),
            ( 6565, tree_controller.set_channel, (1,  57)),
            ( 6575, tree_controller.set_channel, (1,  58)),
            ( 6585, tree_controller.set_channel, (1,  59)),
            ( 6595, tree_controller.set_channel, (1,  60)),
            ( 6606, tree_controller.set_channel, (1,  61)),
            ( 6616, tree_controller.set_channel, (1,  62)),
            ( 6626, tree_controller.set_channel, (1,  63)),
            ( 6636, tree_controller.set_channel, (1,  64)),
            ( 6646, tree_controller.set_channel, (1,  65)),
            ( 6656, tree_controller.set_channel, (1,  66)),
            ( 6666, tree_controller.set_channel, (1,  67)),
            ( 6676, tree_controller.set_channel, (1,  68)),
            ( 6686, tree_controller.set_channel, (1,  69)),
            ( 6696, tree_controller.set_channel, (1,  70)),
            ( 6707, tree_controller.set_channel, (1,  71)),
            ( 6717, tree_controller.set_channel, (1,  72)),
            ( 6727, tree_controller.set_channel, (1,  73)),
            ( 6737, tree_controller.set_channel, (1,  74)),
            ( 6747, tree_controller.set_channel, (1,  75)),
            ( 6757, tree_controller.set_channel, (1,  76)),
            ( 6767, tree_controller.set_channel, (1,  77)),
            ( 6777, tree_controller.set_channel, (1,  78)),
            ( 6787, tree_controller.set_channel, (1,  79)),
            ( 6797, tree_controller.set_channel, (1,  80)),
            ( 6808, tree_controller.set_channel, (1,  81)),
            ( 6818, tree_controller.set_channel, (1,  82)),
            ( 6828, tree_controller.set_channel, (1,  83)),
            ( 6838, tree_controller.set_channel, (1,  84)),
            ( 6848, tree_controller.set_channel, (1,  85)),
            ( 6858, tree_controller.set_channel, (1,  86)),
            ( 6868, tree_controller.set_channel, (1,  87)),
            ( 6878, tree_controller.set_channel, (1,  88)),
            ( 6888, tree_controller.set_channel, (1,  89)),
            ( 6898, tree_controller.set_channel, (1,  90)),
            ( 6909, tree_controller.set_channel, (1,  91)),
            ( 6919, tree_controller.set_channel, (1,  92)),
            ( 6929, tree_controller.set_channel, (1,  93)),
            ( 6939, tree_controller.set_channel, (1,  94)),
            ( 6949, tree_controller.set_channel, (1,  95)),
            ( 6959, tree_controller.set_channel, (1,  96)),
            ( 6969, tree_controller.set_channel, (1,  97)),
            ( 6979, tree_controller.set_channel, (1,  98)),
            ( 6989, tree_controller.set_channel, (1,  99)),
            ( 7000, tree_controller.set_channel, (1, 100)),
            ( 7000, floods_controller.set_channel, ('C7', 7)), # == 7000 == C7=50
            ( 7000, tree_controller.set_channel, (2,   1)),    # == 7000 == 2=0->100 over 1000
            ( 7010, tree_controller.set_channel, (2,   2)),      # (100 steps, 1/10ms)
            ( 7020, tree_controller.set_channel, (2,   3)),
            ( 7030, tree_controller.set_channel, (2,   4)),
            ( 7040, tree_controller.set_channel, (2,   5)),
            ( 7050, tree_controller.set_channel, (2,   6)),
            ( 7060, tree_controller.set_channel, (2,   7)),
            ( 7070, tree_controller.set_channel, (2,   8)),
            ( 7080, tree_controller.set_channel, (2,   9)),
            ( 7090, tree_controller.set_channel, (2,  10)),
            ( 7101, tree_controller.set_channel, (2,  11)),
            ( 7111, tree_controller.set_channel, (2,  12)),
            ( 7121, tree_controller.set_channel, (2,  13)),
            ( 7131, tree_controller.set_channel, (2,  14)),
            ( 7141, tree_controller.set_channel, (2,  15)),
            ( 7151, tree_controller.set_channel, (2,  16)),
            ( 7161, tree_controller.set_channel, (2,  17)),
            ( 7171, tree_controller.set_channel, (2,  18)),
            ( 7181, tree_controller.set_channel, (2,  19)),
            ( 7191, tree_controller.set_channel, (2,  20)),
            ( 7202, tree_controller.set_channel, (2,  21)),
            ( 7212, tree_controller.set_channel, (2,  22)),
            ( 7222, tree_controller.set_channel, (2,  23)),
            ( 7232, tree_controller.set_channel, (2,  24)),
            ( 7242, tree_controller.set_channel, (2,  25)),
            ( 7252, tree_controller.set_channel, (2,  26)),
            ( 7262, tree_controller.set_channel, (2,  27)),
            ( 7272, tree_controller.set_channel, (2,  28)),
            ( 7282, tree_controller.set_channel, (2,  29)),
            ( 7292, tree_controller.set_channel, (2,  30)),
            ( 7303, tree_controller.set_channel, (2,  31)),
            ( 7313, tree_controller.set_channel, (2,  32)),
            ( 7323, tree_controller.set_channel, (2,  33)),
            ( 7333, tree_controller.set_channel, (2,  34)),
            ( 7343, tree_controller.set_channel, (2,  35)),
            ( 7353, tree_controller.set_channel, (2,  36)),
            ( 7363, tree_controller.set_channel, (2,  37)),
            ( 7373, tree_controller.set_channel, (2,  38)),
            ( 7383, tree_controller.set_channel, (2,  39)),
            ( 7393, tree_controller.set_channel, (2,  40)),
            ( 7404, tree_controller.set_channel, (2,  41)),
            ( 7414, tree_controller.set_channel, (2,  42)),
            ( 7424, tree_controller.set_channel, (2,  43)),
            ( 7434, tree_controller.set_channel, (2,  44)),
            ( 7444, tree_controller.set_channel, (2,  45)),
            ( 7454, tree_controller.set_channel, (2,  46)),
            ( 7464, tree_controller.set_channel, (2,  47)),
            ( 7474, tree_controller.set_channel, (2,  48)),
            ( 7484, tree_controller.set_channel, (2,  49)),
            ( 7494, tree_controller.set_channel, (2,  50)),
            ( 7505, tree_controller.set_channel, (2,  51)),
            ( 7515, tree_controller.set_channel, (2,  52)),
            ( 7525, tree_controller.set_channel, (2,  53)),
            ( 7535, tree_controller.set_channel, (2,  54)),
            ( 7545, tree_controller.set_channel, (2,  55)),
            ( 7555, tree_controller.set_channel, (2,  56)),
            ( 7565, tree_controller.set_channel, (2,  57)),
            ( 7575, tree_controller.set_channel, (2,  58)),
            ( 7585, tree_controller.set_channel, (2,  59)),
            ( 7595, tree_controller.set_channel, (2,  60)),
            ( 7606, tree_controller.set_channel, (2,  61)),
            ( 7616, tree_controller.set_channel, (2,  62)),
            ( 7626, tree_controller.set_channel, (2,  63)),
            ( 7636, tree_controller.set_channel, (2,  64)),
            ( 7646, tree_controller.set_channel, (2,  65)),
            ( 7656, tree_controller.set_channel, (2,  66)),
            ( 7666, tree_controller.set_channel, (2,  67)),
            ( 7676, tree_controller.set_channel, (2,  68)),
            ( 7686, tree_controller.set_channel, (2,  69)),
            ( 7696, tree_controller.set_channel, (2,  70)),
            ( 7707, tree_controller.set_channel, (2,  71)),
            ( 7717, tree_controller.set_channel, (2,  72)),
            ( 7727, tree_controller.set_channel, (2,  73)),
            ( 7737, tree_controller.set_channel, (2,  74)),
            ( 7747, tree_controller.set_channel, (2,  75)),
            ( 7757, tree_controller.set_channel, (2,  76)),
            ( 7767, tree_controller.set_channel, (2,  77)),
            ( 7777, tree_controller.set_channel, (2,  78)),
            ( 7787, tree_controller.set_channel, (2,  79)),
            ( 7797, tree_controller.set_channel, (2,  80)),
            ( 7808, tree_controller.set_channel, (2,  81)),
            ( 7818, tree_controller.set_channel, (2,  82)),
            ( 7828, tree_controller.set_channel, (2,  83)),
            ( 7838, tree_controller.set_channel, (2,  84)),
            ( 7848, tree_controller.set_channel, (2,  85)),
            ( 7858, tree_controller.set_channel, (2,  86)),
            ( 7868, tree_controller.set_channel, (2,  87)),
            ( 7878, tree_controller.set_channel, (2,  88)),
            ( 7888, tree_controller.set_channel, (2,  89)),
            ( 7898, tree_controller.set_channel, (2,  90)),
            ( 7909, tree_controller.set_channel, (2,  91)),
            ( 7919, tree_controller.set_channel, (2,  92)),
            ( 7929, tree_controller.set_channel, (2,  93)),
            ( 7939, tree_controller.set_channel, (2,  94)),
            ( 7949, tree_controller.set_channel, (2,  95)),
            ( 7959, tree_controller.set_channel, (2,  96)),
            ( 7969, tree_controller.set_channel, (2,  97)),
            ( 7979, tree_controller.set_channel, (2,  98)),
            ( 7989, tree_controller.set_channel, (2,  99)),
            ( 8000, tree_controller.set_channel, (2, 100)),
                  # == 8000 == 3=100->100 over 1000
                  # already there, so we should not
                  # emit any change events here
            # == 10000 == all fade -> 0 over 1000ms
            # C7 6->0 over 1000ms  
            # 0,1,2,3 99->0 over 1000ms
            (10000, tree_controller.set_channel, (0,  99)),
            (10000, tree_controller.set_channel, (1,  99)),
            (10000, tree_controller.set_channel, (2,  99)),
            (10000, tree_controller.set_channel, (3,  99)),
            (10000, floods_controller.set_channel,('C7', 6)),
            (10010, tree_controller.set_channel, (0,  98)),
            (10010, tree_controller.set_channel, (1,  98)),
            (10010, tree_controller.set_channel, (2,  98)),
            (10010, tree_controller.set_channel, (3,  98)),
            (10020, tree_controller.set_channel, (0,  97)),
            (10020, tree_controller.set_channel, (1,  97)),
            (10020, tree_controller.set_channel, (2,  97)),
            (10020, tree_controller.set_channel, (3,  97)),
            (10030, tree_controller.set_channel, (0,  96)),
            (10030, tree_controller.set_channel, (1,  96)),
            (10030, tree_controller.set_channel, (2,  96)),
            (10030, tree_controller.set_channel, (3,  96)),
            (10040, tree_controller.set_channel, (0,  95)),
            (10040, tree_controller.set_channel, (1,  95)),
            (10040, tree_controller.set_channel, (2,  95)),
            (10040, tree_controller.set_channel, (3,  95)),
            (10050, tree_controller.set_channel, (0,  94)),
            (10050, tree_controller.set_channel, (1,  94)),
            (10050, tree_controller.set_channel, (2,  94)),
            (10050, tree_controller.set_channel, (3,  94)),
            (10060, tree_controller.set_channel, (0,  93)),
            (10060, tree_controller.set_channel, (1,  93)),
            (10060, tree_controller.set_channel, (2,  93)),
            (10060, tree_controller.set_channel, (3,  93)),
            (10070, tree_controller.set_channel, (0,  92)),
            (10070, tree_controller.set_channel, (1,  92)),
            (10070, tree_controller.set_channel, (2,  92)),
            (10070, tree_controller.set_channel, (3,  92)),
            (10080, tree_controller.set_channel, (0,  91)),
            (10080, tree_controller.set_channel, (1,  91)),
            (10080, tree_controller.set_channel, (2,  91)),
            (10080, tree_controller.set_channel, (3,  91)),
            (10090, tree_controller.set_channel, (0,  90)),
            (10090, tree_controller.set_channel, (1,  90)),
            (10090, tree_controller.set_channel, (2,  90)),
            (10090, tree_controller.set_channel, (3,  90)),
            (10101, tree_controller.set_channel, (0,  89)),
            (10101, tree_controller.set_channel, (1,  89)),
            (10101, tree_controller.set_channel, (2,  89)),
            (10101, tree_controller.set_channel, (3,  89)),
            (10111, tree_controller.set_channel, (0,  88)),
            (10111, tree_controller.set_channel, (1,  88)),
            (10111, tree_controller.set_channel, (2,  88)),
            (10111, tree_controller.set_channel, (3,  88)),
            (10121, tree_controller.set_channel, (0,  87)),
            (10121, tree_controller.set_channel, (1,  87)),
            (10121, tree_controller.set_channel, (2,  87)),
            (10121, tree_controller.set_channel, (3,  87)),
            (10131, tree_controller.set_channel, (0,  86)),
            (10131, tree_controller.set_channel, (1,  86)),
            (10131, tree_controller.set_channel, (2,  86)),
            (10131, tree_controller.set_channel, (3,  86)),
            (10141, tree_controller.set_channel, (0,  85)),
            (10141, tree_controller.set_channel, (1,  85)),
            (10141, tree_controller.set_channel, (2,  85)),
            (10141, tree_controller.set_channel, (3,  85)),
            (10151, tree_controller.set_channel, (0,  84)),
            (10151, tree_controller.set_channel, (1,  84)),
            (10151, tree_controller.set_channel, (2,  84)),
            (10151, tree_controller.set_channel, (3,  84)),
            (10161, tree_controller.set_channel, (0,  83)),
            (10161, tree_controller.set_channel, (1,  83)),
            (10161, tree_controller.set_channel, (2,  83)),
            (10161, tree_controller.set_channel, (3,  83)),
            (10166, floods_controller.set_channel,('C7', 5)),
            (10171, tree_controller.set_channel, (0,  82)),
            (10171, tree_controller.set_channel, (1,  82)),
            (10171, tree_controller.set_channel, (2,  82)),
            (10171, tree_controller.set_channel, (3,  82)),
            (10181, tree_controller.set_channel, (0,  81)),
            (10181, tree_controller.set_channel, (1,  81)),
            (10181, tree_controller.set_channel, (2,  81)),
            (10181, tree_controller.set_channel, (3,  81)),
            (10191, tree_controller.set_channel, (0,  80)),
            (10191, tree_controller.set_channel, (1,  80)),
            (10191, tree_controller.set_channel, (2,  80)),
            (10191, tree_controller.set_channel, (3,  80)),
            (10202, tree_controller.set_channel, (0,  79)),
            (10202, tree_controller.set_channel, (1,  79)),
            (10202, tree_controller.set_channel, (2,  79)),
            (10202, tree_controller.set_channel, (3,  79)),
            (10212, tree_controller.set_channel, (0,  78)),
            (10212, tree_controller.set_channel, (1,  78)),
            (10212, tree_controller.set_channel, (2,  78)),
            (10212, tree_controller.set_channel, (3,  78)),
            (10222, tree_controller.set_channel, (0,  77)),
            (10222, tree_controller.set_channel, (1,  77)),
            (10222, tree_controller.set_channel, (2,  77)),
            (10222, tree_controller.set_channel, (3,  77)),
            (10232, tree_controller.set_channel, (0,  76)),
            (10232, tree_controller.set_channel, (1,  76)),
            (10232, tree_controller.set_channel, (2,  76)),
            (10232, tree_controller.set_channel, (3,  76)),
            (10242, tree_controller.set_channel, (0,  75)),
            (10242, tree_controller.set_channel, (1,  75)),
            (10242, tree_controller.set_channel, (2,  75)),
            (10242, tree_controller.set_channel, (3,  75)),
            (10252, tree_controller.set_channel, (0,  74)),
            (10252, tree_controller.set_channel, (1,  74)),
            (10252, tree_controller.set_channel, (2,  74)),
            (10252, tree_controller.set_channel, (3,  74)),
            (10262, tree_controller.set_channel, (0,  73)),
            (10262, tree_controller.set_channel, (1,  73)),
            (10262, tree_controller.set_channel, (2,  73)),
            (10262, tree_controller.set_channel, (3,  73)),
            (10272, tree_controller.set_channel, (0,  72)),
            (10272, tree_controller.set_channel, (1,  72)),
            (10272, tree_controller.set_channel, (2,  72)),
            (10272, tree_controller.set_channel, (3,  72)),
            (10282, tree_controller.set_channel, (0,  71)),
            (10282, tree_controller.set_channel, (1,  71)),
            (10282, tree_controller.set_channel, (2,  71)),
            (10282, tree_controller.set_channel, (3,  71)),
            (10292, tree_controller.set_channel, (0,  70)),
            (10292, tree_controller.set_channel, (1,  70)),
            (10292, tree_controller.set_channel, (2,  70)),
            (10292, tree_controller.set_channel, (3,  70)),
            (10303, tree_controller.set_channel, (0,  69)),
            (10303, tree_controller.set_channel, (1,  69)),
            (10303, tree_controller.set_channel, (2,  69)),
            (10303, tree_controller.set_channel, (3,  69)),
            (10313, tree_controller.set_channel, (0,  68)),
            (10313, tree_controller.set_channel, (1,  68)),
            (10313, tree_controller.set_channel, (2,  68)),
            (10313, tree_controller.set_channel, (3,  68)),
            (10323, tree_controller.set_channel, (0,  67)),
            (10323, tree_controller.set_channel, (1,  67)),
            (10323, tree_controller.set_channel, (2,  67)),
            (10323, tree_controller.set_channel, (3,  67)),
            (10333, tree_controller.set_channel, (0,  66)),
            (10333, tree_controller.set_channel, (1,  66)),
            (10333, tree_controller.set_channel, (2,  66)),
            (10333, tree_controller.set_channel, (3,  66)),
            (10333, floods_controller.set_channel,('C7', 4)),
            (10343, tree_controller.set_channel, (0,  65)),
            (10343, tree_controller.set_channel, (1,  65)),
            (10343, tree_controller.set_channel, (2,  65)),
            (10343, tree_controller.set_channel, (3,  65)),
            (10353, tree_controller.set_channel, (0,  64)),
            (10353, tree_controller.set_channel, (1,  64)),
            (10353, tree_controller.set_channel, (2,  64)),
            (10353, tree_controller.set_channel, (3,  64)),
            (10363, tree_controller.set_channel, (0,  63)),
            (10363, tree_controller.set_channel, (1,  63)),
            (10363, tree_controller.set_channel, (2,  63)),
            (10363, tree_controller.set_channel, (3,  63)),
            (10373, tree_controller.set_channel, (0,  62)),
            (10373, tree_controller.set_channel, (1,  62)),
            (10373, tree_controller.set_channel, (2,  62)),
            (10373, tree_controller.set_channel, (3,  62)),
            (10383, tree_controller.set_channel, (0,  61)),
            (10383, tree_controller.set_channel, (1,  61)),
            (10383, tree_controller.set_channel, (2,  61)),
            (10383, tree_controller.set_channel, (3,  61)),
            (10393, tree_controller.set_channel, (0,  60)),
            (10393, tree_controller.set_channel, (1,  60)),
            (10393, tree_controller.set_channel, (2,  60)),
            (10393, tree_controller.set_channel, (3,  60)),
            (10404, tree_controller.set_channel, (0,  59)),
            (10404, tree_controller.set_channel, (1,  59)),
            (10404, tree_controller.set_channel, (2,  59)),
            (10404, tree_controller.set_channel, (3,  59)),
            (10414, tree_controller.set_channel, (0,  58)),
            (10414, tree_controller.set_channel, (1,  58)),
            (10414, tree_controller.set_channel, (2,  58)),
            (10414, tree_controller.set_channel, (3,  58)),
            (10424, tree_controller.set_channel, (0,  57)),
            (10424, tree_controller.set_channel, (1,  57)),
            (10424, tree_controller.set_channel, (2,  57)),
            (10424, tree_controller.set_channel, (3,  57)),
            (10434, tree_controller.set_channel, (0,  56)),
            (10434, tree_controller.set_channel, (1,  56)),
            (10434, tree_controller.set_channel, (2,  56)),
            (10434, tree_controller.set_channel, (3,  56)),
            (10444, tree_controller.set_channel, (0,  55)),
            (10444, tree_controller.set_channel, (1,  55)),
            (10444, tree_controller.set_channel, (2,  55)),
            (10444, tree_controller.set_channel, (3,  55)),
            (10454, tree_controller.set_channel, (0,  54)),
            (10454, tree_controller.set_channel, (1,  54)),
            (10454, tree_controller.set_channel, (2,  54)),
            (10454, tree_controller.set_channel, (3,  54)),
            (10464, tree_controller.set_channel, (0,  53)),
            (10464, tree_controller.set_channel, (1,  53)),
            (10464, tree_controller.set_channel, (2,  53)),
            (10464, tree_controller.set_channel, (3,  53)),
            (10474, tree_controller.set_channel, (0,  52)),
            (10474, tree_controller.set_channel, (1,  52)),
            (10474, tree_controller.set_channel, (2,  52)),
            (10474, tree_controller.set_channel, (3,  52)),
            (10484, tree_controller.set_channel, (0,  51)),
            (10484, tree_controller.set_channel, (1,  51)),
            (10484, tree_controller.set_channel, (2,  51)),
            (10484, tree_controller.set_channel, (3,  51)),
            (10494, tree_controller.set_channel, (0,  50)),
            (10494, tree_controller.set_channel, (1,  50)),
            (10494, tree_controller.set_channel, (2,  50)),
            (10494, tree_controller.set_channel, (3,  50)),
            (10500, floods_controller.set_channel,('C7', 3)),
            (10505, tree_controller.set_channel, (0,  49)),
            (10505, tree_controller.set_channel, (1,  49)),
            (10505, tree_controller.set_channel, (2,  49)),
            (10505, tree_controller.set_channel, (3,  49)),
            (10515, tree_controller.set_channel, (0,  48)),
            (10515, tree_controller.set_channel, (1,  48)),
            (10515, tree_controller.set_channel, (2,  48)),
            (10515, tree_controller.set_channel, (3,  48)),
            (10525, tree_controller.set_channel, (0,  47)),
            (10525, tree_controller.set_channel, (1,  47)),
            (10525, tree_controller.set_channel, (2,  47)),
            (10525, tree_controller.set_channel, (3,  47)),
            (10535, tree_controller.set_channel, (0,  46)),
            (10535, tree_controller.set_channel, (1,  46)),
            (10535, tree_controller.set_channel, (2,  46)),
            (10535, tree_controller.set_channel, (3,  46)),
            (10545, tree_controller.set_channel, (0,  45)),
            (10545, tree_controller.set_channel, (1,  45)),
            (10545, tree_controller.set_channel, (2,  45)),
            (10545, tree_controller.set_channel, (3,  45)),
            (10555, tree_controller.set_channel, (0,  44)),
            (10555, tree_controller.set_channel, (1,  44)),
            (10555, tree_controller.set_channel, (2,  44)),
            (10555, tree_controller.set_channel, (3,  44)),
            (10565, tree_controller.set_channel, (0,  43)),
            (10565, tree_controller.set_channel, (1,  43)),
            (10565, tree_controller.set_channel, (2,  43)),
            (10565, tree_controller.set_channel, (3,  43)),
            (10575, tree_controller.set_channel, (0,  42)),
            (10575, tree_controller.set_channel, (1,  42)),
            (10575, tree_controller.set_channel, (2,  42)),
            (10575, tree_controller.set_channel, (3,  42)),
            (10585, tree_controller.set_channel, (0,  41)),
            (10585, tree_controller.set_channel, (1,  41)),
            (10585, tree_controller.set_channel, (2,  41)),
            (10585, tree_controller.set_channel, (3,  41)),
            (10595, tree_controller.set_channel, (0,  40)),
            (10595, tree_controller.set_channel, (1,  40)),
            (10595, tree_controller.set_channel, (2,  40)),
            (10595, tree_controller.set_channel, (3,  40)),
            (10606, tree_controller.set_channel, (0,  39)),
            (10606, tree_controller.set_channel, (1,  39)),
            (10606, tree_controller.set_channel, (2,  39)),
            (10606, tree_controller.set_channel, (3,  39)),
            (10616, tree_controller.set_channel, (0,  38)),
            (10616, tree_controller.set_channel, (1,  38)),
            (10616, tree_controller.set_channel, (2,  38)),
            (10616, tree_controller.set_channel, (3,  38)),
            (10626, tree_controller.set_channel, (0,  37)),
            (10626, tree_controller.set_channel, (1,  37)),
            (10626, tree_controller.set_channel, (2,  37)),
            (10626, tree_controller.set_channel, (3,  37)),
            (10636, tree_controller.set_channel, (0,  36)),
            (10636, tree_controller.set_channel, (1,  36)),
            (10636, tree_controller.set_channel, (2,  36)),
            (10636, tree_controller.set_channel, (3,  36)),
            (10646, tree_controller.set_channel, (0,  35)),
            (10646, tree_controller.set_channel, (1,  35)),
            (10646, tree_controller.set_channel, (2,  35)),
            (10646, tree_controller.set_channel, (3,  35)),
            (10656, tree_controller.set_channel, (0,  34)),
            (10656, tree_controller.set_channel, (1,  34)),
            (10656, tree_controller.set_channel, (2,  34)),
            (10656, tree_controller.set_channel, (3,  34)),
            (10666, tree_controller.set_channel, (0,  33)),
            (10666, tree_controller.set_channel, (1,  33)),
            (10666, tree_controller.set_channel, (2,  33)),
            (10666, tree_controller.set_channel, (3,  33)),
            (10666, floods_controller.set_channel,('C7', 2)),
            (10676, tree_controller.set_channel, (0,  32)),
            (10676, tree_controller.set_channel, (1,  32)),
            (10676, tree_controller.set_channel, (2,  32)),
            (10676, tree_controller.set_channel, (3,  32)),
            (10686, tree_controller.set_channel, (0,  31)),
            (10686, tree_controller.set_channel, (1,  31)),
            (10686, tree_controller.set_channel, (2,  31)),
            (10686, tree_controller.set_channel, (3,  31)),
            (10696, tree_controller.set_channel, (0,  30)),
            (10696, tree_controller.set_channel, (1,  30)),
            (10696, tree_controller.set_channel, (2,  30)),
            (10696, tree_controller.set_channel, (3,  30)),
            (10707, tree_controller.set_channel, (0,  29)),
            (10707, tree_controller.set_channel, (1,  29)),
            (10707, tree_controller.set_channel, (2,  29)),
            (10707, tree_controller.set_channel, (3,  29)),
            (10717, tree_controller.set_channel, (0,  28)),
            (10717, tree_controller.set_channel, (1,  28)),
            (10717, tree_controller.set_channel, (2,  28)),
            (10717, tree_controller.set_channel, (3,  28)),
            (10727, tree_controller.set_channel, (0,  27)),
            (10727, tree_controller.set_channel, (1,  27)),
            (10727, tree_controller.set_channel, (2,  27)),
            (10727, tree_controller.set_channel, (3,  27)),
            (10737, tree_controller.set_channel, (0,  26)),
            (10737, tree_controller.set_channel, (1,  26)),
            (10737, tree_controller.set_channel, (2,  26)),
            (10737, tree_controller.set_channel, (3,  26)),
            (10747, tree_controller.set_channel, (0,  25)),
            (10747, tree_controller.set_channel, (1,  25)),
            (10747, tree_controller.set_channel, (2,  25)),
            (10747, tree_controller.set_channel, (3,  25)),
            (10757, tree_controller.set_channel, (0,  24)),
            (10757, tree_controller.set_channel, (1,  24)),
            (10757, tree_controller.set_channel, (2,  24)),
            (10757, tree_controller.set_channel, (3,  24)),
            (10767, tree_controller.set_channel, (0,  23)),
            (10767, tree_controller.set_channel, (1,  23)),
            (10767, tree_controller.set_channel, (2,  23)),
            (10767, tree_controller.set_channel, (3,  23)),
            (10777, tree_controller.set_channel, (0,  22)),
            (10777, tree_controller.set_channel, (1,  22)),
            (10777, tree_controller.set_channel, (2,  22)),
            (10777, tree_controller.set_channel, (3,  22)),
            (10787, tree_controller.set_channel, (0,  21)),
            (10787, tree_controller.set_channel, (1,  21)),
            (10787, tree_controller.set_channel, (2,  21)),
            (10787, tree_controller.set_channel, (3,  21)),
            (10797, tree_controller.set_channel, (0,  20)),
            (10797, tree_controller.set_channel, (1,  20)),
            (10797, tree_controller.set_channel, (2,  20)),
            (10797, tree_controller.set_channel, (3,  20)),
            (10808, tree_controller.set_channel, (0,  19)),
            (10808, tree_controller.set_channel, (1,  19)),
            (10808, tree_controller.set_channel, (2,  19)),
            (10808, tree_controller.set_channel, (3,  19)),
            (10818, tree_controller.set_channel, (0,  18)),
            (10818, tree_controller.set_channel, (1,  18)),
            (10818, tree_controller.set_channel, (2,  18)),
            (10818, tree_controller.set_channel, (3,  18)),
            (10828, tree_controller.set_channel, (0,  17)),
            (10828, tree_controller.set_channel, (1,  17)),
            (10828, tree_controller.set_channel, (2,  17)),
            (10828, tree_controller.set_channel, (3,  17)),
            (10833, floods_controller.set_channel,('C7', 1)),
            (10838, tree_controller.set_channel, (0,  16)),
            (10838, tree_controller.set_channel, (1,  16)),
            (10838, tree_controller.set_channel, (2,  16)),
            (10838, tree_controller.set_channel, (3,  16)),
            (10848, tree_controller.set_channel, (0,  15)),
            (10848, tree_controller.set_channel, (1,  15)),
            (10848, tree_controller.set_channel, (2,  15)),
            (10848, tree_controller.set_channel, (3,  15)),
            (10858, tree_controller.set_channel, (0,  14)),
            (10858, tree_controller.set_channel, (1,  14)),
            (10858, tree_controller.set_channel, (2,  14)),
            (10858, tree_controller.set_channel, (3,  14)),
            (10868, tree_controller.set_channel, (0,  13)),
            (10868, tree_controller.set_channel, (1,  13)),
            (10868, tree_controller.set_channel, (2,  13)),
            (10868, tree_controller.set_channel, (3,  13)),
            (10878, tree_controller.set_channel, (0,  12)),
            (10878, tree_controller.set_channel, (1,  12)),
            (10878, tree_controller.set_channel, (2,  12)),
            (10878, tree_controller.set_channel, (3,  12)),
            (10888, tree_controller.set_channel, (0,  11)),
            (10888, tree_controller.set_channel, (1,  11)),
            (10888, tree_controller.set_channel, (2,  11)),
            (10888, tree_controller.set_channel, (3,  11)),
            (10898, tree_controller.set_channel, (0,  10)),
            (10898, tree_controller.set_channel, (1,  10)),
            (10898, tree_controller.set_channel, (2,  10)),
            (10898, tree_controller.set_channel, (3,  10)),
            (10909, tree_controller.set_channel, (0,   9)),
            (10909, tree_controller.set_channel, (1,   9)),
            (10909, tree_controller.set_channel, (2,   9)),
            (10909, tree_controller.set_channel, (3,   9)),
            (10919, tree_controller.set_channel, (0,   8)),
            (10919, tree_controller.set_channel, (1,   8)),
            (10919, tree_controller.set_channel, (2,   8)),
            (10919, tree_controller.set_channel, (3,   8)),
            (10929, tree_controller.set_channel, (0,   7)),
            (10929, tree_controller.set_channel, (1,   7)),
            (10929, tree_controller.set_channel, (2,   7)),
            (10929, tree_controller.set_channel, (3,   7)),
            (10939, tree_controller.set_channel, (0,   6)),
            (10939, tree_controller.set_channel, (1,   6)),
            (10939, tree_controller.set_channel, (2,   6)),
            (10939, tree_controller.set_channel, (3,   6)),
            (10949, tree_controller.set_channel, (0,   5)),
            (10949, tree_controller.set_channel, (1,   5)),
            (10949, tree_controller.set_channel, (2,   5)),
            (10949, tree_controller.set_channel, (3,   5)),
            (10959, tree_controller.set_channel, (0,   4)),
            (10959, tree_controller.set_channel, (1,   4)),
            (10959, tree_controller.set_channel, (2,   4)),
            (10959, tree_controller.set_channel, (3,   4)),
            (10969, tree_controller.set_channel, (0,   3)),
            (10969, tree_controller.set_channel, (1,   3)),
            (10969, tree_controller.set_channel, (2,   3)),
            (10969, tree_controller.set_channel, (3,   3)),
            (10979, tree_controller.set_channel, (0,   2)),
            (10979, tree_controller.set_channel, (1,   2)),
            (10979, tree_controller.set_channel, (2,   2)),
            (10979, tree_controller.set_channel, (3,   2)),
            (10989, tree_controller.set_channel, (0,   1)),
            (10989, tree_controller.set_channel, (1,   1)),
            (10989, tree_controller.set_channel, (2,   1)),
            (10989, tree_controller.set_channel, (3,   1)),
            (11000, tree_controller.set_channel, (0,   0)),
            (11000, tree_controller.set_channel, (1,   0)),
            (11000, tree_controller.set_channel, (2,   0)),
            (11000, tree_controller.set_channel, (3,   0)),
            (11000, floods_controller.set_channel,('C7', 0)),
        ]))

    def test_sequence_channel_types(self):
        '''Ensure that the channel names get converted to the proper 
        type for indices into the unit's channels array.  Different
        controller drivers use different types for these (string
        vs integer).'''
        # numeric channel numbers
        tree_controller = FireGodControllerUnit(
            'fg', PowerSource('ps1'), TestNetwork(),
            address=1, resolution=101, channels=32)
        tree_controller.add_channel(0, load=1)
        tree_controller.add_channel(1, load=1)
        tree_controller.add_channel(2, load=1)
        tree_controller.add_channel(3, load=1)

        # string channel names
        floods_controller = LynX10ControllerUnit(
            'lx', PowerSource('ps2'), TestNetwork(), resolution=16)
        floods_controller.add_channel('C7', load=1, warm=10, resolution=16)
        s = Sequence()
        s.load_file('data/testchannels.lseq', { 'floods': floods_controller, 'tree': tree_controller })
        self.assert_(type(s._event_list[0][0].channel) is str)
        self.assert_(type(s._event_list[1][0].channel) is int)
        self.assert_(type(s._event_list[2][0].channel) is int)
        self.assert_(type(s._event_list[3][0].channel) is int)

    def compare_timeline_lists(self, actual, expected):
        '''Given two lists of tuples, where the first element of
        the tuple is a timestamp, report on whether each list
        contains identical content, considering that for a
        given timestamp, there could be many entries with
        that timestamp, but could appear in random sequence
        (as can all the elements in the outer list).  We
        just want to be sure the contents are the same
        regardless of order of appearance.
        
        Returns boolean: True if comparison is successful,
        False otherwise (and prints detailed report in the
        failure case).'''

        # first, put them in order
        a = sorted(actual)
        e = sorted(expected)
        if len(a) != len(e):
            print "Actual data dumped to data/SequenceData.timeline."
            outf = file("data/SequenceData.timeline", "w")
            for ev in a:
                print >>outf, "%8d %-10s %s\n" % (ev[0], ev[2], ev[1])
            outf.close()
            print "TIMELINE MISMATCH: actual has %d elements vs. expected %d" % (len(a), len(e))
            return False

        result = True
        for i in range(len(a)):
            if a[i] != e[i]:
                print "TIMELINE MISMATCH: @%d: actual=%s, expected=%s" % (i, a[i], e[i])
                result = False

        return result

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
# 
# $Log: not supported by cvs2svn $
#
