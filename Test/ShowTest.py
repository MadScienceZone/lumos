#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/ShowTest.py,v 1.4 2008-12-31 00:13:32 steve Exp $
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
# vi:set nu ai sm ts=4 sw=4 expandtab:
import unittest, os
from Lumos.Show import Show

# patch in our test network for the purposes of this unit test
import TestNetwork
import Lumos.Network.Networks
Lumos.Network.Networks.supported_network_types['test'] = TestNetwork.TestNetwork

class ShowTest (unittest.TestCase):
    def testLoadFile(self):
        g = Show()
        g.load(open('show.conf'))

        self.assertEqual(g.title, "Example Show")
        self.assertEqual(g.description, "This is an example of how to set up a Lumos show.conf file.\nYou should take this file and edit it to reflect\nyour actual show setup.")
        self.assertEqual(sorted(g.all_power_sources.keys()), ['1', '2a', '2b'])
        self.assertEqual(g.all_power_sources['1'].amps, 20)
        self.assertEqual(g.all_power_sources['2a'].amps, 15)
        self.assertEqual(g.all_power_sources['2b'].amps, 15.5)

        self.assertEqual(sorted(g.networks.keys()), ['floods', 'misc', 'trees'])
        for key, desc, port, baud, bits, units in (
            ('floods', 'X10 network for the floodlights.', 
                2, 1200, 8, [
                    ('floodX10', '2b', 'LynX-10/TW523 Controller', None, (
                        ('A1', 'West flood, blue',  1, 10,   True),
                        ('A2', 'West flood, green', 1, 10,   True),
                        ('C1', 'Snowman power',    20, None, False),
                    ))
                ]
            ),
            ('misc', "Everything that's not a floodlight or a tree.", 
                1, 9600, 8, [
                    ('a', '2a', 'Lumos 48-Channel SSR Controller', 9),
                    ('b', '2a', 'Lumos 48-Channel SSR Controller', 10)
                ]
            ),
            ('trees', 'Separate network of controllers for tree displays.', 
                0, 19200, 8, [
                    ('treea1', '1', 'Lumos 48-Channel SSR Controller', 0, (
                        (0, 'Tree 1 RED 1', .3, None, True),
                        (1, 'Tree 1 RED 2', .3, None, True),
                    )),
                    ('treea2', '1', 'Lumos 48-Channel SSR Controller', 1),
                    ('treeb1', '1', 'Lumos 48-Channel SSR Controller', 2),
                    ('treeb2', '1', 'Lumos 48-Channel SSR Controller', 3)
                ]
            )
        ):
            self.assertEqual(g.networks[key].description, desc)
            self.assertEqual(g.networks[key].args['port'], port)
            self.assertEqual(g.networks[key].args['baudrate'], baud)
            self.assertEqual(g.networks[key].args['bits'], bits)
#            self.assertEqual(g.networks[key].args['parity'], parity)
#            self.assertEqual(g.networks[key].args['stop'], stop)
#            self.assertEqual(g.networks[key].args['xonxoff'], xonxoff)
#            self.assertEqual(g.networks[key].args['rtscts'], rtscts)
            self.assertEqual(sorted(g.networks[key].units.keys()), [i[0] for i in units])
            for unit in units:
                self.assertEqual(g.networks[key].units[unit[0]].power_source.id, unit[1])
                self.assertEqual(g.networks[key].units[unit[0]].type, unit[2])
                if unit[3] is not None:
                    self.assertEqual(g.networks[key].units[unit[0]].address, unit[3])
                # channel tests
                if len(unit) > 4:
                    self.assertEqual(sorted(g.networks[key].units[unit[0]].channels.keys()), [i[0] for i in unit[4]])
                    for channel in unit[4]:
                        self.assertEqual(g.networks[key].units[unit[0]].channels[channel[0]].name, channel[1])
                        self.assertEqual(g.networks[key].units[unit[0]].channels[channel[0]].load, channel[2])
                        if channel[3] is None:
                            self.assertEqual(g.networks[key].units[unit[0]].channels[channel[0]].warm, None)
                        else:
                            self.assertEqual(g.networks[key].units[unit[0]].channels[channel[0]].warm, g.networks[key].units[unit[0]].channels[channel[0]].raw_dimmer_value(channel[3]))
                        self.assertEqual(g.networks[key].units[unit[0]].channels[channel[0]].dimmer, channel[4])

    def testSaveFile(self):
        #try:
            g = Show()
            g.load_file('savetest.in.conf', open_device=False)
            out = open('savetest.out.conf', 'w')
            g.save(out)
            out.close()
            g.save_file('savetest.out2.conf')

            original_data = open('savetest.cmp.conf').read()
            result_1_data = open('savetest.out.conf').read()
            result_2_data = open('savetest.out2.conf').read()

            self.assertEqual(original_data, result_1_data, msg="savetest.cmp.conf vs. savetest.out.conf differ")
            self.assertEqual(original_data, result_2_data, msg="savetest.cmp.conf vs. savetest.out2.conf differ")
        #finally:
            #for name in 'savetest.out.conf', 'savetest.out2.conf':
                #if os.path.exists(name): os.remove(name)

    def test_controller_map(self):
        g = Show()
        g.load_file('show.conf')
        self.assertEqual(g.controllers, {
            'floodX10': g.networks['floods'].units['floodX10'],
            'a':        g.networks['misc'].units['a'],
            'b':        g.networks['misc'].units['b'],
            'treea1':   g.networks['trees'].units['treea1'],
            'treea2':   g.networks['trees'].units['treea2'],
            'treeb1':   g.networks['trees'].units['treeb1'],
            'treeb2':   g.networks['trees'].units['treeb2'],
        })
# 
# $Log: not supported by cvs2svn $
#
