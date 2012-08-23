# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/LCheckTest.py,v 1.5 2008-12-31 00:25:19 steve Exp $
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
import unittest
import subprocess
import os

runenv = os.environ
runenv['PYTHONPATH'] = ':'.join(['../lib'] + os.environ.get('PYTHONPATH', '').split(':'))

def runAfcheck(arglist, srcfile, compfile, difffile):
    try:
        proc = subprocess.Popen(('../bin/lcheck', srcfile) + arglist, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=runenv)
    except:
        # no ../bin directory?  Looks like we're not in our development environment.
        # must have unpacked from a source distribution tarball.  Look for our scripts
        # in ../dist_bin instead, and better make sure they are executable.
        os.chmod('../dist_bin/lcheck', 0755)
        proc = subprocess.Popen(('../dist_bin/lcheck', srcfile) + arglist, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=runenv)
        
    output = proc.communicate()[0]
    cmpout = open(compfile).read()
    if output != cmpout:
        with open(difffile, 'w') as d:
            d.write(output)

    return (proc.returncode, output, cmpout)

class AfcheckTest (unittest.TestCase):
    def testRunV(self):
        (c, a, b) = runAfcheck(('-v',), 'lcheck.conf', 'lcheck.v.out', 'lcheck.v.actual')
        self.assertEqual(c, 0)
        self.assertEqual(a, b, msg="output incorrect; compare lcheck.v.out vs. lcheck.v.actual")

    def testRun(self):
        (c, a, b) = runAfcheck((), 'lcheck.conf', 'lcheck.out', 'lcheck.actual')
        self.assertEqual(c, 0)
        self.assertEqual(a, b, msg="output incorrect; compare lcheck.out vs. lcheck.actual")

    def testDuplicates(self):
        (c, a, b) = runAfcheck((), 'duptest.conf', 'lcheck.dup.out', 'lcheck.dup.actual')
        self.assertEqual(c, 1)
        #self.assertEqual(a, b)
        self.assert_("ValueError: Unit 'a' is not unique!" in a)
