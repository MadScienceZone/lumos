# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS: VIXEN SEQUENCE CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Extras/VixenSequence.py,v 1.3 2008-12-31 00:25:19 steve Exp $
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
from xml.etree.ElementTree import ElementTree
import base64

class InvalidVixenSequenceFile (Exception):
    pass

class VixenChannel (object):
    """Describes a channel from a Vixen sequence.  Has the following
    attributes:

    name:     text label for this channel
    color:    tuple of (red, green, blue) values
    enabled:  boolean (not currently used by Lumos)
    output:   string (not currently used by Lumos)
    """

    def __init__(self, name, color, enabled, output):
        """color may be tuple (r,g,b) or 24-bit signed value

        enabled may be boolean or string with "true/false" text"""

        self.name = name
        if isinstance(color, tuple):
            self.color = color
        else:
            color = int(color)
            self.color = ((color >> 16) & 0xff,
                          (color >>  8) & 0xff,
                           color        & 0xff)

        if isinstance(enabled, bool):
            self.enabled = enabled
        else:
            self.enabled = enabled.lower() != 'false'

        self.output = output

class VixenSequence (object):
    """Objects of this class represent sequences prepared by the 
    Vixen sequence editor.  This is intended for experimental purposes
    or for importing scenes from Vixen to Lumos.

    This has been tested with standard Vixen sequences on version 2.XXX
    and may not work with all possible types of sequences understood by
    Vixen.

    Once a sequence is loaded, the following attributes are publicly 
    available:

    total_time:   the duration of the sequence.  Note that the 
                  duration may extend past the last event 
                  timestamp if there are any events which are
                  not instantaneous and still running at that
                  point.  Integer, measured in milliseconds.

    channels:     a list of VixenChannel objects defined by the 
                  sequence file (q.v.).

    min_val:      minimum range for channel values
    max_val:      maximum range for channel values

    events:       a compressed list of (time, channel#, value) tuples
                  representing the sequence.  "Compressed" is a word which
                  here means, "converted from Vixen's 'time-slice/frame'
                  format to our event-based one, without showing duplicate
                  events when a channel remains steady from one frame to the
                  next."

    audio_filename:  None or the name of the audio clip defined for this
                     sequence.

    This is a fairly simplistic algorithm at the moment.  It needs to
    be completed, and could become confused by too many variations in
    the file parameters.  It does NOT currently take into account
    channels which are disabled or min/max values other than 0-255.
    """

    def __init__(self, vixen_file = None):
        """Create a representation of a sequence obtained from importing
        a Vixen file."""
        self.clear()
        if vixen_file is not None:
            self.load_file(vixen_file)

    def clear(self):
        self.total_time = 0
        self.channels = []
        self.min_val = None
        self.max_val = None
        self.audio_filename = None
        self.events = []

    def load_file(self, filename):
        "Load a Vixen sequence file into this object."
        self.load(file(filename, 'r'))

    def load(self, fileobj):
        "Load a Vixen sequence from a file object."
        self.clear()
        file_data = ElementTree()

        try:
            file_data.parse(fileobj)
            self.total_time = int(file_data.find('Time').text)
            self.min_val    = int(file_data.find('MinimumLevel').text)
            self.max_val    = int(file_data.find('MaximumLevel').text)

            for channel in file_data.find('Channels').getiterator('Channel'):
                self.channels.append(VixenChannel(channel.text, channel.get('color'), channel.get('enabled'), channel.get('output')))

            audio_node = file_data.find('Audio')
            if audio_node is not None:
                self.audio_filename = audio_node.text

            # The events are a giant base-64-encoded block of value
            # bytes giving a view of the state of each channel at each
            # time slice.
            event_raw_data = base64.b64decode(file_data.find('EventValues').text)
            event_period = int(file_data.find('EventPeriodInMilliseconds').text)

            # run through each channel data, record *changes* as events
            # for Lumos
            current_time = 0
            current_channel = 0
            current_value = None
            for v in event_raw_data:
                value = ord(v)
                if value != current_value:
                    current_value = value
                    self.events.append((current_time, current_channel, value))

                current_time += event_period
                if current_time >= self.total_time:
                    current_time = 0
                    current_channel += 1
                    current_value = None
            print("Ended conversion at channel", current_channel, "of", len(self.channels), "; time", current_time, "of", self.total_time)

        except Exception as error:
            raise InvalidVixenSequenceFile('Unable to understand Vixen sequence file (%s)' % error)
#
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
