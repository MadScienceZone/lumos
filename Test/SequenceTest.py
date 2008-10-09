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

    def test_compilation(self):
        tree_controller = FireGodControllerUnit(
            PowerSource('ps1'), TestNetwork(),
            address=1, resolution=101, channels=32)
        tree_controller.add_channel(0, load=1)
        tree_controller.add_channel(1, load=1)
        tree_controller.add_channel(2, load=1)
        tree_controller.add_channel(3, load=1)

        floods_controller = LynX10ControllerUnit(
            PowerSource('ps2'), TestNetwork(), resolution=16)
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

        self.assertEqual(s.compile(), [
            (    0, floods_controller.all_channels_off, ()),
            (    0, tree_controller.all_channels_off, ()),
            ( 1000, floods_controller.set_channel, ('C7', 2)),
            ( 1000, tree_controller.set_channel, (0, 100)),
            ( 1153, floods_controller.set_channel, ('C7', 3)),
            ( 1307, floods_controller.set_channel, ('C7', 4)),
            ( 1461, floods_controller.set_channel, ('C7', 5)),
            ( 1615, floods_controller.set_channel, ('C7', 6)),
            ( 1769, floods_controller.set_channel, ('C7', 7)),
            ( 1923, floods_controller.set_channel, ('C7', 8)),
            ( 2000, tree_controller.set_channel, (0, 0)),
            ( 2000, tree_controller.set_channel, (1, 100)),
            ( 2076, floods_controller.set_channel, ('C7', 9)),
            ( 2230, floods_controller.set_channel, ('C7',10)),
            ( 2384, floods_controller.set_channel, ('C7',11)),
            ( 2538, floods_controller.set_channel, ('C7',12)),
            ( 2692, floods_controller.set_channel, ('C7',13)),
            ( 2846, floods_controller.set_channel, ('C7',14)),
            ( 3000, floods_controller.set_channel, ('C7',15)),
            ( 3000, tree_controller.set_channel, (1, 0)),
            ( 3000, tree_controller.set_channel, (2, 100)),
            ( 4000, tree_controller.set_channel, (2, 0)),
            ( 4000, tree_controller.set_channel, (3, 100)),
            ( 5000, tree_controller.set_channel, (0,   1)),
            ( 5010, tree_controller.set_channel, (0,   2)),
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
            ( 6000, tree_controller.set_channel, (1,   1)),
            ( 6010, tree_controller.set_channel, (1,   2)),
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
            ( 7000, floods_controller.set_channel, ('C7', 7)),
            ( 7000, tree_controller.set_channel, (1, 100)),
            ( 7000, tree_controller.set_channel, (2,   1)),
            ( 7010, tree_controller.set_channel, (2,   2)),
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
            ( 8000, tree_controller.set_channel, (3,   1)),
            ( 8010, tree_controller.set_channel, (3,   2)),
            ( 8020, tree_controller.set_channel, (3,   3)),
            ( 8030, tree_controller.set_channel, (3,   4)),
            ( 8040, tree_controller.set_channel, (3,   5)),
            ( 8050, tree_controller.set_channel, (3,   6)),
            ( 8060, tree_controller.set_channel, (3,   7)),
            ( 8070, tree_controller.set_channel, (3,   8)),
            ( 8080, tree_controller.set_channel, (3,   9)),
            ( 8090, tree_controller.set_channel, (3,  10)),
            ( 8101, tree_controller.set_channel, (3,  11)),
            ( 8111, tree_controller.set_channel, (3,  12)),
            ( 8121, tree_controller.set_channel, (3,  13)),
            ( 8131, tree_controller.set_channel, (3,  14)),
            ( 8141, tree_controller.set_channel, (3,  15)),
            ( 8151, tree_controller.set_channel, (3,  16)),
            ( 8161, tree_controller.set_channel, (3,  17)),
            ( 8171, tree_controller.set_channel, (3,  18)),
            ( 8181, tree_controller.set_channel, (3,  19)),
            ( 8191, tree_controller.set_channel, (3,  20)),
            ( 8202, tree_controller.set_channel, (3,  21)),
            ( 8212, tree_controller.set_channel, (3,  22)),
            ( 8222, tree_controller.set_channel, (3,  23)),
            ( 8232, tree_controller.set_channel, (3,  24)),
            ( 8242, tree_controller.set_channel, (3,  25)),
            ( 8252, tree_controller.set_channel, (3,  26)),
            ( 8262, tree_controller.set_channel, (3,  27)),
            ( 8272, tree_controller.set_channel, (3,  28)),
            ( 8282, tree_controller.set_channel, (3,  29)),
            ( 8292, tree_controller.set_channel, (3,  30)),
            ( 8303, tree_controller.set_channel, (3,  31)),
            ( 8313, tree_controller.set_channel, (3,  32)),
            ( 8323, tree_controller.set_channel, (3,  33)),
            ( 8333, tree_controller.set_channel, (3,  34)),
            ( 8343, tree_controller.set_channel, (3,  35)),
            ( 8353, tree_controller.set_channel, (3,  36)),
            ( 8363, tree_controller.set_channel, (3,  37)),
            ( 8373, tree_controller.set_channel, (3,  38)),
            ( 8383, tree_controller.set_channel, (3,  39)),
            ( 8393, tree_controller.set_channel, (3,  40)),
            ( 8404, tree_controller.set_channel, (3,  41)),
            ( 8414, tree_controller.set_channel, (3,  42)),
            ( 8424, tree_controller.set_channel, (3,  43)),
            ( 8434, tree_controller.set_channel, (3,  44)),
            ( 8444, tree_controller.set_channel, (3,  45)),
            ( 8454, tree_controller.set_channel, (3,  46)),
            ( 8464, tree_controller.set_channel, (3,  47)),
            ( 8474, tree_controller.set_channel, (3,  48)),
            ( 8484, tree_controller.set_channel, (3,  49)),
            ( 8494, tree_controller.set_channel, (3,  50)),
            ( 8505, tree_controller.set_channel, (3,  51)),
            ( 8515, tree_controller.set_channel, (3,  52)),
            ( 8525, tree_controller.set_channel, (3,  53)),
            ( 8535, tree_controller.set_channel, (3,  54)),
            ( 8545, tree_controller.set_channel, (3,  55)),
            ( 8555, tree_controller.set_channel, (3,  56)),
            ( 8565, tree_controller.set_channel, (3,  57)),
            ( 8575, tree_controller.set_channel, (3,  58)),
            ( 8585, tree_controller.set_channel, (3,  59)),
            ( 8595, tree_controller.set_channel, (3,  60)),
            ( 8606, tree_controller.set_channel, (3,  61)),
            ( 8616, tree_controller.set_channel, (3,  62)),
            ( 8626, tree_controller.set_channel, (3,  63)),
            ( 8636, tree_controller.set_channel, (3,  64)),
            ( 8646, tree_controller.set_channel, (3,  65)),
            ( 8656, tree_controller.set_channel, (3,  66)),
            ( 8666, tree_controller.set_channel, (3,  67)),
            ( 8676, tree_controller.set_channel, (3,  68)),
            ( 8686, tree_controller.set_channel, (3,  69)),
            ( 8696, tree_controller.set_channel, (3,  70)),
            ( 8707, tree_controller.set_channel, (3,  71)),
            ( 8717, tree_controller.set_channel, (3,  72)),
            ( 8727, tree_controller.set_channel, (3,  73)),
            ( 8737, tree_controller.set_channel, (3,  74)),
            ( 8747, tree_controller.set_channel, (3,  75)),
            ( 8757, tree_controller.set_channel, (3,  76)),
            ( 8767, tree_controller.set_channel, (3,  77)),
            ( 8777, tree_controller.set_channel, (3,  78)),
            ( 8787, tree_controller.set_channel, (3,  79)),
            ( 8797, tree_controller.set_channel, (3,  80)),
            ( 8808, tree_controller.set_channel, (3,  81)),
            ( 8818, tree_controller.set_channel, (3,  82)),
            ( 8828, tree_controller.set_channel, (3,  83)),
            ( 8838, tree_controller.set_channel, (3,  84)),
            ( 8848, tree_controller.set_channel, (3,  85)),
            ( 8858, tree_controller.set_channel, (3,  86)),
            ( 8868, tree_controller.set_channel, (3,  87)),
            ( 8878, tree_controller.set_channel, (3,  88)),
            ( 8888, tree_controller.set_channel, (3,  89)),
            ( 8898, tree_controller.set_channel, (3,  90)),
            ( 8909, tree_controller.set_channel, (3,  91)),
            ( 8919, tree_controller.set_channel, (3,  92)),
            ( 8929, tree_controller.set_channel, (3,  93)),
            ( 8939, tree_controller.set_channel, (3,  94)),
            ( 8949, tree_controller.set_channel, (3,  95)),
            ( 8959, tree_controller.set_channel, (3,  96)),
            ( 8969, tree_controller.set_channel, (3,  97)),
            ( 8979, tree_controller.set_channel, (3,  98)),
            ( 8989, tree_controller.set_channel, (3,  99)),
            ( 9000, tree_controller.set_channel, (3, 100)),
            (10000, floods_controller.all_channels_off, ()),
            (10000, tree_controller.all_channels_off, ()),
        ])


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
