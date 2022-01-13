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
from Lumos.Device.LumosControllerUnit  import LumosControllerUnit, LumosControllerConfiguration, InternalDeviceError
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
        self.assertEqual(self.n.buffer, b'=8C=ACB=0C')

    def testOnOff(self):
        self.ssr.set_channel_on(2)
        self.ssr.flush()
        self.ssr.set_channel_on(3)
        self.ssr.flush()
        self.ssr.set_channel_off(0)
        self.ssr.flush()
        self.ssr.set_channel_off(2)
        self.ssr.flush()
        self.assertEqual(self.n.buffer, b'''=9CB=9CC=ACB=0C''')

    def testDimmer(self):
        self.ssr.set_channel(0, None)
        self.ssr.set_channel(0, 15)
        self.ssr.set_channel(2, 15)
        self.ssr.set_channel(2, 31)
        self.ssr.set_channel(2, 30)
        self.ssr.flush()
        #self.assertEqual(self.n.buffer, '=AC=00=0F=AC=02=0F=9CB=AC=02=1E')
        self.assertEqual(self.n.buffer, b'=AC@=07=AC=02=0F')
    
    def testWarm(self):
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.assertEqual(self.n.buffer, b'=ACB=0C')

        for i,j in (
            (1,None), (0,None), (2,None), (3,None), (4,None), (5,None), 
            (6,None), (7,None), (25,None), (26,26), (27,27), (28,28), 
            (0,25), (105,105),(2,25), (26,26),(25,25),(254,254),(1,25)
        ):
            # 2,26 -> AC02 AC02|lsb v>>1
            self.n.reset()
            self.ssr.set_channel(2, i)
            self.ssr.flush()
            if j is None:
                self.assertEqual(self.n.buffer, b"", "set_channel(2, %d) -> %s, expected nothing" % (i,self.n.buffer) )
            else:
                self.assertEqual(self.n.buffer, b"=AC" + 
                    quopri.encodestring(bytes([0x02 | ((j<<6) & 0x40)]))+
                    (b'=7F=7F' if j==254 else quopri.encodestring(bytes([((j >> 1) & 0x7f)]))),
                    "set_channel(2, %d) -> %s, expected %x" % (i,self.n.buffer,j))

    def testBulkUpdate(self):
        self.ssr.all_channels_off()
        self.ssr.flush()
        self.n.reset()

        self.ssr.flush()
        self.assertEqual(self.n.buffer, b'')
        self.n.reset()

        self.ssr.flush(force=True)
        self.assertEqual(self.n.buffer.replace(b'=\n',b''), b'=BC=00/=00=00=19'+b'=00'*45+b'U')
        # b? 00cccccc (n-1) <v>*<n> 55
        # 0, 1, 2 (warm 10) 3!dim

