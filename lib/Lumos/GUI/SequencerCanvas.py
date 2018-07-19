# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS GUI SEQUENCE EDITOR CANVAS WIDGET
#
# Lumos Light Orchestration System
# Copyright (c) 2013, 2014 by Steven L. Willoughby, Aloha,
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
########################################################################
import ttk, Tkinter, tkFont
import tkMessageBox, tkFileDialog
import os.path, math, sys
#import Lumos.GUI.Icons as Icons
import traceback
TBLIM=5

from Tkconstants              import *
from Lumos.VirtualChannel     import VirtualChannel
#from Lumos.PowerSource        import PowerSource
#from Lumos.Network.Networks   import network_factory, supported_network_types
#from Lumos.Device.Controllers import controller_unit_factory, supported_controller_types
#from Lumos.Network            import NullNetwork

def debug(message):
    print "DEBUG:", message

class SequencerCanvas (ttk.Frame):
    '''Display a drawing surface to visualize the sequence of events.'''

    def __init__(self, show, sequence, *args, **kwargs):
        ttk.Frame.__init__(self, *args, **kwargs)
        self.show = show
        self.zoom = 1.0
        self.sequence = sequence
        self.file_name = None
        self.clear_changes()
        self.event_clipboard = None
        self._displayed_objects = {}
#        vsb = ttk.Scrollbar(self, orient=VERTICAL)
#        hsb = ttk.Scrollbar(self, orient=HORIZONTAL)
#        self.canvas = Tkinter.Canvas(self, height=600, width=1000, xscrollcommand=hsb.set, yscrollcommand=vsb.set)
#        vsb['command'] = self.canvas.yview
#        hsb['command'] = self.canvas.xview
#        vsb.pack(side=RIGHT, fill=Y, expand=False)
#        self.canvas.pack(side=TOP, fill=BOTH, expand=True)
#        self.canvas.bind('<Button-2>', self._canvas_menu)
#        self.canvas.bind('<Double-Button-1>', self._canvas_menu)
#        hsb.pack(side=BOTTOM, fill=X, expand=False)
        #bb = self.canvas.bbox('elements') or [0,0,0,0]
        self.gui_setup()
        self.refresh()

    def zoom_in(self, *a):
        self.zoom /= 2.0
        self.refresh()

    def zoom_out(self, *a):
        self.zoom *= 2.0
        self.refresh()

    def zoom_to(self, factor):
        self.zoom = float(factor)
        self.refresh()

##    def ps_box(self):
##        r=self.canvas.create_rectangle(0, bb[3]-20, bb[2], bb[3], tags=('power', 'power_ctl'), fill='black')
##        t=self.canvas.create_text(bb[2]/2, bb[3]-10, text="POWER SOURCES", fill='white', anchor=CENTER, tags=('power', 'power_ctl'))
##        self.canvas.bind(t, '<Button-2>', self.power_ctl_menu)
##        print "Canvas:", dir(self.canvas)
##        print "Text", t, ":", self.canvas.itemconfig(t)
##        print "Text bbox", self.canvas.bbox(t)
##        print "rect bbox", self.canvas.bbox(r)
##        self.update()
#
#    def _canvas_menu(self, event):
#        # If this is already handled by another object, don't do anything additional
#        if self.canvas.find_overlapping(event.x, event.y, event.x, event.y):
#            return
#        cx = Tkinter.Menu(self, tearoff=False)
#        self._ctl_submenu(cx)
#        self._net_submenu(cx)
#        cx.add_command(label="Add New Power Source...", command=self.add_power_source)
#        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())
#        
#    def _power_ctl_menu(self, event):
#        cx = Tkinter.Menu(self, tearoff=False)
#        cx.add_command(label="Add New Power Source...", command=self.add_power_source)
#        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())
#
#    def _power_src_menu(self, event, this_ps):
#        cx = Tkinter.Menu(self, tearoff=False)
#        cx.add_command(label="Add Subordinate Power Source to {0}...".format(this_ps.id), command=lambda w=this_ps: self.add_power_source(parent_src=w))
#        cx.add_command(label="Modify Power Source {0}".format(this_ps.id), command=lambda w=this_ps: self.add_power_source(w))
#        cx.add_command(label="Delete Power Source {0}".format(this_ps.id), command=lambda w=this_ps: self.del_power_source(w))
#        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())
#
#    def add_power_source(self, src_obj=None, parent_src=None):
#        PowerSourceEditorDialog(self, self.show, src_obj, parent_src)
#
#
#    def ok_to_del_power_source(self, src_obj, force=False):
#        if src_obj is not None:
#            if src_obj.subordinates:
#                tkMessageBox.showerror("Can't Delete Power Source", "You cannot delete this power source if it still has other power sources plugged into it.")
#                return False
#
#            for controller in self.show.controllers.values():
#                if controller.power is src_obj:
#                    tkMessageBox.showerror("Can't Delete Power Source", "You cannot delete this power source if it still has loads plugged into it.")
#                    return False
#
#                for chan_id in controller.iter_channels():
#                    if controller.channels[chan_id].power is src_obj:
#                        tkMessageBox.showerror("Can't Delete Power Source", "You cannot delete this power source if it still has loads plugged into it.")
#                        return False
#
#            if force:
#                return True
#            return tkMessageBox.askokcancel("Confirm Deletion", "Are you sure you wish to delete power source {0}?".format(src_obj.id), default=tkMessageBox.CANCEL)
#
#    def del_power_source(self, src_obj, force=False):
#        if self.ok_to_del_power_source(src_obj, force):
#            self.show.remove_power_source(src_obj.id)
#        self.refresh()
#        self.modified_since_saved = True
#
    def refresh(self):
        self.timespan = 10000 + self.sequence.total_time
        self.draw_channels()
        self.draw_event_grid()
#        self.draw_power_sources()
#        self.draw_networks()
#        self.draw_controllers()
#
#    def draw_power_sources(self):
#        "Arrange the hierarchy of power sources across the bottom of the canvas."
#        self._power_locations = {}
#        self.canvas.delete('power')
#        bb = [0, 0, int(self.canvas['width'])-1, int(self.canvas['height'])-1]
#        bb[0] = max(0, bb[0])
#        bb[1] = max(0, bb[1])
#        bb[2] = max(bb[0]+50, bb[2])
#        bb[3] = max(bb[1]+50, bb[3])
#
#        top_f = self.canvas.create_rectangle(0, 0, 0, 0, fill='black', tags=('power', 'power_ctl'))
#        top_t = self.canvas.create_text(0, 0, text="POWER SOURCES", fill="white", anchor=CENTER, tags=('power', 'power_ctl'))
#        w, h = self._text_dimens(top_t)
#        self.canvas.tag_bind(top_f, '<Button-2>', self._power_ctl_menu)
#        self.canvas.tag_bind(top_t, '<Button-2>', self._power_ctl_menu)
#        self.canvas.tag_bind(top_t, '<Double-Button-1>', lambda event: self.add_power_source())
#        self.canvas.tag_bind(top_f, '<Double-Button-1>', lambda event: self.add_power_source())
#        self.canvas.coords(top_f, 0, bb[3]-h-4, bb[2], bb[3])
#        self.canvas.coords(top_t, bb[2]/2, bb[3] - h/2 - 2)
#
#        self._create_ps_tree([self.show.all_power_sources[ps] for ps in self.show.top_power_sources])
#        self._render_ps_tree([self.show.all_power_sources[ps] for ps in self.show.top_power_sources], 0, bb[3]-h-4)
#
#    def draw_networks(self):
#        "Arrange the list of networks across the left edge of the canvas."
#        self._network_locations = {}
#        self.canvas.delete('net')
#
#        for w in (
#            # because this version of Tk doesn't support rotated text (the next rev does, though)
#            # draw "NET"
#            self.canvas.create_rectangle(0, 0, 20, 59, fill='black', tags=('net', 'net_ctl')),
#            self.canvas.create_line( 5, 20,  5,  5, 15, 20, 15,  5, fill='white', width=2, tags=('net', 'net_ctl')),
#            self.canvas.create_line(15, 22,  5, 22,  5, 37, 15, 37, fill='white', width=2, tags=('net', 'net_ctl')),
#            self.canvas.create_line( 5, 29, 15, 29,                 fill='white', width=2, tags=('net', 'net_ctl')),
#            self.canvas.create_line( 5, 39, 15, 39,                 fill='white', width=2, tags=('net', 'net_ctl')),
#            self.canvas.create_line(10, 39, 10, 54,                 fill='white', width=2, tags=('net', 'net_ctl')),
#        ):
#            self.canvas.tag_bind(w, '<Button-2>', self._net_ctl_menu)
#            self.canvas.tag_bind(w, '<Double-Button-1>', self._net_ctl_menu)
#
#        cur_y = 0
#        for net_id in sorted(self.show.networks):
#            rect = self.canvas.create_rectangle(0, 0, 0, 0, fill='red', tags=('net', 'net_f_'+net_id))
#            text = self.canvas.create_text(0, 0, text=net_id, fill='white', anchor=CENTER, tags=('net', 'net_id_'+net_id))
#            tw, th = self._text_dimens(text)
#            self.canvas.coords(rect, 20, cur_y, 20+tw+4, cur_y+4+th)
#            self.canvas.coords(text, 20+tw/2+2, th/2+2+cur_y)
#            self._network_locations[net_id] = (cur_y, cur_y+th+4, 20+tw+4)
#            cur_y += th+4
#
#            for w in (rect, text):
#                self.canvas.tag_bind(w, '<Button-2>',        lambda e, n=net_id: self._net_menu(e, n))
#                self.canvas.tag_bind(w, '<Double-Button-1>', lambda e, n=net_id: self.add_network(net_id=n))
#
    def gui_setup(self):
        self.grid_frame = ttk.Frame(self)
        self.grid_frame.pack(expand=True, fill=BOTH)
        self.grid_frame.rowconfigure(1, weight=2)
        self.grid_frame.columnconfigure(1, weight=2)
        self.vc_canvas = Tkinter.Canvas(self.grid_frame)
        self.vc_canvas.grid(column=0, row=1, sticky=N+S+W+E)
        self.tl_canvas = Tkinter.Canvas(self.grid_frame)
        self.tl_canvas.grid(column=1, row=0, sticky=N+S+W+E)
        self.ev_canvas = Tkinter.Canvas(self.grid_frame)
        self.ev_canvas.grid(column=1, row=1, sticky=N+S+W+E)
        self.vsb = ttk.Scrollbar(self.grid_frame, orient=VERTICAL)
        self.hsb = ttk.Scrollbar(self.grid_frame, orient=HORIZONTAL)
        self.vsb.grid(column=2, row=1, sticky=N+S)
        self.hsb.grid(column=1, row=2, sticky=E+W)

        # graphics preferences (styling)
        self.gfx_tl_height = 20
        self.gfx_tl_major  = 3
        self.gfx_tl_minor  = 1
        self.gfx_tl_minor_h= 5
        self.gfx_tl_margin = 5
        self.gfx_tl_1sec_w = 100
        self.gfx_vc_height = 20
        self.gfx_vc_width  = 140
        self.gfx_vc_margin = 5
        self.gfx_vc_pad    = 2
        self.gfx_ev_hr     = 1
        self.gfx_ev_gridclr= '#9999ff'
        self.gfx_ev_bg     = '#777777'
        self.gfx_ev_outline= '#ffffff'


        self.ev_canvas.bind(self.show.gui.menu_button, self.on_grid_menu)

        def locked_y_scroll(*args):
            self.ev_canvas.yview(*args)
            self.vc_canvas.yview(*args)

        def locked_x_scroll(*args):
            self.ev_canvas.xview(*args)
            self.tl_canvas.xview(*args)

        self.vsb['command'] = locked_y_scroll
        self.hsb['command'] = locked_x_scroll

        self.ev_canvas['xscrollcommand'] = self.hsb.set
        self.ev_canvas['yscrollcommand'] = self.vsb.set
        self.tl_canvas['xscrollcommand'] = self.hsb.set
        self.vc_canvas['yscrollcommand'] = self.vsb.set
