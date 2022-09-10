#
# LUMOS SHOW CONFIGURATION HANDLER CLASS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/Show.py,v 1.7 2009-01-23 16:33:29 steve Exp $
#
# Lumos Light Orchestration System
# Copyright (c) 2005, 2006, 2007, 2008, 2014 by Steven L. Willoughby, Aloha,
# Oregon, USA.  All Rights Reserved.  Licensed under the 3-Clause BSD 
# License.
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
import configparser, inspect, sys
from Lumos.PowerSource             import PowerSource
from Lumos.Network.Networks        import network_factory, supported_network_types
from Lumos.Device.Controllers      import controller_unit_factory, supported_controller_types
from Lumos.VirtualChannels.Factory import virtual_channel_factory, supported_virtual_channel_types

class GUIConfiguration (object):
    def __init__(self):
        self.virtual_channel_display_order = []
        if sys.platform == 'darwin':
            self.menu_button = '<Button-2>'
        else:
            self.menu_button = '<Button-3>'

        self.select_button = '<Button-1>'
        self.activate_button = '<Double-Button-1>'
        self.extend_button = '<Shift-Button-1>'

    def load(self, config_obj):
        if config_obj.has_section('gui'):
            if config_obj.has_option('gui', 'virtual_channel_display_order'):
                for vc_id in config_obj.get('gui', 'virtual_channel_display_order').split('\n'):
                    self.virtual_channel_display_order.append(vc_id.strip())

