# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS EVENT SEQUENCE CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Sequence.py,v 1.6 2008-12-31 00:25:19 steve Exp $
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
import csv
from Event      import Event
from ValueEvent import ValueEvent

class InvalidFileFormat (Exception): pass
class InvalidTimestamp (Exception): pass
class InvalidUnitDefinition (Exception): pass
class InvalidEvent (Exception): pass
class InvalidAudioDefinition (Exception): pass
class InvalidSequence (Exception): pass

class AudioTrack (object):
    """Audio track in the sequence.

    Public attributes:

    filename:     the filename of the audio sample.
    volume:       intended playback volume (0-100)
    channels:     1=mono, 2=stereo.
    frequency:    sample frequency (Hz).
    bits:         sample size (bits): <0=signed, >0=unsigned.
    bufsize:      intended buffer size for playback.
    """

    def __init__(self, filename, volume=100, channels=2, frequency=44100, bits=-16, bufsize=4096):
        self.filename = filename
        self.volume = volume
        self.channels = channels
        self.frequency = frequency
        self.bits = bits
        self.bufsize = bufsize

class Sequence (object):
    """The Sequence class represents an ordered collection of Events.

    The following attributes are publicly available:

    total_time:   the duration of the sequence.  Note that the 
                  duration may extend past the last event 
                  timestamp if there are any events which are
                  not instantaneous and still running at that
                  point.  Integer, measured in milliseconds.

    intervals:    an iterable object which will yield, in
                  chronological order, all of the event time
                  stamps in the sequence.
    
    """

    # in order to keep them in time order regardless of the order
    # events were added to them, we'll use a hash to store them, 
    # indexed by timestamp.  Each hash contains a list of all events
    # occurring at that time.  The events at each time stamp are 
    # (currently) retained in the order added to the sequence.

    def __init__(self):
        self.total_time = 0
        self._controllers = []
        self._event_list = {}
        self._vchannels = []
        self._vchannel_index = {}
        self.audio = None

    def load_file(self, filename, controller_map, virtual_channel_map):
        """
        Populate this sequence object with the events described in the named
        sequence file.  This is not safe to call more than once.

        controller_map:     A dictionary which maps controller unit IDs
                            to actual ControllerUnit objects.  Controllers
                            mentioned in the sequence file must be defined
                            in this map to be legal.

        virtual_chanel_map: A dictionary which maps virtual channel IDs
                            to actual VirtualChannel objects.  Virtual
                            channels mentioned in the sequence file must
                            be defined in this map to be legal.
        """

        csvfile = file(filename, 'rb')
        csvreader = csv.reader(csvfile)

        version = None
        timestamp = None

        for record in csvreader:
            #
            # Vn[,...]
            #    first record contains Vn (version #n of the file format)
            #    all other fields ignored, can be used for comments
            #
            if record[0][0] == 'V':
                try:
                    version = int(record[0][1:])
                except ValueError:
                    raise InvalidFileFormat('Cannot understand Vn record at all')

                if version == 1:
                    raise InvalidFileFormat('Lumos sequence file format version 1 is deprecated and no longer supported.')

                if not 2 <= version <= 4:
                    raise InvalidFileFormat('This version of Lumos only supports sequence file formats V2, V3, and V4.')
            #
            # ----- below this point, you need to have seen the Vn record -----
            #
            elif version is None:
                raise InvalidFileFormat('No Vn record found before real data!')
            #
            # A,filename,volume,channels,freq,bits,bufsize
            #    audio playback properties (if any)
            #
            # [V2 V3 V4]
            #
            elif record[0] == 'A':
                def int_or_else(v, default):
                    if v is None or v.strip() == '':
                        return default
                    return int(v)

                if version < 3:
                    raise InvalidFileFormat('The A record does not exist in file formats < V3')

                if not 2 <= len(record) <= 7:
                    raise InvalidAudioDefinition('Badly formed A record "%s"' % record)
                record += [None] * 5    # fill in defaults
                self.audio = AudioTrack(
                        filename = record[1],
                        volume=   int_or_else(record[2],   100),
                        channels= int_or_else(record[3],     2),
                        frequency=int_or_else(record[4], 44100),
                        bits=     int_or_else(record[5],   -16),
                        bufsize=  int_or_else(record[6],  4096)
                )
            #
            # C,type,channelname[,...]
            #    declare one or more virtual channels
            #
            # [V4]
            #
            elif record[0] == 'C':
                if version < 4:
                    raise InvalidFileFormat('C records are not legal before sequence file format V4.')
                if len(record) < 3:
                    raise InvalidUnitDefinition('Badly formed C record "%s"' % record)
                for vchannel_id in record[2:]:
                    if vchannel_id not in virtual_channel_map:
                        raise InvalidUnitDefinition('Unknown channel name "{0}" used in sequence'.format(vchannel_id))

                    if virtual_channel_map[vchannel_id].type != record[1]:
                        raise InvalidUnitDefinition('Sequence file wants channel "{0}" to be type "{1}", but the show defines it to be type "{2}"'.format(
                            vchannel_id, record[1], virtual_channel_map[vchannel_id].type))
                
                    self._vchannels.append(virtual_channel_map[vchannel_id])
            #
            # OBSOLETE - DEPRECATED
            # U,unitname,channelname[,...]
            #    declare a controller unit and its channels
            #
            # [V2 V3]
            #
            elif record[0] == 'U':
                if version > 3:
                    raise InvalidFileFormat('U records are not legal after sequence file format V3.')
                if len(record) < 3:
                    raise InvalidUnitDefinition('Badly formed U record "%s"' % record)
                if record[1] not in controller_map:
                    raise InvalidUnitDefinition('Unknown controller unit "%s" used in sequence' % record[1])

                target_controller = controller_map[record[1]]
                self._controllers.append({
                    'obj': target_controller,
                    'fld': [],
                    'vob': []
                })
                # adjust channel names to be of appropriate type for controller
                for channel_id in record[2:]:
                    # find the virtual channel for this
                    c_id = target_controller.channel_id_from_string(channel_id)
                    c_obj = target_controller.channels[c_id]
                    for v_id in virtual_channel_map:
                        vc = virtual_channel_map[v_id].channel
                        if isinstance(vc, (list,tuple)):
                            if c_obj in vc:
                                raise NotImplementedError("This version of Lumos doesn't support adapting old sequence files to complex virtual channel types; can't handle {0}->{1}.".format(
                                    c_id, v_id))
                        elif c_obj is vc:
                            v_obj = virtual_channel_map[v_id]
                            break
                    else:
                        raise InvalidSequence("Sequence channel #{0} (hardware {1}.{2}) doesn't seem to have a virtual channel!".format(
                            len(self._vchannels), record[1], channel_id))
                            
                    # v_obj is now the virtual channel object for this
                    self._controllers[-1]['fld'].append(target_controller.channel_id_from_string(channel_id))
                    self._controllers[-1]['vob'].append(v_obj)
                    self._vchannels.append(v_obj)
            #
            # T,timestamp
            #    mark time (milliseconds from start of sequence)
            #
            elif record[0] == 'T':
                try:
                    timestamp = int(record[1])
                except:
                    raise InvalidTimestamp('Cannot understand timestamp record "%s"' % record)
            #
            # ----- below this point, you need to have a timestamp in effect -----
            #
            elif timestamp is None:
                raise InvalidTimestamp('No timestamp given for events in file at "%s"' % record)
            #
            # EV,vch,v,dT
            #    value event: change value of virtual channel vch to v over dT milliseconds
            #    v is whatever is appropriate for the channel type
            #
            elif record[0] == 'EV':
                if version < 4:
                    raise InvalidFileFormat('EV records are only available in sequence file format version 2 and 3.')

                try:
                    delta = int(record[3])

                    extent = timestamp + delta
                    if extent > self.total_time:
                        self.total_time = extent

                    if timestamp not in self._event_list:
                        self._event_list[timestamp] = []

