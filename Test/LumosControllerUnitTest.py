# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS 
# $Header: /tmp/cvsroot/lumos/Test/SSR48ControllerUnitTest.py,v 1.5 2008-12-31 00:13:32 steve Exp $
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
import unittest, quopri
from Lumos.Device.LumosControllerUnit  import LumosControllerUnit, LumosControllerConfiguration
from Lumos.PowerSource                 import PowerSource
from TestNetwork                       import TestNetwork

class LumosControllerUnitTest (unittest.TestCase):
    def setUp(self):
        self.n = TestNetwork()
        p = PowerSource('testpower', amps=1)
        self.ssr = LumosControllerUnit('ssr1', p, address=12, network=self.n)
        self.ssr.add_channel(0, load=.3)
        self.ssr.add_channel(1, load=1)
        self.ssr.add_channel(2, load=.3, warm=10)
        self.ssr.add_channel(3, load=1, dimmer=False)


    def test_unit_id(self):
        self.assertEqual(self.ssr.id, 'ssr1')

    def tearDown(self):
        self.ssr = None
        self.n = None

    def testInit(self):
        self.ssr.kill_all_channels()
        self.ssr.all_channels_off()
        self.ssr.flush()
        #self.assertEqual(self.n.buffer, '=8C=AC=02=03')
        self.assertEqual(self.n.buffer, '=8C=ACB=0C')

    def testOnOff(self):
        self.ssr.set_channel_on(2)
        self.ssr.flush()
        self.ssr.set_channel_on(3)
        self.ssr.flush()
        self.ssr.set_channel_off(0)
        self.ssr.flush()
        self.ssr.set_channel_off(2)
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '''=9CB=9CC=ACB=0C''')

    def testDimmer(self):
        self.ssr.set_channel(0, None)
        self.ssr.set_channel(0, 15)
        self.ssr.set_channel(2, 15)
        self.ssr.set_channel(2, 31)
        self.ssr.set_channel(2, 30)
        self.ssr.flush()
        #self.assertEqual(self.n.buffer, '=AC=00=0F=AC=02=0F=9CB=AC=02=1E')
        self.assertEqual(self.n.buffer, '=AC@=07=AC=02=0F')
    
    def testWarm(self):
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.assertEqual(self.n.buffer, '=ACB=0C')

        for i,j in ((1,''), (0,''), (2,''), (3,''), (4,''), 
        (5,''), (6,''), (7,''), (25,''), (26,26), (27,27), (28,28), (0,25), (105,105),(2,25),
            (26,26),(25,25),(254,254),(1,25)):
            # 2,26 -> AC02 AC02|lsb v>>1
            self.n.reset()
            self.ssr.set_channel(2, i)
            self.ssr.flush()
            if j == '':
                self.assertEqual(self.n.buffer, "", "set_channel(2, %d) -> %s, expected nothing" % (i,self.n.buffer) )
            else:
                self.assertEqual(self.n.buffer, "=AC{0}{1}".format(quopri.encodestring(chr(0x02 | ((j<<6) & 0x40))),
                    quopri.encodestring(chr((j >> 1) & 0x7f))),
                    "set_channel(2, %d) -> %s, expected %x" % (i,self.n.buffer,j))

    def testBulkUpdate(self):
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.n.reset()

        self.ssr.flush()
        self.assertEqual(self.n.buffer, '')
        self.n.reset()

        self.ssr.flush(force=True)
        self.assertEqual(self.n.buffer.replace('=\n',''), ('=BC@/=00=00=0C'+'=00'*45+'V=10=00=00=00=00=00=00U'))

    def testLowResBulkUpdate(self):
        p = PowerSource('testpower', amps=1)
        self.ssr = LumosControllerUnit('ssr1', p, address=12, network=self.n, resolution=128)
        self.ssr.add_channel(0, load=.3)
        self.ssr.add_channel(1, load=1)
        self.ssr.add_channel(2, load=.3, warm=10)
        self.ssr.add_channel(3, load=1, dimmer=False)

        self.ssr.all_channels_off()
        self.ssr.flush()
        self.n.reset()

        self.ssr.flush()
        self.assertEqual(self.n.buffer, '')
        self.n.reset()

        self.ssr.flush(force=True)
        self.assertEqual(self.n.buffer.replace('=\n', ''), ('=BC=00/=00=00=0C'+'=00'*45+'U'))

    def testRampUp(self):
        self.ssr.raw_ramp_up(2, 4, 13)      # 4 steps, 13 between
        self.assertEqual(self.n.buffer, "=CCB=03=0C")
        self.n.reset()

        self.ssr.raw_ramp_down(2, 5, 10)   # 5 steps, 10 between
        self.assertEqual(self.n.buffer, "=CC=02=04=09")

    def testSpecials(self):
        for cmd, args, result in (
            ('sleep',    [],    '=FC=00ZZ'),
            ('wake',     [],    '=FC=01ZZ'),
            ('shutdown', [],    '=FC=02XY'),
            ('execute',  [123], '=FC=05{'),
            ('execute',  [0],   '=FC=05=00'),
            ('clearmem', [],    '=FC=08CA'),
            ('masksens', ['A'], '=FC=07=08'),
            ('masksens', ['B'], '=FC=07=04'),
            ('masksens', ['C'], '=FC=07=02'),
            ('masksens', ['D'], '=FC=07=01'),
            ('masksens', ['B','D'], '=FC=07=05'),
            ('masksens', [],    '=FC=07=00'),
            ('__reset__', [],   '=FCq$r'),
            ('__baud__', [4],   '=FCr=04&'),
            ('__baud__', [0],   '=FCr=00&'),
            ('__baud__', [7],   '=FCr=07&'),
            ('noconfig', [],    '=FCp'),
        ):
            self.ssr.raw_control(cmd, *args)
            self.assertEqual(self.n.buffer, result)
            self.n.reset()

        self.assertRaises(ValueError, self.ssr.raw_control, 'xyzzy')

    def testPhase(self):
        for value, result in (
            ( 37, '=FC@%PO'),
            (500, '=FCCtPO'),
            (511, '=FCC=7FPO'),
            (  0, '=FC@=00PO'),
            (256, '=FCB=00PO'),
        ):
            self.ssr.raw_set_phase(value)
            self.assertEqual(self.n.buffer, result)
            self.n.reset()
        
    def testNewAddress(self):
        for value, result in (
            ( 0, '=FC`IAD'),
            ( 1, '=F0aIAD'),
            ( 2, '=F1bIAD'),
            ( 3, '=F2cIAD'),
            ( 4, '=F3dIAD'),
            ( 5, '=F4eIAD'),
            (15, '=F5oIAD'),
            (14, '=FFnIAD'),
            (13, '=FEmIAD'),
            (12, '=FDlIAD'),
            (11, '=FCkIAD'),
            (10, '=FBjIAD'),
            ( 6, '=FAfIAD'),
            ( 9, '=F6iIAD'),
            ( 8, '=F9hIAD'),
            ( 7, '=F8gIAD'),
        ):
            self.ssr.raw_set_address(value)
            self.assertEqual(self.n.buffer, result)
            self.assertEqual(self.ssr.address, value)
            self.n.reset()

        self.assertRaises(ValueError, self.ssr.raw_set_address, -1)
        self.assertRaises(ValueError, self.ssr.raw_set_address, 16)
        self.assertRaises(ValueError, self.ssr.raw_set_address, 100)

    def testDownloadSequence(self):
        for id, bits, result in (
            (  0, [],        '=FC=04=00=00Ds'),
            ( 13, [1,2,3],   '=FC=04\r=03=01=02=03Ds'),
            (127, [200,57,92,19,0,0,0,12],   
                             '=FC=04=7F=08H9\\=13=00=00=00=0CDs'),
        ):
            self.ssr.raw_download_sequence(id, bits)
            self.assertEqual(self.n.buffer, result)
            self.n.reset()

    def testSensorTriggers(self):
        for sens, a, b, c, i, m, res in (
               ('A', 1, 2, 3, True, 'once',  '=FC=06@=01=02=03<'),
               ('B', 55,0, 0, True, 'follow','=FC=06!7=00=00<'),
               ('C', 127,3,19,False,'const', '=FC=06=12=7F=03=13<'),
               ('D', 4, 9,99, False,'follow','=FC=063=04\tc<'),
        ):
            self.ssr.raw_sensor_trigger(sens, a, b, c, inverse=i, mode=m)
            self.assertEqual(self.n.buffer, res)
            self.n.reset()

