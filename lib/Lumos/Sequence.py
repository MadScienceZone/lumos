# vi:set ai nu sm ts=4 sw=4 expandtab:
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
                self._controllers.append({
                    'obj': controller_map[record[1]],
                    'fld': record[2:]
                })

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

        self._build_controller_list()

        outputfile = file(filename, 'wb')
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

    def __getattr__(self, name):
        if name == 'intervals':
            return sorted(self._event_list)