#                    if record[1] == '*':
#                        raise NotImplementedError("Lumos does not currently support wildcards in sequence files")

                    self._event_list[timestamp].append(
                        ValueEvent(None if record[1] == '*' else self._vchannels[int(record[1])], 
                            record[2], int(record[3])
                        )
                    )

                except InvalidEvent:
                    raise
                except Exception as e:
                    raise InvalidEvent('Cannot understand event description "%s" (%s)' % (','.join(record), e))

            #
            # OBSOLETE - DEPRECATED
            # E,u,ch,v,dT
            #    event: change value of unit u's channel ch to v% over dT milliseconds
            #
            elif record[0] == 'E':
                if version > 3:
                    raise InvalidFileFormat('E records are depreceated; not available in file formats after V3.')

                try:
                    delta = int(record[4])

                    extent = timestamp + delta
                    if extent > self.total_time:
                        self.total_time = extent

                    if timestamp not in self._event_list:
                        self._event_list[timestamp] = []

                    if record[1] == '*' and record[2] != '*':
                        raise InvalidEvent('Channel must be "*" if controller ID is "*" in "%s"' % record)

                    if record[2] == '*' and record[1] != '*':
                        raise InvalidEvent('Wildcard channel changes (except system-global) no longer supported (Must be "*,*" or specific channel).')

                    self._event_list[timestamp].append(
                        ValueEvent(
                            (None if record[1] == '*' 
                                else self._controllers[int(record[1])]['vob'][int(record[2])]), 
                            float(record[3]), 
                            int(record[4])
                        )
                    )

