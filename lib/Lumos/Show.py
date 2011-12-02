# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS SHOW CONFIGURATION HANDLER CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Show.py,v 1.7 2009-01-23 16:33:29 steve Exp $
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
import ConfigParser, inspect
from Lumos.PowerSource        import PowerSource
from Lumos.Network.Networks   import network_factory, supported_network_types
from Lumos.Device.Controllers import controller_unit_factory, supported_controller_types

def get_config_dict(conf, section, typemap, objlist=None):
    dict = {}
    for k in conf.options(section):
        if k in typemap:
            if   typemap[k] == 'int':     dict[k] = conf.getint(section, k)
            elif typemap[k] == 'float':   dict[k] = conf.getfloat(section, k)
            elif typemap[k] == 'bool':    dict[k] = conf.getboolean(section, k)
            elif typemap[k] == 'objlist': dict[k] = objlist[conf.get(section, k)]
            elif typemap[k] == 'ignore':  pass
            else:
                raise ValueError, "Invalid typemap value for %s" % section
        else:
            dict[k] = conf.get(section, k)
    return dict

class Show (object):
    '''
    This object describes and orchestrates the show.  It holds descriptions
    of the various hardware plugged in to the host computer. 

    After creating an instance of this class, call the load method to load
    a show configuration into it.  After that, the following attributes
    will be available:

        all_power_sources:  A dictionary of PowerSource objects, indexed by 
                            circuit identifier as given in the show config file.
        top_power_sources:  A list of PowerSource object IDs which are at the
                            top level of the power source hierarchy.

        networks:           A dictionary of Network objects, indexed by network
                            identifier as given in the show config file.  These
                            networks will contain controller units.

        title:              The show title.
        description:        The show's descriptive text.
    '''
    def __init__(self):
        self._clear()

    def _clear(self):
        self.all_power_sources = {}
        self.top_power_sources = []
        self.networks = {}
        self.controllers = {}
        self.title = None
        self.description = None

    def load(self, file, open_device=True):
        '''Load up a show configuration file.  This will instantiate and
        initialize a set of power sources, networks and controllers, ready
        to begin running show sequences.  Pass in a file-like object holding
        the configuration data for the show.
        '''
        self._clear()

        show = ConfigParser.SafeConfigParser()
        show.readfp(file)
        self._load_from_config(show, open_device)

    def _search_for_sub_sources(self, show, parent_ID, parent_obj):
        #
        # SUBORDINATE POWER SOURCES
        #
        #   [power primary.secondary]
        #   definition for "primary.secondary" which is assumed to be
        #   powered by "primary" (arbitrarily nested)
        #
        for source_tag in show.sections():
            if source_tag.startswith('power '+parent_ID+'.'):
                source_ID = source_tag[6:]
                if '.' not in source_ID[len(parent_ID)+1:]: #don't get ahead of ourselves
                    source_obj = PowerSource(source_ID,
                            **get_config_dict(show, source_tag, {
                                'amps': 'float',
                                'gfci': 'bool'
                            }))
                    self.all_power_sources[source_ID] = source_obj
                    parent_obj.add_subordinate_source(source_obj)
                    self._search_for_sub_sources(show, source_ID, source_obj)


    def _load_from_config(self, show, open_device):
        self.title = show.get('show', 'title')
        self.description = show.get('show', 'description')
        #
        # POWER SOURCES
        #
        for source_ID in show.get('show', 'powersources').split():
            source_obj = PowerSource(source_ID, 
                **get_config_dict(show, 'power '+source_ID, {
                    'amps': 'float',
                    'gfci': 'bool'
                }))
            self.all_power_sources[source_ID] = source_obj
            self.top_power_sources.append(source_ID)
            self._search_for_sub_sources(show, source_ID, source_obj)
        #
        # NETWORKS
        #
        for net_ID in show.get('show', 'networks').split():
            net_type = show.get('net '+net_ID, 'type')
            net_args = get_config_dict(show, 'net '+net_ID, {
                'units': 'ignore',
                'type':  'ignore',
            })
            if not open_device:
                net_args['open_device'] = False
            self.networks[net_ID] = network_factory(net_type, **net_args)
            #
            # CONTROLLER UNITS
            #
            for unit_ID in show.get('net '+net_ID, 'units').split():
                unit_type = show.get('unit '+unit_ID, 'type')
                unit_args = get_config_dict(show, 'unit '+unit_ID, {
                    'power': 'objlist',
                    'type':  'ignore'
                }, self.all_power_sources)
                unit_args['id'] = unit_ID
                self.networks[net_ID].add_unit(unit_ID, controller_unit_factory(
                    unit_type, network=self.networks[net_ID], **unit_args))
                self.controllers[unit_ID] = self.networks[net_ID].units[unit_ID]
                #
                # CHANNELS IN CONTROLLER UNIT
                #
                for channel_ID in show.sections():
                    if channel_ID.startswith('chan '+unit_ID+'.'):
                        c_ID = channel_ID[len(unit_ID)+6:]
                        self.networks[net_ID].units[unit_ID].add_channel(c_ID, 
                            **get_config_dict(show, channel_ID, {
                                'load':   'float',
                                'dimmer': 'bool',
                                'warm':   'int',
                                'power':  'objlist',
                            }, self.all_power_sources))

    def load_file(self, filename, open_device=True):
        self.load(open(filename), open_device)

    def save(self, file):
        "Save configuration profile data to file, including general comments."

        def multiline(s):
            "Format multi-line string for proper printing in config file"
            if s is None:
                return ''
            return '\n\t'.join(str(s).split('\n'))

        print >>file, ''';
; vim:set syntax=cfg:
; vi:set ts=4 sw=4 noexpandtab:
;
; Lumos Light Orchestration System
; Show Configuration Profile
;
; Edit this file directly (instructions are provided in-line below, and are
; also explained in the product documentation; see SHOW.CONF(5)), or use
; the lconfig GUI application to edit it in a more friendly and interactive
; manner.
;___________________________________________________________________________
;INTRODUCTION
;
; This file describes the devices connected to your computer, which you will
; have Lumos control.  Generally, you'd design your show, working out what 
; lights will be assigned to which controllers (and what power circuits 
; those will be powered from).  This information is entered into this
; configuration file so that Lumos knows how to control each of your 
; show channels.  The same show will usually use one profile, even though 
; it may use many scene files.
;
; It would probably be a good idea to store the show.conf file along 
; with the scene files which describe a complete show.  Each show will
; likely use different arrangements of lights and controllers, and so it
; would require its own show.conf file.
;___________________________________________________________________________
;FORMAT
;
; A few words about the format of this file:
;
; First, as you have no doubt noticed, lines beginning with a semicolon (;)
; or pound sign (#) are comments and are ignored (up to the end of the line)
; 
; The file is divided up into sections.  A section begins with the section
; name in square brackets on a line.  For example, the line:
;   [show]
; begins a section called "show", which defines the global settings used
; in a show.
;
; Each section contains a number of named values relating to that section.
; These are defined, one per line, in "name=value" or "name: value" notation.
; For example:
;   type=x10
;   power: 12
;
; White space around the '=' or ':' is ignored, but the value name must start
; at the beginning of the line.
;
; Long values may be typed on multiple lines of the file.  Any line which
; is indented (i.e., begins with whitespace) is considered to be a
; continuation of the value from the previous line, in the same fashion as
; RFC 822 mail headers.  For example:
;   description: This channel controls the red
;                rope light which runs around the
;                perimeter of the lawn.
; This would assign the text "This channel controls the red rope light which
; runs around the perimeter of the lawn." as the "description" value.
;
; Common values may be defined in this file and used to define other values.
; For example:
;   basepath=/usr/local/lightshows/data
;   show1=%(basepath)s/first
;   show2=%(basepath)s/second
;
; The syntax for substituting values is %(NAME)s, where NAME is the name
; of the value being substituted here.  (This is an extension of the 
; standard printf() function format syntax, with the name of the value
; being placed in parentheses immediately following the '%' character.  Any
; other valid printf()-style formating controls may appear after the 
; closing parenthesis.)  A literal "%" character is entered by typing "%%".
;
; Values may only be substituted into a given section only if they were
; themselves defined in that same section, or in the [DEFAULT] section.
;
; N.B. IF YOUR PROFILE IS SAVED BY ANOTHER PROGRAM (E.G., LCONFIG), THE
; DEFINITION OF THESE VARIABLES MAY BE LOST although their effect (as of
; that point in time) will be preserved.  In other words, their values 
; will be substituted into the other fields when saved back to the profile.
; If you make significant use of these variables, you should continue 
; maintaining the file manually.  YOU WILL ALSO LOSE COMMENTS if you use
; lconfig or other utility to save this profile data.  In short, for 
; best results either use the GUI tools (lconfig) OR manually edit your
; profile, but don't go back and forth between the two.
;___________________________________________________________________________
;STRUCTURE
;
; This file describes a number of NETWORKS, which each contain a set of
; CONTROLLERS, which in turn control a number of CHANNELS (i.e., electrical
; circuits of, e.g., Christmas light strings).
;
; The first section, [show], describes the overall show setup, with global
; settings related to the show (as opposed to global settings for the 
; Lumos application, which are in the main configuration file).
; This includes a list of networks and power sources available.
;
; Each power source is described in its own section called [power XXX],
; which gives information about available current, phase, etc.
;
; There will then be one section for each network, [net XXX], 
; which define the specific information about each network, including the
; list of controllers present on each.
;
; Each controller is described in its section, [unit XXX], including the
; list of channels controlled by that unit.
;
; Each channel is described by a section called [chan XXX], which describes
; attributes of the show element controlled on that circuit.
;___________________________________________________________________________
;VALIDATION
;
; After making edits to this file, you should run it through the lcheck
; program.  This will read your configuration, alert you to any 
; inconsistencies or errors that it can detect, and provide you with a
; report summarizing the power loads your stated configuration may draw.
;
; Always run lcheck on your configuration files before putting them into
; production use.  It will make tracking down problems easier if you can
; catch common configuration errors early.
;
;===========================================================================

;___________________________________________________________________________
; MAIN SECTION
;
; This describes the overall show setup parameters.
;
;   powersources=1 2a 2b
;     This is a space-separated list of circuits which will feed power to
;     your show.  You can call these anything you like.  We suggest using
;     the same numbering scheme as on your main breaker panel (or whatever
;     easily identifies the circuit in your environment).  Each source will
;     be defined in detail in its own section.
;
;   networks=trees misc floods
;     This is a space-separated list of networks of controllers which will
;     be in use during the show.  These are separate realms of controllers
;     and will be on different devices (e.g., serial ports) from the 
;     computer's point of view.  These network names may be anything which
;     makes sense to you.  They will be defined in detail in their own
;     sections.
;
;   title=...        The name of the show.
;   description=...  A longer description of the show.
;
[show]'''
        print >>file, "powersources=" + ' '.join(sorted(self.top_power_sources))
        print >>file, "networks="     + ' '.join(sorted(self.networks))
        print >>file, "title="        + multiline(self.title)
        print >>file, "description="  + multiline(self.description)
        print >>file, '''
;___________________________________________________________________________
;POWER SOURCES
;
; The following sections, each named [power XXX] where XXX is the name of
; a power source from the "powersources" value in [show], describe the 
; various properties of the power circuits supplying input power for your
; show.
;
; Additionally, subordinate power sources may be declared by naming them
; [power a.b] to mean that source "a.b" is a load on source "a".  Likewise,
; [power a.b.c] defines "a.b.c" which is a load on "a.b", which is in turn
; a load on "a".  Only the "top-level" power sources are listed in the 
; overall show's powersources value.
;
; More power sources than are used may be in the file, but they are ignored
; unless they are listed in the [show] powersources value or are subordinate 
; to one of those.
;
;   amps=...         The maximum current rating for this circuit.
;                    ***NOTE*** this should be the current available
;                    TO YOUR SHOW, after accounting for whatever else
;                    is (or will be) connected to that circuit.
;
;   gfci=yes/no      Set to 'yes' if this circuit has ground fault 
;                    protection.  The default is 'no'.
;'''
        for powerID in sorted(self.all_power_sources):
            print >>file, "[power %s]" % powerID
            print >>file, "amps=%f"    % self.all_power_sources[powerID].amps
            print >>file, "gfci=%s"    % ('yes' if self.all_power_sources[powerID].gfci else 'no')
            print >>file
        print >>file, '''
;___________________________________________________________________________
;NETWORKS
;
; The following sections, each named [net XXX], where XXX is the name of
; a network from the "networks" value in [show], describe the various
; networks of controllers attached to your computer.  Normally, these are
; separate serial ports, connected to some set of channel controller devices.
;
;   type=...        The type of network being defined.  As of the time this
;                   file was written, the currently-defined set of network
;                   types include:
;                       parbit      bit-at-a-time on a parallel port
;                       serial      RS-232 byte-at-a-time stream
;                       serialbit   bit-at-a-time on a serial port
;
;                   Not all of the fields listed below are applicable to
;                   all network types.
;
;   description=... Description explaining what this network is for.
;
;   units=a b c     Space-separated list of controller units attached to
;                   this network.  The names ('a', 'b', 'c' in this example)
;                   are arbitrary but must be unique; these are how the
;                   units are identified within the Lumos application as
;                   the user sees them.
;
;   port=...        Device to which this network is connected.  This is
;                   somewhat platform-specific.  On most systems, you can
;                   simply use 0 for the first port (COM1: on Windows, or
;                   something like /dev/ttyS0 on Unix), 1 for the next port
;                   (COM2:), etc.  If that doesn't work, you can put the
;                   actual device name like /dev/ttyS1 in this value.
;                   (parbit, serial, serialbit)
;
;   baudrate=...    Speed of the port.  Default is 9600.
;                   (serial)
;
;   bits=7/8        Number of data bits.  Default is 8.
;                   (serial)
;
;   parity=...      Parity (none/even/odd/mark/space).  Default is none.
;                   (serial)
;
;   stop=1/2        Number of stop bits.  Default is 1.
;                   (serial)
;
;   xonxoff=yes/no	If yes, use XON/XOFF software flow control.  Default off.
;                   (serial)
;
;   rtscts=yes/no   If yes, use RTS/CTS hardware flow control.  Default off.
;                   (serial)
;'''
        def dump_object_constructor(file, obj, typemap, skip=None, method=None):
            """
            Given a constructable* object, dump out a profile stanza
            describing how to reconstruct it next time we read in the
            profile.

            typemap is a dictionay of type names (as visible in the
            profile file format) to actual object classes.
            ________
            *constructable here means one we can construct from the 
            show profile.  These object classes have interfaces where
            they can be selected by a profile "type=" field, and have
            all the required constructor parameters specified by name
            in the profile file.  Note that we essentially build them
            when we read in the profile by gathering the fields from
            the profile and throwing them over to the constructor as
            its the kwargs.  This is the reverse, which is a bit 
            trickier but not too bad, given Python's nice introspection
            capabilities.
            """

            if skip is None: skip = ()
            if method is None: method = obj.__init__
            #
            # First, we need to figure out what the name for this
            # object might be.  This is backwards from what the
            # *_factory() function does, so we'll just search the
            # list of mappings until we find it.
            #
            if typemap is not None:
                for possible_type in typemap:
                    if type(obj) is typemap[possible_type]:
                        print >>file, 'type=%s' % possible_type
                        break
                else:
                    raise ValueError('Cannot determine profile type-name of object "%s"' % o.id)
            #
            # To dump out the list of relevant attributes
            # for this type of object, we will just look at
            # the object's constructor signature.
            #
            # XXX we could suppress output if the value is the default for that item.
            # XXX we don't, but should we?  (Yes, I think we should)
            #
            for attribute_name in inspect.getargspec(method)[0]:
                if attribute_name in ('self',) + skip:
                    continue
                v = obj.__getattribute__(attribute_name)
                if type(v) is bool:
                    print >>file, "%s=%s" % (attribute_name, ('yes' if v else 'no'))
                elif v is not None:
                    print >>file, "%s=%s" % (attribute_name, multiline(v))

        global_controller_list = {}
        unit_network_id = {}
        for netID, o in sorted(self.networks.iteritems()):
            print >>file, "[net %s]" % netID
            dump_object_constructor(file, o, supported_network_types, skip=('open_device',))
            
            print >>file, "units=%s" % ' '.join(sorted(o.units))
            print >>file
            global_controller_list.update(o.units)
            for u in o.units:
                unit_network_id[u] = netID

        print >>file, '''
;___________________________________________________________________________
;CONTROLLER UNITS
;
; The following sections, each named [unit XXX], where XXX is the name of
; a controller unit from the "units" value in its network section, describe 
; the various controller devices attached to a given network.  Since they
; will be receiving commands over the same wire, all units on a network
; need to have compatible protocols.
; 
;   power=...       The name of the power source which feeds this unit.
;
;   type=...        Unit type.  This must correspond to a known device
;                   driver plug-in installed in Lumos.  As of the time
;                   this file was written, the available types include:
;                      lynx10     LynX-10 serial X-10 controller
;                      48ssr      Author's custom SSR controller device
;                      cm17a      X-10 "Firecracker" serial bit controller
;                      renard     Renard DIY controller, serial protocol
;                      olsen595   Olsen595/Grinch DIY controllers, parallel
;                      firegod    FireGod DIY controller
;
;   address=...     Unit address.  (not all unit types use addresses)
;                   (firegod, renard, 48ssr)
;
;   resolution=n    How many dimmer levels are supported.  If a channel may
;                   go from 0 to 63, its resolution is 64.
;                   (firegod, cm17a, lynx10, renard, 48ssr)
;
;   channels=n      For controllers with variable numbers of channels,
;                   specify how many are attached to this controller unit.
;                   (firegod, olsen595, renard)
;'''
        global_channel_list = {}
        for unitID, o in sorted(global_controller_list.iteritems()):
            print >>file, "[unit %s]" % unitID