#    def testLowResBulkUpdate(self):
#        p = PowerSource('testpower', amps=1)
#        self.ssr = LumosControllerUnit('ssr1', p, address=12, network=self.n, resolution=128)
#        self.ssr.add_channel(0, load=.3)
#        self.ssr.add_channel(1, load=1)
#        self.ssr.add_channel(2, load=.3, warm=10)
#        self.ssr.add_channel(3, load=1, dimmer=False)
#
#        self.ssr.all_channels_off()
#        self.ssr.flush()
#        self.n.reset()
#
#        self.ssr.flush()
#        self.assertEqual(self.n.buffer, '')
#        self.n.reset()
#
#        self.ssr.flush(force=True)
#        self.assertEqual(self.n.buffer.replace('=\n', ''), ('=BC=00/=00=00=0C'+'=00'*45+'U'))

    def testRampUp(self):
        self.ssr.raw_ramp_up(2, 4, 13)      # 4 steps, 13 between
        self.assertEqual(self.n.buffer, b"=CCB=03=0C")
        self.n.reset()

        self.ssr.raw_ramp_down(2, 5, 10)   # 5 steps, 10 between
        self.assertEqual(self.n.buffer, b"=CC=02=04=09")

    def testSpecials(self):
        for cmd, args, result in (
            ('sleep',    [],    b'=FC=00ZZ'),
            ('wake',     [],    b'=FC=01ZZ'),
            ('shutdown', [],    b'=FC=02XY'),
            ('execute',  [123], b'=FC=05{'),
            ('execute',  [0],   b'=FC=05=00'),
            ('clearmem', [],    b'=FC=08CA'),
            ('masksens', ['A'], b'=FC=07=08'),
            ('masksens', ['B'], b'=FC=07=04'),
            ('masksens', ['C'], b'=FC=07=02'),
            ('masksens', ['D'], b'=FC=07=01'),
            ('masksens', ['B','D'], b'=FC=07=05'),
            ('masksens', [],    b'=FC=07=00'),
            ('__reset__', [],   b'=FCs$r'),
            ('__baud__', [4],   b'=FCr=04&'),
            ('__baud__', [0],   b'=FCr=00&'),
            ('__baud__', [7],   b'=FCr=07&'),
            ('noconfig', [],    b'=FCp'),
            ('xconfig',  [],    b'=FCt'),
            ('forbid',   [],    b'=FC=09'),
        ):
            self.ssr.raw_control(cmd, *args)
            self.assertEqual(self.n.buffer, result)
            self.n.reset()

        self.assertRaises(ValueError, self.ssr.raw_control, 'xyzzy')

    def testPhase(self):
        for value, result in (      # Fx 010000pp 0ppppppp 50 4F
            ( 37, b'=FC@%PO'),       #       37=00  0100101=4025=@%
            (500, b'=FCCtPO'),       #      500=11  1110100=4374=Ct
            (511, b'=FCC=7F=7FPO'),     #      511=11  1111111=437F=C<7F>
            (  0, b'=FC@=00PO'),     #        0=00  0000000=4000=@<00>
            (256, b'=FCB=00PO'),     #      256=10  0000000=4200=B<00>
        ):
            self.ssr.raw_set_phase(value)
            self.assertEqual(self.n.buffer, result)
            self.n.reset()
        
    def testNewAddress(self):
        for value, result in (
            ( 0, b'=FC`IAD'),
            ( 1, b'=F0aIAD'),
            ( 2, b'=F1bIAD'),
            ( 3, b'=F2cIAD'),
            ( 4, b'=F3dIAD'),
            ( 5, b'=F4eIAD'),
            (15, b'=F5oIAD'),
            (14, b'=FFnIAD'),
            (13, b'=FEmIAD'),
            (12, b'=FDlIAD'),
            (11, b'=FCkIAD'),
            (10, b'=FBjIAD'),
            ( 6, b'=FAfIAD'),
            ( 9, b'=F6iIAD'),
            ( 8, b'=F9hIAD'),
            ( 7, b'=F8gIAD'),
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
            (  0, bytes([]),        b''),
            ( 13, bytes([1,2,3]),   b'=FC=04\r=02=01=02=03Ds'),
            (127, bytes([200,57,92,19,0,0,0,12]),   
                             b'=FC=04=7F=7F=07~H9\\=13=00=00=00=0CDs'),
        ):
            self.ssr.raw_download_sequence(id, bits)
            self.assertEqual(self.n.buffer, result)
            self.n.reset()

    def DISABLED_testSensorTriggers(self):
        # this is speculative at the moment since it's not implemented.
        # so the test is removed for now.
        for sens, a, b, c, i, m, res in (
               ('A', 1, 2, 3, True, 'once',  b'=FC=06@=01=02=03<'),
               ('B', 55,0, 0, True, 'follow',b'=FC=06!7=00=00<'),
               ('C', 127,3,19,False,'const', b'=FC=06=12=7F=03=13<'),
               ('D', 4, 9,99, False,'follow',b'=FC=063=04\tc<'),
        ):
            self.ssr.raw_sensor_trigger(sens, a, b, c, inverse=i, mode=m)
            self.assertEqual(self.n.buffer, res)
            self.n.reset()

