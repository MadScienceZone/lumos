#  _                              
# | |   _   _ _ __ ___   ___  ___ 
# | |  | | | | '_ ` _ \ / _ \/ __|
# | |__| |_| | | | | | | (_) \__ \
# |_____\__,_|_| |_| |_|\___/|___/
#                                 
# Lumos control API for manual control and simple scripting
# of Lumos-compatible controller units.
#
# For Lumos Hardware Project revision @@RELEASE@@
#
# Copyright (c) 2010, 2011, 2012, 2013, 2022 by Steven L. Willoughby, Aloha,
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
# Previously this code resided in the lumosctl script. Moving here to
# provide a more general approach that can be extended by other 
# Lumos-compatible devices.
#
import configparser
import Lumos
import sys
import re
import time
from   Lumos.Network.SerialNetwork      import SerialNetwork, DeviceTimeoutError
from   Lumos.Device.LumosControllerUnit import LumosControllerUnit, LumosControllerStatus
from   Lumos.Show                       import Show
from   Lumos.PowerSource                import PowerSource
from   Lumos.Hexdump                    import hexdump

class LumosControlAPIError (Exception): pass
class DeviceNotFound (LumosControlAPIError): pass
class DevIOError (LumosControlAPIError): pass
class NotImplemenetedError (LumosControlAPIError): pass
class DeviceConfigurationError (LumosControlAPIError): pass