def get_config_dict(conf, section, typemap, objlist=None):
    a_dict = {}
    for k in conf.options(section):
        if k in typemap:
            if   typemap[k] == 'int':     a_dict[k] = conf.getint(section, k)
            elif typemap[k] == 'float':   a_dict[k] = conf.getfloat(section, k)
            elif typemap[k] == 'bool':    a_dict[k] = conf.getboolean(section, k)
            elif typemap[k] == 'objlist': a_dict[k] = objlist[conf.get(section, k)]
            elif typemap[k] == 'ignore':  pass
            elif typemap[k] == 'objarray':
                a_dict[k] = []
                for index in conf.get(section, k).split():
                    if index in objlist:
                        a_dict[k].append(objlist[index])
                        del objlist[index]
                    else:
                        raise KeyError('Value "{0}" in [{1}] field {2} not expected or valid'.format(
                            index, section, k))
            else:
                raise ValueError("Invalid typemap value for %s" % section)
        else:
            a_dict[k] = conf.get(section, k)
    return a_dict

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

        virtual_channels:   A dictionary of VirtualChannel objects, indexed by
                            the channel ID string.

        gui:                General GUI display settings.
    '''
    def __init__(self):
        self.controller_factories = [controller_unit_factory]
        self.controller_typemaps = [supported_controller_types]
        self._clear()

    def _clear(self):
        self.loaded = False
        self.all_power_sources = {}
        self.top_power_sources = []
        self.virtual_channels = {}
        self.networks = {}
        self.controllers = {}
        self.title = None
        self.description = None
        self.gui = GUIConfiguration()

    def load(self, file, open_device=True, virtual_only=False):
        '''Load up a show configuration file.  This will instantiate and
        initialize a set of power sources, networks and controllers, ready
        to begin running show sequences.  Pass in a file-like object holding
        the configuration data for the show.

        If <virtual_only> is True, we only load up virtual channel
        definitions and don't expect any content which describes real
        hardware yet.
        '''
        self._clear()

        show = configparser.ConfigParser()
        if isinstance(file, (list, tuple)):
            for f in file:
                print(f"opening {f}")
                show.read_file(f)
        else:
            print(f"opening {file}")
            show.read_file(file)
        self._load_from_config(show, open_device, virtual_only)

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
                                'amps':       'float',
                                'disp_order': 'ignore',
                                'gfci':       'ignore',   # no longer used
                            }))
                    parent_obj.add_subordinate_source(source_obj)
                    self.add_power_source(source_obj)
                    self._search_for_sub_sources(show, source_ID, source_obj)


    def _load_from_config(self, show, open_device, virtual_only):
        for s in show:
            print(f"has section {s}")
        self.title = show['show']['title']
        self.description = show['show']['description']
        self.gui.load(show)
        unvirtualized_channels = {}
        #
        # POWER SOURCES
        #
        if not virtual_only:
            for source_ID in show.get('show', 'powersources').split():
                source_obj = PowerSource(source_ID, 
                    **get_config_dict(show, 'power '+source_ID, {
                        'amps': 'float',
                        'gfci': 'ignore',   # no longer used
                    }))
                self.add_power_source(source_obj)
                self._search_for_sub_sources(show, source_ID, source_obj)
                #
                # sort subordinates
                #
                source_obj.subordinates.sort(key=lambda x: show.getint('power '+x.id, 'disp_order') if show.has_option('power '+x.id, 'disp_order') else 0)
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
                        'power_source': 'objlist',
                        'type':  'ignore',
                        'resolution': 'int',
                        'channels': 'int',
                    }, self.all_power_sources)
                    unit_args['id'] = unit_ID
                    error = unit_obj = None
                    for factory in self.controller_factories:
                        try:
                            unit_obj = factory(unit_type, network=self.networks[net_ID], **unit_args)
                        except ValueError as e:
                            error = e
                        else:
                            break

                    if not unit_obj:
                        raise error or ValueError("Can't understand controller unit type \"{0}\"".format(unit_type))

                    self.networks[net_ID].add_unit(unit_ID, unit_obj)
                    self.controllers[unit_ID] = self.networks[net_ID].units[unit_ID]
                    #
                    # CHANNELS IN CONTROLLER UNIT
                    #
                    for channel_ID in show.sections():
                        if channel_ID.startswith('chan '+unit_ID+'.'):
                            c_ID = channel_ID[len(unit_ID)+6:]
                            self.networks[net_ID].units[unit_ID].add_channel(c_ID, 
                                **get_config_dict(show, channel_ID, {
                                    'load':         'float',
                                    'dimmer':       'bool',
                                    'warm':         'int',
                                    'virtual':      'ignore',
                                    'color':        'ignore',
                                    'power_source': 'objlist',
                                }, self.all_power_sources))

                            u_obj = self.networks[net_ID].units[unit_ID]
                            c_obj = u_obj.channels[u_obj.channel_id_from_string(c_ID)]
                            if show.has_option(channel_ID, 'virtual'):
                                # this hardware channel is declaring its own virtual channel
                                v_id = show.get(channel_ID, 'virtual')
                                if v_id in self.virtual_channels or show.has_section('virtual '+v_id):
                                    raise KeyError('virtual channel {0} defined in [{1}] already exists'.format(
                                        v_id, channel_ID))

                                v_name = c_obj.name
                                sequence = 0
                                while not v_name or v_name in self.virtual_channels or show.has_section('virtual '+v_name):
                                    v_name = 'channel {0}.{1}#{2}'.format(unit_ID, c_ID, sequence)
                                    sequence += 1

                                self.virtual_channels[v_id] = virtual_channel_factory(
                                    ('dimmer' if c_obj.dimmer else 'toggle'),
                                    id=v_id,
                                    channel=c_obj,
                                    name=v_name,
                                    color=(show.get(channel_ID, 'color') if show.has_option(channel_ID, 'color') else None),
                                )
                            else:
                                # we'll have to wait until later to match it up with a virtual channel
                                unvirtualized_channels[unit_ID + '.' + c_ID] = c_obj
        #
        # VIRTUAL CHANNELS
        #
        for stanza in show.sections():
            if stanza.startswith('virtual '):
                if len(stanza) < 9:
                    raise ValueError('virtual stanza must be [virtual <id>]')

                v_id = stanza[8:]
                if v_id in self.virtual_channels:
                    raise KeyError('duplicate virtual channel definition [{0}]'.format(stanza))

                v_type = show.get(stanza, 'type')
                if virtual_only:
                    v_args = get_config_dict(show, stanza, {
                        'type':     'ignore',
                        'channel':  'ignore',
                    })
                    v_args['channel'] = None
                else:
                    v_args = get_config_dict(show, stanza, {
                        'type':     'ignore',
                        'channel':  'objarray',
                    }, unvirtualized_channels)
                self.virtual_channels[v_id] = virtual_channel_factory(v_type, id=v_id, **v_args)
        # 
        # create virtual channels for any still left out
        #
        if not virtual_only:
            for c_ID in unvirtualized_channels:
                c_obj = unvirtualized_channels[c_ID]
                v_name = c_obj.name
                v_id = 'v{0}'.format(c_ID)
                channel_ID = 'chan ' + c_ID
                sequence = 0
                while not v_name or v_id in self.virtual_channels or show.has_section('virtual '+v_id):
                    sequence += 1
                    v_name = 'channel {0}#{1}'.format(c_ID, sequence)
                    v_id = 'v{0}_{1}'.format(c_ID, sequence)

                self.virtual_channels[v_id] = virtual_channel_factory(
                    ('dimmer' if c_obj.dimmer else 'toggle'),
                    id=v_id,
                    name=v_name,
                    color=(show.get(channel_ID, 'color') if show.has_option(channel_ID, 'color') else None),
                    channel=c_obj,
                )

        self.loaded = True

    def load_file(self, filename, open_device=True, virtual_only=False):
        if isinstance(filename, (list, tuple)):
            self.load([open(f) for f in filename], open_device, virtual_only)
        else:
            self.load(open(filename), open_device, virtual_only)

    def _dump_ps_tree(self, file, parent):
        if parent.subordinates:
            print("; -- subordinate{1} of {0}:".format(parent.id, '' if len(parent.subordinates)==1 else 's'), file=file)
            for order, sub in enumerate(parent.subordinates):
                print("[power {0}]".format(sub.id), file=file)
                print("disp_order={0}".format(order), file=file)
                print("amps={0:f}".format(sub.amps), file=file)
                print(file=file)
                self._dump_ps_tree(file, sub)

    def save(self, file):
        "Save configuration profile data to file, including general comments."

        def multiline(s):
            "Format multi-line string for proper printing in config file"
            if s is None:
                return ''
            return '\n\t'.join(str(s).split('\n'))

        print(''';