#        self.canvas = Tkinter.Canvas(self, height=600, width=1000, xscrollcommand=hsb.set, yscrollcommand=vsb.set)
#        vsb['command'] = self.canvas.yview
#        hsb['command'] = self.canvas.xview
#        vsb.pack(side=RIGHT, fill=Y, expand=False)
#        self.canvas.pack(side=TOP, fill=BOTH, expand=True)
#        self.canvas.bind('<Button-2>', self._canvas_menu)
#        self.canvas.bind('<Double-Button-1>', self._canvas_menu)
#        hsb.pack(side=BOTTOM, fill=X, expand=False)

    def cut_event_object(self, at_timestamp, target_event_object):
        self.copy_event_object(target_event_object)
        self.delete_event_object(at_timestamp, target_event_object)
        
    def copy_event_object(self, target_event_object):
        self.event_clipboard = target_event_object.copy()

    def paste_event_object(self, at_timestamp, to_replace_object=None, for_vchannel=None):
        if self.event_clipboard is not None:
            new_copy = self.event_clipboard.copy()
            if to_replace_object is not None:
                try:
                    new_copy.change_channel(to_replace_object.vchannel, permissive=True)
                    self.delete_event_object(at_timestamp, to_replace_object)
                    self.sequence.add(at_timestamp, new_copy)
                except ValueError as e:
                    tkMessageBox.showerror("Can't Paste (Replace) Event", "Unable to paste that kind of event here: {0}".format(e))
                finally:
                    self.refresh()
            else:
                try:
                    print "changing channel in {0} to {1}".format(new_copy, for_vchannel.id)
                    new_copy.change_channel(for_vchannel, permissive=True)
                    self.sequence.add(at_timestamp, new_copy)
                    self.note_changed()
                except ValueError as e:
                    tkMessageBox.showerror("Can't Paste Event", "Unable to paste event into that space: {0}".format(e))
                finally:
                    self.refresh()

    def on_grid_menu(self, e):
        # context menu for general areas in the grid
        eventx = self.ev_canvas.canvasx(e.x)
        eventy = self.ev_canvas.canvasy(e.y)

        #
        # Is this an area where there's already an event?
        #
        for element_id in self.ev_canvas.find_overlapping(eventx, eventy, eventx, eventy):
            print "on_grid_menu(): trying {0}".format(element_id)
            for tag in self.ev_canvas.gettags(element_id):
                print "   trying tag {0}".format(tag)
                if tag.startswith('EV:'):
                    timestamp, event_obj_id = [int(i) for i in tag.split(':')[1:3]]
                    print "      Found timestamp={0} ({1}), object={2}".format(
                        timestamp, self.timestamp_to_text(timestamp), event_obj_id
                    )
                    try:
                        for event_obj in self.sequence.events_at(timestamp):
                            print "         Sequence event {0} vs {1}".format(id(event_obj), event_obj_id)
                            if id(event_obj) == event_obj_id:
                                print "            Matched! executing on_event_menu({0}, {1}, {2}, {3})".format(
                                    e, element_id, event_obj, timestamp)
                                return self.on_event_menu(e, element_id, event_obj, timestamp)
                        tkMessageBox.showerror("Error posting context menu",
                            "Can't find that event at time {0}".format(self.timestamp_to_text(timestamp)))
                        return
                    except KeyError:
                        tkMessageBox.showerror("Error posting context menu",
                            "Can't find any events for time mark {0}".format(self.timestamp_to_text(timestamp)))
                        return
                    except ValueError as e:
                        tkMessageBox.showerror("Error processing context menu",
                            "Error handling context menu for event: {0}".format(e))
                        return
        #
        # No appropriate tags found
        # so we're clicking on an empty part of the board.
        # 
        print "Context menu in open space at ({0},{1})".format(eventx, eventy)
        print "_xcoord_to_time({0}) -> {1}".format(eventx, self._xcoord_to_time(eventx))
        print "_ycoord_to_vchannel({0}) -> {1}".format(eventy, self._ycoord_to_vchannel(eventy))

        timestamp = self._xcoord_to_time(eventx)
        time_string = self.timestamp_to_text(timestamp)
        target_channel = self._ycoord_to_vchannel(eventy)

        cx = Tkinter.Menu(self, tearoff=False)
        time_string = self.timestamp_to_text(timestamp)
        cx.add_command(label="New event @{0}...".format(time_string), command=lambda t=timestamp, c=target_channel: self.add_event(t, c))
        if self.event_clipboard is not None:
            cx.add_separator()
            cx.add_command(label="Paste", command=lambda t=timestamp, c=target_channel[1]: self.paste_event_object(t, for_vchannel=c))

        cx.post(e.x+self.winfo_rootx(), e.y+self.winfo_rooty())
        return "break"

    def on_event_menu(self, e, widget_id, event_obj, event_time):
        # context menu for an event object
        cx = Tkinter.Menu(self, tearoff=False)
        time_string = self.timestamp_to_text(event_time) #'{0:02d}:{1:06.3f}'.format(int(event_time // 60), event_time % 60)

        cx.add_command(label="Change Event {0}@{1}...".format(
            ('*' if event_obj.vchannel is None else event_obj.vchannel.name),
            time_string,
            ), command=lambda ev=event_obj: self.edit_event_object(ev))

        cx.add_separator()
        cx.add_command(label="Cut", command=lambda ev=event_obj, t=event_time: self.cut_event_object(t, ev))
        cx.add_command(label="Copy", command=lambda ev=event_obj: self.copy_event_object(ev))
        if self.event_clipboard is not None:
            cx.add_command(label="Paste (Replace)", command=lambda ev=event_obj, t=event_time: self.paste_event_object(t, ev))
        cx.add_separator()
        cx.add_command(label="Delete", command=lambda ev=event_obj, t=event_time: self.delete_event_object(t, ev))
        cx.post(e.x+self.winfo_rootx(), e.y+self.winfo_rooty())
        return "break"

    def timestamp_to_text(self, t):
        return '{0:2d}:{1:06.3f}'.format(int(t // 60000.0), (t % 60000.0) / 1000.0)

    def _xcoord_to_time(self, x):
        "Compute timestamp based on canvas x coordinate and current zoom factor."

        snap = self.zoom / 10.0
        return int((((((x - self.gfx_tl_margin) / self.gfx_tl_1sec_w) * self.zoom) // snap) * snap) * 1000)

    def _ycoord_to_vchannel(self, y):
        "Compute and return index and vchannel object based on canvas y coordinate."

        vc_index = int(((y - self.gfx_vc_margin) / self.gfx_vc_height))
        return vc_index, self.displayed_channels[vc_index]

    def add_event(self, target_time, target_vchannel_obj):
        "Prompt the user to add a new event"
        print "add_event(time={0}, channel={1}".format(target_time, target_vchannel_obj)
        EventEditorDialog(self, self, target_time, vchannel=target_vchannel_obj[1])

    def delete_event_object(self, target_time, target_event_obj):
        try:
            self.sequence.delete_event_at(target_time, target_event_obj)
        except KeyError:
            tkMessageBox.showerror("Can't Delete Event", 
                "Time {0} was not found in the sequence.".format(self.timestamp_to_text(target_time)))
        except ValueError:
            tkMessageBox.showerror("Can't Delete Event", "Unable to locate this event in the sequence.")
        else:
            self.note_changed()
            self.refresh()

    def edit_event_object(self, target_event_obj):
        print "Edit {0}".format(target_event_obj)

    def draw_event_grid(self):
        self.tl_canvas.delete('time')


        ev_ticks = math.ceil((self.timespan/1000.0)/self.zoom)
        ev_w = ev_ticks * self.gfx_tl_1sec_w

        self.ev_canvas['bg'] = self.gfx_ev_bg
        self.tl_canvas['height'] = self.gfx_tl_height + self.gfx_tl_margin * 2
        self.tl_canvas['width']  = min(800, ev_w + self.gfx_tl_margin * 2)
        self.ev_canvas['height'] = min(800, len(self.show.virtual_channels) * self.gfx_vc_height + 2 * self.gfx_vc_margin)
        self.ev_canvas['width']  = min(800, ev_w + self.gfx_tl_margin * 2)
        self.ev_canvas['scrollregion'] = (0, 0, ev_w + self.gfx_tl_margin * 2,
         len(self.show.virtual_channels) * self.gfx_vc_height + 2 * self.gfx_vc_margin)
        self.tl_canvas['scrollregion'] = (0, 0, ev_w + self.gfx_tl_margin * 2,
         self.gfx_tl_height + self.gfx_tl_margin * 2)

        for t in range(int(ev_ticks)):
            tm = t * self.zoom
            self.tl_canvas.create_text(t * self.gfx_tl_1sec_w + self.gfx_tl_major + self.gfx_tl_margin, self.gfx_tl_margin, 
                text="{0:02d}:{1:06.3f}".format(int(tm // 60), tm % 60), anchor=NW, tags="time")
            self.tl_canvas.create_line(t * self.gfx_tl_1sec_w + self.gfx_tl_margin, self.gfx_tl_margin,
                t * self.gfx_tl_1sec_w + self.gfx_tl_margin, self.gfx_tl_height + self.gfx_tl_margin,
                width=self.gfx_tl_major, tags='time');
            self.ev_canvas.create_line(t * self.gfx_tl_1sec_w + self.gfx_tl_margin, self.gfx_vc_margin,
                t * self.gfx_tl_1sec_w + self.gfx_tl_margin, len(self.show.virtual_channels) * self.gfx_vc_height + self.gfx_vc_margin,
                width=self.gfx_tl_major, tags='time', fill=self.gfx_ev_gridclr);
            for minor in range(1,10):
                self.tl_canvas.create_line(t * self.gfx_tl_1sec_w + self.gfx_tl_margin +
                        minor * (self.gfx_tl_1sec_w / 10.0), self.gfx_tl_margin + self.gfx_tl_height - self.gfx_tl_minor_h,
                    t * self.gfx_tl_1sec_w + self.gfx_tl_margin + minor * (self.gfx_tl_1sec_w / 10.0), self.gfx_tl_height + self.gfx_tl_margin,
                    width=self.gfx_tl_minor, tags='time');
                self.ev_canvas.create_line(t * self.gfx_tl_1sec_w + self.gfx_tl_margin + 
                        minor * (self.gfx_tl_1sec_w / 10.0), self.gfx_vc_margin,
                    t * self.gfx_tl_1sec_w + self.gfx_tl_margin +
                        minor * (self.gfx_tl_1sec_w / 10.0), len(self.show.virtual_channels) * self.gfx_vc_height + self.gfx_vc_margin,
                    width=self.gfx_tl_minor, tags='time', fill=self.gfx_ev_gridclr);

        for row in range(len(self.show.virtual_channels)+1):
            self.ev_canvas.create_line(self.gfx_tl_margin, row * self.gfx_vc_height + self.gfx_vc_margin,
                self.gfx_tl_margin + ev_w, row * self.gfx_vc_height + self.gfx_vc_margin,
                tags='time', width=self.gfx_ev_hr, fill=self.gfx_ev_gridclr)

        display_data = {}
        for vc in self.displayed_channels:
            display_data[vc.id] = []
            vc.display_level_change(vc.normalize_level_value('off'))

        for start_time in self.sequence.intervals:
            for event in self.sequence.events_at(start_time):
                if event.vchannel is None:
                    affected_channels = self.displayed_channels
                else:
                    affected_channels = [event.vchannel]

                for vchannel in affected_channels:
                    if event.raw_level is None:
                        before, after = vchannel.display_level_change(vchannel.normalize_level_value(event.level, permissive=True))
                    else:
                        before, after = vchannel.display_level_change(event.raw_level)

                    display_data[vchannel.id].append((start_time, 
                        start_time+(event.delta if vchannel.is_dimmable else 0), before, after, event))

        self.ev_canvas.delete('events')
        self._displayed_objects = {}
        def t_xcoord(t, hedge=False):
            "start and end x coordinates for area which contains time t (ms)"
            s = math.floor(t/100.0/self.zoom)
            e = math.ceil(t/100.0/self.zoom)
            if hedge and s == e:
                e += 1
            return s * (self.gfx_tl_1sec_w / 10.0) + self.gfx_tl_margin, e * (self.gfx_tl_1sec_w / 10.0) + self.gfx_tl_margin


        for idx, vc in enumerate(self.displayed_channels):
            last_time = 0
            last_color = '#000000'
            for start_time, end_time, start_color, end_color, event_obj in display_data[vc.id]:
                if last_time < start_time and last_color != '#000000':
                    wid = None
                    self.ev_canvas.create_rectangle(
                        t_xcoord(last_time)[0], self.gfx_vc_margin + idx*self.gfx_vc_height + self.gfx_vc_height*0.3,
                        t_xcoord(start_time)[0], self.gfx_vc_margin + idx*self.gfx_vc_height + self.gfx_vc_height*0.7,
                        fill=last_color, outline=self.gfx_ev_outline, tags=('events','cont'))

                identity = 'EV:{0}:{1}'.format(start_time, id(event_obj))
                if start_time == end_time:
                    s, e = t_xcoord(start_time, hedge=True)
                    wid = self.ev_canvas.create_rectangle(
                        s, self.gfx_vc_margin + idx*self.gfx_vc_height,
                        e, self.gfx_vc_margin + (idx+1)*self.gfx_vc_height,
                        fill=end_color, outline=self.gfx_ev_outline, tags=('events','point',identity))
                elif start_color == end_color:
                    wid = self.ev_canvas.create_rectangle(
                        t_xcoord(start_time)[0], self.gfx_vc_margin + idx*self.gfx_vc_height,
                        t_xcoord(end_time)[1], self.gfx_vc_margin + (idx+1)*self.gfx_vc_height,
                        fill=end_color, outline=self.gfx_ev_outline, tags=('events','point',identity))
                else:
                    # build gradients
                    s = t_xcoord(start_time)[0]
                    e = t_xcoord(end_time)[1]
                    v = VirtualChannel(None, None)

                    step_size = self.gfx_tl_1sec_w / 30.0
                    steps = int(math.ceil((e - s) / step_size))

                    if steps > 60:
                        step_size = (e-s) / 32.0 
                        steps = int(math.ceil((e - s) / step_size))

                    gs=s
                    ge=gs+step_size
                    sc=v._to_raw_color(start_color)
                    ec=v._to_raw_color(end_color)
                    gc=start_color
                    wid = 'EV#{0}'.format(id(event_obj))
                    for i in range(steps):
                        self.ev_canvas.create_rectangle(
                            gs, self.gfx_vc_margin + idx*self.gfx_vc_height,
                            ge, self.gfx_vc_margin + (idx+1)*self.gfx_vc_height,
                            fill=gc, outline=gc, tags=('events','point',identity))
                        gc = '#{0:02x}{1:02x}{2:02x}'.format(
                            int((sc[0] + i*(float(ec[0]-sc[0])/steps)) * 2.55) & 0xff,
                            int((sc[1] + i*(float(ec[1]-sc[1])/steps)) * 2.55) & 0xff,
                            int((sc[2] + i*(float(ec[2]-sc[2])/steps)) * 2.55) & 0xff,
                        )
                        gs = ge
                        ge += step_size
                    
                last_time = end_time
                last_color = end_color

#                if wid is not None:
#                    self.ev_canvas.tag_bind(wid, self.show.gui.menu_button, 
#                        lambda e, wid=wid, event_obj=event_obj, start_time=start_time: self.on_event_menu(e, wid, event_obj, start_time))

            if last_color != '#000000':
                self.ev_canvas.create_rectangle(
                    t_xcoord(last_time)[0], self.gfx_vc_margin + idx*self.gfx_vc_height + self.gfx_vc_height*0.3,
                    t_xcoord(self.timespan)[1], self.gfx_vc_margin + idx*self.gfx_vc_height + self.gfx_vc_height*0.7,
                    fill=last_color, tags=('events','cont'))

            try:
                self.ev_canvas.tag_raise('point','cont')
            except Tkinter.TclError:
                pass

    def draw_channels(self):
        self.vc_canvas.delete('chan')
        
        self.vc_canvas['height'] = min(800, len(self.show.virtual_channels) * self.gfx_vc_height + 2 * self.gfx_vc_margin)
        self.vc_canvas['width']  = self.gfx_vc_width + 2 * self.gfx_vc_margin
        self.vc_canvas['scrollregion'] = (0, 0,
             self.gfx_vc_width + 2 * self.gfx_vc_margin,
             len(self.show.virtual_channels) * self.gfx_vc_height + 2 * self.gfx_vc_margin)

        #
        # create display list in order
        #
        all_channels = set(self.show.virtual_channels)
        self.displayed_channels = []
        for vc_id in self.show.gui.virtual_channel_display_order:
            if vc_id in all_channels:
                self.displayed_channels.append(self.show.virtual_channels[vc_id])
                all_channels.remove(vc_id)

        for vc_id in sorted(all_channels):
            self.displayed_channels.append(self.show.virtual_channels[vc_id])

        all_channels = None

        for idx, vchan in enumerate(self.displayed_channels):
            self.vc_canvas.create_rectangle(0+self.gfx_vc_margin, idx * self.gfx_vc_height + self.gfx_vc_margin, 
                self.gfx_vc_width, (idx+1) * self.gfx_vc_height + self.gfx_vc_margin, fill=None, tags='chan')
            self.vc_canvas.create_text(0+self.gfx_vc_margin + self.gfx_vc_pad, idx * self.gfx_vc_height + self.gfx_vc_margin + self.gfx_vc_pad, 
                anchor=NW, text=vchan.name, tags='chan')

                # .id .name .dimmer

#    def draw_controllers(self):
#        self._controller_locations = {}
#        self.canvas.delete('ctrl')
#
#        # self.show.controllers{}: dict of id->obj (all existing controllers)
#        # self.show.networks[].units{}: dict of id->obj (all connected to this network)
#        # XXX how to preserve display order on row?  (row=network)
#
#        H_GAP = 5
#        V_GAP = 5
#        cur_x = max([x[2] for x in self._network_locations.values()]+[0]) + H_GAP
#        cur_y = 0
#        for controller_id in sorted(self.show.controllers):
#            ctl_obj = self.show.controllers[controller_id]
#            rect = self.canvas.create_rectangle(0, 0, 0, 0, fill='blue', tags=('ctrl', 'ctrl_f_'+controller_id))
#            text = self.canvas.create_text(0, 0, text='{0} ({1})'.format(controller_id, '???'), fill='white', tags=('ctrl', 'ctrl_id_'+controller_id))
#            tw, th = self._text_dimens(text)
#            self.canvas.coords(rect, cur_x, cur_y, cur_x + tw + 4, cur_y + th + 4)
#            self.canvas.coords(text, cur_x + 2 + tw/2, cur_y + 2 + th/2)
#            cur_x += tw + 4 + H_GAP
#            cur_y += th + 4 + V_GAP
#            for w in (rect, text):
#                self.canvas.tag_bind(w, "<Button-2>",        lambda e, c=ctl_obj: self._ctl_menu(e, c))
#                self.canvas.tag_bind(w, "<Double-Button-1>", lambda e, c=ctl_obj: self.add_controller(ctl_obj=c))
#
#
#    def _net_ctl_menu(self, event):
#        cx = Tkinter.Menu(self, tearoff=False)
#        self._net_submenu(cx)
#        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())
#
#    def _ctl_submenu(self, cx):
#        ctls = Tkinter.Menu(cx, tearoff=False)
#        cx.add_cascade(label="Add New Controller Unit", menu=ctls)
#        for ctype in sorted(supported_controller_types):
#            ctls.add_command(label=ctype+'...', command=lambda ct=ctype: self.add_controller(ctl_type=ct))
#
#    def _net_submenu(self, cx):
#        nets = Tkinter.Menu(cx, tearoff=False)
#        cx.add_cascade(label="Add New Network", menu=nets)
#        for ntype in sorted(supported_network_types):
#            nets.add_command(label=ntype+'...', command=lambda nt=ntype: self.add_network(net_type=nt))
#
#    def _net_menu(self, event, net_id):
#        cx = Tkinter.Menu(self, tearoff=False)
#        cx.add_command(label="Modify Network {0}".format(net_id), command=lambda n=net_id: self.add_network(net_id=n))
#        cx.add_command(label="Delete Network {0}".format(net_id), command=lambda n=net_id: self.del_network(n))
#        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())
#
#    def _ctl_menu(self, event, ctl_obj):
#        cx = Tkinter.Menu(self, tearoff=False)
#        cx.add_command(label="Modify Controller {0}".format(ctl_obj.id), command=lambda n=ctl_obj: self.add_controller(ctl_obj=n))
#        cx.add_command(label="Delete Controller {0}".format(ctl_obj.id), command=lambda n=ctl_obj: self.del_controller(n))
#        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())
#
#    def add_network(self, net_type=None, net_id=None):
#        NetworkEditorDialog(self, self.show, net_type, net_id)
#
#    def add_controller(self, ctl_type=None, ctl_obj=None):
#        ControllerEditorDialog(self, self.show, ctl_type, ctl_obj)
#
#    def ok_to_del_network(self, net_id, force=False):
#        if net_id in self.show.networks:
#            if self.show.networks[net_id].units:
#                tkMessageBox.showerror("Can't Delete Network", "You cannot delete this network if it still has controller units {0} plugged into it.".format(self.show.networks[net_id].units))
#                return False
#
#            if force:
#                return True
#            return tkMessageBox.askokcancel("Confirm Deletion", "Are you sure you wish to delete network {0}?".format(net_id), default=tkMessageBox.CANCEL)
#
#    def del_network(self, net_id, force=False):
#        if self.ok_to_del_network(net_id, force):
#            self.show.remove_network(net_id)
#        self.refresh()
#        self.modified_since_saved = True
#
#
#    def ok_to_del_controller(self, ctl_obj, force=False):
#        return force or tkMessageBox.askokcancel("Confirm Deletion", "Are you sure you wish to delete controller unit {0}?".format(ctl_obj.id), default=tkMessageBox.CANCEL)
#
#    def del_controller(self, ctl_obj, force=False):
#        if self.ok_to_del_controller(ctl_obj, force):
#            self.show.remove_controller(ctl_obj)
#        self.refresh()
#        self.modified_since_saved = True
#
#    def _text_dimens(self, id):
#        bb = self.canvas.bbox(id)
#        if bb is None: return (0, 0)
#        return bb[2]-bb[0], bb[3]-bb[1] # (width, height)
#
#    def _create_ps_tree(self, nodelist):
#        for node in nodelist:
#            rect = self.canvas.create_rectangle(0, 0, 0, 0, fill='green', tags=('power', 'power_f_'+node.id))
#            text = self.canvas.create_text(0, 0, text="{0} {1}A".format(node.id, node.amps), fill='black', anchor=CENTER, tags=('power', 'power_id_'+node.id))
#            for w in (rect, text):
#                self.canvas.tag_bind(w, '<Button-2>',         lambda e, n=node: self._power_src_menu(e, n))
#                self.canvas.tag_bind(w, '<Double-Button-1>',  lambda e, n=node: self.add_power_source(n))
#                self.canvas.tag_bind(w, '<B1-Motion>',        lambda e, n=node, w=rect: self._continue_drag(e, n, w))
#                self.canvas.tag_bind(w, '<B1-ButtonRelease>', lambda e, n=node, w=rect: self._end_drag(e, n, w))
#
#            if node.subordinates:
#                self._create_ps_tree(node.subordinates)
#
#    def _continue_drag(self, event, obj, tag):
#        orig = self.canvas.coords(tag)
#        self.canvas.coords(tag, event.x, orig[1], event.x+orig[2]-orig[0], orig[3])
#
#    def _end_drag(self, event, obj, tag):
#        # did we move into the space occupied by a sibling? past either end?
#        if obj.parent_source is None:
#            # we are a top-level object
#            sibling_id_list = self.show.top_power_sources
#            for i, sibling_id in enumerate(sibling_id_list):
#                if event.x <= self._power_locations[sibling_id][1]:
#                    if sibling_id != obj.id:
#                        # insert at this location
#                        old_index = sibling_id_list.index(obj.id)
#                        sibling_id_list.remove(obj.id)
#                        sibling_id_list.insert(i, obj.id)
#                    break
#            else:
#                # new tail of list
#                print "tail"
#                sibling_id_list.remove(obj.id)
#                sibling_id_list.append(obj.id)
#        else:
#            # we are a subordinate object, which is represented differently
#            sibling_obj_list = obj.parent_source.subordinates
#            for i, sibling_obj in enumerate(sibling_obj_list):
#                if event.x <= self._power_locations[sibling_obj.id][1]:
#                    if sibling_obj.id != obj.id:
#                        # insert at this location
#                        old_index = sibling_obj_list.index(obj)
#                        sibling_obj_list.remove(obj)
#                        sibling_obj_list.insert(i, obj)
#                    break
#            else:
#                # new tail of list
#                sibling_obj_list.remove(obj)
#                sibling_obj_list.append(obj)
#
#
#        self.refresh()
#
#    def _render_ps_tree(self, nodelist, left_x, bottom_y):
#        total_w = 0
#        for node in nodelist:
#            w, h = self._text_dimens('power_id_'+node.id)
#            if node.subordinates:
#                w = max(w + 4, self._render_ps_tree(node.subordinates, left_x, bottom_y - h - 4))
#            else:
#                w += 4
#
#            self.canvas.coords('power_f_'+node.id, left_x, bottom_y, left_x + w, bottom_y - h - 4)
#            self.canvas.coords('power_id_'+node.id, left_x + w/2, bottom_y - h/2 - 2)
#            self._power_locations[node.id] = (left_x, left_x + w)
#            print "Render: {} @{}-{}".format(node.id, left_x, left_x+w)
#            left_x += w
#            total_w += w
#        return total_w
#
#
## Input Validators
#
#
##def _int_validator(old, new):
##    if new.strip() == '':
##        return True
##    if re.match(r'^[-+]?\d+$', new):
##        return True
##    return False
##
##def _float_validator(old, new):
##    if new.strip() == '':
##        return True
##    if re.match(r'^[+-]?(\d+(\.(\d+)?)?|\.\d+)$', new):
##        return True
##    return False
#def _nonneg_validator(old, new):
#    if new.strip() == '':
#        return True
#    if re.match(r'^[+]?\d+$', new):
#        return True
#    return False
#
#def _int_validator(old, new):
#    if re.match(r'^[+-]?\d*$', new):
#        return True
#    return False
#
#def _nonneg_float_validator(old, new):
#    if new.strip() == '':
#        return True
#    if re.match(r'^[+]?\d*\.?\d*$', new):
#        return True
#    return False
#
#def _id_validator(old, new):
#    if re.match(r'^\w*$', new):
#        return True
#    return False
#
#def _float_validator(old, new):
#    if new.strip() == '': return True
#    if re.match(r'^[+-]?\d*\.?\d*$', new):
#        return True
#    return False
#
#        
#

class LumosGenericDialog(ttk.Frame):
    def __init__(self, parent, sequencer):
        dialog = Tkinter.Toplevel()
        dialog.transient(parent)
        ttk.Frame.__init__(self, dialog)
        self.pack(side=TOP, expand=True, fill=BOTH)
        self._L_field_info = {}

    def _set_form(self, id, fields):
        f = ttk.Frame(self)
        self._L_field_info[id] = {}

        for row, field_spec in enumerate(fields):
            tag, control_type, label = field_spec

            l = ttk.Label(f, text=label)
            if control_type == 'toggle':
                v = Tkinter.IntVar()
                w = ttk.Frame(f)

                ttk.Radiobutton(w, text='Off', value=0, variable=v).pack(side=LEFT)
                ttk.Radiobutton(w, text='On',  value=1, variable=v).pack(side=LEFT)
            elif control_type == 'dimmer':
                v = Tkinter.DoubleVar()
                v2= Tkinter.StringVar()
                w = ttk.Frame(f)
                
                v2.set('  0.0%')
                ttk.Scale(w, from_=0.0, to=100.0, variable=v, 
                          command=lambda x, v=v, v2=v2: v2.set("{0:5.1f}%".format(v.get()))).pack(side=LEFT)
                ttk.Label(w, textvariable=v2).pack(side=LEFT)

            elif control_type == 'time':
                vm= Tkinter.StringVar()
                vs= Tkinter.StringVar()
                v = (vm,vs)

                vm.set('0')
                vs.set('0.000')

                w = ttk.Frame(f)
                v1= self.register(self._validate_time_min)
                v2= self.register(self._validate_time_sec)

                ttk.Entry(w, width=3, justify=RIGHT, validate='all', validatecommand=(v1, '%V', '%S', '%P'),
                        textvariable=vm).pack(side=LEFT)
                ttk.Label(w, text=':').pack(side=LEFT)
                ttk.Entry(w, width=7, justify=RIGHT, validate='all', validatecommand=(v2, '%V', '%S', '%P'),
                        textvariable=vs).pack(side=LEFT)

            elif control_type == 'channel':
                v = None
                w = ttk.Frame(f)
            else:
                v = None
                w = ttk.Frame(f)
                
            l.grid(row=row, column=0, sticky=W)
            w.grid(row=row, column=1, sticky=W)
            self._L_field_info[id][tag] = (row, l, w, v)

        f.pack(side=TOP, expand=True, fill=BOTH)

    def _set_cancel_save_buttons(self):
        buttons = ttk.Frame(self)
        buttons.pack(side=BOTTOM, anchor=S)
        ttk.Button(buttons, text="Cancel", command=self.master.destroy).pack(side=LEFT)
        ttk.Button(buttons, text="Save",   command=self._save).pack(side=RIGHT)

    def _save(self):
        tkMessageBox.showerror("No Save", "The save operation for this dialog is not implemented.")

    def _validate_time_min(self, operation, insertvalue, fullvalue):
        if operation=='key' and insertvalue not in '0123456789':
            return False

        try:
            v = int(fullvalue)
        except ValueError:
            return False

        if not 0 <= v:
            return False

        return True

    def _validate_time_sec(self, operation, insertvalue, fullvalue):
        if operation=='key' and insertvalue not in '.0123456789':
            return False

        try:
            v = float(fullvalue)
        except ValueError:
            return False

        if not 0 <= v < 60:
            return False
        return True

#    
# Edit|New Event [chan]@[time]
#---------------------------------------
# Channel Affected:  [All | list]
# Toggle:            []off []on
# Dimmer:            0=================100%
# Color:             [   ] click to change
#
# Event Time:        [nn] minutes [   n.nnn] seconds
# Duration of effect:             [   n.nnn] seconds
#
# [Cancel]                         [Save]
#
class EventEditorDialog (LumosGenericDialog):
    def __init__(self, parent, sequencer, at_time=0, event_obj=None, vchannel=None):
        LumosGenericDialog.__init__(self, parent, sequencer)

        # save app-specific data in this object
        self.event_obj = event_obj
        self.sequencer = sequencer
        self.timestamp = at_time
        self.vchannel  = vchannel

        # set up the GUI widgets

        self.master.title("{2} Event for {0}@{1}".format(
            '*' if vchannel is None else vchannel.name,
            self.sequencer.timestamp_to_text(at_time),
            "Create New" if self.event_obj is None else "Modify"
        ))

        self._set_form('controls', (
            ('vchan', 'channel', 'Channel Affected:',   ),
            ('on',    'toggle',  'Power:',              ),
            ('level', 'dimmer',  'Dimmer:',             ),
            ('color', 'color',   'Color:',              ),
            ('start', 'time',    'Event Time',          ),
            ('delta', 'time',    'Duration of Effect:', ),
        ))
        self._set_cancel_save_buttons()


    def _save(self):
        pass


        
#class PowerSourceEditorDialog(ttk.Frame):
#    def __init__(self, parent, show_obj, power_source_obj=None, parent_source=None):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#
#        if power_source_obj is not None and power_source_obj.parent_source is not None:
#            parent_source = power_source_obj.parent_source
#
#        ttk.Frame.__init__(self, root)
#        self.show_obj = show_obj
#        self.power_source_obj = power_source_obj
#        self.parent_source = parent_source
#        self.parent_widget = parent
#        self.validate_id = (self.register(_id_validator), '%s', '%P')
#        self.validate_nn = (self.register(_nonneg_float_validator), '%s', '%P')
#
#
#        main = ttk.Frame(self)
#        buttons = ttk.Frame(self)
#
#        main.pack(side=TOP, fill=BOTH, expand=True)
#        buttons.pack(side=BOTTOM, anchor=S)
#
#        ttk.Button(buttons, text='Save', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        ttk.Label(main, text="ID:").grid(row=0, column=0, sticky=W)
#        self.v_id = Tkinter.StringVar()
#        if parent_source is not None:
#            idf=ttk.Frame(main)
#            ttk.Label(idf, text=parent_source.id+'.').grid(row=0, column=0, sticky=E)
#            ttk.Entry(idf, textvariable=self.v_id, width=10, justify=LEFT, validate='key', validatecommand=self.validate_id).grid(row=0, column=1, sticky=W)
#            idf.grid(row=0, column=1, sticky=W)
#        else:
#            ttk.Entry(main, textvariable=self.v_id, width=10, justify=LEFT, validate='key', validatecommand=self.validate_id).grid(row=0, column=1, sticky=W)
#            
#
#        ttk.Label(main, text="Capacity:").grid(row=1, column=0, sticky=W)
#        self.v_cap = Tkinter.StringVar()
#        capf=ttk.Frame(main)
#        ttk.Entry(capf, textvariable=self.v_cap, width=4, justify=RIGHT, validate='key', validatecommand=self.validate_nn).grid(row=0, column=0, sticky=W)
#        ttk.Label(capf, text="amps").grid(row=0, column=1, sticky=W)
#        capf.grid(row=1, column=1, sticky=W)
#
#        #ttk.Label(main, text="GFCI Protected?").grid(row=2, column=0, sticky=W)
#        #self.v_gfci = Tkinter.IntVar()
#        #ttk.Checkbutton(main, variable=self.v_gfci).grid(row=2, column=1, sticky=W)
#
#        if power_source_obj is None: 
#            root.title("Enter New Power Source")
#        else:
#            root.title("Edit Power Source {0}".format(power_source_obj.id))
#            if parent_source is not None:
#                self.v_id.set(power_source_obj.id[len(parent_source.id)+1:])
#            else:
#                self.v_id.set(power_source_obj.id)
#            self.v_cap.set(power_source_obj.amps)
#            #self.v_gfci.set(power_source_obj.gfci)
#
#        ttk.Button(main, text="Remove This Source", state='normal' if power_source_obj is not None else 'disabled', command=self.delete_me).grid(row=0, column=10)
#        ttk.Button(main, text="Add Subordinate", state='normal' if power_source_obj is not None else 'disabled', command=self.add_child).grid(row=1, column=10)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def add_child(self):
#        self.parent_widget.add_power_source(parent_src=self.power_source_obj)
#
#    def delete_me(self):
#        if self.parent_widget.ok_to_del_power_source(self.power_source_obj):
#            self.parent_widget.del_power_source(self.power_source_obj, force=True)
#            self.master.destroy()
#
#    def _save(self):
#        #new_id, new_cap, new_gfci = self.v_id.get(), self.v_cap.get(), self.v_gfci.get()
#        new_id, new_cap = self.v_id.get(), self.v_cap.get()
#        if new_id == '':
#            tkMessageBox.showerror("Invalid ID", "Each power source must have an ID.")
#            return
#
#        if self.parent_source is not None:
#            new_id = self.parent_source.id + '.' + new_id
#
#        if new_cap in ('', '+', '.', '+.') or float(new_cap) <= 0:
#            tkMessageBox.showerror("Invalid Capacity", "Each power source must supply at least 1 amp.")
#            return
#
#
#        if not self._is_id_unique(new_id, self.power_source_obj, [self.show_obj.all_power_sources[i] for i in self.show_obj.top_power_sources]):
#            tkMessageBox.showerror("Duplicate ID", 'The ID "{0}" is already assigned to another power source.'.format(new_id))
#            return
#
#        if self.power_source_obj is None:
#            new_source = PowerSource(new_id, amps=float(new_cap)) #, gfci=bool(new_gfci))
#            if self.parent_source is not None:
#                self.parent_source.add_subordinate_source(new_source)
#            self.show_obj.add_power_source(new_source)
#        else:
#            if self.power_source_obj.subordinates and self.power_source_obj.id != new_id:
#                self._propagate_id_prefix(self.power_source_obj.id, new_id, self.power_source_obj.subordinates)
#            self.power_source_obj.id = new_id
#            self.power_source_obj.amps = new_cap
#            #self.power_source_obj.gfci = new_gfci
#
#        self.parent_widget.modified_since_saved = True
#        self.parent_widget.refresh()
#        self.master.destroy()
#            
#
#    def _propagate_id_prefix(self, old_prefix, new_prefix, childlist):
#        for child in childlist:
#            child.id = new_prefix + child.id[len(old_prefix):]
#            if child.subordinates:
#                self._propagate_id_prefix(old_prefix, new_prefix, child.subordinates)
#
#    def _is_id_unique(self, new_id, old_obj, ps_list):
#        for source in ps_list:
#            if source.subordinates and not self._is_id_unique(new_id, old_obj, source.subordinates):
#                return False
#            if source is not old_obj and source.id == new_id:
#                return False
#        return True
#        
#def _introspect_fields(form, frame, obj, typemap, skip=None, method=None):
#    fields = {
#        #'type': (Tkinter.StringVar(), None)
#    }
#    if skip is None: skip = ()
#    if method is None: method = obj.__init__
#    if typemap is not None:
#        for possible_type in typemap:
#            if type(obj) is typemap[possible_type]:
#                fields['_type'] = possible_type
#                break
#        else:
#            raise ValueError('Cannot introspect object type for object with ID {0}'.format(obj.id))
#
#    for attribute_name in inspect.getargspec(method)[0]:
#        if attribute_name in ('self',) + skip:
#            continue
#
#        v = obj.__getattribute__(attribute_name)
#        if attribute_name == "port":
#            # special case (yuck!) for port fields, which need to be strings OR integers.  We
#            # move it to a string here so we don't force it to get stuck as an integer in the
#            # GUI interface.
#            f = Tkinter.StringVar()
#            fields[attribute_name] = (f, ttk.Entry(frame, textvariable=f, width=15, justify=LEFT), str)
#        elif type(v) is bool:
#            f = Tkinter.IntVar()
#            fields[attribute_name] = (f, ttk.Checkbutton(frame, variable=f), bool)
#        elif type(v) is float:
#            f = Tkinter.StringVar()
#            fields[attribute_name] = (f, ttk.Entry(frame, textvariable=f, width=10, justify=RIGHT, validate='key', validatecommand=form.validate_float), float)
#        elif type(v) is int:
#            f = Tkinter.StringVar()
#            fields[attribute_name] = (f, ttk.Entry(frame, textvariable=f, width=10, justify=RIGHT, validate='key', validatecommand=form.validate_int), int)
#        else:
#            f = Tkinter.StringVar()
#            fields[attribute_name] = (f, ttk.Entry(frame, textvariable=f, width=10, justify=LEFT), str)
#
#        f.set(v)
#        print "setting {} (type {}, value {}), result (type {}, value{})".format(
#            attribute_name, type(v), v, type(f.get()), f.get())
#
#    return fields
#
##form, obj, skip=None, method=None):
#def _generate_constructor_args(fields, skip=None, **kw):
#    arglist = {
#    }
#    if skip is None: skip = ()
#
#    for name in fields:
#        if name.startswith('_') or name in skip:
#            continue
#        arglist[name] = fields[name][2](fields[name][0].get())
#
#    arglist.update(kw)
#    return arglist
#
#
#
#class NetworkEditorDialog(ttk.Frame):
#    def __init__(self, parent, show_obj, network_type=None, network_id=None):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#
#        ttk.Frame.__init__(self, root)
#        self.show_obj = show_obj
#        self.network_id = network_id
#        self.network_obj = None if network_id is None else self.show_obj.networks[network_id]
#        self.network_type = network_type
#        self.parent_widget = parent
#        self.validate_id = (self.register(_id_validator), '%s', '%P')
#        self.validate_float = (self.register(_float_validator), '%s', '%P')
#        self.validate_int = (self.register(_int_validator), '%s', '%P')
#        #self.validate_nn = (self.register(_nonneg_float_validator), '%s', '%P')
#        main = ttk.Frame(self)
#        self.field_spec = _introspect_fields(self, main, self.network_obj or network_factory(network_type, open_device=False), supported_network_types, ('open_device',))
#
#        buttons = ttk.Frame(self)
#
#        main.pack(side=TOP, fill=BOTH, expand=True)
#        buttons.pack(side=BOTTOM, anchor=S)
#
#        ttk.Button(buttons, text='Save', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        ttk.Label(main, text="{0} Network ID:".format(self.field_spec['_type'])).grid(row=0, column=0, sticky=W)
#        self.v_id = Tkinter.StringVar()
#        ttk.Entry(main, textvariable=self.v_id, width=10, justify=LEFT, validate='key', validatecommand=self.validate_id).grid(row=0, column=1, sticky=W)
#
#        for row, field_name in enumerate([n for n in sorted(self.field_spec) if not n.startswith('_')]):
#            ttk.Label(main, text=field_name+":").grid(row=row+1, column=0, sticky=W)
#            print field_name
#            print self.field_spec[field_name]
#            self.field_spec[field_name][1].grid(row=row+1, column=1, sticky=W)
#
#        if self.network_obj is None: 
#            root.title("Enter New {0} Network".format(self.field_spec['_type']))
#        else:
#            root.title("Edit {1} Network {0}".format(network_id, self.field_spec['_type']))
#            self.v_id.set(network_id)
#
#
#        ttk.Button(main, text="Remove This Network", state='normal' if self.network_obj is not None else 'disabled', command=self.delete_me).grid(row=0, column=10)
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def delete_me(self):
#        if self.parent_widget.ok_to_del_network(self.network_id):
#            self.parent_widget.del_network(self.network_id, force=True)
#            self.master.destroy()
#
#    def _save(self):
#        new_id = self.v_id.get()
#        if new_id == '':
#            tkMessageBox.showerror("Invalid ID", "Each network must have an ID.")
#            return
#
#        #new_id = self.v_id.get()
#        if new_id in self.show_obj.networks and self.show_obj.networks[new_id] is not self.network_obj:
#            tkMessageBox.showerror("Duplicate ID", 'The ID "{0}" is already assigned to another network.'.format(new_id))
#            return
#
#        if self.network_obj is None:
#            try:
#                new_network = network_factory(self.field_spec['_type'], **_generate_constructor_args(self.field_spec, open_device=False))
#            except Exception as err:
#                tkMessageBox.showerror("Error", "Can't create that network: {0}".format(err))
#                return
#            else:
#                self.show_obj.add_network(new_id, new_network)
#        else:
#            # check to see if the constructor likes these values
#            try:
#                network_factory(self.field_spec['_type'], **_generate_constructor_args(self.field_spec, open_device=False))
#            except Exception as err:
#                tkMessageBox.showerror("Error in network values", "{0}".format(err))
#                return
#
#            if new_id != self.network_id:
#                self.show_obj.remove_network(self.network_id)
#                self.show_obj.add_network(new_id, self.network_obj)
#
#            for f in self.field_spec:
#                if f.startswith('_'):
#                    continue
#                self.network_obj.__setattr__(f, self.field_spec[f][2](self.field_spec[f][0].get()))
#
#            # change port to an integer value if possible; otherwise leave it as a string
#            # XXX check elsewhere to make sure it doesn't get stuck as an int if it started with an int value
#            try:
#                i = int(self.network.port)
#                self.network.port = i
#            except Exception:
#                pass
#
#        self.parent_widget.modified_since_saved = True
#        self.parent_widget.refresh()
#        self.master.destroy()
#            
#class ControllerEditorDialog(ttk.Frame):
#    def __init__(self, parent, show_obj, ctl_type=None, ctl_obj=None):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#
#        ttk.Frame.__init__(self, root)
#        self.show_obj = show_obj
#        self.ctl_obj = ctl_obj
#        self.ctl_type = ctl_type
#        self.parent_widget = parent
#        self.validate_id = (self.register(_id_validator), '%s', '%P')
#        self.validate_float = (self.register(_float_validator), '%s', '%P')
#        self.validate_int = (self.register(_int_validator), '%s', '%P')
#        #self.validate_nn = (self.register(_nonneg_float_validator), '%s', '%P')
#        main = ttk.Frame(self)
#        self.field_spec = _introspect_fields(self, main, self.ctl_obj or controller_unit_factory(ctl_type, id='__null__', network=NullNetwork(), power_source=None), supported_controller_types, ('id', 'power_source', 'network'))
#
#        buttons = ttk.Frame(self)
#
#        main.pack(side=TOP, fill=BOTH, expand=True)
#        buttons.pack(side=BOTTOM, anchor=S)
#
#        ttk.Button(buttons, text='Save', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        ttk.Label(main, text="{0} Controller ID:".format(self.field_spec['_type'])).grid(row=0, column=0, sticky=W)
#        self.v_id = Tkinter.StringVar()
#        ttk.Entry(main, textvariable=self.v_id, width=10, justify=LEFT, validate='key', validatecommand=self.validate_id).grid(row=0, column=1, sticky=W)
#
#        ttk.Label(main, text="Power Source:").grid(row=1, column=0, sticky=W)
#        self.v_power = Tkinter.StringVar()
#        ttk.Combobox(main, textvariable=self.v_power, values=sorted(self.show_obj.all_power_sources), state='readonly').grid(row=1, column=1, sticky=W)
#
#        ttk.Label(main, text="Network:").grid(row=2, column=0, sticky=W)
#        self.v_net = Tkinter.StringVar()
#        ttk.Combobox(main, textvariable=self.v_net, values=sorted(self.show_obj.networks), state='readonly').grid(row=2, column=1, sticky=W)
#
#        for row, field_name in enumerate([n for n in sorted(self.field_spec) if not n.startswith('_')]):
#            ttk.Label(main, text=field_name+":").grid(row=row+3, column=0, sticky=W)
#            print field_name
#            print self.field_spec[field_name]
#            self.field_spec[field_name][1].grid(row=row+3, column=1, sticky=W)
#
#        if self.ctl_obj is None: 
#            root.title("Enter New {0} Controller".format(self.field_spec['_type']))
#        else:
#            root.title("Edit {1} Controller {0}".format(self.ctl_obj.id, self.field_spec['_type']))
#            self.v_id.set(self.ctl_obj.id)
#            self.v_net.set(self.show_obj.find_network(self.ctl_obj.network))
#            self.v_power.set(self.ctl_obj.power_source.id)
#
#        ttk.Button(main, text="Remove This Controller", state='normal' if self.ctl_obj is not None else 'disabled', command=self.delete_me).grid(row=0, column=10)
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    # XXX left off here
#    def delete_me(self):
#        if self.parent_widget.ok_to_del_controller(self.ctl_obj):
#            self.parent_widget.del_controller(self.ctl_obj, force=True)
#            self.master.destroy()
#
#    def _save(self):
#        new_id = self.v_id.get()
#        if new_id == '':
#            tkMessageBox.showerror("Invalid ID", "Each controller must have an ID.")
#            return
#
#        if new_id in self.show_obj.controllers and self.show_obj.controllers[new_id] is not self.ctl_obj:
#            tkMessageBox.showerror("Duplicate ID", 'The ID "{0}" is already assigned to another controller.'.format(new_id))
#            return
#
#        net_id = self.v_net.get()
#        if net_id not in self.show_obj.networks:
#            tkMessageBox.showerror("Missing Network", 'Each controller must be assigned a communications network.')
#            return
#
#        pwr_id = self.v_power.get()
#        if pwr_id not in self.show_obj.all_power_sources:
#            tkMessageBox.showerror("Missing Power Source", 'Each controller must be assigned a power source.')
#            return
#
#        if self.ctl_obj is None:
#            try:
#                new_controller = controller_unit_factory(self.field_spec['_type'], 
#                    **_generate_constructor_args(self.field_spec, id=new_id, 
#                        network=self.show_obj.networks[net_id], 
#                        power_source=self.show_obj.all_power_sources[pwr_id]
#                    )
#                )
#            except Exception as err:
#                tkMessageBox.showerror("Error", "Can't create that controller: {0}".format(err))
#                return
#            else:
#                self.show_obj.add_controller(net_id, new_controller)
#        else:
#            # check to see if the constructor likes these values
#            try:
#                controller_unit_factory(self.field_spec['_type'], **_generate_constructor_args(self.field_spec, id=new_id,
#                    network=self.show_obj.networks[net_id],
#                    power_source=self.show_obj.all_power_sources[pwr_id]))
#            except Exception as err:
#                tkMessageBox.showerror("Error in controller values", "{0}".format(err))
#                return
#
#            if new_id != self.ctl_obj.id:
#                self.show_obj.rename_controller(self.ctl_obj.id, new_id)
#                self.ctl_obj.id = new_id
#
#            for f in self.field_spec:
#                if f.startswith('_'):
#                    continue
#                self.ctl_obj.__setattr__(f, self.field_spec[f][2](self.field_spec[f][0].get()))
#
#            net_obj = self.show_obj.networks[net_id]
#            if net_obj is not self.ctl_obj.network:
#                self.show_obj.change_controller_network(self.ctl_obj, net_id)
#                self.ctl_obj.network = self.show_obj.networks[net_id]
#
#            if pwr_id != self.ctl_obj.power_source.id:
#                self.ctl_obj.power_source = self.show_obj.all_power_sources[pwr_id]
#
#        self.parent_widget.modified_since_saved = True
#        self.parent_widget.refresh()
#        self.master.destroy()
#            
#
from Lumos.Show     import Show
from Lumos.Sequence import Sequence
import argparse

class Application (SequencerCanvas):
    def __init__(self, *a, **k):
        SequencerCanvas.__init__(self, *a, **k)
        self.file_name = None

        menu_bar = Tkinter.Menu(self)
        self.master.config(menu=menu_bar)
        self.master.title("Lumos Sequence Editor")
        self.menu_objects = {}

        def create_menu(parent, title, item_list):
            self.menu_objects[title] = this_menu = Tkinter.Menu(parent, tearoff=False)
            parent.add_cascade(label=title, menu=this_menu)
            accelerator_idx = {
                'darwin':   1,
            }.get(sys.platform, 0)

            for label, accelerators, binding in item_list:
                if label == '---':
                    this_menu.add_separator()
                elif isinstance(binding, (list, tuple)):
                    create_menu(this_menu, label, binding)
                else:
                    if len(accelerators) <= accelerator_idx or accelerators[accelerator_idx] is None: 
                        this_menu.add_command(label=label, command=binding)
                    else: 
                        acc = accelerators[accelerator_idx]
                        if isinstance(acc, (list, tuple)):
                            acc_tag = acc[0]
                            keybind = acc[1]
                        else:
                            acc_tag = keybind = acc

                        if acc_tag is not None:
                            this_menu.add_command(label=label, accelerator=acc_tag, command=binding)
                        if keybind is not None:
                            self.bind_all('<'+keybind+'>', binding)

        #   menu item               (default, Mac, ...)          command
        create_menu(menu_bar, "File", [
            ("New Sequence",         (None, "Command-n",),       self.new_file),
            ("Open Sequence...",     (None, "Command-o",),       self.open_file),
            ("Save Sequence",        (None, "Command-s",),       self.save_file),
            ("Save Sequence As...",  (None, "Shift-Command-S",), self.save_file_as),
            ("---",                  None,                       None),
            ("Load Configuration...",(None, "Command-l",),       self.load_config),
            ("---",                  None,                       None),
            ("Quit",                 (None, "Command-q"),        self.on_quit),
        ])

        create_menu(menu_bar, "View", [
            ("Zoom in",              (None, "Command-=",),       self.zoom_in),
            ("Zoom out",             (None, 
                                        ("Command--","Command-minus")),
                                                                 self.zoom_out),
            ("Zoom",                 (),                         [
                ("10 minutes",       (),                            lambda *e: self.zoom_to(600)),
                ("5 minutes",        (),                            lambda *e: self.zoom_to(300)),
                ("1 minute",         (),                            lambda *e: self.zoom_to(60)),
                ("30 seconds",       (),                            lambda *e: self.zoom_to(30)),
                ("10 seconds",       (),                            lambda *e: self.zoom_to(10)),
                ("5 seconds",        (),                            lambda *e: self.zoom_to(5)),
                ("2 seconds",        (),                            lambda *e: self.zoom_to(2)),
                ("1 second",         (None, "Command-0"),           lambda *e: self.zoom_to(1)),
                ("1/2 second",       (),                            lambda *e: self.zoom_to(.5)),
                ("1/5 second",       (),                            lambda *e: self.zoom_to(.2)),
                ("1/10 second",      (),                            lambda *e: self.zoom_to(.1)),
                ("1/20 second",      (),                            lambda *e: self.zoom_to(.05)),
                ("1/50 second",      (),                            lambda *e: self.zoom_to(.02)),
                ("1/100 second",     (),                            lambda *e: self.zoom_to(.01)),
            ]),
        ])

        parser = argparse.ArgumentParser(description="Test of the SequenceCanvas widget.")
        parser.add_argument('--config',   '-c', help='Show configuration file')
        parser.add_argument('--sequence', '-s', help='Sequence file')
        parser.add_argument('--verbose',  '-v', help='Increase information output level')
        self.options = parser.parse_args()

        if self.options.config:
            self.show.load_file(self.options.config, open_device=False, virtual_only=True)
            self.disable_load_config()

        if self.options.sequence:
            self.sequence.load_file(self.options.sequence, self.show.controllers, self.show.virtual_channels)
            self.file_name = self.options.sequence
            self.set_title()

        if self.options.verbose:
            raise NotImplementedError("-v option not yet implemented")  #XXX

        self.refresh()

    def load_config(self, *a):
        if not self.show.loaded:
            file_name = tkFileDialog.askopenfilename(
                filetypes=(('Lumos Show Configuration File', '.conf'), ('All Files', '*')),
                defaultextension=".conf",
                initialdir=os.getcwd(),
                parent=self,
                title="Load Show Configuration"
            )
            if file_name:
                self.show.load_file(file_name, open_device=False, virtual_only=True)
                self.refresh()
        self.disable_load_config()

    def disable_load_config(self):
        self.menu_objects['File'].entryconfigure('Load Configuration...', state=DISABLED)

    def set_title(self):
        self.master.title("Lumos Sequence Editor - {0} {1}".format(
            self.file_name or 'Untitled',
            '(*)' if self.modified_since_saved else ''
        ))

    def on_quit(self, *a):
        if self.check_unsaved_first(): return
        self.quit()

    def note_changed(self, how_many=1):
        self.modified_since_saved += how_many
        self.set_title()

    def clear_changes(self):
        self.modified_since_saved = 0
        self.set_title()

    def check_unsaved_first(self):
        return self.modified_since_saved and not tkMessageBox.askokcancel('Unsaved Changes', '''
You have made {0} change{1} which {2} been saved.  Are you sure?
If you continue, you will lose {3} change{1}!'''.format(
    self.modified_since_saved,
    '' if self.modified_since_saved == 1 else 's',
    "hasn't" if self.modified_since_saved == 1 else "haven't",
    'that' if self.modified_since_saved == 1 else 'those',
), default=tkMessageBox.CANCEL)
        
    def new_file(self):
        if self.check_unsaved_first(): return
        self.clear_changes()
        self.sequence = Sequence()
        self.file_name = None
        self.set_title()
        self.refresh()

    def open_file(self):
        if self.check_unsaved_first(): return
        file_name = tkFileDialog.askopenfilename(
            filetypes=(('Lumos Sequence File', '.lseq'), ('All Files', '*')),
            defaultextension=".lseq",
            initialdir=os.getcwd(),
            parent=self,
            title="Open Sequence"
        )
        if file_name is not None and file_name.strip() != '':
            try:
                seq = Sequence()
                seq.load_file(file_name, self.show.controllers, self.show.virtual_channels)
            except Exception as err:
                tkMessageBox.showerror("Unable to load file", "Error: {0}".format(traceback.format_exc(TBLIM)))
            else:
                self.clear_changes()
                self.sequence = seq
                self.file_name = file_name
                self.set_title()
                self.refresh()

    def save_file(self):
        if self.file_name is None:
            self.save_file_as()
        else:
            try:
                self.sequence.save_file(self.file_name)
            except Exception as err:
                tkMessageBox.showerror("Error Saving Sequence", "Error writing {1}: {0}".format(traceback.format_exc(0), self.file_name))
            else:
                self.clear_changes()

    def save_file_as(self):
        if self.file_name is None:
            f_dir = os.getcwd()
            f_name = None
        else:
            f_dir, f_name = os.path.split(self.file_name)

        file_name = tkFileDialog.asksaveasfilename(
            defaultextension='.lseq',
            filetypes=(('Lumos Sequence ', '*.lseq'), ('All Files', '*')),
            initialdir=f_dir,
            initialfile=f_name,
            parent=self,
            title="Save Sequence As"
        )
        if file_name is not None and file_name.strip() != '':
            self.file_name = file_name.strip()
            self.save_file()
            self.set_title()

    
if __name__ == "__main__":
#    import sys
#
#    if sys.platform == 'darwin':
#        try:
#            import os
#            os.system('''/usr/bin/osascript -e 'tell app "Finder" to set frontmost of process "Python" to true' ''')
#        except Exception:
#            pass

    root = Tkinter.Tk()
    show = Show()
    seq = Sequence()
    app = Application(show, seq, master=root)
    app.pack(fill=BOTH, expand=True)
    app.mainloop()
    try:
        root.destroy()
    except:
        pass

# minus underscore asciitilde exclam at numbersign dollar percent
# asciicirum ampersand asterisk parenleft parenright plus equal
# F1 F2 ... F10 quoteleft(`) quoteright(') less greater question
# comma period slash braceleft braceright bar colon quotedbl(")
# bracketleft bracketright backslash semicolon Escape 1 2 ... 0
# KP_Enter Up Left Down Right Prior Home Next End
# Super_L (fn)
#
# Single click in grid: select cell (becomes "current" target for commands)
# Shift-click in grid: extend selection to include multiple cells in range
# Control/Command-click in grid: add individual cells to selection list
# Click-drag in grid: select range to add (control/command) to selection list
#
# Insert:
#  ON event (over ranges)
#  OFF event (over ranges)
#  set-level event (over ranges)  )_depends on channel type; both are set-level
#  set-color event (over ranges)  )  really
#  arbitrary event dialog
#
# Delete:
#  events under selection
# 
# Edit:
#  double-click on grid: events under selection 
#       (arbitrary dialog with common fields enabled)
#
# Cut/Copy/Paste events selected
#
# Macro functions:
#  random
#  shimmer
#  sparkle
