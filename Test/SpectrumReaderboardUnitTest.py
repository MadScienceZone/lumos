import unittest
from SpectrumReaderboardUnit import *

class SpectrumReaderboardUnitTest (unittest.TestCase):
	def setUp(self):
		self.rb = SpectrumReaderboardUnit(2)

	def tearDown(self):
		self.rb = None

	def testInit(self):
		self.assertEqual(self.rb.address, 2)

	def testTextExceptions(self):
		self.assertRaises(InvalidTextAlignment, self.rb._text, 'xxx', align='invalid_choice')
		self.assertRaises(InvalidTextMode, self.rb._text, 'xxx', mode='fsfdsf')

	def testTextStrings(self):
		self.assertEquals(self.rb._text('hello, world'), 'AA\0330bhello, world')
		self.assertEquals(self.rb._text('hello', align='middle'), 'AA\033 bhello')
		self.assertEquals(self.rb._text('hello', align='bottom', mode='roll up'), 'AA\033&ehello')
		self.assertEquals(self.rb._text('hello', align='top', mode='rotate', label='Q'), 'AQ\033"ahello')

	def testTextWithAttributes(self):
		self.assertEquals(self.rb._text('Hello$red-red-${yellow}yellow$green-green', align='top', mode='hold', label='A'), 'AA\33"bHello\0341-red-\0343yellow\0342-green')
		self.assertEquals(self.rb._text('Hello$red-red-${yellow}yellow$green-green', align='top', mode='hold', label='A'), 'AA\33"bHello\0341-red-\0343yellow\0342-green')

	def testTextWithBadAttributes(self):
		self.assertRaises(InvalidTextAttribute, self.rb._text, 'x$foo')

	def testStrStrings(self):
		self.assertEquals(self.rb._str('hello, world'), 'G0hello, world')
		self.assertEquals(self.rb._str('hello', label='Q'), 'GQhello')
		self.assertEquals(self.rb._str('xyz', label='2'), 'G2xyz')

	def testStrWithAttributes(self):
		self.assertEquals(self.rb._str('Hello$red-red-${yellow}yellow$green-green', label='A'), 'GAHello\0341-red-\0343yellow\0342-green')
		self.assertEquals(self.rb._str('Hello$red-red-${yellow}yellow$green-green', label='B'), 'GBHello\0341-red-\0343yellow\0342-green')

	def testStrWithBadAttributes(self):
		self.assertRaises(InvalidTextAttribute, self.rb._str, 'x$foo')

	def testInitDev(self):
		self.assertEqual(self.rb.initialize_device(), "\1\1\1\1\1\1Z02\2E,\3\2AA\0330b\4")

	# These just verify that we haven't dropped or added to
	# some special mappings without intending to (including accidentally clobbering
	# a key somewhere).
	def testDictSizes(self):
		self.assertEqual(len(SpectrumReaderboardUnit.text_alignments), 4)
		self.assertEqual(len(SpectrumReaderboardUnit.text_modes), 51)
		self.assertEqual(len(SpectrumReaderboardUnit.text_attributes), 7+26+8+36+12+1+68)
