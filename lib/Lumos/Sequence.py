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
from Event import Event

class InvalidFileFormat (Exception): pass
class InvalidTimestamp (Exception): pass
class InvalidUnitDefinition (Exception): pass
class InvalidEvent (Exception): pass

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
        self.current_state = {}

    def load_file(self, filename, controller_map):
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

                if version > 2:
                    raise InvalidFileFormat('This version of Lumos only supports sequence file format V2.')
            #
            # ----- below this point, you need to have seen the Vn record -----
            #
            elif version is None:
                raise InvalidFileFormat('No Vn record found before real data!')
            #
            # U,unitname,channelname[,...]
            #    declare a controller unit and its channels
            #
            elif record[0] == 'U':
                if len(record) < 3:
                    raise InvalidUnitDefinition('Badly formed U record "%s"' % record)
                if record[1] not in controller_map:
                    raise InvalidUnitDefinition('Unknown controller unit "%s" used in sequence' % record[1])
                target_controller = controller_map[record[1]]
                self._controllers.append({
                    'obj': target_controller,
                    'fld': []
                })
                # adjust channel names to be of appropriate type for controller
                for channel_id in record[2:]:
                    self._controllers[-1]['fld'].append(target_controller.channel_id_from_string(channel_id))

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
            # E,u,ch,v,dT
            #    event: change value of unit u's channel ch to v% over dT milliseconds
            #
            elif record[0] == 'E':
                try:
                    delta = int(record[4])

                    extent = timestamp + delta
                    if extent > self.total_time:
                        self.total_time = extent

                    if timestamp not in self._event_list:
                        self._event_list[timestamp] = []

                    if record[1] == '*' and record[2] != '*':
                        raise InvalidEvent('Channel must be "*" if controller ID is "*" in "%s"' % record)

                    self._event_list[timestamp].append(
                       Event(None if record[1] == '*' else self._controllers[int(record[1])]['obj'],
                             None if record[2] == '*' else self._controllers[int(record[1])]['fld'][int(record[2])],
                             float(record[3]), int(record[4])))
                
                except:
                    raise InvalidEvent('Cannot understand event description "%s"' % record)

    def _build_controller_list(self):
        self._controllers = []
        self._controller_index = {}
        self._controller_channel_index = {}
        #
        # self._controllers = [
        #   { 'obj' : controller_object, 'fld': [channel_id,...] },
        # ...
        # ]
        #  

        for ts in sorted(self._event_list):
            for e in self._event_list[ts]:
                if e.unit is not None:
                    if e.unit not in self._controller_index:
                        self._controller_index[e.unit] = len(self._controllers)
                        self._controller_channel_index[e.unit] = {}
                        self._controllers.append({
                            'obj': e.unit,
                            'fld': []
                        })
                    u_idx = self._controller_index[e.unit]
                    if e.channel is not None and e.channel not in self._controller_channel_index[e.unit]:
                        self._controller_channel_index[e.unit][e.channel] = len(self._controllers[u_idx]['fld'])
                        self._controllers[u_idx]['fld'].append(e.channel)

    def save_file(self, filename):
        "Save sequence data to the named file."
        self.save(file(filename, 'wb'))

    def save(self, outputfile):
        self._build_controller_list()

        output_csv = csv.writer(outputfile)

        output_csv.writerow(('V2','Lumos sequence file "%s"' % outputfile.name))
        for controller in self._controllers:
            output_csv.writerow(['U', controller['obj'].id] + controller['fld'])

        for timestamp in sorted(self._event_list):
            output_csv.writerow(('T', timestamp))
            for event in self._event_list[timestamp]:
                output_csv.writerow(('E',
                    '*' if event.unit is None else self._controller_index[event.unit],
                    '*' if event.channel is None else self._controller_channel_index[event.unit][event.channel],
                    event.level, event.delta))

    def events_at(self, timestamp):
        "Retrieve list of Event objects occurring at specified time."

        return self._event_list[timestamp]

    def compile(self, keep_state=False):
        '''Compile the sequence into a ready-to-execute list of
        device updates.  This will return a list of discrete,
        device-specific updates in the form:
            [(timestamp, method, arglist), ...]
        To play the sequence on the actual hardware, all you
        need to do at that point is to make each method call:
            method(*arglist)
        when <timestamp> milliseconds have elapsed.

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
        previously-known dimmer state.  Otherwise, zero values
        are assumed for all channels.
        '''

        self._build_controller_list()
        if not keep_state:
            self.current_state = {}  # current raw dimmer level for each channel
        ev_list = []

        for timestamp in sorted(self._event_list):
            #print "==", timestamp, "==", len(self._event_list[timestamp]), "events"
            for event in self._event_list[timestamp]:
                unit_list = [event.unit] if event.unit is not None else [i['obj'] for i in self._controllers]
                #print "EVENT", event, "units:", unit_list
                for target_unit in unit_list:
                    channel_list = [event.channel] if event.channel is not None else sorted(target_unit.iter_channels())
                    if event.channel is None and event.level == 0 and event.delta == 0:
                        #print "(adding all-channel-off event)"
                        ev_list.append((timestamp, target_unit.all_channels_off, ()))
                    else:
                        #print "(adding channel event...)"
                        for channel in channel_list:
                            #print "...channel", channel
                            if target_unit.channels[channel] is None:
                                raise InvalidEvent("Sequence uses channel %s.%s which is not configured." % (
                                    target_unit.id, channel))

                            start_raw_value = self.current_state.setdefault((target_unit.id, channel), 
                                target_unit.channels[channel].raw_dimmer_value(0))
                            end_raw_value = target_unit.channels[channel].raw_dimmer_value(event.level)

                            #print "...start:", start_raw_value, "end:", end_raw_value, "time:", event.delta

                            if event.delta == 0:
                                if start_raw_value != end_raw_value:
                                    #print "Adding set event: unit %s ch %s -> %d (%d)" % (
                                    #    target_unit.id, repr(channel), event.level, end_raw_value)
                                    ev_list.append((timestamp, target_unit.set_channel, (channel, end_raw_value)))
                            else:
                                fade_steps = abs(start_raw_value - end_raw_value)
                                fade_incr = 1 if start_raw_value < end_raw_value else -1

                                if fade_steps == 1:
                                    #print "Adding fade sequence (one-step) for %d-%d: unit %s ch %s" % (
                                    #    start_raw_value, end_raw_value, target_unit.id, repr(channel))
                                    ev_list.append((timestamp + event.delta, target_unit.set_channel,
                                        (channel, end_raw_value)))

                                if fade_steps > 1:
                                    for i in range(fade_steps):
                                        #print "Adding fade sequence step %d of %d in %d-%d: unit %s ch %s" % (
                                        #    i+1, fade_steps, start_raw_value, end_raw_value, target_unit.id, repr(channel))
                                        ev_list.append((timestamp + ((event.delta * i) / (fade_steps - 1)),
                                            target_unit.set_channel,
                                            (channel, start_raw_value + (fade_incr * (i + 1)))))

                    for channel in channel_list:
                        if target_unit.channels[channel] is None:
                            continue
                        self.current_state[(target_unit.id,channel)] = target_unit.channels[channel].raw_dimmer_value(event.level)
                        #print "setting current(", target_unit.id, ",", channel, ") to", target_unit.channels[channel].raw_dimmer_value(event.level)

        return ev_list

            # [(2000*i)/13 for i in range(14)]


    def add(self, timestamp, event_obj):
        "Add a new event to the sequence."
        self._event_list.setdefault(timestamp, []).append(event_obj)

    def clear(self):
        "Clear the event list."
        self._event_list = {}

    def __getattr__(self, name):
        if name == 'intervals':
            return sorted(self._event_list)

#
# $Log: not supported by cvs2svn $
# Revision 1.5  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