; vim:set syntax=cfg:
; vi:set ts=4 sw=4 noexpandtab:
;
; Lumos Light Orchestration System
; Show Configuration Profile
;
; Edit this file directly (instructions are provided in-line below, and are
; also explained in the product documentation; see LUMOS-CONFIG(5)), or use
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
[show]''', file=file)
        print("title="        + multiline(self.title), file=file)
        print("description="  + multiline(self.description), file=file)
        print("powersources=" + ' '.join(self.top_power_sources), file=file)
        print("networks="     + ' '.join(sorted(self.networks)), file=file)
        print('''
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
;   disp_order=n     For subordinate power sources, this indicates the
;                    relative display position of this source amongst
;                    its siblings.  (optional)
;
;''', file=file)
#        for powerID in sorted(self.all_power_sources):
#            print >>file, "[power %s]" % powerID
#            print >>file, "amps=%f"    % self.all_power_sources[powerID].amps
#            #print >>file, "gfci=%s"    % ('yes' if self.all_power_sources[powerID].gfci else 'no')
#            print >>file
        for powerID in self.top_power_sources:
            print("[power {0}]".format(powerID), file=file)
            print("amps={0:f}".format(self.all_power_sources[powerID].amps), file=file)
            print(file=file)
            self._dump_ps_tree(file, self.all_power_sources[powerID])

        print('''
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
;                       parallel    byte-at-a-time strobed port
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
;''', file=file)
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
                        print('type=%s' % possible_type, file=file)
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
                    print("%s=%s" % (attribute_name, ('yes' if v else 'no')), file=file)
                elif v is not None:
                    print("%s=%s" % (attribute_name, multiline(v)), file=file)

        global_controller_list = {}
        unit_network_id = {}
        channel_full_id = {}
        for netID, o in sorted(self.networks.items()):
            print("[net %s]" % netID, file=file)
            dump_object_constructor(file, o, supported_network_types, skip=('open_device',))
            
            print("units=%s" % ' '.join(sorted(o.units)), file=file)
            print(file=file)
            global_controller_list.update(o.units)
            for u in o.units:
                unit_network_id[u] = netID

        print('''
