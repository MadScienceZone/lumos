# vi:set ai sm nu ts=4 sw=4 expandtab:
import unittest
from Lumos.ChannelMap  import ChannelMap

class ChannelMapTest(unittest.TestCase):
    def test_read(self):
        x = ChannelMap()
        x.load_file("data/test.cmap")
        #self.assertEqual(len(x), 5)
