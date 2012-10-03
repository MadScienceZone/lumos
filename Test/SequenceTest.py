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
        self.assertEqual(orig, newf, msg="data/test-cmp.lseq vs. data/test-out.lseq mismatch")

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
            address=1, resolution=101, num_channels=32)
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

        self.assertEqual(None, self.compare_timeline_lists(s.compile(), [
            (    0, tree_controller.all_channels_off, ()),       # == 0000 == all off
            (    0, floods_controller.all_channels_off, ()),
            ( 1000, tree_controller.set_channel, (0, 100, False)),      # == 1000 == 0=100
            ( 1000, floods_controller.set_channel, ('C7', 1, False)),   # C7 0->100% over 2000
            ( 1142, floods_controller.set_channel, ('C7', 2, False)),   #  (0-15, 15 steps, 1/133.33ms)
            ( 1285, floods_controller.set_channel, ('C7', 3, False)),
            ( 1428, floods_controller.set_channel, ('C7', 4, False)),
            ( 1571, floods_controller.set_channel, ('C7', 5, False)),
            ( 1714, floods_controller.set_channel, ('C7', 6, False)),
            ( 1857, floods_controller.set_channel, ('C7', 7, False)),
            ( 2000, tree_controller.set_channel, (0, 0, False)),        # == 2000 == 0=0
            ( 2000, tree_controller.set_channel, (1, 100, False)),      #            1=100
            ( 2000, floods_controller.set_channel, ('C7', 8, False)),
            ( 2142, floods_controller.set_channel, ('C7', 9, False)),
            ( 2285, floods_controller.set_channel, ('C7',10, False)),
            ( 2428, floods_controller.set_channel, ('C7',11, False)),
            ( 2571, floods_controller.set_channel, ('C7',12, False)),
            ( 2714, floods_controller.set_channel, ('C7',13, False)),
            ( 2857, floods_controller.set_channel, ('C7',14, False)),
            ( 3000, floods_controller.set_channel, ('C7',15, False)),
            ( 3000, tree_controller.set_channel, (1, 0, False)),        # == 3000 == 1=0, 2=100
            ( 3000, tree_controller.set_channel, (2, 100, False)),
            ( 4000, tree_controller.set_channel, (2, 0, False)),        # == 4000 == 2=0, 3=100
            ( 4000, tree_controller.set_channel, (3, 100, False)),
            ( 5000, tree_controller.set_channel, (0,   1, False)),      # == 5000 == 0=0->100 over 1000
            ( 5010, tree_controller.set_channel, (0,   2, False)),      # (100 steps, 1/10ms)
            ( 5020, tree_controller.set_channel, (0,   3, False)),
            ( 5030, tree_controller.set_channel, (0,   4, False)),
            ( 5040, tree_controller.set_channel, (0,   5, False)),
            ( 5050, tree_controller.set_channel, (0,   6, False)),
            ( 5060, tree_controller.set_channel, (0,   7, False)),
            ( 5070, tree_controller.set_channel, (0,   8, False)),
            ( 5080, tree_controller.set_channel, (0,   9, False)),
            ( 5090, tree_controller.set_channel, (0,  10, False)),
            ( 5101, tree_controller.set_channel, (0,  11, False)),
            ( 5111, tree_controller.set_channel, (0,  12, False)),
            ( 5121, tree_controller.set_channel, (0,  13, False)),
            ( 5131, tree_controller.set_channel, (0,  14, False)),
            ( 5141, tree_controller.set_channel, (0,  15, False)),
            ( 5151, tree_controller.set_channel, (0,  16, False)),
            ( 5161, tree_controller.set_channel, (0,  17, False)),
            ( 5171, tree_controller.set_channel, (0,  18, False)),
            ( 5181, tree_controller.set_channel, (0,  19, False)),
            ( 5191, tree_controller.set_channel, (0,  20, False)),
            ( 5202, tree_controller.set_channel, (0,  21, False)),
            ( 5212, tree_controller.set_channel, (0,  22, False)),
            ( 5222, tree_controller.set_channel, (0,  23, False)),
            ( 5232, tree_controller.set_channel, (0,  24, False)),
            ( 5242, tree_controller.set_channel, (0,  25, False)),
            ( 5252, tree_controller.set_channel, (0,  26, False)),
            ( 5262, tree_controller.set_channel, (0,  27, False)),
            ( 5272, tree_controller.set_channel, (0,  28, False)),
            ( 5282, tree_controller.set_channel, (0,  29, False)),
            ( 5292, tree_controller.set_channel, (0,  30, False)),
            ( 5303, tree_controller.set_channel, (0,  31, False)),
            ( 5313, tree_controller.set_channel, (0,  32, False)),
            ( 5323, tree_controller.set_channel, (0,  33, False)),
            ( 5333, tree_controller.set_channel, (0,  34, False)),
            ( 5343, tree_controller.set_channel, (0,  35, False)),
            ( 5353, tree_controller.set_channel, (0,  36, False)),
            ( 5363, tree_controller.set_channel, (0,  37, False)),
            ( 5373, tree_controller.set_channel, (0,  38, False)),
            ( 5383, tree_controller.set_channel, (0,  39, False)),
            ( 5393, tree_controller.set_channel, (0,  40, False)),
            ( 5404, tree_controller.set_channel, (0,  41, False)),
            ( 5414, tree_controller.set_channel, (0,  42, False)),
            ( 5424, tree_controller.set_channel, (0,  43, False)),
            ( 5434, tree_controller.set_channel, (0,  44, False)),
            ( 5444, tree_controller.set_channel, (0,  45, False)),
            ( 5454, tree_controller.set_channel, (0,  46, False)),
            ( 5464, tree_controller.set_channel, (0,  47, False)),
            ( 5474, tree_controller.set_channel, (0,  48, False)),
            ( 5484, tree_controller.set_channel, (0,  49, False)),
            ( 5494, tree_controller.set_channel, (0,  50, False)),
            ( 5505, tree_controller.set_channel, (0,  51, False)),
            ( 5515, tree_controller.set_channel, (0,  52, False)),
            ( 5525, tree_controller.set_channel, (0,  53, False)),
            ( 5535, tree_controller.set_channel, (0,  54, False)),
            ( 5545, tree_controller.set_channel, (0,  55, False)),
            ( 5555, tree_controller.set_channel, (0,  56, False)),
            ( 5565, tree_controller.set_channel, (0,  57, False)),
            ( 5575, tree_controller.set_channel, (0,  58, False)),
            ( 5585, tree_controller.set_channel, (0,  59, False)),
            ( 5595, tree_controller.set_channel, (0,  60, False)),
            ( 5606, tree_controller.set_channel, (0,  61, False)),
            ( 5616, tree_controller.set_channel, (0,  62, False)),
            ( 5626, tree_controller.set_channel, (0,  63, False)),
            ( 5636, tree_controller.set_channel, (0,  64, False)),
            ( 5646, tree_controller.set_channel, (0,  65, False)),
            ( 5656, tree_controller.set_channel, (0,  66, False)),
            ( 5666, tree_controller.set_channel, (0,  67, False)),
            ( 5676, tree_controller.set_channel, (0,  68, False)),
            ( 5686, tree_controller.set_channel, (0,  69, False)),
            ( 5696, tree_controller.set_channel, (0,  70, False)),
            ( 5707, tree_controller.set_channel, (0,  71, False)),
            ( 5717, tree_controller.set_channel, (0,  72, False)),
            ( 5727, tree_controller.set_channel, (0,  73, False)),
            ( 5737, tree_controller.set_channel, (0,  74, False)),
            ( 5747, tree_controller.set_channel, (0,  75, False)),
            ( 5757, tree_controller.set_channel, (0,  76, False)),
            ( 5767, tree_controller.set_channel, (0,  77, False)),
            ( 5777, tree_controller.set_channel, (0,  78, False)),
            ( 5787, tree_controller.set_channel, (0,  79, False)),
            ( 5797, tree_controller.set_channel, (0,  80, False)),
            ( 5808, tree_controller.set_channel, (0,  81, False)),
            ( 5818, tree_controller.set_channel, (0,  82, False)),
            ( 5828, tree_controller.set_channel, (0,  83, False)),
            ( 5838, tree_controller.set_channel, (0,  84, False)),
            ( 5848, tree_controller.set_channel, (0,  85, False)),
            ( 5858, tree_controller.set_channel, (0,  86, False)),
            ( 5868, tree_controller.set_channel, (0,  87, False)),
            ( 5878, tree_controller.set_channel, (0,  88, False)),
            ( 5888, tree_controller.set_channel, (0,  89, False)),
            ( 5898, tree_controller.set_channel, (0,  90, False)),
            ( 5909, tree_controller.set_channel, (0,  91, False)),
            ( 5919, tree_controller.set_channel, (0,  92, False)),
            ( 5929, tree_controller.set_channel, (0,  93, False)),
            ( 5939, tree_controller.set_channel, (0,  94, False)),
            ( 5949, tree_controller.set_channel, (0,  95, False)),
            ( 5959, tree_controller.set_channel, (0,  96, False)),
            ( 5969, tree_controller.set_channel, (0,  97, False)),
            ( 5979, tree_controller.set_channel, (0,  98, False)),
            ( 5989, tree_controller.set_channel, (0,  99, False)),
            ( 6000, tree_controller.set_channel, (0, 100, False)),
            ( 6000, tree_controller.set_channel, (1,   1, False)),      # == 6000 == 1=0->100 over 1000
            ( 6010, tree_controller.set_channel, (1,   2, False)),      # (100 steps, 1/10ms)
            ( 6020, tree_controller.set_channel, (1,   3, False)),
            ( 6030, tree_controller.set_channel, (1,   4, False)),
            ( 6040, tree_controller.set_channel, (1,   5, False)),
            ( 6050, tree_controller.set_channel, (1,   6, False)),
            ( 6060, tree_controller.set_channel, (1,   7, False)),
            ( 6070, tree_controller.set_channel, (1,   8, False)),
            ( 6080, tree_controller.set_channel, (1,   9, False)),
            ( 6090, tree_controller.set_channel, (1,  10, False)),
            ( 6101, tree_controller.set_channel, (1,  11, False)),
            ( 6111, tree_controller.set_channel, (1,  12, False)),
            ( 6121, tree_controller.set_channel, (1,  13, False)),
            ( 6131, tree_controller.set_channel, (1,  14, False)),
            ( 6141, tree_controller.set_channel, (1,  15, False)),
            ( 6151, tree_controller.set_channel, (1,  16, False)),
            ( 6161, tree_controller.set_channel, (1,  17, False)),
            ( 6171, tree_controller.set_channel, (1,  18, False)),
            ( 6181, tree_controller.set_channel, (1,  19, False)),
            ( 6191, tree_controller.set_channel, (1,  20, False)),
            ( 6202, tree_controller.set_channel, (1,  21, False)),
            ( 6212, tree_controller.set_channel, (1,  22, False)),
            ( 6222, tree_controller.set_channel, (1,  23, False)),
            ( 6232, tree_controller.set_channel, (1,  24, False)),
            ( 6242, tree_controller.set_channel, (1,  25, False)),
            ( 6252, tree_controller.set_channel, (1,  26, False)),
            ( 6262, tree_controller.set_channel, (1,  27, False)),
            ( 6272, tree_controller.set_channel, (1,  28, False)),
            ( 6282, tree_controller.set_channel, (1,  29, False)),
            ( 6292, tree_controller.set_channel, (1,  30, False)),
            ( 6303, tree_controller.set_channel, (1,  31, False)),
            ( 6313, tree_controller.set_channel, (1,  32, False)),
            ( 6323, tree_controller.set_channel, (1,  33, False)),
            ( 6333, tree_controller.set_channel, (1,  34, False)),
            ( 6343, tree_controller.set_channel, (1,  35, False)),
            ( 6353, tree_controller.set_channel, (1,  36, False)),
            ( 6363, tree_controller.set_channel, (1,  37, False)),
            ( 6373, tree_controller.set_channel, (1,  38, False)),
            ( 6383, tree_controller.set_channel, (1,  39, False)),
            ( 6393, tree_controller.set_channel, (1,  40, False)),
            ( 6404, tree_controller.set_channel, (1,  41, False)),
            ( 6414, tree_controller.set_channel, (1,  42, False)),
            ( 6424, tree_controller.set_channel, (1,  43, False)),
            ( 6434, tree_controller.set_channel, (1,  44, False)),
            ( 6444, tree_controller.set_channel, (1,  45, False)),
            ( 6454, tree_controller.set_channel, (1,  46, False)),
            ( 6464, tree_controller.set_channel, (1,  47, False)),
            ( 6474, tree_controller.set_channel, (1,  48, False)),
            ( 6484, tree_controller.set_channel, (1,  49, False)),
            ( 6494, tree_controller.set_channel, (1,  50, False)),
            ( 6505, tree_controller.set_channel, (1,  51, False)),
            ( 6515, tree_controller.set_channel, (1,  52, False)),
            ( 6525, tree_controller.set_channel, (1,  53, False)),
            ( 6535, tree_controller.set_channel, (1,  54, False)),
            ( 6545, tree_controller.set_channel, (1,  55, False)),
            ( 6555, tree_controller.set_channel, (1,  56, False)),
            ( 6565, tree_controller.set_channel, (1,  57, False)),
            ( 6575, tree_controller.set_channel, (1,  58, False)),
            ( 6585, tree_controller.set_channel, (1,  59, False)),
            ( 6595, tree_controller.set_channel, (1,  60, False)),
            ( 6606, tree_controller.set_channel, (1,  61, False)),
            ( 6616, tree_controller.set_channel, (1,  62, False)),
            ( 6626, tree_controller.set_channel, (1,  63, False)),
            ( 6636, tree_controller.set_channel, (1,  64, False)),
            ( 6646, tree_controller.set_channel, (1,  65, False)),
            ( 6656, tree_controller.set_channel, (1,  66, False)),
            ( 6666, tree_controller.set_channel, (1,  67, False)),
            ( 6676, tree_controller.set_channel, (1,  68, False)),
            ( 6686, tree_controller.set_channel, (1,  69, False)),
            ( 6696, tree_controller.set_channel, (1,  70, False)),
            ( 6707, tree_controller.set_channel, (1,  71, False)),
            ( 6717, tree_controller.set_channel, (1,  72, False)),
            ( 6727, tree_controller.set_channel, (1,  73, False)),
            ( 6737, tree_controller.set_channel, (1,  74, False)),
            ( 6747, tree_controller.set_channel, (1,  75, False)),
            ( 6757, tree_controller.set_channel, (1,  76, False)),
            ( 6767, tree_controller.set_channel, (1,  77, False)),
            ( 6777, tree_controller.set_channel, (1,  78, False)),
            ( 6787, tree_controller.set_channel, (1,  79, False)),
            ( 6797, tree_controller.set_channel, (1,  80, False)),
            ( 6808, tree_controller.set_channel, (1,  81, False)),
            ( 6818, tree_controller.set_channel, (1,  82, False)),
            ( 6828, tree_controller.set_channel, (1,  83, False)),
            ( 6838, tree_controller.set_channel, (1,  84, False)),
            ( 6848, tree_controller.set_channel, (1,  85, False)),
            ( 6858, tree_controller.set_channel, (1,  86, False)),
            ( 6868, tree_controller.set_channel, (1,  87, False)),
            ( 6878, tree_controller.set_channel, (1,  88, False)),
            ( 6888, tree_controller.set_channel, (1,  89, False)),
            ( 6898, tree_controller.set_channel, (1,  90, False)),
            ( 6909, tree_controller.set_channel, (1,  91, False)),
            ( 6919, tree_controller.set_channel, (1,  92, False)),
            ( 6929, tree_controller.set_channel, (1,  93, False)),
            ( 6939, tree_controller.set_channel, (1,  94, False)),
            ( 6949, tree_controller.set_channel, (1,  95, False)),
            ( 6959, tree_controller.set_channel, (1,  96, False)),
            ( 6969, tree_controller.set_channel, (1,  97, False)),
            ( 6979, tree_controller.set_channel, (1,  98, False)),
            ( 6989, tree_controller.set_channel, (1,  99, False)),
            ( 7000, tree_controller.set_channel, (1, 100, False)),
            ( 7000, floods_controller.set_channel, ('C7', 7, False)), # == 7000 == C7=50
            ( 7000, tree_controller.set_channel, (2,   1, False)),    # == 7000 == 2=0->100 over 1000
            ( 7010, tree_controller.set_channel, (2,   2, False)),      # (100 steps, 1/10ms)
            ( 7020, tree_controller.set_channel, (2,   3, False)),
            ( 7030, tree_controller.set_channel, (2,   4, False)),
            ( 7040, tree_controller.set_channel, (2,   5, False)),
            ( 7050, tree_controller.set_channel, (2,   6, False)),
            ( 7060, tree_controller.set_channel, (2,   7, False)),
            ( 7070, tree_controller.set_channel, (2,   8, False)),
            ( 7080, tree_controller.set_channel, (2,   9, False)),
            ( 7090, tree_controller.set_channel, (2,  10, False)),
            ( 7101, tree_controller.set_channel, (2,  11, False)),
            ( 7111, tree_controller.set_channel, (2,  12, False)),
            ( 7121, tree_controller.set_channel, (2,  13, False)),
            ( 7131, tree_controller.set_channel, (2,  14, False)),
            ( 7141, tree_controller.set_channel, (2,  15, False)),
            ( 7151, tree_controller.set_channel, (2,  16, False)),
            ( 7161, tree_controller.set_channel, (2,  17, False)),
            ( 7171, tree_controller.set_channel, (2,  18, False)),
            ( 7181, tree_controller.set_channel, (2,  19, False)),
            ( 7191, tree_controller.set_channel, (2,  20, False)),
            ( 7202, tree_controller.set_channel, (2,  21, False)),
            ( 7212, tree_controller.set_channel, (2,  22, False)),
            ( 7222, tree_controller.set_channel, (2,  23, False)),
            ( 7232, tree_controller.set_channel, (2,  24, False)),
            ( 7242, tree_controller.set_channel, (2,  25, False)),
            ( 7252, tree_controller.set_channel, (2,  26, False)),
            ( 7262, tree_controller.set_channel, (2,  27, False)),
            ( 7272, tree_controller.set_channel, (2,  28, False)),
            ( 7282, tree_controller.set_channel, (2,  29, False)),
            ( 7292, tree_controller.set_channel, (2,  30, False)),
            ( 7303, tree_controller.set_channel, (2,  31, False)),
            ( 7313, tree_controller.set_channel, (2,  32, False)),
            ( 7323, tree_controller.set_channel, (2,  33, False)),
            ( 7333, tree_controller.set_channel, (2,  34, False)),
            ( 7343, tree_controller.set_channel, (2,  35, False)),
            ( 7353, tree_controller.set_channel, (2,  36, False)),
            ( 7363, tree_controller.set_channel, (2,  37, False)),
            ( 7373, tree_controller.set_channel, (2,  38, False)),
            ( 7383, tree_controller.set_channel, (2,  39, False)),
            ( 7393, tree_controller.set_channel, (2,  40, False)),
            ( 7404, tree_controller.set_channel, (2,  41, False)),
            ( 7414, tree_controller.set_channel, (2,  42, False)),
            ( 7424, tree_controller.set_channel, (2,  43, False)),
            ( 7434, tree_controller.set_channel, (2,  44, False)),
            ( 7444, tree_controller.set_channel, (2,  45, False)),
            ( 7454, tree_controller.set_channel, (2,  46, False)),
            ( 7464, tree_controller.set_channel, (2,  47, False)),
            ( 7474, tree_controller.set_channel, (2,  48, False)),
            ( 7484, tree_controller.set_channel, (2,  49, False)),
            ( 7494, tree_controller.set_channel, (2,  50, False)),
            ( 7505, tree_controller.set_channel, (2,  51, False)),
            ( 7515, tree_controller.set_channel, (2,  52, False)),
            ( 7525, tree_controller.set_channel, (2,  53, False)),
            ( 7535, tree_controller.set_channel, (2,  54, False)),
            ( 7545, tree_controller.set_channel, (2,  55, False)),
            ( 7555, tree_controller.set_channel, (2,  56, False)),
            ( 7565, tree_controller.set_channel, (2,  57, False)),
            ( 7575, tree_controller.set_channel, (2,  58, False)),
            ( 7585, tree_controller.set_channel, (2,  59, False)),
            ( 7595, tree_controller.set_channel, (2,  60, False)),
            ( 7606, tree_controller.set_channel, (2,  61, False)),
            ( 7616, tree_controller.set_channel, (2,  62, False)),
            ( 7626, tree_controller.set_channel, (2,  63, False)),
            ( 7636, tree_controller.set_channel, (2,  64, False)),
            ( 7646, tree_controller.set_channel, (2,  65, False)),
            ( 7656, tree_controller.set_channel, (2,  66, False)),
            ( 7666, tree_controller.set_channel, (2,  67, False)),
            ( 7676, tree_controller.set_channel, (2,  68, False)),
            ( 7686, tree_controller.set_channel, (2,  69, False)),
            ( 7696, tree_controller.set_channel, (2,  70, False)),
            ( 7707, tree_controller.set_channel, (2,  71, False)),
            ( 7717, tree_controller.set_channel, (2,  72, False)),
            ( 7727, tree_controller.set_channel, (2,  73, False)),
            ( 7737, tree_controller.set_channel, (2,  74, False)),
            ( 7747, tree_controller.set_channel, (2,  75, False)),
            ( 7757, tree_controller.set_channel, (2,  76, False)),
            ( 7767, tree_controller.set_channel, (2,  77, False)),
            ( 7777, tree_controller.set_channel, (2,  78, False)),
            ( 7787, tree_controller.set_channel, (2,  79, False)),
            ( 7797, tree_controller.set_channel, (2,  80, False)),
            ( 7808, tree_controller.set_channel, (2,  81, False)),
            ( 7818, tree_controller.set_channel, (2,  82, False)),
            ( 7828, tree_controller.set_channel, (2,  83, False)),
            ( 7838, tree_controller.set_channel, (2,  84, False)),
            ( 7848, tree_controller.set_channel, (2,  85, False)),
            ( 7858, tree_controller.set_channel, (2,  86, False)),
            ( 7868, tree_controller.set_channel, (2,  87, False)),
            ( 7878, tree_controller.set_channel, (2,  88, False)),
            ( 7888, tree_controller.set_channel, (2,  89, False)),
            ( 7898, tree_controller.set_channel, (2,  90, False)),
            ( 7909, tree_controller.set_channel, (2,  91, False)),
            ( 7919, tree_controller.set_channel, (2,  92, False)),
            ( 7929, tree_controller.set_channel, (2,  93, False)),
            ( 7939, tree_controller.set_channel, (2,  94, False)),
            ( 7949, tree_controller.set_channel, (2,  95, False)),
            ( 7959, tree_controller.set_channel, (2,  96, False)),
            ( 7969, tree_controller.set_channel, (2,  97, False)),
            ( 7979, tree_controller.set_channel, (2,  98, False)),
            ( 7989, tree_controller.set_channel, (2,  99, False)),
            ( 8000, tree_controller.set_channel, (2, 100, False)),
                  # == 8000 == 3=100->100 over 1000
                  # already there, so we should not
                  # emit any change events here
            # == 10000 == all fade -> 0 over 1000ms
            # C7 6->0 over 1000ms  
            # 0,1,2,3 99->0 over 1000ms
            (10000, tree_controller.set_channel, (0,  99, False)),
            (10000, tree_controller.set_channel, (1,  99, False)),
            (10000, tree_controller.set_channel, (2,  99, False)),
            (10000, tree_controller.set_channel, (3,  99, False)),
            (10000, floods_controller.set_channel,('C7', 6, False)),
            (10010, tree_controller.set_channel, (0,  98, False)),
            (10010, tree_controller.set_channel, (1,  98, False)),
            (10010, tree_controller.set_channel, (2,  98, False)),
            (10010, tree_controller.set_channel, (3,  98, False)),
            (10020, tree_controller.set_channel, (0,  97, False)),
            (10020, tree_controller.set_channel, (1,  97, False)),
            (10020, tree_controller.set_channel, (2,  97, False)),
            (10020, tree_controller.set_channel, (3,  97, False)),
            (10030, tree_controller.set_channel, (0,  96, False)),
            (10030, tree_controller.set_channel, (1,  96, False)),
            (10030, tree_controller.set_channel, (2,  96, False)),
            (10030, tree_controller.set_channel, (3,  96, False)),
            (10040, tree_controller.set_channel, (0,  95, False)),
            (10040, tree_controller.set_channel, (1,  95, False)),
            (10040, tree_controller.set_channel, (2,  95, False)),
            (10040, tree_controller.set_channel, (3,  95, False)),
            (10050, tree_controller.set_channel, (0,  94, False)),
            (10050, tree_controller.set_channel, (1,  94, False)),
            (10050, tree_controller.set_channel, (2,  94, False)),
            (10050, tree_controller.set_channel, (3,  94, False)),
            (10060, tree_controller.set_channel, (0,  93, False)),
            (10060, tree_controller.set_channel, (1,  93, False)),
            (10060, tree_controller.set_channel, (2,  93, False)),
            (10060, tree_controller.set_channel, (3,  93, False)),
            (10070, tree_controller.set_channel, (0,  92, False)),
            (10070, tree_controller.set_channel, (1,  92, False)),
            (10070, tree_controller.set_channel, (2,  92, False)),
            (10070, tree_controller.set_channel, (3,  92, False)),
            (10080, tree_controller.set_channel, (0,  91, False)),
            (10080, tree_controller.set_channel, (1,  91, False)),
            (10080, tree_controller.set_channel, (2,  91, False)),
            (10080, tree_controller.set_channel, (3,  91, False)),
            (10090, tree_controller.set_channel, (0,  90, False)),
            (10090, tree_controller.set_channel, (1,  90, False)),
            (10090, tree_controller.set_channel, (2,  90, False)),
            (10090, tree_controller.set_channel, (3,  90, False)),
            (10101, tree_controller.set_channel, (0,  89, False)),
            (10101, tree_controller.set_channel, (1,  89, False)),
            (10101, tree_controller.set_channel, (2,  89, False)),
            (10101, tree_controller.set_channel, (3,  89, False)),
            (10111, tree_controller.set_channel, (0,  88, False)),
            (10111, tree_controller.set_channel, (1,  88, False)),
            (10111, tree_controller.set_channel, (2,  88, False)),
            (10111, tree_controller.set_channel, (3,  88, False)),
            (10121, tree_controller.set_channel, (0,  87, False)),
            (10121, tree_controller.set_channel, (1,  87, False)),
            (10121, tree_controller.set_channel, (2,  87, False)),
            (10121, tree_controller.set_channel, (3,  87, False)),
            (10131, tree_controller.set_channel, (0,  86, False)),
            (10131, tree_controller.set_channel, (1,  86, False)),
            (10131, tree_controller.set_channel, (2,  86, False)),
            (10131, tree_controller.set_channel, (3,  86, False)),
            (10141, tree_controller.set_channel, (0,  85, False)),
            (10141, tree_controller.set_channel, (1,  85, False)),
            (10141, tree_controller.set_channel, (2,  85, False)),
            (10141, tree_controller.set_channel, (3,  85, False)),
            (10151, tree_controller.set_channel, (0,  84, False)),
            (10151, tree_controller.set_channel, (1,  84, False)),
            (10151, tree_controller.set_channel, (2,  84, False)),
            (10151, tree_controller.set_channel, (3,  84, False)),
            (10161, tree_controller.set_channel, (0,  83, False)),
            (10161, tree_controller.set_channel, (1,  83, False)),
            (10161, tree_controller.set_channel, (2,  83, False)),
            (10161, tree_controller.set_channel, (3,  83, False)),
            (10166, floods_controller.set_channel,('C7', 5, False)),
            (10171, tree_controller.set_channel, (0,  82, False)),
            (10171, tree_controller.set_channel, (1,  82, False)),
            (10171, tree_controller.set_channel, (2,  82, False)),
            (10171, tree_controller.set_channel, (3,  82, False)),
            (10181, tree_controller.set_channel, (0,  81, False)),
            (10181, tree_controller.set_channel, (1,  81, False)),
            (10181, tree_controller.set_channel, (2,  81, False)),
            (10181, tree_controller.set_channel, (3,  81, False)),
            (10191, tree_controller.set_channel, (0,  80, False)),
            (10191, tree_controller.set_channel, (1,  80, False)),
            (10191, tree_controller.set_channel, (2,  80, False)),
            (10191, tree_controller.set_channel, (3,  80, False)),
            (10202, tree_controller.set_channel, (0,  79, False)),
            (10202, tree_controller.set_channel, (1,  79, False)),
            (10202, tree_controller.set_channel, (2,  79, False)),
            (10202, tree_controller.set_channel, (3,  79, False)),
            (10212, tree_controller.set_channel, (0,  78, False)),
            (10212, tree_controller.set_channel, (1,  78, False)),
            (10212, tree_controller.set_channel, (2,  78, False)),
            (10212, tree_controller.set_channel, (3,  78, False)),
            (10222, tree_controller.set_channel, (0,  77, False)),
            (10222, tree_controller.set_channel, (1,  77, False)),
            (10222, tree_controller.set_channel, (2,  77, False)),
            (10222, tree_controller.set_channel, (3,  77, False)),
            (10232, tree_controller.set_channel, (0,  76, False)),
            (10232, tree_controller.set_channel, (1,  76, False)),
            (10232, tree_controller.set_channel, (2,  76, False)),
            (10232, tree_controller.set_channel, (3,  76, False)),
            (10242, tree_controller.set_channel, (0,  75, False)),
            (10242, tree_controller.set_channel, (1,  75, False)),
            (10242, tree_controller.set_channel, (2,  75, False)),
            (10242, tree_controller.set_channel, (3,  75, False)),
            (10252, tree_controller.set_channel, (0,  74, False)),
            (10252, tree_controller.set_channel, (1,  74, False)),
            (10252, tree_controller.set_channel, (2,  74, False)),
            (10252, tree_controller.set_channel, (3,  74, False)),
            (10262, tree_controller.set_channel, (0,  73, False)),
            (10262, tree_controller.set_channel, (1,  73, False)),
            (10262, tree_controller.set_channel, (2,  73, False)),
            (10262, tree_controller.set_channel, (3,  73, False)),
            (10272, tree_controller.set_channel, (0,  72, False)),
            (10272, tree_controller.set_channel, (1,  72, False)),
            (10272, tree_controller.set_channel, (2,  72, False)),
            (10272, tree_controller.set_channel, (3,  72, False)),
            (10282, tree_controller.set_channel, (0,  71, False)),
            (10282, tree_controller.set_channel, (1,  71, False)),
            (10282, tree_controller.set_channel, (2,  71, False)),
            (10282, tree_controller.set_channel, (3,  71, False)),
            (10292, tree_controller.set_channel, (0,  70, False)),
            (10292, tree_controller.set_channel, (1,  70, False)),
            (10292, tree_controller.set_channel, (2,  70, False)),
            (10292, tree_controller.set_channel, (3,  70, False)),
            (10303, tree_controller.set_channel, (0,  69, False)),
            (10303, tree_controller.set_channel, (1,  69, False)),
            (10303, tree_controller.set_channel, (2,  69, False)),
            (10303, tree_controller.set_channel, (3,  69, False)),
            (10313, tree_controller.set_channel, (0,  68, False)),
            (10313, tree_controller.set_channel, (1,  68, False)),
            (10313, tree_controller.set_channel, (2,  68, False)),
            (10313, tree_controller.set_channel, (3,  68, False)),
            (10323, tree_controller.set_channel, (0,  67, False)),
            (10323, tree_controller.set_channel, (1,  67, False)),
            (10323, tree_controller.set_channel, (2,  67, False)),
            (10323, tree_controller.set_channel, (3,  67, False)),
            (10333, tree_controller.set_channel, (0,  66, False)),
            (10333, tree_controller.set_channel, (1,  66, False)),
            (10333, tree_controller.set_channel, (2,  66, False)),
            (10333, tree_controller.set_channel, (3,  66, False)),
            (10333, floods_controller.set_channel,('C7', 4, False)),
            (10343, tree_controller.set_channel, (0,  65, False)),
            (10343, tree_controller.set_channel, (1,  65, False)),
            (10343, tree_controller.set_channel, (2,  65, False)),
            (10343, tree_controller.set_channel, (3,  65, False)),
            (10353, tree_controller.set_channel, (0,  64, False)),
            (10353, tree_controller.set_channel, (1,  64, False)),
            (10353, tree_controller.set_channel, (2,  64, False)),
            (10353, tree_controller.set_channel, (3,  64, False)),
            (10363, tree_controller.set_channel, (0,  63, False)),
            (10363, tree_controller.set_channel, (1,  63, False)),
            (10363, tree_controller.set_channel, (2,  63, False)),
            (10363, tree_controller.set_channel, (3,  63, False)),
            (10373, tree_controller.set_channel, (0,  62, False)),
            (10373, tree_controller.set_channel, (1,  62, False)),
            (10373, tree_controller.set_channel, (2,  62, False)),
            (10373, tree_controller.set_channel, (3,  62, False)),
            (10383, tree_controller.set_channel, (0,  61, False)),
            (10383, tree_controller.set_channel, (1,  61, False)),
            (10383, tree_controller.set_channel, (2,  61, False)),
            (10383, tree_controller.set_channel, (3,  61, False)),
            (10393, tree_controller.set_channel, (0,  60, False)),
            (10393, tree_controller.set_channel, (1,  60, False)),
            (10393, tree_controller.set_channel, (2,  60, False)),
            (10393, tree_controller.set_channel, (3,  60, False)),
            (10404, tree_controller.set_channel, (0,  59, False)),
            (10404, tree_controller.set_channel, (1,  59, False)),
            (10404, tree_controller.set_channel, (2,  59, False)),
            (10404, tree_controller.set_channel, (3,  59, False)),
            (10414, tree_controller.set_channel, (0,  58, False)),
            (10414, tree_controller.set_channel, (1,  58, False)),
            (10414, tree_controller.set_channel, (2,  58, False)),
            (10414, tree_controller.set_channel, (3,  58, False)),
            (10424, tree_controller.set_channel, (0,  57, False)),
            (10424, tree_controller.set_channel, (1,  57, False)),
            (10424, tree_controller.set_channel, (2,  57, False)),
            (10424, tree_controller.set_channel, (3,  57, False)),
            (10434, tree_controller.set_channel, (0,  56, False)),
            (10434, tree_controller.set_channel, (1,  56, False)),
            (10434, tree_controller.set_channel, (2,  56, False)),
            (10434, tree_controller.set_channel, (3,  56, False)),
            (10444, tree_controller.set_channel, (0,  55, False)),
            (10444, tree_controller.set_channel, (1,  55, False)),
            (10444, tree_controller.set_channel, (2,  55, False)),
            (10444, tree_controller.set_channel, (3,  55, False)),
            (10454, tree_controller.set_channel, (0,  54, False)),
            (10454, tree_controller.set_channel, (1,  54, False)),
            (10454, tree_controller.set_channel, (2,  54, False)),
            (10454, tree_controller.set_channel, (3,  54, False)),
            (10464, tree_controller.set_channel, (0,  53, False)),
            (10464, tree_controller.set_channel, (1,  53, False)),
            (10464, tree_controller.set_channel, (2,  53, False)),
            (10464, tree_controller.set_channel, (3,  53, False)),
            (10474, tree_controller.set_channel, (0,  52, False)),
            (10474, tree_controller.set_channel, (1,  52, False)),
            (10474, tree_controller.set_channel, (2,  52, False)),
            (10474, tree_controller.set_channel, (3,  52, False)),
            (10484, tree_controller.set_channel, (0,  51, False)),
            (10484, tree_controller.set_channel, (1,  51, False)),
            (10484, tree_controller.set_channel, (2,  51, False)),
            (10484, tree_controller.set_channel, (3,  51, False)),
            (10494, tree_controller.set_channel, (0,  50, False)),
            (10494, tree_controller.set_channel, (1,  50, False)),
            (10494, tree_controller.set_channel, (2,  50, False)),
            (10494, tree_controller.set_channel, (3,  50, False)),
            (10500, floods_controller.set_channel,('C7', 3, False)),
            (10505, tree_controller.set_channel, (0,  49, False)),
            (10505, tree_controller.set_channel, (1,  49, False)),
            (10505, tree_controller.set_channel, (2,  49, False)),
            (10505, tree_controller.set_channel, (3,  49, False)),
            (10515, tree_controller.set_channel, (0,  48, False)),
            (10515, tree_controller.set_channel, (1,  48, False)),
            (10515, tree_controller.set_channel, (2,  48, False)),
            (10515, tree_controller.set_channel, (3,  48, False)),
            (10525, tree_controller.set_channel, (0,  47, False)),
            (10525, tree_controller.set_channel, (1,  47, False)),
            (10525, tree_controller.set_channel, (2,  47, False)),
            (10525, tree_controller.set_channel, (3,  47, False)),
            (10535, tree_controller.set_channel, (0,  46, False)),
            (10535, tree_controller.set_channel, (1,  46, False)),
            (10535, tree_controller.set_channel, (2,  46, False)),
            (10535, tree_controller.set_channel, (3,  46, False)),
            (10545, tree_controller.set_channel, (0,  45, False)),
            (10545, tree_controller.set_channel, (1,  45, False)),
            (10545, tree_controller.set_channel, (2,  45, False)),
            (10545, tree_controller.set_channel, (3,  45, False)),
            (10555, tree_controller.set_channel, (0,  44, False)),
            (10555, tree_controller.set_channel, (1,  44, False)),
            (10555, tree_controller.set_channel, (2,  44, False)),
            (10555, tree_controller.set_channel, (3,  44, False)),
            (10565, tree_controller.set_channel, (0,  43, False)),
            (10565, tree_controller.set_channel, (1,  43, False)),
            (10565, tree_controller.set_channel, (2,  43, False)),
            (10565, tree_controller.set_channel, (3,  43, False)),
            (10575, tree_controller.set_channel, (0,  42, False)),
            (10575, tree_controller.set_channel, (1,  42, False)),
            (10575, tree_controller.set_channel, (2,  42, False)),
            (10575, tree_controller.set_channel, (3,  42, False)),
            (10585, tree_controller.set_channel, (0,  41, False)),
            (10585, tree_controller.set_channel, (1,  41, False)),
            (10585, tree_controller.set_channel, (2,  41, False)),
            (10585, tree_controller.set_channel, (3,  41, False)),
            (10595, tree_controller.set_channel, (0,  40, False)),
            (10595, tree_controller.set_channel, (1,  40, False)),
            (10595, tree_controller.set_channel, (2,  40, False)),
            (10595, tree_controller.set_channel, (3,  40, False)),
            (10606, tree_controller.set_channel, (0,  39, False)),
            (10606, tree_controller.set_channel, (1,  39, False)),
            (10606, tree_controller.set_channel, (2,  39, False)),
            (10606, tree_controller.set_channel, (3,  39, False)),
            (10616, tree_controller.set_channel, (0,  38, False)),
            (10616, tree_controller.set_channel, (1,  38, False)),
            (10616, tree_controller.set_channel, (2,  38, False)),
            (10616, tree_controller.set_channel, (3,  38, False)),
            (10626, tree_controller.set_channel, (0,  37, False)),
            (10626, tree_controller.set_channel, (1,  37, False)),
            (10626, tree_controller.set_channel, (2,  37, False)),
            (10626, tree_controller.set_channel, (3,  37, False)),
            (10636, tree_controller.set_channel, (0,  36, False)),
            (10636, tree_controller.set_channel, (1,  36, False)),
            (10636, tree_controller.set_channel, (2,  36, False)),
            (10636, tree_controller.set_channel, (3,  36, False)),
            (10646, tree_controller.set_channel, (0,  35, False)),
            (10646, tree_controller.set_channel, (1,  35, False)),
            (10646, tree_controller.set_channel, (2,  35, False)),
            (10646, tree_controller.set_channel, (3,  35, False)),
            (10656, tree_controller.set_channel, (0,  34, False)),
            (10656, tree_controller.set_channel, (1,  34, False)),
            (10656, tree_controller.set_channel, (2,  34, False)),
            (10656, tree_controller.set_channel, (3,  34, False)),
            (10666, tree_controller.set_channel, (0,  33, False)),
            (10666, tree_controller.set_channel, (1,  33, False)),
            (10666, tree_controller.set_channel, (2,  33, False)),
            (10666, tree_controller.set_channel, (3,  33, False)),
            (10666, floods_controller.set_channel,('C7', 2, False)),
            (10676, tree_controller.set_channel, (0,  32, False)),
            (10676, tree_controller.set_channel, (1,  32, False)),
            (10676, tree_controller.set_channel, (2,  32, False)),
            (10676, tree_controller.set_channel, (3,  32, False)),
            (10686, tree_controller.set_channel, (0,  31, False)),
            (10686, tree_controller.set_channel, (1,  31, False)),
            (10686, tree_controller.set_channel, (2,  31, False)),
            (10686, tree_controller.set_channel, (3,  31, False)),
            (10696, tree_controller.set_channel, (0,  30, False)),
            (10696, tree_controller.set_channel, (1,  30, False)),
            (10696, tree_controller.set_channel, (2,  30, False)),
            (10696, tree_controller.set_channel, (3,  30, False)),
            (10707, tree_controller.set_channel, (0,  29, False)),
            (10707, tree_controller.set_channel, (1,  29, False)),
            (10707, tree_controller.set_channel, (2,  29, False)),
            (10707, tree_controller.set_channel, (3,  29, False)),
            (10717, tree_controller.set_channel, (0,  28, False)),
            (10717, tree_controller.set_channel, (1,  28, False)),
            (10717, tree_controller.set_channel, (2,  28, False)),
            (10717, tree_controller.set_channel, (3,  28, False)),
            (10727, tree_controller.set_channel, (0,  27, False)),
            (10727, tree_controller.set_channel, (1,  27, False)),
            (10727, tree_controller.set_channel, (2,  27, False)),
            (10727, tree_controller.set_channel, (3,  27, False)),
            (10737, tree_controller.set_channel, (0,  26, False)),
            (10737, tree_controller.set_channel, (1,  26, False)),
            (10737, tree_controller.set_channel, (2,  26, False)),
            (10737, tree_controller.set_channel, (3,  26, False)),
            (10747, tree_controller.set_channel, (0,  25, False)),
            (10747, tree_controller.set_channel, (1,  25, False)),
            (10747, tree_controller.set_channel, (2,  25, False)),
            (10747, tree_controller.set_channel, (3,  25, False)),
            (10757, tree_controller.set_channel, (0,  24, False)),
            (10757, tree_controller.set_channel, (1,  24, False)),
            (10757, tree_controller.set_channel, (2,  24, False)),
            (10757, tree_controller.set_channel, (3,  24, False)),
            (10767, tree_controller.set_channel, (0,  23, False)),
            (10767, tree_controller.set_channel, (1,  23, False)),
            (10767, tree_controller.set_channel, (2,  23, False)),
            (10767, tree_controller.set_channel, (3,  23, False)),
            (10777, tree_controller.set_channel, (0,  22, False)),
            (10777, tree_controller.set_channel, (1,  22, False)),
            (10777, tree_controller.set_channel, (2,  22, False)),
            (10777, tree_controller.set_channel, (3,  22, False)),
            (10787, tree_controller.set_channel, (0,  21, False)),
            (10787, tree_controller.set_channel, (1,  21, False)),
            (10787, tree_controller.set_channel, (2,  21, False)),
            (10787, tree_controller.set_channel, (3,  21, False)),
            (10797, tree_controller.set_channel, (0,  20, False)),
            (10797, tree_controller.set_channel, (1,  20, False)),
            (10797, tree_controller.set_channel, (2,  20, False)),
            (10797, tree_controller.set_channel, (3,  20, False)),
            (10808, tree_controller.set_channel, (0,  19, False)),
            (10808, tree_controller.set_channel, (1,  19, False)),
            (10808, tree_controller.set_channel, (2,  19, False)),
            (10808, tree_controller.set_channel, (3,  19, False)),
            (10818, tree_controller.set_channel, (0,  18, False)),
            (10818, tree_controller.set_channel, (1,  18, False)),
            (10818, tree_controller.set_channel, (2,  18, False)),
            (10818, tree_controller.set_channel, (3,  18, False)),
            (10828, tree_controller.set_channel, (0,  17, False)),
            (10828, tree_controller.set_channel, (1,  17, False)),
            (10828, tree_controller.set_channel, (2,  17, False)),
            (10828, tree_controller.set_channel, (3,  17, False)),
            (10833, floods_controller.set_channel,('C7', 1, False)),
            (10838, tree_controller.set_channel, (0,  16, False)),
            (10838, tree_controller.set_channel, (1,  16, False)),
            (10838, tree_controller.set_channel, (2,  16, False)),
            (10838, tree_controller.set_channel, (3,  16, False)),
            (10848, tree_controller.set_channel, (0,  15, False)),
            (10848, tree_controller.set_channel, (1,  15, False)),
            (10848, tree_controller.set_channel, (2,  15, False)),
            (10848, tree_controller.set_channel, (3,  15, False)),
            (10858, tree_controller.set_channel, (0,  14, False)),
            (10858, tree_controller.set_channel, (1,  14, False)),
            (10858, tree_controller.set_channel, (2,  14, False)),
            (10858, tree_controller.set_channel, (3,  14, False)),
            (10868, tree_controller.set_channel, (0,  13, False)),
            (10868, tree_controller.set_channel, (1,  13, False)),
            (10868, tree_controller.set_channel, (2,  13, False)),
            (10868, tree_controller.set_channel, (3,  13, False)),
            (10878, tree_controller.set_channel, (0,  12, False)),
            (10878, tree_controller.set_channel, (1,  12, False)),
            (10878, tree_controller.set_channel, (2,  12, False)),
            (10878, tree_controller.set_channel, (3,  12, False)),
            (10888, tree_controller.set_channel, (0,  11, False)),
            (10888, tree_controller.set_channel, (1,  11, False)),
            (10888, tree_controller.set_channel, (2,  11, False)),
            (10888, tree_controller.set_channel, (3,  11, False)),
            (10898, tree_controller.set_channel, (0,  10, False)),
            (10898, tree_controller.set_channel, (1,  10, False)),
            (10898, tree_controller.set_channel, (2,  10, False)),
            (10898, tree_controller.set_channel, (3,  10, False)),
            (10909, tree_controller.set_channel, (0,   9, False)),
            (10909, tree_controller.set_channel, (1,   9, False)),
            (10909, tree_controller.set_channel, (2,   9, False)),
            (10909, tree_controller.set_channel, (3,   9, False)),
            (10919, tree_controller.set_channel, (0,   8, False)),
            (10919, tree_controller.set_channel, (1,   8, False)),
            (10919, tree_controller.set_channel, (2,   8, False)),
            (10919, tree_controller.set_channel, (3,   8, False)),
            (10929, tree_controller.set_channel, (0,   7, False)),
            (10929, tree_controller.set_channel, (1,   7, False)),
            (10929, tree_controller.set_channel, (2,   7, False)),
            (10929, tree_controller.set_channel, (3,   7, False)),
            (10939, tree_controller.set_channel, (0,   6, False)),
            (10939, tree_controller.set_channel, (1,   6, False)),
            (10939, tree_controller.set_channel, (2,   6, False)),
            (10939, tree_controller.set_channel, (3,   6, False)),
            (10949, tree_controller.set_channel, (0,   5, False)),
            (10949, tree_controller.set_channel, (1,   5, False)),
            (10949, tree_controller.set_channel, (2,   5, False)),
            (10949, tree_controller.set_channel, (3,   5, False)),
            (10959, tree_controller.set_channel, (0,   4, False)),
            (10959, tree_controller.set_channel, (1,   4, False)),
            (10959, tree_controller.set_channel, (2,   4, False)),
            (10959, tree_controller.set_channel, (3,   4, False)),
            (10969, tree_controller.set_channel, (0,   3, False)),
            (10969, tree_controller.set_channel, (1,   3, False)),
            (10969, tree_controller.set_channel, (2,   3, False)),
            (10969, tree_controller.set_channel, (3,   3, False)),
            (10979, tree_controller.set_channel, (0,   2, False)),
            (10979, tree_controller.set_channel, (1,   2, False)),
            (10979, tree_controller.set_channel, (2,   2, False)),
            (10979, tree_controller.set_channel, (3,   2, False)),
            (10989, tree_controller.set_channel, (0,   1, False)),
            (10989, tree_controller.set_channel, (1,   1, False)),
            (10989, tree_controller.set_channel, (2,   1, False)),
            (10989, tree_controller.set_channel, (3,   1, False)),
            (11000, tree_controller.set_channel, (0,   0, False)),
            (11000, tree_controller.set_channel, (1,   0, False)),
            (11000, tree_controller.set_channel, (2,   0, False)),
            (11000, tree_controller.set_channel, (3,   0, False)),
            (11000, floods_controller.set_channel,('C7', 0, False)),
        ]))

    def test_sequence_channel_types(self):
        '''Ensure that the channel names get converted to the proper 
        type for indices into the unit's channels array.  Different
        controller drivers use different types for these (string
        vs integer).'''
        # numeric channel numbers
        tree_controller = FireGodControllerUnit(
            'fg', PowerSource('ps1'), TestNetwork(),
            address=1, resolution=101, num_channels=32)
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
        result = None
        if len(a) != len(e):
            print "Actual data dumped to data/SequenceData.timeline."
            outf = file("data/SequenceData.timeline", "w")
            for ev in a:
                print >>outf, "%8d %-10s %s\n" % (ev[0], ev[2], ev[1])
            outf.close()
            return "TIMELINE MISMATCH: actual has %d elements vs. expected %d" % (len(a), len(e))

        for i in range(len(a)):
            if a[i] != e[i]:
                if result is None:
                    result = "TIMELINE MISMATCH: @%d: actual=%s, expected=%s" % (i, a[i], e[i])
                else:
                    result = "MULTIPLE TIMELINE MISMATCHES, including @%d: actual=%s, expected=%s" % (i, a[i], e[i])

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
