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
import os.path
#import Lumos.GUI.Icons as Icons
import traceback
TBLIM=5

from Tkconstants              import *
#from Lumos.PowerSource        import PowerSource
#from Lumos.Network.Networks   import network_factory, supported_network_types
#from Lumos.Device.Controllers import controller_unit_factory, supported_controller_types
#from Lumos.Network            import NullNetwork

def debug(message):
    print "DEBUG:", message

class SequencerCanvas (Tkinter.Frame):
    '''Display a drawing surface to visualize the sequence of events.'''

    def __init__(self, show, sequence, *args, **kwargs):
        Tkinter.Frame.__init__(self, *args, **kwargs)
        self.show = show
        self.sequence = sequence
        self['bg']='yellow'
        vsb = ttk.Scrollbar(self, orient=VERTICAL)
        hsb = ttk.Scrollbar(self, orient=HORIZONTAL)
        self.modified_since_saved = False
        self.canvas = Tkinter.Canvas(self, height=600, width=1000, xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        vsb['command'] = self.canvas.yview
        hsb['command'] = self.canvas.xview
        vsb.pack(side=RIGHT, fill=Y, expand=False)
        self.canvas.pack(side=TOP, fill=BOTH, expand=True)
#        self.canvas.bind('<Button-2>', self._canvas_menu)
#        self.canvas.bind('<Double-Button-1>', self._canvas_menu)
        hsb.pack(side=BOTTOM, fill=X, expand=False)
        #bb = self.canvas.bbox('elements') or [0,0,0,0]
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
        self.draw_channels()
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
    def draw_channels(self):
        self.canvas.delete('chan')
        
        for vchan in self.show.virtual_channels.values():
            print vchan.id

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

        file_menu = Tkinter.Menu(menu_bar, tearoff=False)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Sequence", command=self.new_file)
        file_menu.add_command(label="Open Sequence...", command=self.open_file)
        file_menu.add_command(label="Save Sequence", command=self.save_file)
        file_menu.add_command(label="Save Sequence As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.on_quit)

        parser = argparse.ArgumentParser(description="Test of the SequenceCanvas widget.")
        parser.add_argument('--config',   '-c', help='Show configuration file')
        parser.add_argument('--sequence', '-s', help='Sequence file')
        self.options = parser.parse_args()

        if self.options.config:
            show.load_file(self.options.config, open_device=False)

        if self.options.sequence:
            seq.load_file(self.options.sequence)

    def on_quit(self):
        if self.check_unsaved_first(): return
        self.quit()

    def check_unsaved_first(self):
        return self.modified_since_saved and not tkMessageBox.askokcancel('Unsaved Changes', '''
You have made changes which haven't been saved.  Are you sure?
If you continue, you will lose those changes!
''', default=tkMessageBox.CANCEL)
        
    def new_file(self):
        if self.check_unsaved_first(): return
        self.show = Show()
        self.file_name = None
        self.refresh()

    def open_file(self):
        if self.check_unsaved_first(): return
        file_name = tkFileDialog.askopenfilename(
            filetypes=(('Lumos Configuration Profile', '.conf'), ('All Files', '*')),
            defaultextension=".lseq",
            initialdir=os.getcwd(),
            parent=self,
            title="Open Sequence"
        )
        if file_name is not None and file_name.strip() != '':
            try:
                show = Show()
                show.load_file(file_name, open_device=False)
            except Exception as err:
                tkMessageBox.showerror("Unable to load file", "Error: {0}".format(traceback.format_exc(TBLIM)))
            else:
                self.show = show
                self.file_name = file_name
                self.refresh()

    def save_file(self):
        if self.file_name is None:
            self.save_file_as()
        else:
            try:
                #  self.show.save_file(self.file_name)
                raise NotImplementedError('no save funtion')
            except Exception as err:
                tkMessageBox.showerror("Error Saving Sequence", "Error writing {1}: {0}".format(traceback.format_exc(0), self.file_name))
            else:
                self.modified_since_saved = False

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

    
if __name__ == "__main__":
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