# ValueEvent(virtualchannelobj, newlevel, interval)

#                       Event(None if record[1] == '*' else self._controllers[int(record[1])]['obj'],
#                             None if record[2] == '*' else self._controllers[int(record[1])]['fld'][int(record[2])],
#                             float(record[3]), int(record[4])))
                
                except InvalidEvent:
                    raise
                except Exception as e:
                    raise InvalidEvent('Cannot understand event description "%s" (%s)' % (','.join(record), e))

            #
            # #... comments
            #
            elif record[0].startswith('#'):
                pass
            else:
                raise InvalidFileFormat('Unrecognized sequence record "{0}"'.format(
                    ','.join(record)))

    def _build_vchannel_list(self):
        self._vchannel_index = {}

        for i, vchannel in enumerate(self._vchannels):
            if id(vchannel) in self._vchannel_index:
                raise InvalidSequence('Duplicate virtual channel found in sequence ("id={0}, name={1}")'.format(
                    vchannel.id, vchannel.name))
            self._vchannel_index[id(vchannel)] = i

        self._all_controllers = set([c.controller for v in self._vchannels for c in v.all_hardware_channels()])
        self._all_networks = set([c.network for c in self._all_controllers])

#    def _build_controller_list(self):
#        self._controllers = []
#        self._controller_index = {}
#        self._controller_channel_index = {}
#        #
#        # self._controllers = [
#        #   { 'obj' : controller_object, 'fld': [channel_id,...] },
#        # ...
#        # ]
#        #  
#
#        for ts in sorted(self._event_list):
#            for e in self._event_list[ts]:
#                if e.unit is not None:
#                    if e.unit not in self._controller_index:
#                        self._controller_index[e.unit] = len(self._controllers)
#                        self._controller_channel_index[e.unit] = {}
#                        self._controllers.append({
#                            'obj': e.unit,
#                            'fld': []
#                        })
#                    u_idx = self._controller_index[e.unit]
#                    if e.channel is not None and e.channel not in self._controller_channel_index[e.unit]:
#                        self._controller_channel_index[e.unit][e.channel] = len(self._controllers[u_idx]['fld'])
#                        self._controllers[u_idx]['fld'].append(e.channel)

    def save_file(self, filename):
        "Save sequence data to the named file."
        self.save(file(filename, 'wb'))

    def save(self, outputfile):