;___________________________________________________________________________
;CONTROLLER UNITS
;
; The following sections, each named [unit XXX], where XXX is the name of
; a controller unit from the "units" value in its network section, describe 
; the various controller devices attached to a given network.  Since they
; will be receiving commands over the same wire, all units on a network
; need to have compatible protocols.
; 
;   power_source=N  The name of the power source which feeds this unit.
;
;   type=...        Unit type.  This must correspond to a known device
;                   driver plug-in installed in Lumos.  As of the time
;                   this file was written, the available types include:
;                      lynx10     LynX-10 serial X-10 controller
;                      lumos      Lumos SSR controller device
;                      cm17a      X-10 "Firecracker" serial bit controller
;                      renard     Renard DIY controller, serial protocol
;                      olsen595   Olsen595/Grinch DIY controllers, parallel
;                      firegod    FireGod DIY controller
;                      udmx       Micro DMX USB controller
;
;   address=...     Unit address.  (not all unit types use addresses)
;                   (firegod, renard, lumos)
;
;   resolution=n    How many dimmer levels are supported.  If a channel may
;                   go from 0 to 63, its resolution is 64.
;                   (firegod, cm17a, lynx10, renard, lumos)
;
;   channels=n      For controllers with variable numbers of channels,
;                   specify how many are attached to this controller unit.
;                   (firegod, olsen595, renard, lumos)
;''', file=file)
        global_channel_list = {}
        for unitID, o in sorted(global_controller_list.items()):
            print("[unit %s]" % unitID, file=file)
#           print >>file, 'network=%s' % unit_network_id[unitID]
            print('power_source=%s' % o.power_source.id, file=file)
            typemap = {}
            for t in self.controller_typemaps:
                typemap.update(t)
            dump_object_constructor(file, o, typemap, skip=('power_source', 'network', 'id'))
            print(file=file)
            global_channel_list[unitID] = o.channels
        print('''
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
;   power_source=ID power source ID feeding this channel, if different from the
;                   one feeding the controller unit as a whole.
;''', file=file)
        for unitID, unit_channel_list in sorted(global_channel_list.items()):
            unitObj = global_controller_list[unitID]
            for channelID, o in sorted(unit_channel_list.items()):
                print("[chan %s.%s]" % (unitID, channelID), file=file)
                if o.warm is not None:
                    print('warm=%.2f' % o.pct_dimmer_value(o.warm), file=file)
                if o.power_source is not None and o.power_source is not unitObj.power_source:
                    print('power_source=%s' % o.power_source.id, file=file)
                dump_object_constructor(file, o, None, skip=('id', 'warm', 'power_source'), method=unitObj.add_channel)
                channel_full_id[id(o)] = '{0}.{1}'.format(unitID, channelID)
                print(file=file)
        print(''';
;___________________________________________________________________________
;VIRTUAL CHANNELS
;
; The following sections, each named [virtual ID], where ID is some unique
; identifier, describe each virtual channel in the system.  These are the
; higher-level abstraction of the hardware channels and are what the user
; actually works with in the sequence editor.
;
;   name=...        User-friendly name for the virtual channel.
;
;   type=...        Channel type.  For example:
;                   dimmer    Channels with dimmer capability
;                   toggle    Channels which can only be turned on or off
;                   rgb       Multi-color channels
;
;   channel=ID      ID (as defined in [chan ID] stanza) of the hardware
;                   channel which corresponds to this virtual channel.  For
;                   some devices, such as RGB-type, this is a space-separated
;                   list of channels.
;
;   color=#rrggbb   Color to use when representing the channel to the user.
;''', file=file)
        for v_id, v_obj in sorted(self.virtual_channels.items()):
            print("[virtual {0}]".format(v_id), file=file)
            dump_object_constructor(file, v_obj, supported_virtual_channel_types, skip=('id','channel'))
            if isinstance(v_obj.channel, (list,tuple)):
                print("channel={0}".format(' '.join([channel_full_id[id(o)] for o in v_obj.channel])), file=file)
            else:
                print("channel={0}".format(channel_full_id[id(v_obj.channel)]), file=file)
                    
            print(file=file)

        print(''';
