#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/SpectrumReaderboardUnitTest.py,v 1.3 2008-12-31 00:13:32 steve Exp $
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
#
# vi:set ai sm nu ts=4 sw=4 expandtab:
#
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
        self.assertEqual(self.rb._text('hello, world'), 'AA\0330bhello, world')
        self.assertEqual(self.rb._text('hello', align='middle'), 'AA\033 bhello')
        self.assertEqual(self.rb._text('hello', align='bottom', mode='roll up'), 'AA\033&ehello')
        self.assertEqual(self.rb._text('hello', align='top', mode='rotate', label='Q'), 'AQ\033"ahello')

    def testTextWithAttributes(self):
        self.assertEqual(self.rb._text('Hello$red-red-${yellow}yellow$green-green', align='top', mode='hold', label='A'), 'AA\33"bHello\0341-red-\0343yellow\0342-green')
        self.assertEqual(self.rb._text('Hello$red-red-${yellow}yellow$green-green', align='top', mode='hold', label='A'), 'AA\33"bHello\0341-red-\0343yellow\0342-green')

    def testTextWithBadAttributes(self):
        self.assertRaises(InvalidTextAttribute, self.rb._text, 'x$foo')

    def testStrStrings(self):
        self.assertEqual(self.rb._str('hello, world'), 'G0hello, world')
        self.assertEqual(self.rb._str('hello', label='Q'), 'GQhello')
        self.assertEqual(self.rb._str('xyz', label='2'), 'G2xyz')

    def testStrWithAttributes(self):
        self.assertEqual(self.rb._str('Hello$red-red-${yellow}yellow$green-green', label='A'), 'GAHello\0341-red-\0343yellow\0342-green')
        self.assertEqual(self.rb._str('Hello$red-red-${yellow}yellow$green-green', label='B'), 'GBHello\0341-red-\0343yellow\0342-green')

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
# 
# $Log: not supported by cvs2svn $
#