class ControlAPI:
    """ControlAPI encapsulates a connection to a Lumos device, with high-level
    methods to manipulate and query that device via the underlying Lumos framework,
    along with support for interactive and scripted use."""

    def factory_settings(self):
        return LumosControllerStatus()

    def begin(self):
        "Begin sequence of operations by priming our status cache, etc."
        if not self.read_only:
            self.verifystatus({})

    def __init__(self, address=0, duplex='full', port=0, speed=19200, txmode='dtr', timeout=1, txlevel=1, txdelay=2, main_output=sys.stdout, trace_file=sys.stderr, probe=False, read_only=False, verbose=0, from_cli=None):
        """Set up the API to talk to a device.
        
        main_output=sys.stdout  send informative output here (unless None)
        trace_file=sys.stderr   send debugging info here (unless None)
        from_cli                options from CLI (alternative to individual args)
        """
        self.devices = []
        self.status_cache = None
        self.address = address
        self.duplex  = duplex
        self.port    = port
        self.do_probe = probe
        self.read_only = read_only
        self.speed = speed
        self.timeout = timeout
        self.txdelay = txdelay
        self.txlevel = txlevel
        self.txmode = txmode
        self.verbose = verbose
        self.trace_file = trace_file
        self.main_output = main_output

        if from_cli:
            if from_cli.address   is not None: self.address = from_cli.address
            if from_cli.duplex    is not None: self.duplex = from_cli.duplex
            if from_cli.port      is not None: self.port = from_cli.port
            if from_cli.probe     is not None: self.do_probe = from_cli.probe
            if from_cli.read_only is not None: self.read_only = from_cli.read_only
            if from_cli.speed     is not None: self.speed = from_cli.speed
            if from_cli.timeout   is not None: self.timeout = from_cli.timeout
            if from_cli.txdelay   is not None: self.txdelay = from_cli.txdelay
            if from_cli.txlevel   is not None: self.txlevel = from_cli.txlevel
            if from_cli.txmode    is not None: self.txmode = from_cli.txmode
            if from_cli.verbose   is not None: self.verbose = from_cli.verbose

        #
        # validate options
        #
        if not 0 <= self.address <= 15:
            raise ValueError('valid unit addresses are in the range 0..15 only')

        if self.duplex not in ['full', 'half']:
            raise ValueError('duplex value must be "full" or "half"')

        if self.txmode not in ['dtr', 'rts']:
            raise ValueError('txmode value must be "dtr" or "rts"')

        if not 0 <= self.txlevel <= 1:
            raise ValueError('txlevel value must be 0 or 1')

        if not 0 <= self.txdelay <= 127:
            raise ValueError('txdelay value must be 0-127')

        self._setup_lumos()

        if self.verbose > 2:
            self.io.set_verbose(trace_file)

        if self.do_probe:
            self.devices = self.probe()
        elif self.read_only:
            self.devices = [(self.address, None)]
        else:
            self.devices = [(self.address, self.getstatus())]

        if not self.devices:
            raise DeviceNotFound('no target device found')

    def trace(self, level, msg, stream=None, eol=True):
        if stream is None:
            stream = self.trace_file
        if self.verbose >= level:
            stream.write(msg)
            if eol:
                stream.write('\n')
            else:
                stream.flush()

    def report_on(self, device):
        if not self.main_output:
            return

        if not device:
            self.main_output.write('No device information to report.')
            return

        self.main_output.write(f'''\
Device Type:            {device.hardware_type} ({device.channels} channels)
Serial Number:          {device.serial_number or "N/A"}
ROM Revision:           {device.revision[0]}.{device.revision[1]}.{device.revision[2]}  (deprecated field {device.rom_version[0]}.{device.rom_version[1]})
Lumos Protocol:         {device.protocol}
Configuration Mode:     {"ON" if device.in_config_mode else "OFF"}
Resume Configuration:   {"FORBIDDEN" if device.config_mode_locked else "Allowed"}
Sleep Mode:             {"ON" if device.in_sleep_mode  else "OFF"}
Currently Executing:    {device.current_sequence or "Nothing"}
EEPROM Memory Free:     {device.eeprom_memory_free:04d}
RAM Memory Free:        {device.ram_memory_free:04d}
Last Memory Write:      {"*ERROR* MEMORY FULL" if device.err_memory_full else "Successful"}
Phase Offset:           CPU0 {device.phase_offset:04d}; CPU1 {device.phase_offset2:04d}
''')
        if device.hardware_type == 'lumos48ctl':
            self.main_output.write(f'Last Fault Condition:   CPU0 0x{device.last_error:02X}; CPU1 0x{device.last_error2:02X}\n')
        else:
            self.main_output.write(f'Last Fault Condition:   0x{device.last_error << 16 | device.last_error2:04X}\n')

        if device.config.dmx_start is None:
            self.main_output.write(f'DMX Mode:               OFF\n')
        else:
            self.main_output.write(f'DMX Mode:               Channel #0-{device.channels - 1} is DMX #{device.config.dmx_start}-{device.config.dmx_start + device.channels - 1}\n')

        if not device.config.configured_sensors:
            self.main_output.write("No configured sensors.\n")
        else:
            self.main_output.write("SENSORS  ENABLED LOGIC ACTIVE MODE   PRE TRG PST\n")
            for sensor in device.config.configured_sensors:
                self.main_output_write("   {0}     {1:3s}     {2:4s}  {3:3s}    {4:6s} {5:3d} {6:3d} {7:3d}\n".format(
                    sensor,
                    'Yes' if device.sensors[sensor].enabled else 'No',
                    '----',
    #                'Low' if device.sensors[sensor].active_low else 'High',
                    'Yes' if device.sensors[sensor].on else 'No',
    #                device.sensors[sensor].trigger_mode,
                    '------',
                    device.sensors[sensor].pre_trigger,
                    device.sensors[sensor].trigger,
                    device.sensors[sensor].post_trigger,
                ))
        
        self.main_output.write(f'Model-Specific Data:    {len(device.model_specific_data)} bytes\n')
        hexdump(device.model_specific_data, output=self.main_output)


    def probe(self):
        devices = []
        old_address = self.target.address

        for address in range(16):
            self.trace(1, f'Probing io.{address:02d}...', eol=False)
            self.target.address = address
            try:
                device = self.target.raw_query_device_status(timeout=self.timeout)
            except DeviceTimeoutError:
                self.trace(1, "nothing detected")
            else:
                self.trace(1, device.hardware_type)
                devices.append((address, device))

        self.target.address = old_address
        if self.main_output is not None:
            self.main_output.write(f'Probe discovered {len(devices)} device{"s." if len(devices) == 0 else (":" if len(devices) == 1 else "s:")}\n')
        return devices


    def getstatus(self):
        try:
            devstatus = self.target.raw_query_device_status(timeout=self.timeout)
        except DeviceTimeoutError as e:
            raise DevIOError(f'no response received from device at address {self.target.address} (read {len(e.read_so_far)} byte{"" if not e.read_so_far else "s"} before timeout)')
        return devstatus

    def factory_reset(self):
        self.assert_priv('factory-reset')
        self.trace(0, '** Returning device to factory settings **')
        self.target.raw_control('__reset__')
        self.trace(0, '** Waiting 10 seconds for device to reset **')
        time.sleep(10)
        self.io.set_baud_rate(19200)
        self.target.address = 0
        self.trace(1, 'Baud rate reset to 19.2k due to factory setting reset')
        self.trace(1, 'Device should now be at address 0 due to factory setting reset')
        self.trace(0, '** Verifying board settings...')
        if not self.read_only: self.verifystatus(baseline=self.factory_settings())

    def set_phase(self, offset):
        self.assert_priv('set-phase')
        self.trace(1, f'Setting phase offset to {offset}')
        self.target.raw_set_phase(offset)
        if not self.read_only: self.verifystatus({'phase_offset': offset})

    def drop_config_mode(self):
        self.assert_priv('drop-configuration-mode')
        self.target.raw_control('noconfig')
        if not self.read_only: self.verifystatus({'in_config_mode': False})

    def sleep(self):
        self.trace(1, "Putting unit to sleep")
        self.target.raw_control('sleep')
        if not self.read_only: self.verifystatus({'in_sleep_mode' : True})

    def perform_actions_from_cli(self, options):
        if options.set_address is not None:
            self.assert_priv('set-address')
            self.target.raw_set_address(options.set_address)
            # XXX does this update target's address?

        if options.set_baud_rate is not None:
            self.assert_priv('set-baud-rate')
            self.change_speed(options.set_baud_rate)

        if options.factory_reset:
            self.factory_reset()

        if options.set_phase:
            self.set_phase(options.set_phase)

        if options.load_configuration_file:
            self.assert_priv('load-configuration-file')
            new_config = self.load_configuration(options.load_configuration_file)

        if options.dump_configuration_file:
            self.dump_configuration(options.dump_configuration_file)

        if options.drop_configuration_mode:
            self.drop_config_mode()