#        self._build_controller_list()
        self._build_vchannel_list()

        output_csv = csv.writer(outputfile)

        output_csv.writerow(('V4','Lumos sequence file "%s"' % outputfile.name))
        if self.audio is not None:
            output_csv.writerow(['A',
                self.audio.filename,
                self.audio.volume,
                self.audio.channels,
                self.audio.frequency,
                self.audio.bits,
                self.audio.bufsize
            ])

#        for controller in self._controllers:
#            output_csv.writerow(['U', controller['obj'].id] + controller['fld'])
        for vchannel in self._vchannels:
            output_csv.writerow(('C', vchannel.type, vchannel.id))

        for timestamp in sorted(self._event_list):
            output_csv.writerow(('T', timestamp))
            for event in self._event_list[timestamp]:
                output_csv.writerow(('EV',
                    '*' if event.vchannel is None else self._vchannel_index[id(event.vchannel)],
                    event.level, event.delta))

#                output_csv.writerow(('E',
#                    '*' if event.unit is None else self._controller_index[event.unit],
#                    '*' if event.channel is None else self._controller_channel_index[event.unit][event.channel],
#                    event.level, event.delta))


    def events_at(self, timestamp):
        "Retrieve list of Event objects occurring at specified time."

        return self._event_list[timestamp]

    def compile_stream(self, event_list=None, keep_state=False, force=False, skew=0):
        '''Compile the sequence all the way into a list of bytes to transmit
        to the output networks, avoiding the need to interpret events in real time.
        
        If the sequence has already been compiled to an event list, pass that list
        to this method's event_list parameter:
            sequence.compile_stream(sequence.compile(...))

        Otherwise, calling compile_stream will invoke compile() for you.  In this
        case, you may use the keep_state, force, and skew parameters in the same
        way the compile() method uses them.

        The return value from compile_stream() is a list in the same format as
        that returned from compile(), however the bound methods will be to network
        objects, and their argument lists will be ready-to-send strings of data bytes,
        so each scheduled action will be nothing more than blasting blocks of bits
        out into the networks.

        N.B.: In order to accomplish this, the compile_stream() method takes control
        of the controllers and networks, "playing" the sequences but diverting their
        output internally.  This means you can't compile a stream at the same time as
        you're running a show with those networks and/or controllers.

        It is assumed that the input event_list will be sorted in order of increasing
        timestamp values (which is the way compile() generates it).
        '''

        if event_list is None: 
            event_list = self.compile(keep_state, force, skew)

        # build list of events by time and priority
        event_blocks = {}
        for timestamp, method, arglist, priority in event_list:
            if timestamp not in event_blocks:
                event_blocks[timestamp] = {}
            if priority not in event_blocks[timestamp]:
                event_blocks[timestamp][priority] = []
            event_blocks[timestamp][priority].append((method,arglist))

        # "play" them (with output diverted) in time/priority order
        #network_list = set([c['obj'].network for c in self._controllers])
        ev_list = []
        for timestamp in sorted(event_blocks):
            for network in self._all_networks:
                network.divert_output()
            for priority in sorted(event_blocks[timestamp]):
                for method, arglist in event_blocks[timestamp][priority]:
                    method(*arglist)
            for network in self._all_networks:
                bytes_to_send = network.end_divert_output()
                if bytes_to_send:
                    ev_list.append((timestamp, network.send, (bytes_to_send,), 1))

        return ev_list

    def compile(self, keep_state=False, force=False, skew=0):
        '''
        Compile the sequence into a ready-to-execute list of
        device updates.  This will return a list of discrete,
        device-specific updates in the form:
            [(timestamp, method, arglist, priority), ...]
        To play the sequence on the actual hardware, all you
        need to do at that point is to make each method call:
            method(*arglist)
        when <timestamp> milliseconds have elapsed.

        If priority is given, give this event priority over the
        others.  The lower the number, the more urgent the event.
        The default is 5.

        This will resolve all the high-level concepts from the
        Event/Sequence model into low-level actions by the hardware
        (for example, the event "Transition a channel from current
        value to 10% over a period of 5 seconds" would become a
        series of individual channel value changes over that 5-second
        interval, depending on the hardware's dimmer resolution.
        
        NOTE: This code assumes that all channels begin at 0%
        dimmer levels at the start of the sequence.  If this is
        not the case, the scene should begin either with an explicit
        level-set event for every channel or fade effects
        may not be evaluated correctly.  All other effects should
        work fine in any event.
        
        NOTE: The result is undefined if multiple concurrent events
        exist which modify the same channel.  For example, if an 
        event fades a channel from its current value to 0 over a
        period of 3 seconds, while another event changes that
        channel's value during the period it is already fading
        (before the effects of the first event complete).

        If the keep_state parameter is given a True value, the
        actions taken will consider the current states of all the
        virtual channels (at the moment of compilation) as the
        starting point being modified by the events in the sequence.
        The result of the sequence will be reflected in the new
        states of the virtual channels after compilation, as if
        the sequence had actually occurred.  This way, a chain
        of sequences can be compiled which build on each other's
        final state. 

        Otherwise, (if keep_state is False [the default]), then
        the compiled sequence will assume that all virtual channels
        are at an initial "zero" state (although it will not actually
        contain commands to set them to that state without an explicit
        event commanding such to happen).  When the compilation is
        complete, the virtual channels will be restored to their state
        as they were before compile() was invoked.
        [Default: False]

        If the force parameter is given a True value, events will
        be generated even if the sequence compiler believes they
        are unnecessary because the output channel is already
        at the desired state.
        [Default: False]

        If the skew value is given, all timed events will be delayed
        by that many milliseconds before actually taking place.  This
        value may be negative to make them occur sooner, but it is
        undefined what may happen if that makes an event begin before
        the sequence itself was supposed to start.  
        [Default: 0]
        '''

        self._build_vchannel_list()
        ev_list = []

        if not keep_state:
            # save the state of all the virtual channels
            saved_vchannel_state = {}
            for vchannel in self._vchannels:
                saved_vchannel_state[vchannel.id] = vchannel.current_raw_value

        for timestamp in sorted(self._event_list):
            flush_set = set()

            for event in self._event_list[timestamp]:
                if event.vchannel is None:
                    if (event.level == 0 or event.level == '0') and event.delta == 0:
                        affected_controllers = self._all_controllers
                        compiled_event_list = [
                            (timestamp + skew, controller.all_channels_off, (), 1)
                                for controller in self._all_controllers
                        ]
                    else:
                        affected_controllers = set()
                        compiled_event_list = []
                        for vchannel in self._vchannels:
                            a, c = event.compile(timestamp + skew, for_vchannel=vchannel)
                            affected_controllers.update(a)
                            compiled_event_list.extend(c)
                else:
                    affected_controllers, compiled_event_list = event.compile(timestamp + skew)

                ev_list.extend(compiled_event_list)
                flush_set.update(affected_controllers)

            for controller in flush_set:
                ev_list.append((timestamp + skew, controller.flush, (), 2))

        #
        # restore vchannel states if we aren't keeping them.
        #
        if not keep_state:
            for vchannel in self._vchannels:
                vchannel.current_raw_value = saved_vchannel_state[vchannel.id]

        #
        # run through and eliminate all duplicate flushes which we can accumulate
        # thanks to the way fades are handled by the virtual channels
        # 
        # this also has the effect of sorting the events here, for whatever that
        # might be worth.
        #
        final_ev_list = []
        last_time_seen = None
        flush_seen_for = set()
        for event in sorted(ev_list):
            if last_time_seen is None or last_time_seen != event[0]:
                flush_seen_for = set()
                last_time_seen = event[0]

            if event[1].__name__ == 'flush':
                if id(event[1].__self__) in flush_seen_for:
                    # DUPLICATE! skip this one
                    continue
                flush_seen_for.add(id(event[1].__self__))

            final_ev_list.append(event)

        return final_ev_list

    def add(self, timestamp, event_obj):
        "Add a new event to the sequence."
        self._event_list.setdefault(timestamp, []).append(event_obj)

    def clear(self):
        "Clear the event list."
        self._event_list = {}

    def __getattr__(self, name):
        if name == 'intervals':
            return sorted(self._event_list)
