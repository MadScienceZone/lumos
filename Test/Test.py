# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/Test.py,v 1.4 2008-12-31 00:13:32 steve Exp $
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
from unittest import TestSuite, findTestCases

def suite():
    modules_to_test = (
      'ChannelTest',
	  'ControllersTest',
      'ControllerUnitTest',
	  'DeviceTest',
	  'EventTest',
	  'FirecrackerX10ControllerUnitTest',
	  'FireGodControllerUnitTest',
	  'LCheckTest',
	  'LumosTest',
      'LynX10ControllerUnitTest',
      'NetworkTest',
	  'NetworksTest',
	  'Olsen595ControllerUnitTest',
	  'PowerSourceTest',
	  'RenardControllerUnitTest',
	  'ShowTest',
	  'SerialNetworkTest',        # XXX device tests?
	  'ParallelBitNetworkTest',   # XXX device tests?
	  'SequenceTest',
	  'SerialBitNetworkTest',     # XXX device tests?
#     'SpectrumReaderboardUnitTest',
	  'SSR48ControllerUnitTest',
	  'TestNetworkTest',
	  'TestParallelNetworkTest',
      'TimeRangeTest',
	  'VixenSequenceTest',
      'X10ControllerUnitTest'
    )
    suite = TestSuite()
    for module in map(__import__, modules_to_test):
        suite.addTest(findTestCases(module))
    return suite
# 
# $Log: not supported by cvs2svn $
#