#        def smask(opt, delete=False):
#            s = set([i.id for i in list(self.status_cache.sensors.values()) if i.enabled])
#            expected = dict([(id, self.status_cache.sensors[id].copy()) for id in 'ABCD'])
#
#            if '*' in opt:
#                opt = 'ABCD'
#
#            for o in opt.upper():
#                if o in 'ABCD':
#                    if delete:
#                        s.discard(o)
#                    else:
#                        s.add(o)
#                    expected[o].enabled = not delete
#                else:
#                    raise ValueError("sensors are A, B, C, and D")
#
#            self.target.raw_control('masksens', s)
#            if not self.read_only: self.verifystatus({'sensors': expected})
#
#        for sens_id, sens_opt, sens_pre, sens_trig, sens_post in sensor_triggers:
#            old = self.status_cache.sensors
#            new = dict([(id, self.status_cache.sensors[id].copy()) for id in self.status_cache.sensors])
#
#            new[sens_id].active_low = ('+' not in sens_opt)
#            new[sens_id].pre_trigger = sens_pre
#            new[sens_id].trigger = sens_trig
#            new[sens_id].post_trigger = sens_post
#            new[sens_id].trigger_mode = (
#                'while'  if 'W' in sens_opt else
#                'repeat' if 'R' in sens_opt else
#                'once'
#            )
#            self.target.raw_sensor_trigger(sens_id, sens_pre, sens_trig, sens_post, 
#                inverse = not new[sens_id].active_low,
#                mode = new[sens_id].trigger_mode
#            )
#            if not self.read_only: self.verifystatus({'sensors': new})
#
#        if options.disable_sensor: smask(self.target, options.disable_sensor, delete=True)
#        if options.enable_sensor:  smask(self.target, options.enable_sensor)

        #
        # Sequence Management
        #