#        self.ssr.ramp_to(2, 255, 2000)
#        # channel 2 is at 25; ramp to 255 over 2000 mS = 
#        self.assertEqual(self.n.buffer, "

    def testFirstInit(self):
        self.ssr.initialize_device()
        #self.assertEqual(self.n.buffer, "=FCa=8C=AC=02=03")      !cfg kill 2=00011001
        #self.assertEqual(self.n.buffer, "=FCp=8C=ACB=0C")      # FC 70 8C AC 42 02 03
        #self.assertEqual(self.n.buffer, "=FCt=8C=ACB=0C")      # FC 74 8C AC 42 02 03
        self.assertEqual(self.n.buffer, b"=FC=09=8C=ACB=0C")     # FC 09 8C AC 42 02 03


    def test_iterator(self):
        self.assertEqual(sorted(self.ssr.iter_channels()), [0, 1, 2, 3])

    def test_optimized_all_off(self):
        self.ssr.kill_all_channels()
        self.ssr.flush()
        self.n.reset()

        self.ssr.flush(force=True)
        self.assertEqual(self.n.buffer, b'=8C')

    def test_config(self):
        con = LumosControllerConfiguration()
        for sens, D, R, res in (
            (['A','B','C','D'], None, 256, b'=FCqx=00:=3D'),
            ([               ],    0, 256, b'=FCq=00=00:=3D'),
            ([    'B','C',   ],  500, 128, b'=FCq7s:=3D'),   
            (['A',           ],  157, 256, b'=FCqE=1C:=3D'),  
            (['A',        'D'], None, 128, b'=FCqH=00:=3D'),
        ):
            con.configured_sensors = sens
            con.dmx_start          = D
            self.ssr.raw_configure_device(con)
            self.assertEqual(self.n.buffer, res)
            self.n.reset()

    # FC 1F 30 50 00 00 40 02 00 4F 01 27 00 00 
    # ----- -- ----- -- ----- ----- ----- -----
    #   |   |    |   |    |     |     |     |   
    #   |   |    |   |    |     |     |     no seq exec; dev=48ssr
    #   |   |    |   |    |     |     free RAM=0127 = 295
    #   |   |    |   |    |     free EEPROM= 004F = 79
    #   |   |    |   |    active=a, phase=2
    #   |   |    |   mask=nil, !priv, !sleep, !overflow
    #   |   vers sensors a,c !dmx
    #   reply from unit C
    #
    # 00 00 00 00 01 00 00 00 10 00 00 00 11 00 00 00 
    # ----------- ----------- ----------- ----------- 
    # sensor a    sensor b    sensor c    sensor d    
    #
    # 12 34 00 02 12 34 33
    # ----- ----- ----- --
    # fault phase  S/N  sentinel
    #
    def test_query(self):
        self.n.input_data(b'\xFC\x1F\x30\x50\x00\x00\x40\x02\x00\x4f\x01\x27\x00\x00'
            + b'\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x12\x34\x00\x02\x12\x34\x33')
        reply = self.ssr.raw_query_device_status()
        self.assertEqual(self.n.buffer, b"=FC=03$T")
        self.assertEqual(reply.config.configured_sensors, ['A','C'])
        self.assertEqual(reply.config.dmx_start, None)
        #self.assertEqual(reply.config.resolution, 256)
        #self.assertEqual(reply.enabled_sensors, [])
        self.assertEqual(reply.rom_version, (3, 0))
        self.assertEqual(reply.sensors['A'].enabled, True, 'sensor A enabled')
        self.assertEqual(reply.sensors['B'].enabled, True, 'sensor B enabled')
        self.assertEqual(reply.sensors['C'].enabled, True, 'sensor C enabled')
        self.assertEqual(reply.sensors['D'].enabled, True, 'sensor D enabled')
        self.assertEqual(reply.sensors['A'].on, True, 'sensor A on')
        self.assertEqual(reply.sensors['B'].on, False, 'sensor B on')
        self.assertEqual(reply.sensors['C'].on, False, 'sensor C on')
        self.assertEqual(reply.sensors['D'].on, False, 'sensor D on')
        self.assertEqual(reply.in_config_mode, False, 'config')
        self.assertEqual(reply.in_sleep_mode, False, 'sleep')
        self.assertEqual(reply.err_memory_full, False, 'memfull')
        #self.assertEqual(reply.sensors_on, ['A'])
        self.assertEqual(reply.phase_offset, 2)
        self.assertEqual(reply.eeprom_memory_free, 0x4f)
        self.assertEqual(reply.ram_memory_free, 0xa7)
        self.assertEqual(reply.current_sequence, None)
        self.assertEqual(reply.hardware_type, 'lumos48ctl')
        self.assertEqual(reply.last_error, 0x12)
        self.assertEqual(reply.last_error2, 0x34)
        self.assertEqual(reply.phase_offset2, 2)
        self.assertEqual(reply.serial_number, 0x1234)

    def test_query_phase_mismatch(self):
        self.n.input_data(b'\xFC\x1F\x30\x50\x00\x00\x40\x02\x00\x4f\x01\x27\x00\x00'
            + b'\x00\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x03\x00\x00\x00\x12\x34\x00\x03\x12\x34\x33')
        self.assertRaises(InternalDeviceError, self.ssr.raw_query_device_status)



# 
# $Log: not supported by cvs2svn $
#