#           print >>file, 'network=%s' % unit_network_id[unitID]
            print >>file, 'power=%s' % o.power_source.id
            dump_object_constructor(file, o, supported_controller_types, skip=('power', 'network', 'id'))
            print >>file
            global_channel_list[unitID] = o.channels
        print >>file, '''
;___________________________________________________________________________
;CONTROLLER CHANNELS
;
; The following sections, each named [chan XXX.YYY], where XXX is the name 
; of a controller and YYY is the unit-specific designation for a channel,
; describe each output circuit controlled by Lumos.
;
; The numbering scheme for channels depends on the type of unit.
;
;   name=...        Channel name as it will appear in the software.   
;
;   load=...        Amperage rating of the load to be connected.
;
;   dimmer=yes/no	Can load be dimmed?  Default=yes.
;                   ***NOTE*** Indicating "no" here will inform Lumos
;                   that it should interpret any non-zero level for that
;                   channel as fully ON, and zero as fully OFF.  However, we
;                   cannot guarantee that a software or hardware bug or mal-
;                   function, communication glitch or other circumstance might
;                   not cause it to go into dimmer mode anyway.  DO NOT 
;                   connect anything to a dimmable controller output which
;                   would be damaged if it happens to be dimmed. ***
;
;   warm=...        Level (percentage) to keep light at to keep it warm all
;                   the time.  This is effectively a minimum level to which
;                   the circuit dimmer will be set if the scene calls for it
;                   to go lower than this threshold.  So if this were set as:
;                      warm=10
;                   then any level setting of 0-10% would result in an actual
;                   output of 10%, while any setting above 10 would be output
;                   normally.  Default is to disable this feature, and allow
;                   the channel to be turned competely off.  A value of 0 
;                   will keep the channel on, and dimmed to 0% output minimum.
;
;   power=ID        power source ID feeding this channel, if different from the
;                   one feeding the controller unit as a whole.
;'''
        for unitID, unit_channel_list in sorted(global_channel_list.iteritems()):
            unitObj = global_controller_list[unitID]
            for channelID, o in sorted(unit_channel_list.iteritems()):
                print >>file, "[chan %s.%s]" % (unitID, channelID)
                if o.warm is not None:
                    print >>file, 'warm=%.2f' % o.pct_dimmer_value(o.warm)
                if o.power_source is not None and o.power is not unitObj.power_source:
                    print >>file, 'power=%s' % o.power_source.id
                dump_object_constructor(file, o, None, skip=('id', 'warm', 'power'), method=unitObj.add_channel)
                print >>file
        print >>file, ''';
; End Configuration Profile.
;'''

    def save_file(self, filename):
        output = open(filename, "w")
        self.save(output)
        output.close()

# XXX call initializeDevice on all controllers
# XXX startup all the comm network drivers
#
# $Log: not supported by cvs2svn $
# Revision 1.6  2008/12/31 00:25:19  steve
# Preparing 0.3a1 release
#
# Revision 1.5  2008/12/30 22:58:02  steve
# General cleanup and updating before 0.3 alpha release.
#
#