#        if options.clear_sequences:
#            self.target.raw_control('clearmem')
#            if self.main_output is not None:
#                self.main_output.write("Sequences cleared.  Available memory now: EEPROM={0.eeprom.memory.free}, RAM={0.ram_memory_free}\n".format(self.getstatus()))
#
#        if options.load_sequence:
#            raise NotImplementedError('the load-sequence option is not yet implemented; use load-compiled-sequence instead')
#
#        if options.load_compiled_sequence is not None:
#          for filename in options.load_compiled_sequence:
#            #
#            # file:
#            # #{$<hexid>|<decid>}
#            # $<hex byte> <space> <hex byte> ...
#            # ...
#            # @<dec_#_bytes>
#            #
#            sequence_bits = []
#            length = None
#            with open(filename, 'r') as infile:
#                for line in infile:
#                    if line[0] == '#':
#                        if line[1] == '$':
#                            id = int(line[2:], 16)
#                        else:
#                            id = int(line[1:])
#                    elif line[0] == '$':
#                        for byte in line[1:].split():
#                            sequence_bits.append(ord(int(byte, 16)))
#                    elif line[0] == '@':
#                        length = int(line[1:])
#                        break
#                    else:
#                        raise ValueError('invalid line in compiled sequence file {0}: {1}'.format(filename, line))
#
#            if length is None:
#                raise ValueError('missing @ record from compiled sequence file {0}'.format(filename))
#
#            if length != len(sequence_bits):
#                raise ValueError('compiled sequence file {0} claims {1} byte{2} but actually read {3}'.format(
#                    filename, length, '' if length==1 else 's', len(sequence_bits)))
        #
        # Misc
        #
        if options.kill_all:
            self.trace(1, 'Killing all channel outputs')
            self.target.kill_all_channels(force=True)

        if options.sleep:
            self.sleep()

        if options.wake:
            self.wake()
        #
        # kill the device if requested
        #
        if options.shutdown:
            self.target.raw_control('shutdown')
        #
        # send raw data bytes to the device
        # (we will impose the 7/8-bit protocol automatically)
        #
        if options.send:
            # yes, I know it's wrong to call a private method, but really this should
            # not be private to us.
            #send_buffer = target._8_bit_string([int(i, 16) for i in options.send.split()])
            send_buffer = ''.join([chr(int(i, 16)) for i in options.send.split()])
            if self.main_output is not None:
                self.main_output.write("Sending {0} byte{1} to device:\n".format(len(send_buffer), '' if len(send_buffer)==1 else 's'))
            hexdump(send_buffer, output=self.main_output)
            self.target.flush()
            self.target.network.send(send_buffer)
            self.target.flush()
        #
        # receive raw data bytes from the device
        # (we will interpret the 7/8-bit protocol automatically)
        #
        if options.receive:
            if self.main_output is not None:
                self.main_output.write("Receiving {0} byte{1} from device...\n".format(options.receive,
                '' if options.receive == 1 else 's'))
            rec_buffer = ''
            try:
                rec_buffer = self.target.network.input(bytes=options.receive, timeout=self.timeout)
            except DeviceTimeoutError:
                self.trace(0, "(read timed out)")
            #hexdump(target._8_bit_decode_string([ord(i) for i in rec_buffer]))
            hexdump(rec_buffer, output=self.main_output)

        self.report_on_all_devices(options.report)

    def wake(self):
        self.trace(1, "Waking up unit")
        self.target.raw_control('wake')
        if not self.read_only: self.verifystatus({'in_sleep_mode' : False})

    def run_script(self, filename):
        pass

    def interactive(self):
        "Prompt the user to enter commands interactively"
        print('Type "help" for a list of commands.')
        print('End with EOF or "quit".')
        command_list = self.get_command_list()
        while True:
            try:
                cmd = input('> ')
            except EOFError:
                return

            args = cmd.split()
            if args[0] == 'quit':
                return

            try:
                if args[0].startswith('/'):
                    self.assert_priv(args[0])

                if args[0] in command_list:
                    if command_list[args[0]][0] is None:
                        command_list[args[0]][1](args[1:])
                    else:
                        if len(args) != command_list[args[0]][0] + 1:
                            print(f"Arg count wrong. Usage: {command_list[args[0]][2]}")
                            continue

                        if command_list[args[0]][3]:
                            args[1] = int(args[1])

                        command_list[args[0]][1](*args[1:])
                else:
                    print('Unrecognized command. Type "help" for a list of commands.')
            except Exception as e:
                print(f'*Error: {e}')

    def get_command_list(self):
        return {
                'help':           (0, self.help, 'help', False),
                'query':          (0, self.query, 'query', False),
                '/set-address':   (1, self.target.raw_set_address, '/set-address <addr>', True),
                '/set-baud-rate': (1, self.change_speed, '/set-baud-rate <speed>', True),
                '/factory-reset': (0, self.factory_reset, '/factory-reset', False),
                '/set-phase':     (1, self.set_phase, '/set-phase <offset>', True),
                '/load-configuration': (1, self.load_configuration, '/load-configuration <file>', False),
                '/dump-configuration': (1, self.dump_configuration, '/dump-configuration <file>', False),
                '/drop-config-mode': (0, self.drop_config_mode, '/drop-config-mode', False),
                'forbid-config-mode': (0, lambda: self.target.raw_control('forbid'), 'forbit-config-mode', False),
                'config-mode': (0, lambda: self.target.raw_control('config'), 'config-mode', False),
                'kill-all': (0, lambda: self.target.kill_all_channels(force=True), 'kill-all', False),
                'sleep': (0, self.sleep, 'sleep', False),
                'wake': (0, self.wake, 'wake', False),
                'shutdown': (0, lambda: self.target.raw_control('shutdown'), 'shutdown', False),
                'do': (None, self.perform_operations, 'do <op> <op>...', False),
            }

    def query(self):
        self.report_on(self.getstatus())

    def help(self):
        print('''Interactive commands:
config-mode                enter config mode
do <operation> [...]       perform channel operation(s)
    <channel>@<level>[,<level>...]
    <channel>              (fully on)
    <channel>[c]u[:<steps>[:<delay>]]
    <channel>[c]d[:<steps>[:<delay>]]
    x<sequence>
forbid-config-mode         prevent config mode
help                       print this text
kill-all                   kill all outputs
query                      report on device status
quit                       exit interactive mode
shutdown                   shut down device 
sleep                      put device to sleep
wake                       wake device from sleep

Config Mode Commands
/drop-config-mode          leave config mode
/dump-configuration <file> save state to file
/factory-reset             restore default settings
/load-configuration <file> configure from file
/set-address <addr>        change device address
/set-baud-rate <speed>     change device speed
/set-phase <offset>        change phase offset
''')




    def _setup_lumos(self):
        self.show = Show()
        self.show.title = 'lumosctl'
        self.show.description = 'Lumos Configuration Utility'
        self.ps = PowerSource('power')
        self.io = SerialNetwork(
            description='Serial port for Lumos devices',
            port = self.port,
            baudrate = self.speed,
            bits = 8,
            parity = 'none',
            stop = 1,
            xonxoff = False,
            rtscts = False,
            duplex = self.duplex,
            txmode = self.txmode,
            txlevel = self.txlevel,
            txdelay = self.txdelay,
        )
        self._setup_unit()

    def _setup_unit(self):
        self.target = LumosControllerUnit(
            id='target',
            power_source = self.ps,
            network = self.io,
            address = self.address,
            num_channels = 48,
        )
        self.show.add_network('io', self.io)
        self.show.add_controller('io', self.target)
        for channel_id in range(48):
            self.target.add_channel(channel_id, load=0)

    def verifystatus(self, fields=None, baseline=None):
        "Get the target's current status and compare with the baseline settings"

        if fields is None:
            fields = {
                'config': baseline.config, 
                'in_config_mode': baseline.in_config_mode, 
                'in_sleep_mode': baseline.in_sleep_mode,
                'phase_offset': baseline.phase_offset, 
                'current_sequence': baseline.current_sequence, 
                'sensors': baseline.sensors,
            }

        self.status_cache = self.getstatus()
        for field in fields:
            if self.status_cache.__getattribute__(field) != fields[field]:
                raise DeviceConfigurationError(f"device's configuration not as expected ({field}={self.status_cache.__getattribute__(field)}, expected {fields[field]})")

    def assert_priv(self, operation):
        if self.read_only:
            if self.main_output is not None:
                self.main_output.write("**WARNING: In Read-only mode, can't verify board is in configuration mode.\n")
            return

        if not self.status_cache.in_config_mode:
            if self.main_output is not None:
                self.main_output.write(f"**WARNING: The Lumos board is not in the configuration mode required by {operation}.\n")

    def change_speed(self, new_speed):
        self.trace(1, f"Changing baud rate to {new_speed}")
        supported_speeds = {
               300:  0,
               600:  1,
              1200:  2,
              2400:  3,
              4800:  4,
              9600:  5,
             19200:  6,
             38400:  7,
             57600:  8,
            115200:  9,
            250000: 10,
            500000: 11,
           1000000: 12,
           2000000: 13,
           2500000: 14,
           5000000: 15,
          10000000: 16,
        }
        if new_speed not in supported_speeds:
            raise ValueError("new baud rate must be one of {0}".format(', '.join(map(str, list(supported_speeds.keys())))))
        self.trace(2, "Changing device's configured speed...")
        self.target.raw_control('__baud__', supported_speeds[new_speed])
        time.sleep(1)
        self.trace(2, "Changing our serial port's configured speed...")
        self.io.set_baud_rate(new_speed)
        time.sleep(1)
        self.trace(2, "Verifying...")
        if not self.read_only:
            self.getstatus()   # try talking to it at the new speed
        self.speed = new_speed

    def dump_configuration(self, filename):  # ..., stat):
        self.trace(1, f"Writing configuration to {filename}")
        writer = configparser.SafeConfigParser()
        config = self.getstatus()
        writer.add_section('lumos_device_settings')
        for field, opt in (
            (config.config.dmx_start, 'dmxchannel'),
    #        (config.resolution, 'resolution'),
            (config.phase_offset, 'phase'),
            (self.speed, 'baud'),
            (''.join(config.config.configured_sensors), 'sensors'),
        ):
            if field is not None:
                writer.set('lumos_device_settings', opt, str(field))
        
        for s in config.config.configured_sensors:
            k = 'lumos_device_sensor_' + s
            d = config.sensors[s]
            writer.add_section(k)
            writer.set(k, 'active_low', 'yes' if d.active_low else 'no')
            writer.set(k, 'enabled',    'yes' if d.enabled    else 'no')
            writer.set(k, 'setup',      str(d.pre_trigger))
            writer.set(k, 'sequence',   str(d.trigger))
            writer.set(k, 'terminate',  str(d.post_trigger))
            writer.set(k, 'mode',       str(d.trigger_mode))

        with open(filename, 'w') as outfile:
            writer.write(outfile)
            
    
    def load_configuration(self, filename):
        def getint(p, field, minimum=None, maximum=None, section='lumos_device_settings'):
            i = p.getint(section, field)
            if minimum is not None and i < minimum:
                raise ValueError('Lumos configuration value "{0}" cannot be less than {1}.]'.format(
                    field, minimum))
            if maximum is not None and i > maximum:
                raise ValueError('Lumos configuration value "{0}" cannot be greater than {1}.]'.format(
                    field, maximum))

            return i

        self.trace(1, f"Reading configuration file from {filename}")
        config = LumosControllerStatus()
        parser = configparser.SafeConfigParser()
        parser.read(filename)

        if parser.has_option('lumos_device_settings', 'dmxchannel'):
            config.config.dmx_start = getint(parser, 'dmxchannel', 1, 512)
        else:
            config.config.dmx_start = None

        #config.resolution = getint(parser, 'resolution')
        #if config.resolution not in (128, 256):
            #raise ValueError('Lumos configuration value "resolution" must be 128 or 256.')

        config.phase_offset = getint(parser, 'phase', 0, 511)
        baud_rate = getint(parser, 'baud', 300)
        if baud_rate != self.speed:
            self.trace(1, "** Changing baud rate of device from {0} to {1}".format(
                self.speed, baud_rate))
            self.change_speed(baud_rate)
        
        # XXX default values from config file??

        for s in parser.get('lumos_device_settings', 'sensors').upper().strip():
            if s not in "ABCD":
                raise ValueError('Lumos configuration value "sensors" requires letters A, B, C, and/or D.')
            if s not in config.config.configured_sensors:
                config.config.configured_sensors.append(s)
            k = 'lumos_device_sensor_' + s
            if not parser.has_section(k):
                self.trace(0, "WARNING: missing ["+k+"] section; assuming default values")
                config.sensors[s].configured = True
            else:
                config.sensors[s].configured = True
                config.sensors[s].active_low = parser.getboolean(k, 'active_low')
                config.sensors[s].enabled = parser.getboolean(k, 'enabled')
                config.sensors[s].pre_trigger = getint(parser, 'setup', 0, 127, k)
                config.sensors[s].trigger = getint(parser, 'sequence', 0, 127, k)
                config.sensors[s].post_trigger = getint(parser, 'terminate', 0, 127, k)
                config.sensors[s].trigger_mode = parser.get(k, 'mode')
                if config.sensors[s].trigger_mode not in ('once', 'while', 'repeat'):
                    raise ValueError('Lumos configuration value "["+k+"] mode must be "once", "while", or "repeat".')

        self.target.raw_configure_device(config.config)
        time.sleep(2)
        if not self.read_only: verifystatus(target, {'config': config.config})

        try:
            if config.phase_offset != self.status_cache.phase_offset:
                self.trace(1, "Changing phase offset from {0} to {1} (per {2})".format(status_cache.phase_offset,
                    config.phase_offset, filename))
                self.target.raw_set_phase(config.phase_offset)
                if not self.read_only: self.verifystatus({'phase_offset': config.phase_offset})
        except:
            self.trace(0, "WARNING: unable to read/update device phase offset (benign in read-only mode)")

            # XXX raw_sensor_trigger(sens_id, i, p, t, inverse, mode)
            # XXX 

    def report_on_all_devices(self, report=True):
        if self.main_output is not None:
            for address, devstat in self.devices:
                self.main_output.write(f'Address {address:02d}: {devstat.hardware_type if devstat else "N/A"}\n')
                if report:
                    self.report_on(devstat)

    def perform_operations(self, operations):
        for action in operations:
            m = re.match(r'^(\d+)@(\d+(,\d+)*)$', action)
            if m:
                # <channel>@<level>[,<level>...]
                start_chan = int(m.group(1))
                levels = [int(x) for x in m.group(2).split(',')]

                for idx, level in enumerate(levels):
                    if not self.read_only and self.status_cache.channels and not 0 <= start_chan + idx < self.status_cache.channels:
                        raise ValueError("{0}: channel number {1} does not exist for this controller model (valid range is [0,{2}])".format(
                            action, start_chan + idx, status_cache.channels - 1))
                    self.target.set_channel(start_chan + idx, level)
                self.target.flush()

            else:
                m = re.match(r'^\d+$', action)
                # <channel>
                if m:
                    channel = int(action)
                    if not self.read_only and self.status_cache.channels and not 0 <= channel < self.status_cache.channels:
                        raise ValueError("{0}: channel number {1} does not exist for this controller model (valid range is [0,{2}])".format(
                            action, channel, status_cache.channels - 1))
                    self.target.set_channel(channel, 255)
                    self.target.flush()
                else:
                    m = re.match(r'^(\d+)(c?[ud])(:(\d+)(:(\d*\.\d+|\d+\.?)(s(ec(onds?)?)?)?)?)?(c?)$', action)
                    # <channel>[c]u[:<steps>[:<delay>]]
                    if m:
                        channel = int(m.group(1))
                        steps = int(m.group(4) or 1)
                        if m.group(7):
                            delay = int(float((m.group(6) or 1) * 120))
                            self.trace(1, "Using {0}/120 sec for {1} sec".format(delay, m.group(4)))
                        else:
                            delay = int(m.group(6) or 1)

                        if not 1 <= steps <= 128:
                            raise ValueError("{0}: step value of {1} not in required range [1,128]".format(action, steps))

                        if not 1 <= delay <= 128:
                            raise ValueError("{0}: delay value of {1} not in required range [1,128]".format(action, delay))

                        if not self.read_only and self.status_cache.channels and not 0 <= channel < self.status_cache.channels:
                            raise ValueError("{0}: channel number {1} does not exist for this controller model (valid range is [0,{2}])".format(
                                action, channel, status_cache.channels - 1))

                        if 'u' in m.group(2):
                            self.target.raw_ramp_up(channel, steps, delay, cycle=('c' in m.group(2)))
                        else:
                            self.target.raw_ramp_down(channel, steps, delay, cycle=('c' in m.group(2)))
                    else:
                        m = re.match(r'^x(\d+)$', action)
                        if m:
                            sequence = int(m.group(1))
                            if not 0 <= sequence <= 127:
                                raise ValueError("{0}: sequence number {1} outside valid range [0, 127]".format(action, sequence))
                            self.target.raw_control('execute', sequence)
                        else:
                            m = re.match(r'^p(\d*\.\d+|\d+\.?)(s(ec(onds?)?)?)?$', action)
                            if m:
                                wait_for = float(m.group(1))
                                self.trace(1, "pausing {0} sec...".format(wait_for))
                                time.sleep(wait_for)
                                self.trace(2, "resuming after pause")
                            else:
                                raise ValueError("{0}: Unrecognized action".format(action))