;___________________________________________________________________________
;GUI CONTROLS
;
; Settings to customize the appearance and behavior of GUI tools
; in general (these are shared between all tools).  If tool-specific
; settings are needed, they will go into a separate section for that
; tool).
;
;   virtual_channel_display_order:
;                   Newline-separated list of virtual channel IDs in the
;                   order in which they should appear on-screen.
;''', file=file)
        if self.gui.virtual_channel_display_order:
            print("virtual_channel_display_order:", file=file)
            for vc_id in self.gui.virtual_channel_display_order:
                print("    {0}".format(vc_id), file=file)
        
        print(''';
;___________________________________________________________________________
;
; End Configuration Profile.
;___________________________________________________________________________''', file=file)

    def save_file(self, filename):
        output = open(filename, "w")
        self.save(output)
        output.close()

    def add_power_source(self, ps_obj):
        if ps_obj.id in self.all_power_sources:
            raise KeyError('Duplicate power source ID {0} cannot be added to show.'.format(ps_obj.id))

        self.all_power_sources[ps_obj.id] = ps_obj
        if ps_obj.parent_source is None:
            self.top_power_sources.append(ps_obj.id)

    def remove_power_source(self, ps_id):
        if ps_id in self.all_power_sources: 
            obj = self.all_power_sources[ps_id]
            if obj.parent_source is not None:
                obj.parent_source.orphan(obj)
            del self.all_power_sources[ps_id]
        if ps_id in self.top_power_sources: 
            self.top_power_sources.remove(ps_id)

    def remove_network(self, net_id):
        del self.networks[net_id]

    def add_network(self, net_id, net_obj):
        if net_id in self.networks:
            raise KeyError('Duplicate network ID {0} cannot be added to show.'.format(net_id))

        self.networks[net_id] = net_obj

    def remove_controller(self, ctl_obj):
        del self.controllers[ctl_obj.id]
        for n in self.networks:
            if ctl_obj.id in self.networks[n].units:
                del self.networks[n].units[ctl_obj.id]
                
    def rename_controller(self, old_id, new_id):
        if old_id in self.controllers:
            self.controllers[new_id] = self.controllers[old_id]
            del self.controllers[old_id]
        else:
            raise KeyError("Can't rename controller from {0} to {1}: no such ID".format(old_id, new_id))

    def add_controller(self, net_id, ctl_obj):
        self.networks[net_id].add_unit(ctl_obj.id, ctl_obj)
        self.controllers[ctl_obj.id] = ctl_obj

    def change_controller_network(self, ctl_obj, new_net_id):
        if new_net_id not in self.networks:
            raise KeyError("Can't move controller to {0}: no such network".format(new_net_id))

        new_net = self.networks[new_net_id]
        if ctl_obj.network is not new_net:
            if ctl_obj.network is not None:
                ctl_obj.network.remove_unit(ctl_obj.id)
            new_net.add_unit(ctl_obj.id, ctl_obj)

    def find_network(self, net_obj):
        "Locate a network object and return its ID"
        # Yeah, this is because network objects don't know their own ID.
        # On second thought, that wasn't a bright idea.
        for n in self.networks:
            if self.networks[n] is net_obj:
                return n
        return None

    def register_controller_factory(self, factory, typemap):
        "Add a local controller factory to the list to try."
        self.controller_factories.append(factory)
        self.controller_typemaps.append(typemap)


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