#        self.ssr.ramp_to(2, 255, 2000)
#        # channel 2 is at 25; ramp to 255 over 2000 mS = 
#        self.assertEqual(self.n.buffer, "

    def testFirstInit(self):
        self.ssr.initialize_device()
        #self.assertEqual(self.n.buffer, "=FCa=8C=AC=02=03")
        self.assertEqual(self.n.buffer, "=FCp=8C=ACB=0C")

    def test_iterator(self):
        self.assertEquals(sorted(self.ssr.iter_channels()), [0, 1, 2, 3])

    def test_optimized_all_off(self):
        self.ssr.kill_all_channels()
        self.ssr.flush()
        self.n.reset()

        self.ssr.flush(force=True)
        self.assertEqual(self.n.buffer, '=8C')

    def test_config(self):
        con = LumosControllerConfiguration()
        for sens, D, R, res in (
            (['A','B','C','D'], None, 256, '=FCqx=00z=3D'),
            ([               ],    0, 256, '=FCq=00=00z=3D'),
            ([    'B','C',   ],  500, 128, '=FCq7s:=3D'),   
            (['A',           ],  157, 256, '=FCqE=1Cz=3D'),  
            (['A',        'D'], None, 128, '=FCqH=00:=3D'),
        ):
            con.configured_sensors = sens
            con.dmx_start          = D
            con.resolution         = R
            self.ssr.raw_configure_device(con)
            self.assertEqual(self.n.buffer, res)
            self.n.reset()

    def test_query(self):
        self.n.input_data('\xFC\x1F\x50\x00\x00\x44\x02\x00\x4f\x01\x27\x00\x00\x33')
        reply = self.ssr.raw_query_device_status()
        self.assertEqual(self.n.buffer, "=FC=03$T")
        self.assertEqual(reply.config.configured_sensors, ['A','C'])
        self.assertEqual(reply.config.dmx_start, None)
        self.assertEqual(reply.config.resolution, 256)
        self.assertEqual(reply.enabled_sensors, [])
        self.assertEqual(reply.in_config_mode, False)
        self.assertEqual(reply.in_sleep_mode, False)
        self.assertEqual(reply.err_memory_full, False)
        self.assertEqual(reply.sensors_on, ['A'])
        self.assertEqual(reply.phase_offset, 2)
        self.assertEqual(reply.eeprom_memory_free, 0x4f)
        self.assertEqual(reply.ram_memory_free, 0xa7)
        self.assertEqual(reply.current_sequence, None)
        self.assertEqual(reply.hardware_type, 'lumos48ctl')



# 
# $Log: not supported by cvs2svn $
#
