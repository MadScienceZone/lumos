# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS GUI CONFIGURATION EDITOR CANVAS WIDGET
#
# Lumos Light Orchestration System
# Copyright (c) 2012 by Steven L. Willoughby, Aloha,
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
import re, os.path, inspect
#import Lumos.GUI.Icons as Icons
import traceback
TBLIM=5

from Tkconstants              import *
from Lumos.PowerSource        import PowerSource
from Lumos.Network.Networks   import network_factory, supported_network_types
from Lumos.Device.Controllers import controller_unit_factory, supported_controller_types
from Lumos.Network            import NullNetwork

def debug(message):
    #print "DEBUG:", message
    pass


class ConfigurationCanvas (Tkinter.Frame):
    '''Display a drawing surface to visualize the show configuration.'''

    def __init__(self, show, *args, **kwargs):
        Tkinter.Frame.__init__(self, *args, **kwargs)
        self.show = show
        self['bg']='yellow'
        vsb = ttk.Scrollbar(self, orient=VERTICAL)
        hsb = ttk.Scrollbar(self, orient=HORIZONTAL)
        self.modified_since_saved = False
        self.canvas = Tkinter.Canvas(self, xscrollcommand=hsb.set, yscrollcommand=vsb.set)
        vsb['command'] = self.canvas.yview
        hsb['command'] = self.canvas.xview
        vsb.pack(side=RIGHT, fill=Y, expand=False)
        self.canvas.pack(side=TOP, fill=BOTH, expand=True)
        self.canvas.bind('<Button-2>', self._canvas_menu)
        self.canvas.bind('<Double-Button-1>', self._canvas_menu)
        hsb.pack(side=BOTTOM, fill=X, expand=False)
        #bb = self.canvas.bbox('elements') or [0,0,0,0]
        self.refresh()

#    def ps_box(self):
#        r=self.canvas.create_rectangle(0, bb[3]-20, bb[2], bb[3], tags=('power', 'power_ctl'), fill='black')
#        t=self.canvas.create_text(bb[2]/2, bb[3]-10, text="POWER SOURCES", fill='white', anchor=CENTER, tags=('power', 'power_ctl'))
#        self.canvas.bind(t, '<Button-2>', self.power_ctl_menu)
#        print "Canvas:", dir(self.canvas)
#        print "Text", t, ":", self.canvas.itemconfig(t)
#        print "Text bbox", self.canvas.bbox(t)
#        print "rect bbox", self.canvas.bbox(r)
#        self.update()

    def _canvas_menu(self, event):
        # If this is already handled by another object, don't do anything additional
        if self.canvas.find_overlapping(event.x, event.y, event.x, event.y):
            return
        cx = Tkinter.Menu(self, tearoff=False)
        self._ctl_submenu(cx)
        self._net_submenu(cx)
        cx.add_command(label="Add New Power Source...", command=self.add_power_source)
        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())
        
    def _power_ctl_menu(self, event):
        cx = Tkinter.Menu(self, tearoff=False)
        cx.add_command(label="Add New Power Source...", command=self.add_power_source)
        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())

    def _power_src_menu(self, event, this_ps):
        cx = Tkinter.Menu(self, tearoff=False)
        cx.add_command(label="Add Subordinate Power Source to {0}...".format(this_ps.id), command=lambda w=this_ps: self.add_power_source(parent_src=w))
        cx.add_command(label="Modify Power Source {0}".format(this_ps.id), command=lambda w=this_ps: self.add_power_source(w))
        cx.add_command(label="Delete Power Source {0}".format(this_ps.id), command=lambda w=this_ps: self.del_power_source(w))
        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())

    def add_power_source(self, src_obj=None, parent_src=None):
        PowerSourceEditorDialog(self, self.show, src_obj, parent_src)


    def ok_to_del_power_source(self, src_obj, force=False):
        if src_obj is not None:
            if src_obj.subordinates:
                tkMessageBox.showerror("Can't Delete Power Source", "You cannot delete this power source if it still has other power sources plugged into it.")
                return False

            for controller in self.show.controllers.values():
                if controller.power is src_obj:
                    tkMessageBox.showerror("Can't Delete Power Source", "You cannot delete this power source if it still has loads plugged into it.")
                    return False

                for chan_id in controller.iter_channels():
                    if controller.channels[chan_id].power is src_obj:
                        tkMessageBox.showerror("Can't Delete Power Source", "You cannot delete this power source if it still has loads plugged into it.")
                        return False

            if force:
                return True
            return tkMessageBox.askokcancel("Confirm Deletion", "Are you sure you wish to delete power source {0}?".format(src_obj.id), default=tkMessageBox.CANCEL)

    def del_power_source(self, src_obj, force=False):
        if self.ok_to_del_power_source(src_obj, force):
            self.show.remove_power_source(src_obj.id)
        self.refresh()
        self.modified_since_saved = True

    def refresh(self):
        self.draw_power_sources()
        self.draw_networks()
        self.draw_controllers()

    def draw_power_sources(self):
        "Arrange the hierarchy of power sources across the bottom of the canvas."
        self._power_locations = {}
        self.canvas.delete('power')
        bb = [0, 0, int(self.canvas['width'])-1, int(self.canvas['height'])-1]
        bb[0] = max(0, bb[0])
        bb[1] = max(0, bb[1])
        bb[2] = max(bb[0]+50, bb[2])
        bb[3] = max(bb[1]+50, bb[3])

        top_f = self.canvas.create_rectangle(0, 0, 0, 0, fill='black', tags=('power', 'power_ctl'))
        top_t = self.canvas.create_text(0, 0, text="POWER SOURCES", fill="white", anchor=CENTER, tags=('power', 'power_ctl'))
        w, h = self._text_dimens(top_t)
        self.canvas.tag_bind(top_f, '<Button-2>', self._power_ctl_menu)
        self.canvas.tag_bind(top_t, '<Button-2>', self._power_ctl_menu)
        self.canvas.tag_bind(top_t, '<Double-Button-1>', lambda event: self.add_power_source())
        self.canvas.tag_bind(top_f, '<Double-Button-1>', lambda event: self.add_power_source())
        self.canvas.coords(top_f, 0, bb[3]-h-4, bb[2], bb[3])
        self.canvas.coords(top_t, bb[2]/2, bb[3] - h/2 - 2)

        self._create_ps_tree([self.show.all_power_sources[ps] for ps in self.show.top_power_sources])
        self._render_ps_tree([self.show.all_power_sources[ps] for ps in self.show.top_power_sources], 0, bb[3]-h-4)

    def draw_networks(self):
        "Arrange the list of networks across the left edge of the canvas."
        self._network_locations = {}
        self.canvas.delete('net')

        for w in (
            # because this version of Tk doesn't support rotated text (the next rev does, though)
            # draw "NET"
            self.canvas.create_rectangle(0, 0, 20, 59, fill='black', tags=('net', 'net_ctl')),
            self.canvas.create_line( 5, 20,  5,  5, 15, 20, 15,  5, fill='white', width=2, tags=('net', 'net_ctl')),
            self.canvas.create_line(15, 22,  5, 22,  5, 37, 15, 37, fill='white', width=2, tags=('net', 'net_ctl')),
            self.canvas.create_line( 5, 29, 15, 29,                 fill='white', width=2, tags=('net', 'net_ctl')),
            self.canvas.create_line( 5, 39, 15, 39,                 fill='white', width=2, tags=('net', 'net_ctl')),
            self.canvas.create_line(10, 39, 10, 54,                 fill='white', width=2, tags=('net', 'net_ctl')),
        ):
            self.canvas.tag_bind(w, '<Button-2>', self._net_ctl_menu)
            self.canvas.tag_bind(w, '<Double-Button-1>', self._net_ctl_menu)

        cur_y = 0
        for net_id in sorted(self.show.networks):
            rect = self.canvas.create_rectangle(0, 0, 0, 0, fill='red', tags=('net', 'net_f_'+net_id))
            text = self.canvas.create_text(0, 0, text=net_id, fill='white', anchor=CENTER, tags=('net', 'net_id_'+net_id))
            tw, th = self._text_dimens(text)
            self.canvas.coords(rect, 20, cur_y, 20+tw+4, cur_y+4+th)
            self.canvas.coords(text, 20+tw/2+2, th/2+2+cur_y)
            self._network_locations[net_id] = (cur_y, cur_y+th+4, 20+tw+4)
            cur_y += th+4

            for w in (rect, text):
                self.canvas.tag_bind(w, '<Button-2>',        lambda e, n=net_id: self._net_menu(e, n))
                self.canvas.tag_bind(w, '<Double-Button-1>', lambda e, n=net_id: self.add_network(net_id=n))

    def draw_controllers(self):
        self._controller_locations = {}
        self.canvas.delete('ctrl')

        # self.show.controllers{}: dict of id->obj (all existing controllers)
        # self.show.networks[].units{}: dict of id->obj (all connected to this network)
        # XXX how to preserve display order on row?  (row=network)

        H_GAP = 5
        V_GAP = 5
        cur_x = max([x[2] for x in self._network_locations.values()]+[0]) + H_GAP
        cur_y = 0
        for controller_id in sorted(self.show.controllers):
            ctl_obj = self.show.controllers[controller_id]
            rect = self.canvas.create_rectangle(0, 0, 0, 0, fill='blue', tags=('ctrl', 'ctrl_f_'+controller_id))
            text = self.canvas.create_text(0, 0, text='{0} ({1})'.format(controller_id, '???'), fill='white', tags=('ctrl', 'ctrl_id_'+controller_id))
            tw, th = self._text_dimens(text)
            self.canvas.coords(rect, cur_x, cur_y, cur_x + tw + 4, cur_y + th + 4)
            self.canvas.coords(text, cur_x + 2 + tw/2, cur_y + 2 + th/2)
            cur_x += tw + 4 + H_GAP
            cur_y += th + 4 + V_GAP
            for w in (rect, text):
                self.canvas.tag_bind(w, "<Button-2>",        lambda e, c=ctl_obj: self._ctl_menu(e, c))
                self.canvas.tag_bind(w, "<Double-Button-1>", lambda e, c=ctl_obj: self.add_controller(ctl_obj=c))


    def _net_ctl_menu(self, event):
        cx = Tkinter.Menu(self, tearoff=False)
        self._net_submenu(cx)
        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())

    def _ctl_submenu(self, cx):
        ctls = Tkinter.Menu(cx, tearoff=False)
        cx.add_cascade(label="Add New Controller Unit", menu=ctls)
        for ctype in sorted(supported_controller_types):
            ctls.add_command(label=ctype+'...', command=lambda ct=ctype: self.add_controller(ctl_type=ct))

    def _net_submenu(self, cx):
        nets = Tkinter.Menu(cx, tearoff=False)
        cx.add_cascade(label="Add New Network", menu=nets)
        for ntype in sorted(supported_network_types):
            nets.add_command(label=ntype+'...', command=lambda nt=ntype: self.add_network(net_type=nt))

    def _net_menu(self, event, net_id):
        cx = Tkinter.Menu(self, tearoff=False)
        cx.add_command(label="Modify Network {0}".format(net_id), command=lambda n=net_id: self.add_network(net_id=n))
        cx.add_command(label="Delete Network {0}".format(net_id), command=lambda n=net_id: self.del_network(n))
        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())

    def _ctl_menu(self, event, ctl_obj):
        cx = Tkinter.Menu(self, tearoff=False)
        cx.add_command(label="Modify Controller {0}".format(ctl_obj.id), command=lambda n=ctl_obj: self.add_controller(ctl_obj=n))
        cx.add_command(label="Delete Controller {0}".format(ctl_obj.id), command=lambda n=ctl_obj: self.del_controller(n))
        cx.post(event.x+self.winfo_rootx(), event.y+self.winfo_rooty())

    def add_network(self, net_type=None, net_id=None):
        NetworkEditorDialog(self, self.show, net_type, net_id)

    def add_controller(self, ctl_type=None, ctl_obj=None):
        ControllerEditorDialog(self, self.show, ctl_type, ctl_obj)

    def ok_to_del_network(self, net_id, force=False):
        if net_id in self.show.networks:
            if self.show.networks[net_id].units:
                tkMessageBox.showerror("Can't Delete Network", "You cannot delete this network if it still has controller units {0} plugged into it.".format(self.show.networks[net_id].units))
                return False

            if force:
                return True
            return tkMessageBox.askokcancel("Confirm Deletion", "Are you sure you wish to delete network {0}?".format(net_id), default=tkMessageBox.CANCEL)

    def del_network(self, net_id, force=False):
        if self.ok_to_del_network(net_id, force):
            self.show.remove_network(net_id)
        self.refresh()
        self.modified_since_saved = True


    def ok_to_del_controller(self, ctl_obj, force=False):
        return force or tkMessageBox.askokcancel("Confirm Deletion", "Are you sure you wish to delete controller unit {0}?".format(ctl_obj.id), default=tkMessageBox.CANCEL)

    def del_controller(self, ctl_obj, force=False):
        if self.ok_to_del_controller(ctl_obj, force):
            self.show.remove_controller(ctl_obj)
        self.refresh()
        self.modified_since_saved = True

    def _text_dimens(self, id):
        bb = self.canvas.bbox(id)
        if bb is None: return (0, 0)
        return bb[2]-bb[0], bb[3]-bb[1] # (width, height)

    def _create_ps_tree(self, nodelist):
        for node in nodelist:
            rect = self.canvas.create_rectangle(0, 0, 0, 0, fill='green', tags=('power', 'power_f_'+node.id))
            text = self.canvas.create_text(0, 0, text="{0} {1}A".format(node.id, node.amps), fill='black', anchor=CENTER, tags=('power', 'power_id_'+node.id))
            for w in (rect, text):
                self.canvas.tag_bind(w, '<Button-2>',         lambda e, n=node: self._power_src_menu(e, n))
                self.canvas.tag_bind(w, '<Double-Button-1>',  lambda e, n=node: self.add_power_source(n))
                self.canvas.tag_bind(w, '<B1-Motion>',        lambda e, n=node, w=rect: self._continue_drag(e, n, w))
                self.canvas.tag_bind(w, '<B1-ButtonRelease>', lambda e, n=node, w=rect: self._end_drag(e, n, w))

            if node.subordinates:
                self._create_ps_tree(node.subordinates)

    def _continue_drag(self, event, obj, tag):
        orig = self.canvas.coords(tag)
        self.canvas.coords(tag, event.x, orig[1], event.x+orig[2]-orig[0], orig[3])

    def _end_drag(self, event, obj, tag):
        # did we move into the space occupied by a sibling? past either end?
        if obj.parent_source is None:
            # we are a top-level object
            sibling_id_list = self.show.top_power_sources
            for i, sibling_id in enumerate(sibling_id_list):
                if event.x <= self._power_locations[sibling_id][1]:
                    if sibling_id != obj.id:
                        # insert at this location
                        old_index = sibling_id_list.index(obj.id)
                        sibling_id_list.remove(obj.id)
                        sibling_id_list.insert(i, obj.id)
                    break
            else:
                # new tail of list
                print "tail"
                sibling_id_list.remove(obj.id)
                sibling_id_list.append(obj.id)
        else:
            # we are a subordinate object, which is represented differently
            sibling_obj_list = obj.parent_source.subordinates
            for i, sibling_obj in enumerate(sibling_obj_list):
                if event.x <= self._power_locations[sibling_obj.id][1]:
                    if sibling_obj.id != obj.id:
                        # insert at this location
                        old_index = sibling_obj_list.index(obj)
                        sibling_obj_list.remove(obj)
                        sibling_obj_list.insert(i, obj)
                    break
            else:
                # new tail of list
                sibling_obj_list.remove(obj)
                sibling_obj_list.append(obj)


        self.refresh()

    def _render_ps_tree(self, nodelist, left_x, bottom_y):
        total_w = 0
        for node in nodelist:
            w, h = self._text_dimens('power_id_'+node.id)
            if node.subordinates:
                w = max(w + 4, self._render_ps_tree(node.subordinates, left_x, bottom_y - h - 4))
            else:
                w += 4

            self.canvas.coords('power_f_'+node.id, left_x, bottom_y, left_x + w, bottom_y - h - 4)
            self.canvas.coords('power_id_'+node.id, left_x + w/2, bottom_y - h/2 - 2)
            self._power_locations[node.id] = (left_x, left_x + w)
            print "Render: {} @{}-{}".format(node.id, left_x, left_x+w)
            left_x += w
            total_w += w
        return total_w


# Input Validators


#def _int_validator(old, new):
#    if new.strip() == '':
#        return True
#    if re.match(r'^[-+]?\d+$', new):
#        return True
#    return False
#
#def _float_validator(old, new):
#    if new.strip() == '':
#        return True
#    if re.match(r'^[+-]?(\d+(\.(\d+)?)?|\.\d+)$', new):
#        return True
#    return False
def _nonneg_validator(old, new):
    if new.strip() == '':
        return True
    if re.match(r'^[+]?\d+$', new):
        return True
    return False

def _int_validator(old, new):
    if re.match(r'^[+-]?\d*$', new):
        return True
    return False

def _nonneg_float_validator(old, new):
    if new.strip() == '':
        return True
    if re.match(r'^[+]?\d*\.?\d*$', new):
        return True
    return False

def _id_validator(old, new):
    if re.match(r'^\w*$', new):
        return True
    return False

def _float_validator(old, new):
    if new.strip() == '': return True
    if re.match(r'^[+-]?\d*\.?\d*$', new):
        return True
    return False

        
class PowerSourceEditorDialog(ttk.Frame):
    def __init__(self, parent, show_obj, power_source_obj=None, parent_source=None):
        root = Tkinter.Toplevel()
        root.transient(parent)

        if power_source_obj is not None and power_source_obj.parent_source is not None:
            parent_source = power_source_obj.parent_source

        ttk.Frame.__init__(self, root)
        self.show_obj = show_obj
        self.power_source_obj = power_source_obj
        self.parent_source = parent_source
        self.parent_widget = parent
        self.validate_id = (self.register(_id_validator), '%s', '%P')
        self.validate_nn = (self.register(_nonneg_float_validator), '%s', '%P')


        main = ttk.Frame(self)
        buttons = ttk.Frame(self)

        main.pack(side=TOP, fill=BOTH, expand=True)
        buttons.pack(side=BOTTOM, anchor=S)

        ttk.Button(buttons, text='Save', command=self._save).pack(side=RIGHT)
        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)

        ttk.Label(main, text="ID:").grid(row=0, column=0, sticky=W)
        self.v_id = Tkinter.StringVar()
        if parent_source is not None:
            idf=ttk.Frame(main)
            ttk.Label(idf, text=parent_source.id+'.').grid(row=0, column=0, sticky=E)
            ttk.Entry(idf, textvariable=self.v_id, width=10, justify=LEFT, validate='key', validatecommand=self.validate_id).grid(row=0, column=1, sticky=W)
            idf.grid(row=0, column=1, sticky=W)
        else:
            ttk.Entry(main, textvariable=self.v_id, width=10, justify=LEFT, validate='key', validatecommand=self.validate_id).grid(row=0, column=1, sticky=W)
            

        ttk.Label(main, text="Capacity:").grid(row=1, column=0, sticky=W)
        self.v_cap = Tkinter.StringVar()
        capf=ttk.Frame(main)
        ttk.Entry(capf, textvariable=self.v_cap, width=4, justify=RIGHT, validate='key', validatecommand=self.validate_nn).grid(row=0, column=0, sticky=W)
        ttk.Label(capf, text="amps").grid(row=0, column=1, sticky=W)
        capf.grid(row=1, column=1, sticky=W)

        #ttk.Label(main, text="GFCI Protected?").grid(row=2, column=0, sticky=W)
        #self.v_gfci = Tkinter.IntVar()
        #ttk.Checkbutton(main, variable=self.v_gfci).grid(row=2, column=1, sticky=W)

        if power_source_obj is None: 
            root.title("Enter New Power Source")
        else:
            root.title("Edit Power Source {0}".format(power_source_obj.id))
            if parent_source is not None:
                self.v_id.set(power_source_obj.id[len(parent_source.id)+1:])
            else:
                self.v_id.set(power_source_obj.id)
            self.v_cap.set(power_source_obj.amps)
            #self.v_gfci.set(power_source_obj.gfci)

        ttk.Button(main, text="Remove This Source", state='normal' if power_source_obj is not None else 'disabled', command=self.delete_me).grid(row=0, column=10)
        ttk.Button(main, text="Add Subordinate", state='normal' if power_source_obj is not None else 'disabled', command=self.add_child).grid(row=1, column=10)

        self.pack(side=TOP, expand=True, fill=BOTH)

    def add_child(self):
        self.parent_widget.add_power_source(parent_src=self.power_source_obj)

    def delete_me(self):
        if self.parent_widget.ok_to_del_power_source(self.power_source_obj):
            self.parent_widget.del_power_source(self.power_source_obj, force=True)
            self.master.destroy()

    def _save(self):
        #new_id, new_cap, new_gfci = self.v_id.get(), self.v_cap.get(), self.v_gfci.get()
        new_id, new_cap = self.v_id.get(), self.v_cap.get()
        if new_id == '':
            tkMessageBox.showerror("Invalid ID", "Each power source must have an ID.")
            return

        if self.parent_source is not None:
            new_id = self.parent_source.id + '.' + new_id

        if new_cap in ('', '+', '.', '+.') or float(new_cap) <= 0:
            tkMessageBox.showerror("Invalid Capacity", "Each power source must supply at least 1 amp.")
            return


        if not self._is_id_unique(new_id, self.power_source_obj, [self.show_obj.all_power_sources[i] for i in self.show_obj.top_power_sources]):
            tkMessageBox.showerror("Duplicate ID", 'The ID "{0}" is already assigned to another power source.'.format(new_id))
            return

        if self.power_source_obj is None:
            new_source = PowerSource(new_id, amps=float(new_cap)) #, gfci=bool(new_gfci))
            if self.parent_source is not None:
                self.parent_source.add_subordinate_source(new_source)
            self.show_obj.add_power_source(new_source)
        else:
            if self.power_source_obj.subordinates and self.power_source_obj.id != new_id:
                self._propagate_id_prefix(self.power_source_obj.id, new_id, self.power_source_obj.subordinates)
            self.power_source_obj.id = new_id
            self.power_source_obj.amps = new_cap
            #self.power_source_obj.gfci = new_gfci

        self.parent_widget.modified_since_saved = True
        self.parent_widget.refresh()
        self.master.destroy()
            

    def _propagate_id_prefix(self, old_prefix, new_prefix, childlist):
        for child in childlist:
            child.id = new_prefix + child.id[len(old_prefix):]
            if child.subordinates:
                self._propagate_id_prefix(old_prefix, new_prefix, child.subordinates)

    def _is_id_unique(self, new_id, old_obj, ps_list):
        for source in ps_list:
            if source.subordinates and not self._is_id_unique(new_id, old_obj, source.subordinates):
                return False
            if source is not old_obj and source.id == new_id:
                return False
        return True
        
def _introspect_fields(form, frame, obj, typemap, skip=None, method=None):
    fields = {
        #'type': (Tkinter.StringVar(), None)
    }
    if skip is None: skip = ()
    if method is None: method = obj.__init__
    if typemap is not None:
        for possible_type in typemap:
            if type(obj) is typemap[possible_type]:
                fields['_type'] = possible_type
                break
        else:
            raise ValueError('Cannot introspect object type for object with ID {0}'.format(obj.id))

    for attribute_name in inspect.getargspec(method)[0]:
        if attribute_name in ('self',) + skip:
            continue

        v = obj.__getattribute__(attribute_name)
        if attribute_name == "port":
            # special case (yuck!) for port fields, which need to be strings OR integers.  We
            # move it to a string here so we don't force it to get stuck as an integer in the
            # GUI interface.
            f = Tkinter.StringVar()
            fields[attribute_name] = (f, ttk.Entry(frame, textvariable=f, width=15, justify=LEFT), str)
        elif type(v) is bool:
            f = Tkinter.IntVar()
            fields[attribute_name] = (f, ttk.Checkbutton(frame, variable=f), bool)
        elif type(v) is float:
            f = Tkinter.StringVar()
            fields[attribute_name] = (f, ttk.Entry(frame, textvariable=f, width=10, justify=RIGHT, validate='key', validatecommand=form.validate_float), float)
        elif type(v) is int:
            f = Tkinter.StringVar()
            fields[attribute_name] = (f, ttk.Entry(frame, textvariable=f, width=10, justify=RIGHT, validate='key', validatecommand=form.validate_int), int)
        else:
            f = Tkinter.StringVar()
            fields[attribute_name] = (f, ttk.Entry(frame, textvariable=f, width=10, justify=LEFT), str)

        f.set(v)
        print "setting {} (type {}, value {}), result (type {}, value{})".format(
            attribute_name, type(v), v, type(f.get()), f.get())

    return fields

#form, obj, skip=None, method=None):
def _generate_constructor_args(fields, skip=None, **kw):
    arglist = {
    }
    if skip is None: skip = ()

    for name in fields:
        if name.startswith('_') or name in skip:
            continue
        arglist[name] = fields[name][2](fields[name][0].get())

    arglist.update(kw)
    return arglist



class NetworkEditorDialog(ttk.Frame):
    def __init__(self, parent, show_obj, network_type=None, network_id=None):
        root = Tkinter.Toplevel()
        root.transient(parent)

        ttk.Frame.__init__(self, root)
        self.show_obj = show_obj
        self.network_id = network_id
        self.network_obj = None if network_id is None else self.show_obj.networks[network_id]
        self.network_type = network_type
        self.parent_widget = parent
        self.validate_id = (self.register(_id_validator), '%s', '%P')
        self.validate_float = (self.register(_float_validator), '%s', '%P')
        self.validate_int = (self.register(_int_validator), '%s', '%P')
        #self.validate_nn = (self.register(_nonneg_float_validator), '%s', '%P')
        main = ttk.Frame(self)
        self.field_spec = _introspect_fields(self, main, self.network_obj or network_factory(network_type, open_device=False), supported_network_types, ('open_device',))

        buttons = ttk.Frame(self)

        main.pack(side=TOP, fill=BOTH, expand=True)
        buttons.pack(side=BOTTOM, anchor=S)

        ttk.Button(buttons, text='Save', command=self._save).pack(side=RIGHT)
        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)

        ttk.Label(main, text="{0} Network ID:".format(self.field_spec['_type'])).grid(row=0, column=0, sticky=W)
        self.v_id = Tkinter.StringVar()
        ttk.Entry(main, textvariable=self.v_id, width=10, justify=LEFT, validate='key', validatecommand=self.validate_id).grid(row=0, column=1, sticky=W)

        for row, field_name in enumerate([n for n in sorted(self.field_spec) if not n.startswith('_')]):
            ttk.Label(main, text=field_name+":").grid(row=row+1, column=0, sticky=W)
            print field_name
            print self.field_spec[field_name]
            self.field_spec[field_name][1].grid(row=row+1, column=1, sticky=W)

        if self.network_obj is None: 
            root.title("Enter New {0} Network".format(self.field_spec['_type']))
        else:
            root.title("Edit {1} Network {0}".format(network_id, self.field_spec['_type']))
            self.v_id.set(network_id)


        ttk.Button(main, text="Remove This Network", state='normal' if self.network_obj is not None else 'disabled', command=self.delete_me).grid(row=0, column=10)
        self.pack(side=TOP, expand=True, fill=BOTH)

    def delete_me(self):
        if self.parent_widget.ok_to_del_network(self.network_id):
            self.parent_widget.del_network(self.network_id, force=True)
            self.master.destroy()

    def _save(self):
        new_id = self.v_id.get()
        if new_id == '':
            tkMessageBox.showerror("Invalid ID", "Each network must have an ID.")
            return

        #new_id = self.v_id.get()
        if new_id in self.show_obj.networks and self.show_obj.networks[new_id] is not self.network_obj:
            tkMessageBox.showerror("Duplicate ID", 'The ID "{0}" is already assigned to another network.'.format(new_id))
            return

        if self.network_obj is None:
            try:
                new_network = network_factory(self.field_spec['_type'], **_generate_constructor_args(self.field_spec, open_device=False))
            except Exception as err:
                tkMessageBox.showerror("Error", "Can't create that network: {0}".format(err))
                return
            else:
                self.show_obj.add_network(new_id, new_network)
        else:
            # check to see if the constructor likes these values
            try:
                network_factory(self.field_spec['_type'], **_generate_constructor_args(self.field_spec, open_device=False))
            except Exception as err:
                tkMessageBox.showerror("Error in network values", "{0}".format(err))
                return

            if new_id != self.network_id:
                self.show_obj.remove_network(self.network_id)
                self.show_obj.add_network(new_id, self.network_obj)

            for f in self.field_spec:
                if f.startswith('_'):
                    continue
                self.network_obj.__setattr__(f, self.field_spec[f][2](self.field_spec[f][0].get()))

            # change port to an integer value if possible; otherwise leave it as a string
            # XXX check elsewhere to make sure it doesn't get stuck as an int if it started with an int value
            try:
                i = int(self.network.port)
                self.network.port = i
            except Exception:
                pass

        self.parent_widget.modified_since_saved = True
        self.parent_widget.refresh()
        self.master.destroy()
            
class ControllerEditorDialog(ttk.Frame):
    def __init__(self, parent, show_obj, ctl_type=None, ctl_obj=None):
        root = Tkinter.Toplevel()
        root.transient(parent)

        ttk.Frame.__init__(self, root)
        self.show_obj = show_obj
        self.ctl_obj = ctl_obj
        self.ctl_type = ctl_type
        self.parent_widget = parent
        self.validate_id = (self.register(_id_validator), '%s', '%P')
        self.validate_float = (self.register(_float_validator), '%s', '%P')
        self.validate_int = (self.register(_int_validator), '%s', '%P')
        #self.validate_nn = (self.register(_nonneg_float_validator), '%s', '%P')
        main = ttk.Frame(self)
        self.field_spec = _introspect_fields(self, main, self.ctl_obj or controller_unit_factory(ctl_type, id='__null__', network=NullNetwork(), power_source=None), supported_controller_types, ('id', 'power_source', 'network'))

        buttons = ttk.Frame(self)

        main.pack(side=TOP, fill=BOTH, expand=True)
        buttons.pack(side=BOTTOM, anchor=S)

        ttk.Button(buttons, text='Save', command=self._save).pack(side=RIGHT)
        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)

        ttk.Label(main, text="{0} Controller ID:".format(self.field_spec['_type'])).grid(row=0, column=0, sticky=W)
        self.v_id = Tkinter.StringVar()
        ttk.Entry(main, textvariable=self.v_id, width=10, justify=LEFT, validate='key', validatecommand=self.validate_id).grid(row=0, column=1, sticky=W)

        ttk.Label(main, text="Power Source:").grid(row=1, column=0, sticky=W)
        self.v_power = Tkinter.StringVar()
        ttk.Combobox(main, textvariable=self.v_power, values=sorted(self.show_obj.all_power_sources), state='readonly').grid(row=1, column=1, sticky=W)

        ttk.Label(main, text="Network:").grid(row=2, column=0, sticky=W)
        self.v_net = Tkinter.StringVar()
        ttk.Combobox(main, textvariable=self.v_net, values=sorted(self.show_obj.networks), state='readonly').grid(row=2, column=1, sticky=W)

        for row, field_name in enumerate([n for n in sorted(self.field_spec) if not n.startswith('_')]):
            ttk.Label(main, text=field_name+":").grid(row=row+3, column=0, sticky=W)
            print field_name
            print self.field_spec[field_name]
            self.field_spec[field_name][1].grid(row=row+3, column=1, sticky=W)

        if self.ctl_obj is None: 
            root.title("Enter New {0} Controller".format(self.field_spec['_type']))
        else:
            root.title("Edit {1} Controller {0}".format(self.ctl_obj.id, self.field_spec['_type']))
            self.v_id.set(self.ctl_obj.id)
            self.v_net.set(self.show_obj.find_network(self.ctl_obj.network))
            self.v_power.set(self.ctl_obj.power_source.id)

        ttk.Button(main, text="Remove This Controller", state='normal' if self.ctl_obj is not None else 'disabled', command=self.delete_me).grid(row=0, column=10)
        self.pack(side=TOP, expand=True, fill=BOTH)

    # XXX left off here
    def delete_me(self):
        if self.parent_widget.ok_to_del_controller(self.ctl_obj):
            self.parent_widget.del_controller(self.ctl_obj, force=True)
            self.master.destroy()

    def _save(self):
        new_id = self.v_id.get()
        if new_id == '':
            tkMessageBox.showerror("Invalid ID", "Each controller must have an ID.")
            return

        if new_id in self.show_obj.controllers and self.show_obj.controllers[new_id] is not self.ctl_obj:
            tkMessageBox.showerror("Duplicate ID", 'The ID "{0}" is already assigned to another controller.'.format(new_id))
            return

        net_id = self.v_net.get()
        if net_id not in self.show_obj.networks:
            tkMessageBox.showerror("Missing Network", 'Each controller must be assigned a communications network.')
            return

        pwr_id = self.v_power.get()
        if pwr_id not in self.show_obj.all_power_sources:
            tkMessageBox.showerror("Missing Power Source", 'Each controller must be assigned a power source.')
            return

        if self.ctl_obj is None:
            try:
                new_controller = controller_unit_factory(self.field_spec['_type'], 
                    **_generate_constructor_args(self.field_spec, id=new_id, 
                        network=self.show_obj.networks[net_id], 
                        power_source=self.show_obj.all_power_sources[pwr_id]
                    )
                )
            except Exception as err:
                tkMessageBox.showerror("Error", "Can't create that controller: {0}".format(err))
                return
            else:
                self.show_obj.add_controller(net_id, new_controller)
        else:
            # check to see if the constructor likes these values
            try:
                controller_unit_factory(self.field_spec['_type'], **_generate_constructor_args(self.field_spec, id=new_id,
                    network=self.show_obj.networks[net_id],
                    power_source=self.show_obj.all_power_sources[pwr_id]))
            except Exception as err:
                tkMessageBox.showerror("Error in controller values", "{0}".format(err))
                return

            if new_id != self.ctl_obj.id:
                self.show_obj.rename_controller(self.ctl_obj.id, new_id)
                self.ctl_obj.id = new_id

            for f in self.field_spec:
                if f.startswith('_'):
                    continue
                self.ctl_obj.__setattr__(f, self.field_spec[f][2](self.field_spec[f][0].get()))

            net_obj = self.show_obj.networks[net_id]
            if net_obj is not self.ctl_obj.network:
                self.show_obj.change_controller_network(ctl_obj, net_id)
                self.ctl_obj.network = self.show_obj.networks[net_id]

            if pwr_id != self.ctl_obj.power_source.id:
                self.ctl_obj.power_source = self.show_obj.all_power_sources[pwr_id]

        self.parent_widget.modified_since_saved = True
        self.parent_widget.refresh()
        self.master.destroy()
            


#class CharacterAbilityScores (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        self.nn = (self.register(_nonneg_validator), '%s', '%P')
#        
#        base = ttk.Labelframe(self, text='Permanent', underline=0)
#        temp = ttk.Labelframe(self, text='Temporary', underline=0)
#        misc = ttk.Labelframe(self, text='Misc.',     underline=0)
#        buttons = ttk.Frame(self)
#
#        buttons.pack(side=BOTTOM, fill=X, expand=True)
#        misc.pack(side=BOTTOM, fill=X, expand=True, padx=2, pady=2)
#        base.pack(side=LEFT, fill=BOTH, padx=2, pady=2)
#        temp.pack(side=LEFT, fill=BOTH, padx=2, pady=2)
#
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        self.fields = {}
#        for r, w,  frm,  attr,         label in (
#           (0, 3, base,  'Bstr',       'Strength:'),
#           (1, 3, base,  'Bdex',       'Dexterity:'),
#           (2, 3, base,  'Bcon',       'Constitution:'),
#           (3, 3, base,  'Bint',       'Intelligence:'),
#           (4, 3, base,  'Bwis',       'Wisdom:'),
#           (5, 3, base,  'Bcha',       'Charisma:'),
#
#           (0, 3, temp,  'Tstr',       ''),
#           (1, 3, temp,  'Tdex',       ''),
#           (2, 3, temp,  'Tcon',       ''),
#           (3, 3, temp,  'Tint',       ''),
#           (4, 3, temp,  'Twis',       ''),
#           (5, 3, temp,  'Tcha',       ''),
#
#           (0, 30, misc,  '$comments',  'Notes:'),
#        ):
#            ttk.Label(frm, text=label).grid(row=r, column=0, sticky=W)
#            self.fields[attr] = Tkinter.StringVar()
#
#            if attr == '$comments':
#                f = ttk.Frame(frm)
#                f.grid(row=r, column=1, sticky=N+S+E+W)
#                sb = ttk.Scrollbar(f)
#                t = Tkinter.Text(f,
#                    width=w,
#                    height=4,
#                    wrap=NONE,
#                    yscrollcommand=sb.set,
#                )
#                sb['command'] = t.yview
#                sb.pack(side=RIGHT, fill=Y, expand=True)
#                t.pack(fill=BOTH, expand=True)
#                self.comment_widget = t
#
#                for a in 'str', 'dex', 'con', 'int', 'wis', 'cha':
#                    if a in self.char_obj.comment_blocks:
#                        t.insert(END, '\n'.join(self.char_obj.comment_blocks[a])+'\n')
#                t.see(1.0)
#
#            else:
#                ttk.Entry(frm, 
#                    textvariable=self.fields[attr],
#                    width=w,
#                    justify=RIGHT,
#                    validate='key', 
#                    validatecommand=self.nn,
#                ).grid(row=r, column=1, sticky=W)
#
#                if attr[0] == 'B':
#                    self.fields[attr].set(str(self.char_obj.ability[attr[1:]].base))
#                else:
#                    self.fields[attr].set(str('' if self.char_obj.ability[attr[1:]].temp is None else self.char_obj.ability[attr[1:]].temp))
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for k in self.fields:
#            v = self.fields[k].get()
#            if k[0] == 'T':
#                if v.strip() == '':
#                    v = None
#                else:
#                    try:
#                        v = int(v)
#                        assert(v >= 0)
#                    except Exception as err:
#                        tkMessageBox.showerror("Value Error", "The value for temporary ability scores must be non-negative integers or completely empty.")
#                        return
#                self.char_obj.ability[k[1:]].temp = v
#
#            elif k[0] == 'B':
#                try:
#                    v = int(v)
#                    assert(v >= 0)
#                except Exception as err:
#                    tkMessageBox.showerror("Value Error", "The value for base ability scores must be non-negative integers.")
#                    return
#                self.char_obj.ability[k[1:]].base = v
#
#            elif k[0] == '$':
#                # special cases we need to handle specially
#                if k == '$comments':
#                    self.char_obj.comment_blocks['str'] = filter(None, self.comment_widget.get(1.0, END).split('\n'))
#                    for a in 'dex', 'con', 'int', 'wis', 'cha':
#                        if a in self.char_obj.comment_blocks:
#                            del self.char_obj.comment_blocks[a]
#
#        self.parent_widget.refresh()
#        self.master.destroy()

if __name__ == "__main__":
    from Lumos.Show import Show

    class Application (ConfigurationCanvas):
        def __init__(self, *a, **k):
            ConfigurationCanvas.__init__(self, *a, **k)
            self.file_name = None

            menu_bar = Tkinter.Menu(self)
            self.master.config(menu=menu_bar)

            file_menu = Tkinter.Menu(menu_bar, tearoff=False)
            menu_bar.add_cascade(label="Configuration", menu=file_menu)
            file_menu.add_command(label="New Configuration Profile", command=self.new_file)
            file_menu.add_command(label="Open Configuration Profile...", command=self.open_file)
            file_menu.add_command(label="Save Configuration Profile", command=self.save_file)
            file_menu.add_command(label="Save Configuration Profile As...", command=self.save_file_as)
            file_menu.add_separator()
            file_menu.add_command(label="Quit", command=self.on_quit)

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
                #filetypes=(('Lumos Configuration Profile', '.conf'), ('All Files', '*')),
                defaultextension=".conf",
                initialdir=os.getcwd(),
                parent=self,
                title="Open Configuration Profile"
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
                    self.show.save_file(self.file_name)
                except Exception as err:
                    tkMessageBox.showerror("Error Saving Configuration Profile", "Error writing {1}: {0}".format(traceback.format_exc(0), self.file_name))
                else:
                    self.modified_since_saved = False

        def save_file_as(self):
            if self.file_name is None:
                f_dir = os.getcwd()
                f_name = None
            else:
                f_dir, f_name = os.path.split(self.file_name)

            file_name = tkFileDialog.asksaveasfilename(
                defaultextension='.config',
                filetypes=(('Lumos Configuration Profile', '*.config'), ('All Files', '*')),
                initialdir=f_dir,
                initialfile=f_name,
                parent=self,
                title="Save Configuraiton Profile As"
            )
            if file_name is not None and file_name.strip() != '':
                self.file_name = file_name.strip()
                self.save_file()

    root = Tkinter.Tk()
    app = Application(Show(), master=root)
    app.pack(fill=BOTH, expand=True)
    app.mainloop()
    try:
        root.destroy()
    except:
        pass

## vi:set ai sm nu ts=4 sw=4 expandtab:
#########################################################################
##   _______  _______  _______                 ___       _______        #
##  (  ____ \(       )(  ___  )               /   )     (  __   )       #
##  | (    \/| () () || (   ) |              / /) |     | (  )  |       #
##  | |      | || || || (___) |             / (_) (_    | | /   |       #
##  | | ____ | |(_)| ||  ___  |            (____   _)   | (/ /) |       #
##  | | \_  )| |   | || (   ) |   Game          ) (     |   / | |       #
##  | (___) || )   ( || )   ( |   Master's      | |   _ |  (__) |       #
##  (_______)|/     \||/     \|   Assistant     (_)  (_)(_______)       #
##                                                                      #
#########################################################################
##
## Current Version: 4.0
## Adapted for the Pathfinder RPG, which is what we're playing now 
## (and this software is primarily for our own use in our play group, 
## anyway, but could be generalized later as a stand-alone product).
##
## Copyright (c) 2011 by Steven L. Willoughby, Aloha, Oregon, USA.
## All Rights Reserved.  dba Software Alchemy of Aloha, Oregon.
## Licensed under the terms and conditions of the Open Software License,
## version 3.0.
##
## Based on earlier code (versions before 4.x) by the same
## author, unreleased for the author's personal use; copyright (c)
## 1992-2009.
##
## This product is provided for educational, experimental,
## entertainment, or personal interest use, in accordance with the 
## aforementioned license agreement, ON AN "AS IS" BASIS AND WITHOUT 
## WARRANTY, EITHER EXPRESS OR IMPLIED, INCLUDING, WITHOUT LIMITATION, 
## THE WARRANTIES OF NON-INFRINGEMENT, MERCHANABILITY, OR FITNESS FOR 
## A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY OF THE 
## ORIGINAL WORK IS WITH YOU.  (See the license agreement for full 
## details including disclaimer of warranty and limitation of 
## liability.)
##
#########################################################################
#def debug(msg):
#    #print "DEBUG:", msg
#    pass
#
#import ttk, Tkinter, tkFont
#import tkMessageBox, tkFileDialog
#import traceback
#import re, os.path
#import itertools
#from Tkconstants import *
#
#from   SoftwareAlchemy.GMA.AbilityScore       import AbilityScore
#from   SoftwareAlchemy.GMA.Alignment          import Alignment
#from   SoftwareAlchemy.GMA.Class              import Class
#from   SoftwareAlchemy.GMA.Dice               import Dice
#import SoftwareAlchemy.GMA.GUI.Icons          as     Icons
#from   SoftwareAlchemy.GMA.GUI.ScrollingFrame import ScrollingFrame
#import SoftwareAlchemy.GMA.GUI.Typesetting    as     Typesetting
#from   SoftwareAlchemy.GMA.Feat               import Feat
#from   SoftwareAlchemy.GMA.Formatting         import generate_substitution_list
#from   SoftwareAlchemy.GMA.InventoryItem      import InventoryItem
#from   SoftwareAlchemy.GMA.Race               import Race
#from   SoftwareAlchemy.GMA.Skill              import Skill
#from   SoftwareAlchemy.GMA.Spell              import Spell, SpellCollection
#from   SoftwareAlchemy.Common.MarkupText      import MarkupText
#from   SoftwareAlchemy.Common.RomanNumerals   import to_roman
#from   SoftwareAlchemy.Common.WeightsAndMeasures import str_g2lb, pounds_to_grams, grams_to_pounds
#
#
#class ValidationFailure (Exception): pass
#class InternalSoftwareFault (Exception): pass
#
#def _nonneg_validator(old, new):
#    if new.strip() == '':
#        return True
#    if re.match(r'^[+]?\d+$', new):
#        return True
#    return False
#
#def _int_validator(old, new):
#    if new.strip() == '':
#        return True
#    if re.match(r'^[-+]?\d+$', new):
#        return True
#    return False
#
#def _float_validator(old, new):
#    if new.strip() == '':
#        return True
#    if re.match(r'^[+-]?(\d+(\.(\d+)?)?|\.\d+)$', new):
#        return True
#    return False
#
#class CharacterBasicInfo (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        iv = (self.register(_int_validator), '%s', '%P')
#        self.nn = nn = (self.register(_nonneg_validator), '%s', '%P')
#        
#        nb_f = ttk.Frame(self)
#        name = ttk.Labelframe(nb_f, text="Name", underline=0)
#        back = ttk.Labelframe(nb_f, text="Background", underline=0)
#        stat = ttk.Labelframe(self, text='Stats', underline=0)
#        clas = ttk.Labelframe(self, text='Classes', underline=0)
#        xpts = ttk.Labelframe(self, text='XP', underline=0)
#        buttons = ttk.Frame(self)
#
#        buttons.pack(side=BOTTOM, fill=X, expand=True)
#        name.pack(side=TOP, fill=X, padx=2, pady=2)
#        back.pack(side=BOTTOM, fill=BOTH, padx=2, pady=2)
#        nb_f.pack(side=LEFT, fill=Y)
#        stat.pack(side=LEFT, fill=BOTH, padx=2, pady=2)
#        clas.pack(side=TOP, fill=BOTH, padx=2, pady=2)
#        xpts.pack(side=BOTTOM, fill=X, padx=2, pady=2)
#
#        self.clas = clas
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        self.fields = {}
#        for r, w,  frm,  attr,         label in (
#           (0, 20, name, 'name',       'Character:'),
#           (1, 20, name, 'nickname',   'Nickname:'),
#           (2, 20, name, 'player_name','Player:'),
#           (0, 20, back, 'deity',      'Deity:'),
#           (1, 50, back, 'appearance', 'Appearance:'),
#           (2, 50, back, 'background', 'Background:'),
#           (3, 50, back, '$comments',  'Notes:'),
#           (0,  0, stat, '$race',      'Race:'),
#           (1,  0, stat, '$alignment', 'Alignment:'),
#           (2,  0, stat, '$sex',       'Sex:'),
#           (3,  5, stat, '#age',       'Age:'),
#           (4,  0, stat, '$height',    'Height:'),
#           (5,  0, stat, '$weight',    'Weight:'),
#           (6, 10, stat, 'eyes',       'Eyes:'),
#           (7, 10, stat, 'hair',       'Hair:'),
#           (8, 10, stat, 'skin',       'Skin:'),
#           (0, 10, xpts, '#xp',        'XP:'),
#           (0,  0, clas, ':Level',     'Class'),
#        ):
#            ttk.Label(frm, text=label).grid(row=r, column=0, sticky=W)
#            self.fields[attr] = Tkinter.StringVar()
#
#            if attr[0] == ':':
#                ttk.Label(frm, text=attr[1:]).grid(row=r, column=1, sticky=W)
#
#            elif attr[0] == '#':
#                ttk.Entry(frm, 
#                    textvariable=self.fields[attr],
#                    width=w,
#                    justify=RIGHT,
#                    validate='key', 
#                    validatecommand=nn,
#                ).grid(row=r, column=1, sticky=W)
#                self.fields[attr].set(str(self.char_obj.__getattribute__(attr[1:])))
#
#            elif attr[0] == '$':
#                if attr == '$alignment':
#                    ttk.Combobox(frm,
#                        state='readonly',
#                        values=[v[1] for v in sorted(Alignment.all_alignments())],
#                        textvariable=self.fields[attr]
#                    ).grid(row=r, column=1, sticky=W)
#                    self.fields[attr].set(self.char_obj.alignment.name)
#
#                elif attr == '$comments':
#                    f = ttk.Frame(frm)
#                    f.grid(row=r, column=1, sticky=N+S+E+W)
#                    sb = ttk.Scrollbar(f)
#                    t = Tkinter.Text(f,
#                        width=w,
#                        height=4,
#                        wrap=NONE,
#                        yscrollcommand=sb.set,
#                    )
#                    sb['command'] = t.yview
#                    sb.pack(side=RIGHT, fill=Y, expand=True)
#                    t.pack(fill=BOTH, expand=True)
#                    self.comment_widget = t
#
#                    if 'title' in self.char_obj.comment_blocks:
#                        t.insert(END, '\n'.join(self.char_obj.comment_blocks['title']))
#                    t.see(1.0)
#
#                elif attr == '$height':
#                    f = ttk.Frame(frm)
#                    f.grid(row=r, column=1, sticky=W)
#                    self.fields['$height$in'] = Tkinter.StringVar()
#                    ttk.Entry(f,
#                        textvariable=self.fields[attr],
#                        validate='key',
#                        validatecommand=nn,
#                        width=4,
#                        justify=RIGHT
#                    ).pack(side=LEFT)
#                    ttk.Label(f, text="' ").pack(side=LEFT)
#                    ttk.Entry(f,
#                        textvariable=self.fields['$height$in'],
#                        validate='key',
#                        validatecommand=nn,
#                        width=3,
#                        justify=RIGHT
#                    ).pack(side=LEFT)
#                    ttk.Label(f, text='"').pack(side=LEFT)
#                    ht_in = round(self.char_obj.ht / 2.54)
#                    ht_ft = ht_in // 12
#                    ht_in -= ht_ft * 12
#                    self.fields['$height'].set('{:.0f}'.format(ht_ft))
#                    self.fields['$height$in'].set('{:.0f}'.format(ht_in))
#
#                elif attr == '$race':
#                    ttk.Combobox(frm,
#                        state='readonly',
#                        values=[v[1] for v in sorted(Race.all_races())],
#                        textvariable=self.fields[attr]
#                    ).grid(row=r, column=1, sticky=W)
#                    self.fields[attr].set(self.char_obj.race.name)
#
#                elif attr == '$sex':
#                    ttk.Combobox(frm,
#                        state='readonly',
#                        values=['Female', 'Male'],
#                        textvariable=self.fields[attr]
#                    ).grid(row=r, column=1, sticky=W)
#                    self.fields[attr].set('Female' if self.char_obj.sex_code == 'F' else 'Male')
#
#                elif attr == '$weight':
#                    f = ttk.Frame(frm)
#                    f.grid(row=r, column=1, sticky=W)
#                    ttk.Entry(f,
#                        textvariable=self.fields[attr],
#                        validate='key',
#                        validatecommand=nn,
#                        width=4,
#                        justify=RIGHT
#                    ).pack(side=LEFT)
#                    ttk.Label(f, text='#').pack(side=LEFT)
#                    self.fields['$weight'].set('{:.0f}'.format(round(self.char_obj.wt * 0.0022)))
#
#                else:
#                    raise InternalSoftwareFault('Unsupported field attr {}'.format(attr))
#            else:
#                ttk.Entry(frm,
#                    textvariable=self.fields[attr], 
#                    width=w, 
#                    justify=LEFT
#                ).grid(row=r, column=1, sticky=W)
#                self.fields[attr].set(self.char_obj.__getattribute__(attr) or '')
#
#        self.classvars=[]
#        self.levelvars=[]
#        self.classwidgets=[]
#
#        self.del_button = ttk.Button(clas,
#            style='CharFormMini.Toolbutton',
#            image=Icons.icon_delete,
#            command=self._delete_class,
#        )
#        self.add_button = ttk.Button(clas, 
#            style='CharFormMini.Toolbutton',
#            image=Icons.icon_add, 
#            command=self._add_class
#        )
#
#        for c in self.char_obj.classes:
#            self._add_class()
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#
#    def _add_class(self):
#        self.classvars.append(Tkinter.StringVar())
#        self.levelvars.append(Tkinter.StringVar())
#        r = len(self.classvars)
#
#        c = ttk.Combobox(self.clas,
#            state='readonly',
#            values=[v[1] for v in sorted(Class.all_classes())],
#            textvariable=self.classvars[-1],
#        )
#        c.grid(row=r, column=0, sticky=W)
#
#        l = ttk.Entry(self.clas,
#            textvariable=self.levelvars[r-1],
#            width=3,
#            justify=RIGHT,
#            validate='key',
#            validatecommand=self.nn,
#        )
#        l.grid(row=r, column=1, sticky=W)
#
#        self.classwidgets.append((c,l))
#
#        if len(self.char_obj.classes) >= r:
#            self.classvars[-1].set(self.char_obj.classes[r-1].name)
#            self.levelvars[-1].set(str(self.char_obj.classes[r-1].level))
#        else:
#            self.classvars[-1].set(sorted(Class.all_classes())[0][1])
#            self.levelvars[-1].set('1')
#
#        if r > 1:
#            self.del_button.grid(row=r, column=2, sticky=E)
#        self.add_button.grid(row=r+1, column=2, sticky=E)
#
#    def _delete_class(self):
#        self.del_button.grid_forget()
#        self.add_button.grid_forget()
#
#        if len(self.classvars) > 1:
#            for w in (0, 1):
#                self.classwidgets[-1][w].grid_forget()
#                self.classwidgets[-1][w].destroy()
#            self.classwidgets.pop()
#            self.classvars.pop()
#            self.levelvars.pop()
#
#            r = len(self.classvars)
#            if r > 1:
#                self.del_button.grid(row=r, column=2, sticky=E)
#            self.add_button.grid(row=r+1, column=2, sticky=E)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for k in self.fields:
#            if k[0] == ':':
#                # this was just an on-screen label
#                continue
#
#            v = self.fields[k].get()
#            if k[0] == '#':
#                # non-negative integer value
#                # really, we shouldn't run into this error if the validator worked
#                # but we're paranoid.
#                try:
#                    v = int(v or 0)
#                    assert(v >= 0)
#                except Exception as err:
#                    tkMessageBox.showerror("Value Error", "The value for {} must be a non-negative integer.".format(k[1:]))
#                    return
#
#                self.char_obj.__setattr__(k[1:], v)
#            elif k[0] == '$':
#                # special cases we need to handle specially
#                if k == '$alignment':
#                    self.char_obj.alignment = Alignment(Alignment.code_for(v))
#                elif k == '$comments':
#                    self.char_obj.comment_blocks['title'] = filter(None, self.comment_widget.get(1.0, END).split('\n'))
#                elif k == '$height':
#                    try:
#                        ht_in = int(self.fields['$height$in'].get() or 0)
#                        ht_ft = int(self.fields['$height'].get() or 0)
#                        assert(ht_in >= 0 and ht_ft >= 0)
#                    except Exception as err:
#                        tkMessageBox.showerror("Value Error", "The value for height (both feet and inches) must be a non-negative integers.")
#                        return
#                    self.char_obj.ht = int((ht_ft * 12 + ht_in) * 2.54)
#                elif k == '$height$in':
#                    pass
#                elif k == '$race':
#                    self.char_obj.race = Race(Race.code_for(v))
#                elif k == '$sex':
#                    self.char_obj.sex_code = v[0].upper()
#                elif k == '$weight':
#                    try:
#                        wt = int(v or 0)
#                        assert(wt >= 0)
#                    except Exception as err:
#                        tkMessageBox.showerror('Value Error', 'The value for weight must be an integer number of pounds.')
#                        return
#
#                    self.char_obj.wt = int(round(wt / 0.0022))
#                else:
#                    raise InternalSoftwareFault('Unsupported field attr {}'.format(k))
#            else:
#                # normal string value stored to character attribute named k
#                self.char_obj.__setattr__(k, v)
#
#        # that just leaves the classes and levels to clean up
#        self.classes = [v.get() for v in self.classvars]
#        self.levels  = [int(v.get() or 0) for v in self.levelvars]
#
#        if self.char_obj.classes != self.classes:
#            if len(self.char_obj.classes) > len(self.classes):
#                if tkMessageBox.askokcancel('Confirm Class Change', 
#'''You are reducing the number of character
#classes from {} to {}, which will completely
#remove {}.
#
#Are you sure you want to do this?'''.format(
#    len(self.char_obj.classes), len(self.classes),
#    ', '.join([c.name for c in self.char_obj.classes[len(self.classes):]])
#    ), default=tkMessageBox.CANCEL):
#                    # XXX what other implications propagate out from this?
#                    del self.char_obj.classes[len(self.classes):]
#                else:
#                    tkMessageBox.showinfo('Change Canceled', "Ok, then, I won't change that.")
#
#            for i in range(len(self.classes)):
#                if i >= len(self.char_obj.classes):
#                    if tkMessageBox.askokcancel('Confirm Class Addition',
#'''You are about to add an additional class of
#{} (level {}) to your character.
#
#Are you sure you want to do this?'''.format(self.classes[i], self.levels[i]),
#default=tkMessageBox.CANCEL):
#                        self.char_obj.classes.append(Class(Class.code_for(self.classes[i]), self.levels[i], self.char_obj.special_ability_dict))
#                    else:
#                        tkMessageBox.showinfo('Change Canceled', "Ok, then, I won't change that.")
#                else:
#                    if self.char_obj.classes[i].code != Class.code_for(self.classes[i]) \
#                            or self.char_obj.classes[i].level != self.levels[i]:
#                        if tkMessageBox.askokcancel('Confirm Class Change',
#'''Are you sure you want to change class #{}
#from {} {} to {} {}?'''.format(i+1, 
#    self.char_obj.classes[i].name, self.char_obj.classes[i].level,
#    self.classes[i], self.levels[i]), default=tkMessageBox.CANCEL):
#                            self.char_obj.classes[i] = Class(Class.code_for(self.classes[i]), self.levels[i], self.char_obj.special_ability_dict)
#                        else:
#                            tkMessageBox.showinfo('Change Canceled', "Ok, then, I won't change that.")
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterAbilityScores (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        self.nn = (self.register(_nonneg_validator), '%s', '%P')
#        
#        base = ttk.Labelframe(self, text='Permanent', underline=0)
#        temp = ttk.Labelframe(self, text='Temporary', underline=0)
#        misc = ttk.Labelframe(self, text='Misc.',     underline=0)
#        buttons = ttk.Frame(self)
#
#        buttons.pack(side=BOTTOM, fill=X, expand=True)
#        misc.pack(side=BOTTOM, fill=X, expand=True, padx=2, pady=2)
#        base.pack(side=LEFT, fill=BOTH, padx=2, pady=2)
#        temp.pack(side=LEFT, fill=BOTH, padx=2, pady=2)
#
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        self.fields = {}
#        for r, w,  frm,  attr,         label in (
#           (0, 3, base,  'Bstr',       'Strength:'),
#           (1, 3, base,  'Bdex',       'Dexterity:'),
#           (2, 3, base,  'Bcon',       'Constitution:'),
#           (3, 3, base,  'Bint',       'Intelligence:'),
#           (4, 3, base,  'Bwis',       'Wisdom:'),
#           (5, 3, base,  'Bcha',       'Charisma:'),
#
#           (0, 3, temp,  'Tstr',       ''),
#           (1, 3, temp,  'Tdex',       ''),
#           (2, 3, temp,  'Tcon',       ''),
#           (3, 3, temp,  'Tint',       ''),
#           (4, 3, temp,  'Twis',       ''),
#           (5, 3, temp,  'Tcha',       ''),
#
#           (0, 30, misc,  '$comments',  'Notes:'),
#        ):
#            ttk.Label(frm, text=label).grid(row=r, column=0, sticky=W)
#            self.fields[attr] = Tkinter.StringVar()
#
#            if attr == '$comments':
#                f = ttk.Frame(frm)
#                f.grid(row=r, column=1, sticky=N+S+E+W)
#                sb = ttk.Scrollbar(f)
#                t = Tkinter.Text(f,
#                    width=w,
#                    height=4,
#                    wrap=NONE,
#                    yscrollcommand=sb.set,
#                )
#                sb['command'] = t.yview
#                sb.pack(side=RIGHT, fill=Y, expand=True)
#                t.pack(fill=BOTH, expand=True)
#                self.comment_widget = t
#
#                for a in 'str', 'dex', 'con', 'int', 'wis', 'cha':
#                    if a in self.char_obj.comment_blocks:
#                        t.insert(END, '\n'.join(self.char_obj.comment_blocks[a])+'\n')
#                t.see(1.0)
#
#            else:
#                ttk.Entry(frm, 
#                    textvariable=self.fields[attr],
#                    width=w,
#                    justify=RIGHT,
#                    validate='key', 
#                    validatecommand=self.nn,
#                ).grid(row=r, column=1, sticky=W)
#
#                if attr[0] == 'B':
#                    self.fields[attr].set(str(self.char_obj.ability[attr[1:]].base))
#                else:
#                    self.fields[attr].set(str('' if self.char_obj.ability[attr[1:]].temp is None else self.char_obj.ability[attr[1:]].temp))
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for k in self.fields:
#            v = self.fields[k].get()
#            if k[0] == 'T':
#                if v.strip() == '':
#                    v = None
#                else:
#                    try:
#                        v = int(v)
#                        assert(v >= 0)
#                    except Exception as err:
#                        tkMessageBox.showerror("Value Error", "The value for temporary ability scores must be non-negative integers or completely empty.")
#                        return
#                self.char_obj.ability[k[1:]].temp = v
#
#            elif k[0] == 'B':
#                try:
#                    v = int(v)
#                    assert(v >= 0)
#                except Exception as err:
#                    tkMessageBox.showerror("Value Error", "The value for base ability scores must be non-negative integers.")
#                    return
#                self.char_obj.ability[k[1:]].base = v
#
#            elif k[0] == '$':
#                # special cases we need to handle specially
#                if k == '$comments':
#                    self.char_obj.comment_blocks['str'] = filter(None, self.comment_widget.get(1.0, END).split('\n'))
#                    for a in 'dex', 'con', 'int', 'wis', 'cha':
#                        if a in self.char_obj.comment_blocks:
#                            del self.char_obj.comment_blocks[a]
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#
#class SpellCollectionEditor (ttk.Frame):
#    def __init__(self, parent, char_obj, spell_type):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        root.title("Editing Specification for "+spell_type+" spells")
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.spell_type = spell_type
#        self.parent_widget = parent
#        self.individual_selection = {}
#
#        if spell_type not in self.char_obj.spell_types:
#            # creating it now
#            self.char_obj.spell_types.append(spell_type)
#            self.char_obj.spells[spell_type] = SpellCollection(spell_type)
#            self.char_obj.spell_criteria[spell_type] = {
#                    'all_level': None,
#                    'except':    None,
#            }
#
#        #
#        # check that the whole list makes sense, since we're in here already anyway
#        #
#        typelist = self.char_obj.spells.keys()
#        for st in typelist:
#            coll = self.char_obj.spells[st]
#            if coll.class_code not in [c.code for c in self.char_obj.classes]:
#                tkMessageBox.showerror('Cannot Cast {} Spells'.format(st),
#                        "Your character cannot cast {} spells.  All information about this spell type is removed.".format(st))
#                del self.char_obj.spells[st]
#                self.char_obj.spell_types.remove(st)
#                del self.char_obj.spell_criteria[st]
#
#        if spell_type not in self.char_obj.spells:
#            self._cancel()
#            return
#
#        self.collection = self.char_obj.spells[spell_type]
#        self.criteria = self.char_obj.spell_criteria[spell_type]
#        root.title("Editing Specification for "+self.collection.type_description())
#        nnv = (self.register(_nonneg_validator), '%s', '%P')
#        
#        buttons = ttk.Frame(self)
#        individuals = ttk.Labelframe(self, text="Individual Spell Selection")
#
#        buttons.pack(side=BOTTOM, fill=X, pady=5, expand=False)
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self._cancel).pack(side=LEFT)
#
#        self.fields = {}
#        self.widgets = {}
#        self.fields['up_to'] = Tkinter.StringVar()
#        self.fields['inc_rule'] = Tkinter.IntVar()
#        self.rule_widgets = []
#        self.descriptors = []
#
#        if self.collection.supplimental_type == 'sp':
#            self.fields['inc_rule'].set(0)
#        else:
#            rules = ttk.Labelframe(self, text="Include by Rule")
#            rules.pack(side=TOP, fill=BOTH, expand=False, padx=2, pady=2)
#            ttk.Checkbutton(rules, 
#                text="Include all spells through level:", 
#                variable=self.fields['inc_rule'],
#                command=self._enable_rules,
#            ).grid(row=0, column=0, columnspan=3, sticky=W)
#            f = ttk.Entry(rules, 
#                textvariable=self.fields['up_to'],
#                justify=RIGHT,
#                validate='key',
#                validatecommand=nnv,
#            )
#            f.grid(row=0, column=3, sticky=E+W)
#            self.rule_widgets.append(f)
#
## XXX char_obj.spell_criteria[all_level|except|sp|0..ix] = [...]
## XXX                         int/None   |list  [] []
## XXX None level is "sp" for add_spell
## XXX specials always explicit
## XXX needs to save back in here. the collection list is not the 
## XXX source for read/write; the criteria is.
#            ttk.Label(rules, text="Except:").grid(row=1, column=0, sticky=W)
#            r=c=1
#            old_exc_str = self.criteria.get('except')
#            if old_exc_str is None:
#                old_exclusions = []
#            else:
#                old_exclusions = filter(str.strip, filter(None, self.criteria['except'].split('|')))
#            for key in Spell.all_descriptors():
#                self.fields['D$'+key] = Tkinter.IntVar()
#                self.descriptors.append(key)
#                f = ttk.Checkbutton(rules,
#                    text=key,
#                    variable=self.fields['D$'+key],
#                )
#                if key in old_exclusions:
#                    f.state(['selected'])
#                f.grid(row=r, column=c, sticky=W)
#                self.rule_widgets.append(f)
#                c += 1
#                if c > 3:
#                    c = 1
#                    r += 1
#
#        individuals.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
#        self.level_f = []
#        self.individual_checkbuttons = []
#        if self.collection.supplimental_type == 'sp':
#            f = ttk.Frame(individuals)
#            self._add_spell_tab(None, f)
#        else:
#            nb = ttk.Notebook(individuals)
#            nb.pack(expand=True, fill=BOTH)
#            for sp_level in range(10):
#                f = ttk.Frame(nb)
#                nb.add(f, text=('Level ' if sp_level==0 else '') + to_roman(sp_level))
#                self._add_spell_tab(sp_level, f)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#        self._refresh()
#
#    def _add_spell_tab(self, sp_level, f):
#        sb = ttk.Scrollbar(f, orient=VERTICAL)
#        sf = ScrollingFrame(f, yscrollcommand=sb.set)
#        sb['command'] = sf.yview
#        self.level_f.append(sf)
#        section = 'sp' if sp_level is None else to_roman(sp_level)
#
#        f = self.level_f[-1].scrolled_frame
#        self.individual_checkbuttons.append({})
#        for sp_name in self.collection.each_possible_spell(sp_level or 0):
#            self.individual_selection[sp_name] = Tkinter.IntVar()
#            self.individual_checkbuttons[-1][sp_name] = ttk.Checkbutton(f, 
#                    variable=self.individual_selection[sp_name],
#                    text=sp_name
#            )
#            self.individual_checkbuttons[-1][sp_name].pack(side=TOP, anchor=W, padx=2)
#            if section in self.criteria and sp_name in self.criteria[section]:
#                self.individual_selection[sp_name].set(1)
#            else:
#                self.individual_selection[sp_name].set(0)
#
#        sf.set_scroll_region()
#
#        sb.pack(side=RIGHT, fill=Y)
#        sf.pack(fill=BOTH, expand=True)
#
#    def _refresh(self):
#        all = self.criteria['all_level']
#        if all is not None:
#            self.fields['up_to'].set(str(all))
#            self.fields['inc_rule'].set(1)
#        else:
#            self.fields['up_to'].set('')
#            self.fields['inc_rule'].set(0)
#        self._enable_rules()
#
#
#    def _enable_rules(self):
#        #print "_enable_rules", self.fields['inc_rule'].get()
#        if self.fields['inc_rule'].get():
#            #print "enabling fields"
#            for w in self.rule_widgets:
#                w.state(['!disabled'])
#        else:
#            #print "disabling fields"
#            for w in self.rule_widgets:
#                w.state(['disabled'])
#
#    def _cancel(self):
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#    def _save(self):
#        # first, a little validation
#        if self.fields['inc_rule'].get():
#            up_to_level = self.fields['up_to'].get()
#            if up_to_level is None or up_to_level.strip() == '':
#               if not tkMessageBox.askyesno('Confirm Rule',
#               '''You indicated that you want to include all spells up to a certain level, but did not specify which level.  Do you want me to assume you really did NOT mean to include all spells?
#
#If you answer YES, then ONLY the explicitly-checked spell names will be included, disregarding any rules checked.
#
#If you answer NO, you will be able to correct this and try again.''', default='no'):
#                    return
#            else:
#                try:
#                    up_to_level = min(max(int(up_to_level), 0), 9)
#                except:
#                    tkMessageBox.showerror("Invalid level",
#                    '''You did not specify an integer value for the maximum level of spell you wish to have copied into your character's list.''')
#                    return
#
#                # rule-based inclusion and exclusion
#                self.collection.clear()
#                self.collection.add_up_to_level(up_to_level)
#                except_list = []
#                for exclusion in self.descriptors:
#                    if self.fields['D$'+exclusion].get():
#                        self.collection.remove_type(exclusion)
#                        except_list.append(exclusion)
#
#                self.criteria.clear()
#                self.criteria.update({
#                    'all_level': up_to_level,
#                    'except': '|'.join(except_list) if except_list else None,
#                })
#        else:
#            self.collection.clear()
#            self.criteria.clear()
#            self.criteria.update({
#                'all_level': None,
#                'except': None,
#            })
#
#        # explicit inclusion lists
#        if self.collection.supplimental_type == 'sp':
#            self.criteria['sp'] = []
#            for sp_name, choice in self.individual_checkbuttons[0].items():
#                if choice.instate(['selected']):
#                    self.collection.add_spell(sp_name, None)
#                    self.criteria['sp'].append(sp_name)
#        else:
#            for sp_level in range(10):
#                rom = to_roman(sp_level)
#                for sp_name, choice in self.individual_checkbuttons[sp_level].items():
#                    if choice.instate(['selected']):
#                        if rom not in self.criteria:
#                            self.criteria[rom] = []
#                        self.criteria[rom].append(sp_name)
#                        self.collection.add_spell(sp_name, sp_level)
#
#        self._cancel()
#
#class InventoryItemEditor (ttk.Frame):
#    def _grams_validator(self, old, new):
#        if not _nonneg_validator(old, new): return False
#        g = new or 0
#        lb, ilb, oz = grams_to_pounds(int(g))
#
#        self.fields['$lbs'].set(str(ilb))
#        self.fields['$oz'].set(str(oz))
#        return True
#
#    def _lbs_validator(self, old, new):
#        if not _nonneg_validator(old, new): return False
#        oz = self.fields['$oz'].get() or 0
#        lb = new or 0
#        g = pounds_to_grams(float(lb) + float(oz)/16.0)
#        self.fields['#wt'].set(str(g))
#        return True
#
#    def _oz_validator(self, old, new):
#        if not _nonneg_validator(old, new): return False
#        oz = new or 0
#        lb = self.fields['$lbs'].get() or 0
#        g = pounds_to_grams(float(lb) + float(oz)/16.0)
#        self.fields['#wt'].set(str(g))
#        return True
#
#    def __init__(self, parent, char_obj, item):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.item = item
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        nnv = (self.register(_nonneg_validator), '%s', '%P')
#        flv = (self.register(_float_validator), '%s', '%P')
#        gval = (self.register(self._grams_validator), '%s', '%P')
#        lbval = (self.register(self._lbs_validator), '%s', '%P')
#        ozval = (self.register(self._oz_validator), '%s', '%P')
#        
#        buttons = ttk.Frame(self)
#        basic = ttk.Labelframe(self, text="Basic Information")
#        weight = ttk.Labelframe(self, text="Weight")
#        qty = ttk.Labelframe(self, text="Quantities")
#        desc = ttk.Labelframe(self, text="Details")
#
#        buttons.pack(side=BOTTOM, fill=X, pady=5, expand=False)
#        basic.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
#        weight.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
#        qty.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
#        desc.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self._cancel).pack(side=LEFT)
#        ttk.Button(buttons, text="DELETE", command=self._delete).pack(side=LEFT)
#
#        self.fields = {}
#        self.widgets = {}
#        for r, c, w, s, frm,    validator, attr,         label in (
#           (0, 0, 0, 3, basic,  None,      ':code',    'Type:'),
#           (1, 0,10, 3, basic,  None,      'id',       'ID:'),
#           (2, 0,50, 3, basic,  None,      'name',     'Description:'),
#           (3, 0,10, 3, basic,  None,      'location', 'Location:'),
#           (4, 0,10, 1, basic,  None,      '>cost',    'Cost:'),
#           #(4, 2, 0, 1, basic,  None,      None,       'gp'),
#           #(4, 3, 0, 1, basic,  None,      None,       ' '),
#
#           (0, 0, 0, 8, weight, None,      '?carried', 'Carried (included in character weight load)'),
#           (1, 0,10, 1, weight, gval,      '#wt',      'Weight:'),
#           (1, 2, 5, 1, weight, lbval,     '$lbs',     'g ='),
#           (1, 4, 5, 1, weight, ozval,     '$oz',      'lbs.,'),
#           (1, 6, 0, 1, weight, None,      None,       'oz (each)'),
#           (2, 0,10, 1, weight, None,      '>ttl_g',   None),
#           (2, 2, 5, 1, weight, None,      '>ttl_lbs', 'g ='),
#           (2, 4, 5, 1, weight, None,      '>ttl_oz',  'lbs.,'),
#           (2, 6, 0, 1, weight, None,      None,       'oz (total carried weight)'),
#
#           (0, 0, 0, 2, qty,    None,      '?$has_qty','Has quantity of (expendable) items'),
#           (1, 0, 5, 1, qty,    None,      '#maxqty',   'Maximum Qty:'),
#           (1, 1, 0, 1, qty,    None,      '>maxerr',   None),
#           (2, 0, 5, 1, qty,    None,      '#qty',      'Current Qty:'),
#           (2, 1, 0, 1, qty,    None,      '>qtyerr',   None),
#           (3, 0, 5, 1, qty,    None,      '#tapqty',   'Tapped Qty:'),
#        ):
#            if label is not None and (attr is None or attr[0] != '?'):
#                ttk.Label(frm, text=label).grid(row=r, column=c, sticky=W)
#
#            if attr is not None:
#                self.fields[attr] = Tkinter.StringVar()
#
#                if attr[0] == ':':      # constant field
#                    ttk.Label(frm, textvariable=self.fields[attr]).grid(row=r, column=c+1, sticky=W, columnspan=s)
#
#                elif attr[0] == '>':      # constant field
#                    ttk.Label(frm, textvariable=self.fields[attr]).grid(row=r, column=c+1, sticky=E, columnspan=s)
#
#                elif attr[0] == '?':    # checkbutton
#                    self.fields[attr] = Tkinter.IntVar()
#                    ttk.Checkbutton(frm, text=label, command=self.set_btns, variable=self.fields[attr]).grid(row=r, column=c, sticky=W, columnspan=s)
#
#                elif attr[0] == '#':    # integer input field
#                    self.widgets[attr] = ttk.Entry(frm, 
#                        textvariable=self.fields[attr],
#                        width=w,
#                        justify=RIGHT,
#                        validate='key', 
#                        validatecommand=validator,
#                    )
#                    self.widgets[attr].grid(row=r, column=c+1, sticky=W, columnspan=s)
#
#                elif attr[0] == '!':    # float input field
#                    ttk.Entry(frm, 
#                        textvariable=self.fields[attr],
#                        width=w,
#                        justify=RIGHT,
#                        validate='key', 
#                        validatecommand=validator,
#                    ).grid(row=r, column=c+1, sticky=W, columnspan=s)
#
#                elif attr in ('$lbs', '$oz'):
#                    ttk.Entry(frm, 
#                        textvariable=self.fields[attr],
#                        width=w,
#                        justify=RIGHT,
#                        validate='key', 
#                        validatecommand=validator,
#                    ).grid(row=r, column=c+1, sticky=W, columnspan=s)
#
#                else: # string input field
#                    ttk.Entry(frm, 
#                        textvariable=self.fields[attr],
#                        width=w,
#                        justify=LEFT,
#                    ).grid(row=r, column=c+1, sticky=W, columnspan=s)
#
#        self.widgets['#qty'].bind('<FocusOut>', self.set_btns)
#        self.widgets['#maxqty'].bind('<FocusOut>', self.set_btns)
#        self.widgets['#tapqty'].bind('<FocusOut>', self.set_btns)
#
#        sb = ttk.Scrollbar(desc)
#        sb.pack(side=RIGHT, fill=Y)
#        self.details_w = Tkinter.Text(desc, yscrollcommand=sb.set, height=5, wrap=WORD)
#        sb.config(command=self.details_w.yview)
#        self.details_w.pack(side=LEFT, fill=BOTH, expand=True)
#        Typesetting.set_text_tags(self.details_w)
#        self.pack(side=TOP, expand=True, fill=BOTH)
#        self._refresh()
#
#    def _enter_hyperlink(self, event): self.details_w['cursor'] = 'hand2'
#    def _leave_hyperlink(self, event): self.details_w['cursor'] = ''
#    def _disabled(self): tkMessageBox.showerror("Disabled", "Nothing happens.")
#
#    def _refresh(self):
#        "update fields from object"
#        for k in self.fields:
#            if k == '>cost':
#                self.fields[k].set(self.item.str_cost())
#                continue
#            elif k[0] in '?$>':
#                continue
#            elif k[0] in ':!#':
#                v = self.item.__getattribute__(k[1:])
#            else:
#                v = self.item.__getattribute__(k)
#
#            if v is not None:
#                self.fields[k].set(str(v))
#            else:
#                self.fields[k].set('')
#
#        self.fields['?$has_qty'].set(int(self.item.maxqty is not None or self.item.qty is not None or self.item.tapqty is not None))
#        self.fields['?carried'].set(int(self.item.carried))
#        lb, ilb, oz = grams_to_pounds(self.item.wt)
#        self.fields['$lbs'].set(str(ilb))
#        self.fields['$oz'].set(str(oz))
#        self.set_btns()
#
#        self.details_w['state'] = NORMAL
#        self.details_w.delete(1.0, END)
#        if self.item.description is not None:
#            MarkupText(self.item.description).render(Typesetting.TextWidgetFormatter(
#                    self.details_w, 
#                    default_link_type='Item', 
#                    event_obj=None, 
#                    char_obj=self.char_obj
#                )
#            )
#        self.details_w['state']=DISABLED
#
#    def set_btns(self, event=None):
#        q = bool(self.fields['?$has_qty'].get())
#        for f in '#maxqty', '#qty', '#tapqty':
#            self.widgets[f].configure(state=NORMAL if q else DISABLED)
#            if q and self.fields[f].get().strip() == '':
#                self.fields[f].set('0')
#
#        if q:
#            mq = int(self.fields['#maxqty'].get() or 0)
#            qq = int(self.fields['#qty'].get() or 0)
#            tq = int(self.fields['#tapqty'].get() or 0)
#            if qq < tq:
#                self.fields['>qtyerr'].set("Quantity adjusted to allow for tapped qty")
#                self.fields['#qty'].set('{}'.format(tq))
#                qq = tq
#            else:
#                self.fields['>qtyerr'].set('')
#
#            if mq < qq:
#                self.fields['>maxerr'].set("Max qty adjusted to allow for quantity")
#                self.fields['#maxqty'].set('{}'.format(qq))
#                mq = qq
#            else:
#                self.fields['>maxerr'].set('')
#
#        if self.fields['?carried'].get():
#            self.item.carried = True
#            g = int(self.fields['#wt'].get() or 0) 
#            if q:
#                qty = int(self.fields['#qty'].get() or 0)
#            else:
#                qty = 1
#
#            lbs, ilbs, oz = grams_to_pounds(int(g*qty))
#            self.fields['>ttl_g'].set(str(int(g*qty)))
#            self.fields['>ttl_lbs'].set(str(ilbs))
#            self.fields['>ttl_oz'].set(str(oz))
#        else:
#            self.fields['>ttl_g'].set('0')
#            self.fields['>ttl_lbs'].set('0')
#            self.fields['>ttl_oz'].set('0')
#
#    def _delete(self):
#        "delete this item from the character's inventory"
#        if tkMessageBox.askokcancel('Confirm Deletion', '''Are you sure you want to remove
#{0.name} (ID {0.id})
#permanently from your inventory?
#
#This action cannot be undone!'''.format(self.item), default='cancel'):
#            try:
#                self.char_obj.inventory.remove(self.item)
#            except ValueError:
#                tkMessageBox.showerror('Mysteriously Vanished', '''That item doesn't seem to be in your inventory.  No action taken, but I'm mystified.''')
#
#            self.parent_widget.refresh()
#            self.master.destroy()
#        else:
#            tkMessageBox.showinfo("Canceled", "Ok, then, I won't delete it.")
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        the_id = self.fields['id'].get().strip()
#        if not valid_id(the_id):
#            tkMessageBox.showerror("Invalid ID", '"{}" is not a valid item ID.\nIt must be alphanumeric only.'.format(the_id))
#            return
#        for item in self.char_obj.inventory:
#            if item is not self.item and item.id == the_id:
#                tkMessageBox.showerror("Duplicate ID", '"{}" duplicates the ID of another object\n("{}").'.format(the_id, item.name))
#                return
#        has_qty = bool(self.fields['?$has_qty'].get())
#        for k in self.fields:
#            if k[0] == ':': continue
#            v = self.fields[k].get()
#
#            if k[0] == '!':
#                try:
#                    self.item.__setattr__(k[1:], None if v is None or v.strip()=='' else float(v))
#                except:
#                    tkMessageBox.showerror("Value Error", "The value for {} is not understandable.  It should be a floating point value.".format(k[1:]))
#                    return
#
#            if k[0] == '#':
#                try:
#                    self.item.__setattr__(k[1:], None if v is None or v.strip()=='' else int(v))
#                except:
#                    tkMessageBox.showerror("Value Error", "The value for {} is not understandable.  It should be an integer value.".format(k[1:]))
#                    return
#
#            elif k[0] == '?':
#                if k == '?$has_qty': 
#                    continue
#
#                try:
#                    self.item.__setattr__(k[1:], bool(v or False))
#                except:
#                    tkMessageBox.showerror("Value Error", "The value for {} is not understandable.  It should be a boolean value.".format(k[1:]))
#                    return
#
#            elif k[0] == '$':
#                continue
#
#            else:
#                self.item.__setattr__(k, v)
#
#            if not has_qty:
#                self.qty = self.maxqty = self.tapqty = None
#
#        self._cancel()
#
#    def _cancel(self):
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterSavingThrows (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        mods = ttk.Frame(self)
#        buttons = ttk.Frame(self)
#
#        buttons.pack(side=BOTTOM, fill=X, expand=True)
#        mods.pack(side=BOTTOM, fill=BOTH, expand=True)
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        self.fields = {}
#        for r, w,  frm,  attr,         label in (
#           (0, 50, mods, 'SM0',        'Mods (line 1):'),
#           (1, 50, mods, 'SM1',        'Mods (line 2):'),
#           (2, 50, mods, '$comments',  'Notes:'),
#        ):
#            ttk.Label(frm, text=label).grid(row=r, column=0, sticky=W)
#            self.fields[attr] = Tkinter.StringVar()
#
#            if attr == '$comments':
#                f = ttk.Frame(frm)
#                f.grid(row=r, column=1, sticky=N+S+E+W)
#                sb = ttk.Scrollbar(f)
#                t = Tkinter.Text(f,
#                    width=w,
#                    height=4,
#                    wrap=NONE,
#                    yscrollcommand=sb.set,
#                )
#                sb['command'] = t.yview
#                sb.pack(side=RIGHT, fill=Y, expand=True)
#                t.pack(fill=BOTH, expand=True)
#                self.comment_widget = t
#
#                if 'save' in self.char_obj.comment_blocks:
#                    t.insert(END, '\n'.join(self.char_obj.comment_blocks['save']))
#                t.see(1.0)
#
#            else:
#                ttk.Entry(frm, 
#                    textvariable=self.fields[attr],
#                    width=w,
#                    justify=LEFT,
#                ).grid(row=r, column=1, sticky=W)
#
#        self.fields['SM0'].set(self.char_obj.save_mods[0] if len(self.char_obj.save_mods)>0 else '')
#        self.fields['SM1'].set(self.char_obj.save_mods[1] if len(self.char_obj.save_mods)>1 else '')
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        k = filter(None, self.comment_widget.get(1.0, END).split('\n'))
#        if not k:
#            if 'save' in self.char_obj.comment_blocks:
#                del self.char_obj.comment_blocks['save']
#        else:
#            self.char_obj.comment_blocks['save'] = k
#
#        self.char_obj.save_mods = filter(None, [
#                self.fields['SM0'].get(),
#                self.fields['SM1'].get(),
#        ])
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterSkills (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        skills = ttk.Frame(self)
#        buttons = ttk.Frame(self)
#
#        buttons.pack(side=BOTTOM, fill=X, expand=True)
#        skills.pack(side=BOTTOM, fill=BOTH, expand=True)
#        self.nn = nn = (self.register(_nonneg_validator), '%s', '%P')
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        skp_per_level, ttl_skp_per_lev, max_ranks, skp_bonus, total_skp = self.char_obj.skill_points_per_level()
#
#        self.fields = {}
#        maxcols=1
#        for r, w,  frm,    label, attr in (
#           (0,  0, skills, 'Class:', [c.name for c in self.char_obj.classes]),
#           (1,  0, skills, 'Base Points/Level:', ['{}'.format(s) for s in skp_per_level]),
#           (2,  0, skills, '+ Intelligence Modifier:', ['{:+}'.format(self.char_obj.ability['int'].mod()) for s in skp_per_level]),
#           (3,  0, skills, '+ Racial Modifier:', ['{:+}'.format(self.char_obj.race.skill_points) for s in skp_per_level]),
#           (4,  0, skills, '= Total Points/Level:', ['{}'.format(s) for s in ttl_skp_per_lev]),
#           (5,  0, skills, '', '>'),
#           (6,  0, skills, 'x Class Levels:', ['x{}'.format(c.level) for c in self.char_obj.classes]),
#           (7,  0, skills, '= Total Points/Class:', ['={}'.format(c.level*s) for c, s in zip(self.char_obj.classes, ttl_skp_per_lev)]),
#           (8,  0, skills, '', '>'),
#           (9,  3, skills, '+ Bonus Points Taken When Advancing:', '#bonus'),
#           (10, 0, skills, '= Total Skill Points:', '>{}'.format(total_skp)),
#           (11, 0, skills, 'Maximum Ranks per Skill:', '>{}'.format(max_ranks)),
#           (12, 0, skills, 'Skill Point Allocation:', '$points'),
#           (13,50, skills, 'Notes:', '$comments'),
#        ):
#            ttk.Label(frm, text=label).grid(row=r, column=0, sticky=W)
#            if isinstance(attr, (list,tuple)):
#                maxcols = max(maxcols, len(attr))
#                for c,v in enumerate(attr):
#                    ttk.Label(frm, text=v).grid(row=r, column=c+1, sticky=E)
#            elif attr[0] == '>':
#                ttk.Label(frm, text=attr[1:]).grid(row=r, column=1, sticky=W)
#            else:
#                self.fields[attr] = Tkinter.StringVar()
#                if attr == '$comments':
#                    f = ttk.Frame(frm)
#                    f.grid(row=r, column=1, columnspan=maxcols+1, sticky=N+S+E+W)
#                    sb = ttk.Scrollbar(f)
#                    t = Tkinter.Text(f,
#                        width=w,
#                        height=4,
#                        wrap=NONE,
#                        yscrollcommand=sb.set,
#                    )
#                    sb['command'] = t.yview
#                    sb.pack(side=RIGHT, fill=Y, expand=True)
#                    t.pack(fill=BOTH, expand=True)
#                    self.comment_widget = t
#
#                    if 'skills' in self.char_obj.comment_blocks:
#                        t.insert(END, '\n'.join(self.char_obj.comment_blocks['skills']))
#                    t.see(1.0)
#                elif attr == '$points':
#                    f = ttk.Frame(frm)
#                    f.grid(row=r, column=1, columnspan=maxcols+1, sticky=N+S+E+W)
#
#                    r = 0
#                    slist = [x for x in Skill.all_skill_codes()]
#                    skill_count = len(slist)
#                    rows = (skill_count+4) // 5
#                    for skill_code, skill_name in slist:
#                        kk = attr + '$' + skill_code
#                        self.fields[kk] = Tkinter.StringVar()
#                        ttk.Label(f, text=skill_name+":").grid(row=r%rows, column=2*(r//rows), sticky=W)
#                        ttk.Entry(f, 
#                            textvariable=self.fields[kk], 
#                            width=3, 
#                            justify=RIGHT
#                        ).grid(row=r%rows, column=1+2*(r//rows), sticky=W, padx=2)
#                        if skill_code in self.char_obj.skills:
#                            self.fields[kk].set(str(self.char_obj.skills[skill_code].ranks))
#                        else:
#                            self.fields[kk].set('0')
#                        r += 1
#
#                elif attr[0]=='#':
#                    ttk.Entry(frm, 
#                        textvariable=self.fields[attr],
#                        width=w,
#                        justify=RIGHT,
#                        validate='key', 
#                        validatecommand=nn,
#                    ).grid(row=r, column=1, sticky=W)
#
#            for c in range(1, maxcols+1):
#                skills.grid_columnconfigure(c, pad=1, weight=0)
#            skills.grid_columnconfigure(maxcols+1, pad=1, weight=1)
#
#        self.fields['#bonus'].set(str(self.char_obj.skp_bonus))
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for k in self.fields:
#            if k == '$comments':
#                kk = filter(None, self.comment_widget.get(1.0, END).split('\n'))
#                if not kk:
#                    if 'skills' in self.char_obj.comment_blocks:
#                        del self.char_obj.comment_blocks['skills']
#                else:
#                    self.char_obj.comment_blocks['skills'] = kk
#            elif k == '#bonus':
#                try:
#                    self.char_obj.skp_bonus = int(self.fields['#bonus'].get())
#                except:
#                    tkMessageBox.showerror("Value Error", "The value for the skill point bonus must be a non-negative integer.")
#            elif k.startswith('$points$'):
#                try:
#                    ranks = int(self.fields[k].get())
#                except:
#                    tkMessageBox.showerror("Value Error", "The value for the {} skill ranks must be a non-negative integer.".format(k[8:]))
#                    continue
#
#                sc = k[8:]
#                debug('skill {} (field {}) ranks={}'.format(sc, k, ranks))
#                if sc in self.char_obj.skills:
#                    skill = self.char_obj.skills[sc]
#                    if ranks == 0 and skill.trained:
#                        if tkMessageBox.askokcancel('Confirm Skill Deletion',
#                                """\
#You reduced the ranks for the {} skill to zero.
#This skill requires training, so continuing will remove
#this skill from your character.""".format(
#                                    skill.name
#                                )):
#                            skill.ranks = 0
#                            del self.char_obj.skills[sc]
#                        continue
#                    elif ranks == 0 and skill.sub:
#                        if tkMessageBox.askokcancel('Confirm Skill Deletion',
#                                """\
#You reduced the ranks for the {} skill to zero.
#This skill is a specific subclass of a general skill,
#so continuing to remove all ranks will remove it entirely
#from your character.""".format(skill.name)):
#                            skill.ranks=0
#                            del self.char_obj.skills[sc]
#                        continue
#                    skill.ranks = ranks
#                elif ranks > 0:
#                    skill = Skill(sc)
#                    if tkMessageBox.askokcancel('Confirm Skill Addition', 
#                            """\
#You added {} rank{} for the {} skill.  This skill did not
#previously exist for this character.  Continuing will 
#add this skill to your character.""".format(
#                                ranks, 's' if ranks > 1 else '',
#                                skill.name
#                            )):
#                        self.char_obj.skills[sc] = skill
#                        skill.ranks = ranks
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterClassAbilities (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        self.fields={}
#        for c in char_obj.classes:
#            f = ttk.Labelframe(self, text='{} Class Ability Parameters'.format(c.name))
#            f.pack(side=TOP, fill=X, expand=True)
#
#            r=0
#            for a in c.feats:
#                if a.meta_data:
#                    ttk.Label(f, text=a.code).grid(row=r, column=0, sticky=W)
#                    col=1
#                    for i,md in enumerate(a.meta_data):
#                        if 'label' in md:
#                            ttk.Label(f, text=md['label']).grid(row=r, column=col, sticky=W)
#                            col += 1
#                        k = '{}${}'.format(c.code, a.code)
#                        self.fields[k] = Tkinter.StringVar()
#                        if 'values' in md:
#                            ttk.Combobox(f,
#                                    state='readonly',
#                                    values=md['values'],
#                                    textvariable=self.fields[k],
#                            ).grid(row=r, column=col, sticky=W)
#                        else:
#                            ttk.Entry(f, textvariable=self.fields[k]
#                                    ).grid(row=r, column=col, sticky=W)
#                        self.fields[k].set(str(a.extra[i]))
#                r += 1
#
#        buttons = ttk.Frame(self)
#        if not self.fields:
#            ttk.Label(self, text='Your character has no class abilities which require editing.').pack(side=TOP)
#        else:
#            ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#        buttons.pack(side=BOTTOM, expand=True, fill=X)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for c in self.char_obj.classes:
#            for a in c.feats:
#                if a.meta_data:
#                    for i,md in enumerate(a.meta_data):
#                        a.extra[i] = self.fields['{}${}'.format(c.code, a.code)].get()
#                    c.update_feat_data(a.code, a.extra)
#
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterRacialAbilities (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        self.fields={}
#        r=0
#        for a in char_obj.race.ability_adj:
#            if a.meta_data:
#                ttk.Label(f, text=a.code).grid(row=r, column=0, sticky=W)
#                col=1
#                for i,md in enumerate(a.meta_data):
#                    if 'label' in md:
#                        ttk.Label(f, text=md['label']).grid(row=r, column=col, sticky=W)
#                        col += 1
#                    k = '{}${}'.format(c.code, a.code)
#                    self.fields[k] = Tkinter.StringVar()
#                    if 'values' in md:
#                        ttk.Combobox(f,
#                                state='readonly',
#                                values=md['values'],
#                                textvariable=self.fields[k],
#                        ).grid(row=r, column=col, sticky=W)
#                    else:
#                        ttk.Entry(f, textvariable=self.fields[k]
#                                ).grid(row=r, column=col, sticky=W)
#                    self.fields[k].set(str(a.extra[i]))
#            r += 1
#
#        buttons = ttk.Frame(self)
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#        buttons.pack(side=BOTTOM, expand=True, fill=X)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for a in self.char_obj.race.ability_adj:
#            if a.meta_data:
#                for i,md in enumerate(a.meta_data):
#                    a.extra[i] = self.fields['{}${}'.format(c.code, a.code)].get()
#                c.update_feat_data(a.code, a.extra)
#
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterFeats (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        # ensure only one of us is here
#        if parent.feat_w is not None and parent.feat_w.winfo_exists():
#            parent.feat_w.master.deiconify()  # pop to front (including if iconified)
#            return
#
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        parent.feat_w = self     # register for global menus to find us
#        
#        self.fields=[[], []]
#        self.feat_grid=[
#            char_obj.feats[::2],
#            char_obj.feats[1::2]
#        ]
#        self.feat_frames = [ttk.Labelframe(self, text="Left column"),
#                            ttk.Labelframe(self, text="Right column")]
#
#        for c, feat_list in enumerate(self.feat_grid):
#            for r, feat in enumerate(feat_list):
#                self.fields[c].append([])
#                if feat is not None and feat.meta_data is not None:
#                    for value in feat.extra:
#                        self.fields[c][-1].append(Tkinter.StringVar())
#                        self.fields[c][-1][-1].set(str(value))
#
#        buttons = ttk.Frame(self)
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self._cancel).pack(side=LEFT)
#        buttons.pack(side=BOTTOM, expand=True, fill=X)
#        self.feat_frames[0].pack(side=LEFT, expand=True, fill=BOTH)
#        self.feat_frames[1].pack(side=RIGHT, expand=True, fill=BOTH)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#        self._refresh()
#
#    def _refresh(self):
#        for c in (0, 1):
#            old_widgets = self.feat_frames[c].children.values()
#            for w in old_widgets:
#                w.grid_forget()
#                w.destroy()
#
#            r = 0
#            f = self.feat_frames[c]
#
#            for fr, ff in enumerate(self.feat_grid[c]):
#                if ff is None:
#                    ttk.Label(f, text='<<NEW>>', style='CharFormWarning.TLabel').grid(row=r, column=0)
#                    ttk.Label(f, text='(Select from Feats menu)', style='CharFormWarning.TLabel').grid(row=r, column=1, columnspan=5)
#                else:
#                    ttk.Label(f, text=ff.code).grid(row=r, column=0, sticky=W)
#                    if ff.meta_data:
#                        col=1
#                        for i, md in enumerate(ff.meta_data):
#                            if 'label' in md:
#                                ttk.Label(f, text=md['label']).grid(row=r, column=col, sticky=W)
#                                col += 1
#
#                            if 'values' in md:
#                                ttk.Combobox(f,
#                                    state='readonly',
#                                    values=md['values'],
#                                    textvariable=self.fields[c][fr][i],
#                                ).grid(row=r, column=col, sticky=W)
#                            else:
#                                ttk.Entry(f, textvariable=self.fields[c][fr][i]).grid(row=r, column=col, sticky=W)
#                            col += 1
#
#                if r > 0:
#                    ttk.Button(f,
#                        style="CharFormMini.Toolbutton", 
#                        image=Icons.icon_arrow_up,
#                        command=lambda r=fr, c=c: self._shift_feat_up(r,c)
#                    ).grid(row=r, column=97)
#                if fr < len(self.feat_grid[c])-1:
#                    ttk.Button(f,
#                        style="CharFormMini.Toolbutton", 
#                        image=Icons.icon_arrow_down,
#                        command=lambda r=fr, c=c: self._shift_feat_down(r,c)
#                    ).grid(row=r, column=98)
#                ttk.Button(f,
#                    style="CharFormMini.Toolbutton", 
#                    image=Icons.icon_arrow_right if c==0 else Icons.icon_arrow_left,
#                    #text='>' if c==0 else '<',
#                    command=lambda r=fr, c=c: self._shift_feat_column(r,c)
#                ).grid(row=r, column=99)
#                ttk.Button(f,
#                    style="CharFormMini.Toolbutton", 
#                    image=Icons.icon_delete,
#                    command=lambda r=fr, c=c: self._delete_feat(r,c)
#                ).grid(row=r, column=100)
#                r += 1
#                if ff is not None and isinstance(ff.description, (list,tuple)):
#                    for i in range(1, len(ff.description)):
#                        ttk.Label(f, image=Icons.icon_arrow_down).grid(row=r, column=0)
#                        r += 1
#
#            ttk.Button(f,
#                style='CharFormMini.Toolbutton',
#                image=Icons.icon_add,
#                command=lambda c=c: self._add_feat(c),
#            ).grid(row=r, column=100)
#
#    def insert_feat(self, new_feat):
#        "Fill in a place-holder for a new feat, if any.  Returns True if successful."
#        for c, feat_list in enumerate(self.feat_grid):
#            for r, feat in enumerate(feat_list):
#                if feat is None:
#                    self.feat_grid[c][r] = new_feat
#                    if new_feat.meta_data is not None:
#                        for i, md in enumerate(new_feat.meta_data):
#                            self.fields[c][r].append(Tkinter.StringVar())
#                            self.fields[c][r][-1].set(str(new_feat.extra[i]) if 
#                                len(new_feat.extra) > i else '')
#                    self._refresh()
#                    return True
#        return False
#
#    def _shift_feat_up(self, r, c):
#        "Move feat up a row"
#        self.feat_grid[c] = self.feat_grid[c][:r-1] + self.feat_grid[c][r:r+1] + self.feat_grid[c][r-1:r] + self.feat_grid[c][r+1:]
#        self.fields[c] = self.fields[c][:r-1] + self.fields[c][r:r+1] + self.fields[c][r-1:r] + self.fields[c][r+1:]
#        self._refresh()
#
#    def _shift_feat_down(self, r, c):
#        "Move feat down a row"
#        self.feat_grid[c] = self.feat_grid[c][:r] + self.feat_grid[c][r+1:r+2] + self.feat_grid[c][r:r+1] + self.feat_grid[c][r+2:]
#        self.fields[c] = self.fields[c][:r] + self.fields[c][r+1:r+2] + self.fields[c][r:r+1] + self.fields[c][r+2:]
#        self._refresh()
#                    
#    def _shift_feat_column(self, r, c):
#        "Move feat to the other column"
#        self.feat_grid[(c+1)%2].append(self.feat_grid[c][r])
#        self.fields[(c+1)%2].append(self.fields[c][r])
#        del self.feat_grid[c][r]
#        del self.fields[c][r]
#        self._refresh()
#
#    def _add_feat(self, c):
#        "Add new feat slot in column c"
#        self.feat_grid[c].append(None)
#        self.fields[c].append([])
#        self._refresh()
#
#    def _delete_feat(self, r, c):
#        "Delete feat slot in row r of column c"
#        del self.feat_grid[c][r]
#        del self.fields[c][r]
#        self._refresh()
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        # update any variables the user typed into the feat objects
#        for c, feat_list in enumerate(self.feat_grid):
#            for r, feat in enumerate(feat_list):
#                if feat is None:
#                    if not tkMessageBox.askokcancel('Pending New Feat Slots',
#                        '''You have a new feat slot which you have not yet filled in with a feat.
#If you continue, the new slot will be lost.  Are you sure you wish to continue and abandon the new slot?'''):
#                        tkMessageBox.showinfo('Aborted', "Save aborted.  Finish filling out the form then click OK again.")
#                        return
#                    tkMessageBox.showinfo("New Slot Abandoned", "Ok, I won't worry about it then.")
#                    continue
#                if feat.meta_data:
#                    feat.extra = []
#                    for i in range(len(feat.meta_data)):
#                        feat.extra.append(self.fields[c][r][i].get())
#
#        # save the new list of feat objects into the character object
#        self.char_obj.feats = []
#        for feat in itertools.chain(*itertools.izip_longest(*self.feat_grid)):
#            if feat is None:
#                feat = Feat('[Blank Line]')
#            self.char_obj.feats.append(feat)
#
#        self.parent_widget.refresh()
#        self._cancel()
#
#    def _cancel(self):
#        self.master.destroy()
#        self.parent_widget.feat_w = None
#
#class PageSetup (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        f = ttk.Frame(self)
#        ttk.Label(f, text="These page setup options will be saved with the character.").grid(columnspan=2)
#
#        r=1
#        self.fields = {}
#        f.grid_columnconfigure(0, pad=2)
#        f.grid_columnconfigure(1, pad=2)
#        for label, field in (
#            ('Color Scheme',                'opt_color_scheme'),
#            ('Suppress spell descriptions', '?opt_suppress_spell_desc'),
#            ('Compress descriptive text',   '?opt_compact_text'),
#            ('Print on both sides (duplex)','?opt_duplex'),
#        ):
#            if field[0] == '?':
#                self.fields[field] = Tkinter.IntVar()
#                self.fields[field].set(self.char_obj.__getattribute__(field[1:]))
#                ttk.Checkbutton(f, text=label, variable=self.fields[field]).grid(row=r, columnspan=2, sticky=W)
#            else:
#                ttk.Label(f, text=label).grid(row=r, column=0, sticky=W)
#                self.fields[field] = Tkinter.StringVar()
#                if field == 'opt_color_scheme':
#                    ttk.Combobox(f,
#                        state='readonly',
#                        values=['red', 'green', 'blue', 'violet', 'black'],
#                        textvariable=self.fields[field]
#                    ).grid(row=r, column=1, sticky=W)
#                    self.fields[field].set(self.char_obj.opt_color_scheme)
#            r += 1
#
#        buttons = ttk.Frame(self)
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self._cancel).pack(side=LEFT)
#        buttons.pack(side=BOTTOM, expand=False, fill=X)
#        f.pack(side=TOP, expand=True, fill=BOTH)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data"
#
#        for fld in self.fields:
#            if fld[0] == '?':
#                self.char_obj.__setattr__(fld[1:], bool(self.fields[fld].get()))
#            else:
#                self.char_obj.__setattr__(fld, self.fields[fld].get())
#
#        self._cancel()
#
#    def _cancel(self):
#        self.master.destroy()
#
#class CharacterForm (ttk.Frame):
#    def __init__(self, master, char_obj, *args, **kw):
#        ttk.Frame.__init__(self, master, *args, **kw)
#        self.char_obj = char_obj
#        Icons.init()
#
#        self.feat_w = None
#        self.styles = ttk.Style()
#        self.styles.configure('CharFormLabel.TLabel', font='Helvetica 10')
#        self.styles.configure('CharFormValue.TLabel', font='Helvetica 12 bold')
#        self.styles.configure('CharFormWarning.TLabel', 
#                font='Helvetica 11 bold', 
#                foreground='red', 
#        )
#        self.styles.configure('CharFormMini.Toolbutton', padding=0)
#
#        nb = ttk.Notebook(self)
#        nb.enable_traversal()
#        self.fields = {}
#
#        basics = ttk.Frame(nb)
#        nb.add(basics, text='General', underline=0)
#
#        abils = ttk.Frame(nb)
#        nb.add(abils, text='Abilities', underline=0)
#
#        saves = ttk.Frame(nb)
#        nb.add(saves, text='Saving Throws', underline=2)
#
#        combat = ttk.Frame(nb)
#        nb.add(combat, text='Combat', underline=0)
#
#        self.skills_f = ttk.Frame(nb)
#        nb.add(self.skills_f, text='Skills', underline=1)
#
#        sa = ttk.Frame(nb)
#        nb.add(sa, text='Special Abilities', underline=1)
#        self.ca_f = ttk.Labelframe(sa, text="Class Abilities", underline=0)
#        self.ca_f.pack(side=LEFT, fill=BOTH, expand=True, padx=2, pady=2)
#        self.ra_f = ttk.Labelframe(sa, text="Racial Abilities", underline=0)
#        self.ra_f.pack(side=RIGHT, fill=BOTH, expand=True, padx=2, pady=2)
#
#        feats = ttk.Frame(nb)
#        nb.add(feats, text='Feats', underline=0)
#        self.feat_f = [ttk.Labelframe(feats, text='Feats (left column)'),
#                       ttk.Labelframe(feats, text='Feats (right column)')]
#
#        self.feat_f[0].pack(side=LEFT, fill=BOTH, expand=True, padx=2, pady=2)
#        self.feat_f[1].pack(side=RIGHT, fill=BOTH, expand=True, padx=2, pady=2)
#
#        invent = ttk.Frame(nb)
#        nb.add(invent, text='Inventory', underline=0)
#
#        self.spells_f = ttk.Frame(nb)
#        nb.add(self.spells_f, text='Spells', underline=0)
#
#        for frm,   x, y, span, label,         attr in (
#           (basics,0, 0,    3, 'Character:',  '$name'),
#           (basics,0, 1,    1, 'Class:',      '$classes'),
#           (basics,0, 2,    1, 'Favored:',    '$favored'),
#           (basics,0, 3,    1, 'Sex:',        '$sex'),
#
#           (basics,2, 1,    1, 'Level:',      '$levels'),
#           (basics,2, 2,    1, 'Race:',       '$race'),
#           (basics,2, 3,    1, 'Age:',        'age'),
#           (basics,2, 4,    1, 'Eyes:',       'eyes'),
#           (basics,2, 5,    1, 'Hair:',       'hair'),
#           (basics,2, 6,    1, 'Skin:',       'skin'),
#           
#           (basics,4, 0,    1, '',            'id'),
#           (basics,4, 1,    1, 'XP:',         'xp'),
#           (basics,4, 2,    1, 'Alignment:',  '$alignment'),
#           (basics,4, 3,    1, 'Size Code:',  '$size'),
#           (basics,4, 4,    1, 'Height:',     '$height'),
#           (basics,4, 5,    1, 'Weight:',     '$weight'),
#           (basics,4, 6,    1, 'Hit Dice:',   '$HD'),
#
#           (basics,0, 7,    5, 'Appearance:', 'appearance'),
#           (basics,0, 8,    5, 'Background:', 'background'),
#           (basics,0, 9,    5, 'Notes:',      '$comments'),
#
#           (abils, 0, 0,    1, 'Strength:',   '$a$b$str'),
#           (abils, 0, 1,    1, 'Dexterity:',  '$a$b$dex'),
#           (abils, 0, 2,    1, 'Constitution:','$a$b$con'),
#           (abils, 0, 3,    1, 'Intelligence:','$a$b$int'),
#           (abils, 0, 4,    1, 'Wisdom:',     '$a$b$wis'),
#           (abils, 0, 5,    1, 'Charisma:',   '$a$b$cha'),
#
#           (abils, 2, 0,    1, 'Mod:',        '$a$m$str'),
#           (abils, 2, 1,    1, '',            '$a$m$dex'),
#           (abils, 2, 2,    1, '',            '$a$m$con'),
#           (abils, 2, 3,    1, '',            '$a$m$int'),
#           (abils, 2, 4,    1, '',            '$a$m$wis'),
#           (abils, 2, 5,    1, '',            '$a$m$cha'),
#
#           (abils, 4, 0,    1, 'Temp:',       '$a$t$str'),
#           (abils, 4, 1,    1, '',            '$a$t$dex'),
#           (abils, 4, 2,    1, '',            '$a$t$con'),
#           (abils, 4, 3,    1, '',            '$a$t$int'),
#           (abils, 4, 4,    1, '',            '$a$t$wis'),
#           (abils, 4, 5,    1, '',            '$a$t$cha'),
#
#           (abils, 6, 0,    1, 'Mod:',        '$a$M$str'),
#           (abils, 6, 1,    1, '',            '$a$M$dex'),
#           (abils, 6, 2,    1, '',            '$a$M$con'),
#           (abils, 6, 3,    1, '',            '$a$M$int'),
#           (abils, 6, 4,    1, '',            '$a$M$wis'),
#           (abils, 6, 5,    1, '',            '$a$M$cha'),
#
#           (abils, 0, 6,    1, '',            None),
#           (abils, 0, 7,    7, 'Speed:',      '$speed'),
#           (abils, 0, 8,    7, 'Carrying:',   '$carry'),
#           (abils, 0, 9,    7, 'Lifting:',    '$lifting'),
#           (abils, 0,10,    7, 'Push/Drag:',  '$push/drag'),
#
#           (abils, 0,11,    7, 'Notes:',      '$comments.abils'),
#
#           (saves, 0, 0,    1, 'Fortitude:',  '$STfort'),
#           (saves, 0, 1,    1, 'Reflex:',     '$STrefl'),
#           (saves, 0, 2,    1, 'Will:',       '$STwill'),
#
#           (saves, 2, 0,    1, '=',           '$SXfort'),
#           (saves, 2, 1,    1, '=',           '$SXrefl'),
#           (saves, 2, 2,    1, '=',           '$SXwill'),
#
#           (saves, 4, 0,    1, '@roll',       lambda: self.roll_save('fort')),
#           (saves, 4, 1,    1, '@roll',       lambda: self.roll_save('refl')),
#           (saves, 4, 2,    1, '@roll',       lambda: self.roll_save('will')),
#           (saves, 0, 3,    5, '',            None),
#           (saves, 0, 4,    5, 'Mods (line 1):','$SM0'),
#           (saves, 0, 5,    5, 'Mods (line 2):','$SM1'),
#           (saves, 0, 6,    5, '',            None),
#           (saves, 0, 7,    5, 'Notes:',      '$comments.saves'),
#
#
##
## Temporary attack bonus: [____]  Damage: [____]  Saves: [____]  Skills: [____]
##
## Melee  +1 = base+str+size+misc+[___]      Normal    -1 []     Init +3
## Ranged +5 = base+dex+size+misc+[___]      Off-hand  -1 []     =Dex +3
## CMB    +1 = base+str+size+misc+[___]      Two-hand  -1 []     +... +0
##    .    .                                 Bow/sling -1 []     +... +0
##    .    .                                                     +... +0
##    .    .
##
## Weapon Desc      Attack+[_]  Damage+[_]  Threat Crit Range Reach Wt Sz Type  ID
## Weapon Desc      Attack+[_]  Damage+[_]  Threat Crit Range Reach Wt Sz Type  ID
## Weapon Desc      Attack+[_]  Damage+[_]  Threat Crit Range Reach Wt Sz Type  ID
## Weapon Desc      Attack+[_]  Damage+[_]  Threat Crit Range Reach Wt Sz Type  ID
##
#
##
## AC    16  = ...       HP 8/16   Wounds: 5  Non-lethal: 3
## Touch 13  = ...       Heal Rate 1/day
## Flat  13  = ...       DR
## CMD   14  = ...       SR
##   .    .  = ...
##   .    .  = ...
##   .    .  = ...
##
## [] Armor      bonus type mdex chk spl spd wt  id
## [] Armor      bonus type mdex chk spl spd wt  id
## [] Armor      bonus type mdex chk spl spd wt  id
## [] Armor      bonus type mdex chk spl spd wt  id
##
#
##
## Spells
## spells[type] => spell_group (.class_code MUST BE IN CHAR)
#
##
#
#       ):
#            if label == '@roll':
#                ttk.Button(frm, style='CharFormMini.Toolbutton', image=Icons.icon_die_16, command=attr).grid(row=y, column=x)
#            else:
#                ttk.Label(frm, text=label, style='CharFormLabel.TLabel').grid(row=y, column=x, sticky=W)
#                if attr is not None:
#                    self.fields[attr] = ttk.Label(frm, style='CharFormValue.TLabel')
#                    if attr=='id' or attr[:3] == '$a$':
#                        self.fields[attr].grid(row=y, column=x+1, columnspan=span, sticky=E)
#                    else:
#                        self.fields[attr].grid(row=y, column=x+1, columnspan=span, sticky=W)
#
#        basics.columnconfigure(1, weight=2)
#        basics.columnconfigure(3, weight=2)
#        basics.columnconfigure(5, weight=2)
#
#        for f in (self.ca_f, self.ra_f, self.feat_f[0], self.feat_f[1]):
#            f.grid_columnconfigure(0, pad=1, weight=1)
#            f.grid_columnconfigure(1, pad=1, weight=0)
#            f.grid_columnconfigure(2, pad=1, weight=0)
#
#        #
#        # Inventory
#        #
#
#        i_summary = ttk.Frame(invent)
#        i_summary.pack(side=BOTTOM, pady=5)
#
#        ttk.Label(i_summary, text='Total weight:').pack(side=LEFT, padx=2)
#        self.inventory_ttl_wt = ttk.Label(i_summary, text='(calculating)')
#        self.inventory_ttl_wt.pack(side=LEFT, padx=2)
#        self.inventory_ttl_wt_warning = ttk.Label(i_summary, text='')
#        self.inventory_ttl_wt_warning.pack(side=LEFT, padx=2)
#
#        i_scroller = ttk.Scrollbar(invent)
#        i_scroller.pack(side=RIGHT, fill=Y)
#
#        self.inventory_w = ttk.Treeview(invent,
#            columns = ['Carried?', 'Location', 'Weight', 'ID'],
#            selectmode = 'none',
#            yscrollcommand = i_scroller.set,
#        )
#        i_scroller.config(command=self.inventory_w.yview)
#
#        ifont = tkFont.Font(family="Helvetica", size=10)
#        self.inventory_w.tag_configure('row0', background='#ffffff', font=ifont)
#        self.inventory_w.tag_configure('row1', background='#ccccff', font=ifont)
#        self.inventory_w.tag_configure('disabled', foreground='#888888')
#        self.inventory_w.tag_bind('item', '<Button-1>', self._inventory_item_context_menu)
#        self.inventory_w.tag_bind('qty', '<Button-1>', self._inventory_qty_context_menu)
#        for i, heading in enumerate(('Item Description', 'Carried?', 'Location', 'Weight', 'ID')):
#            self.inventory_w.heading('#{}'.format(i), text=heading)
#        for col, anchor, width in (
#            ('#1', W, 'MMMMMM'),
#            ('#2', W, 'MMMMMMMMMM'),
#            ('#3', E, 'MMMMMMM'),
#            ('#4', W, 'MMMMMMMMMM'),
#        ):
#            self.inventory_w.column(col, anchor=anchor, width=ifont.measure(width), stretch=False)
#        self.inventory_w.column('#0', stretch=True)
#        self.inventory_w.pack(side=LEFT, fill=BOTH, expand=True)
#            
#        nb.pack(expand=True, fill=BOTH)
#        self.refresh()
#
#    def refresh(self):
#        carrycap = self.char_obj.carrying_capacity_lbs()
#
#        #
#        # reset skill matrix
#        #
#        old_widgets = self.skills_f.children.values()
#        for w in old_widgets:
#            w.grid_forget()
#            w.destroy()
#
#        allocated_pts = 0
#        skp_per_level, ttl_skp_per_lev, max_ranks, skp_bonus, total_skp = self.char_obj.skill_points_per_level()
#
#        r=0
#        for skill_code in sorted(self.char_obj.skills):
#            skill = self.char_obj.skills[skill_code]
#            allocated_pts += skill.ranks
#            self.char_obj.set_class_skill(skill)
#            ttk.Label(self.skills_f, text='C' if skill.class_skill else '').grid(row=r, column=0)
#            ttk.Label(self.skills_f, text='T' if skill.trained else '').grid(row=r, column=1)
#            ttk.Label(self.skills_f, text='A' if skill.armor else '').grid(row=r, column=2)
#            ttk.Label(self.skills_f, text=skill.name).grid(row=r, column=3, sticky=W)
#            ttk.Label(self.skills_f, text='{:+}'.format(self.char_obj.skill_mod(skill))).grid(row=r, column=4, sticky=E)
#            ttk.Button(self.skills_f, style='CharFormMini.Toolbutton', image=Icons.icon_information, command=lambda s=skill_code: self.display_skill(s)).grid(row=r, column=5)
#            ttk.Button(self.skills_f, style='CharFormMini.Toolbutton', image=Icons.icon_die_16, command=lambda s=skill_code: self.roll_skill(s)).grid(row=r, column=6)
#            ttk.Label(self.skills_f, text=skill.description).grid(row=r, column=7, sticky=W)
#            if skill.ranks > max_ranks:
#                r += 1
#                Tkinter.Label(self.skills_f, text="WARNING: {} SKILL RANKS EXCEEDS MAXIMUM OF {}!".format(
#                    skill.name.upper(),
#                    max_ranks
#                ), foreground='yellow', background='red').grid(row=r, column=0, columnspan=8, sticky=W+E)
#            r += 1
#
#        if allocated_pts != total_skp:
#            r += 1
#            ttk.Label(self.skills_f, text="WARNING: YOU HAVE ALLOCATED {} SKILL POINT{} TOO {}!".format(
#                abs(allocated_pts - total_skp),
#                '' if -1 <= (allocated_pts - total_skp) <= 1 else 'S',
#                'MANY' if allocated_pts > total_skp else 'FEW',
#            ), style="CharFormWarning.TLabel").grid(row=r, column=0, columnspan=8, sticky=W+E)
#
#        #
#        # reset feat list
#        #
#        for ff in (self.ca_f, self.ra_f, self.feat_f[0], self.feat_f[1]):
#            old_widgets = ff.children.values()
#            for w in old_widgets:
#                w.grid_forget()
#                w.destroy()
#
#        vars = generate_substitution_list(
#            abilities = self.char_obj.ability,
#            classes = self.char_obj.classes,
#            deprecated = True,
#            arcane_levels = sum([cc.level for cc in self.char_obj.classes if cc.code in ('S','W')])
#        )
#
#        r=0
#        for ra in self.char_obj.race.ability_adj:
#            for line_item in ra.description_text(vars):
#                ttk.Label(self.ra_f, text=line_item).grid(row=r, column=0, sticky=W)
#                ttk.Label(self.ra_f, text='{}'.format(ra.ref)).grid(row=r, column=1, sticky=E)
#                ttk.Button(self.ra_f,
#                        style='CharFormMini.Toolbutton', 
#                        image=Icons.icon_information,
#                        command=lambda f=ra: self.display_racial_ability(f)
#                ).grid(row=r, column=2)
#                r += 1
#
#        r=0
#        for c in self.char_obj.classes:
#            if len(self.char_obj.classes) > 1:
#                ttk.Label(self.ca_f, 
#                        text='{} {}:'.format(c.name, c.level)
#                ).grid(row=r, sticky=W)
#                r += 1
#            vars = generate_substitution_list(
#                abilities = self.char_obj.ability,
#                classes = self.char_obj.classes,
#                deprecated = True,
#                caster_level = max(0, c.level + c.CL_adj),
#                arcane_levels = sum([cc.level for cc in self.char_obj.classes if cc.code in ('S','W')])
#            )
#            for ff in c.feats:
#                for line_item in ff.description_text(vars):
#                    ttk.Label(self.ca_f, text=line_item).grid(row=r, column=0, sticky=W)
#                    ttk.Label(self.ca_f, text="{}".format(ff.ref)).grid(row=r, column=1, sticky=E)
#                    ttk.Button(self.ca_f, 
#                            style="CharFormMini.Toolbutton",
#                            image=Icons.icon_information,
#                            command=lambda c=c, f=ff: self.display_class_ability(c, f)
#                    ).grid(row=r, column=2)
#                    r += 1
#
#        #
#        # General Feats
#        #
#        vars = generate_substitution_list(
#            abilities=self.char_obj.ability,
#            classes=self.char_obj.classes,
#            deprecated=True,
#            arcane_levels=sum([cc.level for cc in self.char_obj.classes if cc.code in ('S','W')])
#        )
#        r=[0,0]
#        c=0
#        for ff in self.char_obj.feats:
#            if ff is not None:
#                for line_item in ff.description_text(vars):
#                    ttk.Label(self.feat_f[c], text=line_item).grid(row=r[c], column=0, sticky=W)
#                    ttk.Label(self.feat_f[c], text='{}'.format(ff.ref)).grid(row=r[c], column=1, sticky=E)
#                    ttk.Button(self.feat_f[c],
#                        style="CharFormMini.Toolbutton",
#                        image=Icons.icon_information,
#                        command=lambda f=ff: self.display_feat(f)
#                    ).grid(row=r[c], column=2)
#                    r[c] += 1
#            else:
#                ttk.Label(self.feat_f[c], text='').grid(row=r[c])
#                r[c] += 1
#            c = (c + 1) % 2
#        #
#        # various data fields
#        #
#        for k,f in self.fields.iteritems():
#            if k[0] == '$':
#                if k == '$alignment':
#                    f['text'] = self.char_obj.alignment.name
#
#                elif k == '$carry':
#                    f['text'] = 'Light: {0:,}-{1:,}#, Medium: {2:,}-{3:,}#, Heavy: {4:,}-{5:,}#'.format(
#                            0, carrycap[0], 
#                            carrycap[0]+1, carrycap[1], 
#                            carrycap[1]+1, carrycap[2]
#                    )
#
#                elif k == '$classes':
#                    f['text'] = '/'.join([c.name for c in self.char_obj.classes])
#
#                elif k == '$comments':
#                    for kk, sec in (
#                            ('$comments',       'title'),
#                            ('$comments.abils', 'str'),
#                            ('$comments.saves', 'save'),
#                    ):
#                        ff = self.fields[kk]
#                        if sec in self.char_obj.comment_blocks:
#                            ff['text'] = '\n'.join(self.char_obj.comment_blocks[sec])
#                        else:
#                            ff['text'] = ''
#
#                elif k == '$comments.abils': pass
#                elif k == '$comments.saves': pass
#
#                elif k == '$favored':
#                    f['text'] = self.char_obj.classes[0].name   # XXX
#
#                elif k == '$HD':
#                    f['text'] = '/'.join([c.hd_type for c in self.char_obj.classes])
#
#                elif k == '$height':
#                    ht_in = round(self.char_obj.ht / 2.54)
#                    ht_ft = ht_in // 12
#                    ht_in -= ht_ft * 12
#                    f['text'] = '''{:.0f}' {:.0f}"'''.format(ht_ft, ht_in)
#
#                elif k == '$levels':
#                    f['text'] = '/'.join([str(c.level) for c in self.char_obj.classes])
#
#                elif k == '$lifting':
#                    f['text'] = '{:,}#'.format(carrycap[3])
#
#                elif k == '$name':
#                    if self.char_obj.nickname:
#                        f['text'] = '{} ("{}")'.format(self.char_obj.name, self.char_obj.nickname)
#                    else:
#                        f['text'] = self.char_obj.name
#
#                elif k == '$push/drag':
#                    f['text'] = '{:,}#'.format(carrycap[4])
#
#                elif k == '$race':
#                    f['text'] = self.char_obj.race.name
#
#                elif k == '$sex':
#                    f['text'] = 'Male' if self.char_obj.sex_code == 'M' else\
#                                'Female' if self.char_obj.sex_code == 'F' else 'Unknown'
#
#                elif k == '$size':
#                    f['text'] = self.char_obj.race.size_code()
#
#                elif k == '$speed':
#                    f['text'] = "{}' normally, {}' in armor or loaded".format(
#                            self.char_obj.race.speed[0], 
#                            self.char_obj.race.speed[1]
#                    ) 
#
#                elif k == '$SM0':
#                    f['text'] = self.char_obj.save_mods[0] if len(self.char_obj.save_mods) > 0 else ''
#                elif k == '$SM1':
#                    f['text'] = self.char_obj.save_mods[1] if len(self.char_obj.save_mods) > 1 else ''
#                elif k[:3] == '$ST':
#                    f['text'] = "{:+}".format(self.char_obj.saving_throw(k[3:]))
#
#                elif k[:3] == '$SX':
#                    details = self.char_obj.saving_throw_details(k[3:])
#                    f['text'] = '{:+} (class) {:+} ({})'.format(
#                            sum(details[0]),
#                            details[1][1],
#                            details[1][0]
#                    )
#                    if details[2] is not None:
#                        f['text'] += ' {:+} (magic)'.format(details[2])
#                    if details[3] is not None:
#                        f['text'] += ' {:+} (race)'.format(details[3])
#                    if details[4] is not None:
#                        f['text'] += ' {:+} (misc.)'.format(details[4])
#
#                elif k == '$weight':
#                    f['text'] = '{:.0f}#'.format(self.char_obj.wt * 0.0022)
#                elif k[:3] == '$a$':
#                    if k[3:5] == 'b$': f['text'] = str(self.char_obj.ability[k[5:]].base)
#                    if k[3:5] == 'm$': f['text'] = '{:+}'.format(self.char_obj.ability[k[5:]].mod(of=self.char_obj.ability[k[5:]].base))
#                    if k[3:5] == 't$': f['text'] = '' if self.char_obj.ability[k[5:]].temp is None else str(self.char_obj.ability[k[5:]].temp)
#                    if k[3:5] == 'M$': f['text'] = '' if self.char_obj.ability[k[5:]].temp is None else '{:+}'.format(self.char_obj.ability[k[5:]].mod())
#            elif k == 'xp':
#                f['text'] = '{:,}'.format(self.char_obj.xp)
#            else:
#                f['text'] = self.char_obj.__getattribute__(k)
#
#        #
#        # rebuild inventory list
#        #
#        def _tcl_false(v):
#            "a false property in a Tcl object"
#            if v is None or not v: return True
#            s = str(v).lower()
#            if s == 'false' or s == '0' or s == '': return True
#            return False
#
#        old_ilist = self.inventory_w.get_children()
#        if old_ilist:
#            self.char_obj.inventory_closed_IDs = set([id for id in old_ilist if _tcl_false(self.inventory_w.item(id, option='open'))])
#            self.inventory_w.delete(*old_ilist)
#
#        row=0
#        for i, item in enumerate(self.char_obj.inventory):
#            if item.id is None or item.id.strip()=='':
#                item.id = self.assign_item_id(i)
#
#            self.inventory_w.insert('', 1000000, iid=item.id,
#                text=item.name,
#                values=['Yes' if item.carried else 'No',item.location,str_g2lb(item.current_wt()),item.id],
#                tags=['item', 'row{}'.format(row%2)],
#                open=item.id not in self.char_obj.inventory_closed_IDs,
#                image=Icons.icon_box,
#            )
#
#            if item.maxqty is not None:
#                self.inventory_w.insert(item.id, 10000000, iid='Q$'+item.id,
#                    text='Qty: {}{} out of {}'.format(
#                        item.qty if item.qty is not None else 'N/A',
#                        ' (tapped {})'.format(item.tapqty) if item.tapqty else '',
#                        item.maxqty if item.maxqty is not None else 'N/A',
#                    ),
#                    values=['[+1]','[-1]','','',],
#                    tags=['qty', 'row{}'.format(row%2)],
#                    #open=True,
#                )
#            row += 1
#
#        ttlwt = sum([i.current_wt() for i in self.char_obj.inventory])
#        self.inventory_ttl_wt['text'] = str_g2lb(ttlwt)
#        cap_l, cap_m, cap_h, maxlift, maxpush = self.char_obj.carrying_capacity_g()
#        if ttlwt > maxpush:
#            self.inventory_ttl_wt_warning['text'] = '*** EXCEEDS MAXIMUM CARRYING/LIFTING/PUSHING WEIGHT ***'
#        elif ttlwt > maxlift:
#            self.inventory_ttl_wt_warning['text'] = '*** EXCEEDS MAXIMUM CARRYING/LIFTING WEIGHT (May only push/drag) ***'
#        elif ttlwt > cap_h:
#            self.inventory_ttl_wt_warning['text'] = '*** EXCEEDS MAXIMUM CARRYING WEIGHT (May only lift overhead or push/drag) ***'
#        elif ttlwt > cap_m:
#            self.inventory_ttl_wt_warning['text'] = '*** HEAVILY LOADED (ENCUMBERED/SLOWED) ***'
#        elif ttlwt > cap_l:
#            self.inventory_ttl_wt_warning['text'] = '(Medium load)'
#        else:
#            self.inventory_ttl_wt_warning['text'] = '(Light load)'
#
#        #
#        # Spells
#        #
#        # check and rebuild here in case the character changed in a way that affects
#        # spellcasting.
#        #
#        # 
#        # For spontaneous casters:
#        # Level 0: [][][][]...   []
#        #       I: [][][][]...   []
#        #      II: [][][][]...   []
#        #
#        # For those who prepare:
#        # [clear all]
#        # Level 0: [----------------] [i] [prep]
#        #
#        # [prep] button calls up menu of all spells to assign to that slot
#        #  by Level -> alphabet if necessary -> spell
#        # click on spell name to toggle casting status
#        # omit (sp) abilities; they'll be in class ability lists
#
#        self._update_slot_state()
#        old_slist = self.spells_f.children.values()
#        for child in old_slist:
#            child.pack_forget()
#            child.destroy()
#
#        nb = ttk.Notebook(self.spells_f)
#        nb.pack(fill=BOTH, expand=True)
#        for spell_type in sorted(self.char_obj.spell_types):
#            sp = self.char_obj.spells[spell_type]
#            if sp.supplimental_type is not None:
#                continue
#
#            f = ttk.Frame(nb)
#            nb.add(f, text=sp.typename)
#
#            for c in self.char_obj.classes:
#                if sp.class_code == c.code:
#                    casting_class = c
#                    break
#            else:
#                ttk.Label(f, text="You cannot cast {} spells.".format(spell_type)).pack()
#                ttk.Label(f, text="You are not of the required class.").pack()
#                continue
#
#            score = self.char_obj.ability[casting_class.spell_ability].base 
#            DC_mod = self.char_obj.ability[casting_class.spell_ability].mod() 
#            if score < 10:
#                ttk.Label(f, text="You cannot cast {} spells due to your low {} score ({})."
#                        .format(spell_type, casting_class.spell_ability.upper(), score)).pack()
#                continue
#
#            if sp.spontaneous_casting:
#                # In this case, we draw checkboxes for the spell slots
#                # on a single frame, since we don't need to actually assign
#                # specific spells there.
#                #
#                # we keep track of these as a list of levels, with the number
#                # checked as the value
#                #
#
#                slots = self.char_obj.spell_slots[spell_type]
#                for spell_level in range(10):
#                    spd = sp.spells_per_day(spell_level, casting_class.level, score)
#                    skn = sp.spells_known(spell_level, casting_class.level, score)
#                    ttk.Label(f, text=to_roman(spell_level)).grid(row=spell_level)
#                    if spd is not None:
#                        if spd[0] < 0:
#                            ttk.Label(f, text="(at will)").grid(
#                                    row=spell_level, 
#                                    column=1, 
#                                    columnspan=9,
#                                    sticky=W,
#                            )
#                        else:
#                            while len(slots['vars'][spell_level]) < spd[0]:
#                                slots['vars'][spell_level].append(Tkinter.IntVar())
#                            while len(slots['spec_vars'][spell_level]) < spd[1]:
#                                slots['spec_vars'][spell_level].append(Tkinter.IntVar())
#
#                            for i in range(spd[0]):
#                                ttk.Checkbutton(f, 
#                                    variable=slots['vars'][spell_level][i],
#                                ).grid(row=spell_level, column=i+1)
#                                if i < slots['state'][spell_level]:
#                                    slots['vars'][spell_level][i].set(1)
#                                else:
#                                    slots['vars'][spell_level][i].set(0)
#
#                            for i in range(spd[1]):
#                                if i==0: 
#                                    ttk.Label(f, text="|").grid(row=spell_level, column=99)
#                                ttk.Checkbutton(f,
#                                    variable=slots['spec_vars'][spell_level][i],
#                                ).grid(row=spell_level, column=100+i)
#                                if i < slots['spec_state'][spell_level]:
#                                    slots['spec_vars'][spell_level][i].set(1)
#                                else:
#                                    slots['spec_vars'][spell_level][i].set(0)
#
#
#            else:
#                #
#                # for memorized spell slots, we need to record which
#                # spell goes in which slot, AND whether it's cast already
#                # AND allow for any spell to go in any slot (due to metamagic)
#                # BUT reserve special slots for domain/school spells.
#                #
#                # We create a tab for each level, and inside that we have
#                # a list of slots:
#                #
#                # __/Level 0\/I\/II\/III\/IV\/V\/VI\/VII\/VIII\/IX\_______
#                # | Spell Slots Assigned:
#                # |
#                # | [reset all] [clear all]
#                # | [] [___________] [assign] [
#                # |
#                # |_________________________________________________________
#                #
#                level_nb = ttk.Notebook(f)
#                level_nb.pack(fill=BOTH, expand=True)
#                slots = self.char_obj.spell_slots[spell_type]
#
###                for spell_level in range(10):
###                    ff = ttk.Frame(level_nb)
###                    level_nb.add(ff, text="{}{}".format(
###                        'Level ' if spell_level == 0 else '',
###                        to_roman(spell_level)
###                    ))
###
###                    spd = sp.spells_per_day(spell_level, casting_class.level, score)
###                    skn = sp.spells_known(spell_level, casting_class.level, score)
###
###                    if spd is None:
###                        ttk.Label(ff, text="You cannot cast level {} {} spells."
###                                .format(spell_level, spell_type)).pack()
###                        continue
###
###                    subs = self.char_obj.substitution_list(max(0, casting_class.level + casting_class.CL_adj))
###                    ttk.Label(ff, text="LEVEL {} {} SPELL SLOTS (DC {})".format(
###                        to_roman(spell_level), sp.type.upper(), 10 + spell_level + DC_mod
###                    )).grid(row=0, column=0, columnspan=100)
###
###                    ttk.Label(ff, text="Spell Slots:").grid(
###                            row=1,
###                            column=0,
###                            columnspan=3,
###                    )
###                    ttk.Label(ff, text="Domain/Special Slots:").grid(
###                            row=1,
###                            column=3,
###                            columnspan=3)
###
###                    if spd[0] < 0:
###                        ttk.Label(ff, text="(cast at will)").grid(
###                            row=2,
###                            column=0,
###                            columnspan=3)
###                    else:
###                        # For these, vars holds a tuple of the checkmark and spell name
###                        for idx, category in enumerate(('vars','spec_vars')):
###                            while len(slots[category][spell_level]) < spd[idx]:
###                                slots[category][spell_level].append((
###                                    Tkinter.IntVar(), Tkinter.StringVar()))
###
###                        for i in range(spd[0]):
###                            ttk.Checkbutton(ff,
###                                variable=slots['vars'][spell_level][i][0],
###                            ).grid(row=i+2, column=0)
###                            mb = ttk.Menubutton(
###                                textvariable=slots['vars'][spell_level][i][1],
###                                text='xz',
###                            )
###                            mb['menu'] = self._spell_level_menu(mb, spell_type, spell_level)
###                            mb.grid(row=i+2, column=1)
###                            slots['vars'][spell_level][i][1].set('xyzzy')
#                            # spd[1]? XXX
#                            # XXX-XXX 
#
#
#                            # spd[0] spell slots + spd[1] special slots
#                            # skn is -1 for unlimited or # of spells known
#
#        self.update()
#
#    def _spell_level_menu(self, parent, sp_type, sp_lvl):
#        "Create menu of spells of given type, with the given level on top"
#
#        m = Tkinter.Menu(parent, tearoff=False)
#        m.add_command(label='xxx')
#        m.add_command(label='xxx')
#        m.add_separator()
#        for l in range(0):
#            if l != sp_lvl:
#                m.add_cascade(label='Level '+to_roman(l))
#        return m
#
#
#    def _update_slot_state(self):
#        "pull GUI widget states into character object state"
#        for spell_type in self.char_obj.spell_types:
#            sp = self.char_obj.spells[spell_type]
#            if sp.supplimental_type is not None:
#                continue
#
#            if sp.spontaneous_casting:
#                if spell_type not in self.char_obj.spell_slots:
#                    self.char_obj.spell_slots[spell_type] = {
#                            'state':      [0] * 10,
#                            'vars':       [[] for i in range(10)],
#                            'spec_state': [0] * 10,
#                            'spec_vars':  [[] for i in range(10)],
#                    }
#                else:
#                    for spell_level in range(10):
#                        for sublist, substate in ('vars', 'state'), ('spec_vars', 'spec_state'):
#                            if self.char_obj.spell_slots[spell_type][sublist][spell_level]:
#                                self.char_obj.spell_slots[spell_type][substate][spell_level] = sum([
#                                    v.get() for v in self.char_obj.spell_slots[spell_type][sublist][spell_level]
#                                ])
#            else:
#                if spell_type not in self.char_obj.spell_slots:
#                    self.char_obj.spell_slots[spell_type] = {
#                            'state':      [[] for i in range(10)],
#                            'vars':       [[] for i in range(10)],
#                            'spec_state': [[] for i in range(10)],
#                            'spec_vars':  [[] for i in range(10)],
#                    }
#                else:
#                    for spell_level in range(10):
#                        for sublist, substate in ('vars','state'),('spec_vars','spec_state'):
#                            if self.char_obj.spell_slots[spell_type][sublist][spell_level]:
#                                self.char_obj.spell_slots[spell_type][substate][spell_level] =[
#                                    (bool(v[0].get()), v[1].get())
#                                        for v in self.char_obj.spell_slots[spell_level][sublist][spell_level]
#                                ]
#
#    def assign_item_id(self, idx):
#        taken = filter(None, [i.id.strip() if i.id is not None else None for i in self.char_obj.inventory])
#        new_id = None
#        n = 0
#        while new_id is None or new_id in taken:
#            new_id = '{}G{:03d}'.format(self.char_obj.id, n)
#            n += 1
#
#        self.char_obj.inventory[idx].id = new_id
#        return new_id
#
#    def add_inventory(self, item_type): 
#        new_item = InventoryItem(item_type)
#        self.char_obj.inventory.append(new_item)
#        self.assign_item_id(-1)
#        InventoryItemEditor(self, self.char_obj, new_item)
#
#    def edit_basic(self):               CharacterBasicInfo(self, self.char_obj)
#    def edit_abilities(self):           CharacterAbilityScores(self, self.char_obj)
#    def edit_saves(self):               CharacterSavingThrows(self, self.char_obj)
#    def edit_skills(self):              CharacterSkills(self, self.char_obj)
#    def edit_class_abilities(self):     CharacterClassAbilities(self, self.char_obj)
#    def edit_racial_abilities(self):    CharacterRacialAbilities(self, self.char_obj)
#    def edit_feat_list(self):           CharacterFeats(self, self.char_obj)
#    def page_setup(self):               PageSetup(self, self.char_obj)
#    def edit_spell_type(self, sp_type): SpellCollectionEditor(self, self.char_obj, sp_type)
#
#    def display_skill(self, skill_code):
#        Typesetting.display_skill(skill_code, char_obj=self.char_obj)
#
#    def display_class_ability(self, cls, feat):
#        Typesetting.display_class_ability(cls, feat, char_obj=self.char_obj)
#
#    def display_racial_ability(self, feat):
#        Typesetting.display_racial_ability(feat, char_obj=self.char_obj)
#
#    def display_feat(self, feat):
#        if self.feat_w is not None:
#            if self.feat_w.winfo_exists():
#                if self.feat_w.insert_feat(feat):
#                    return
#            else:
#                self.feat_w = None
#
#        Typesetting.display_feat(feat, char_obj=self.char_obj)
#
#    def _inventory_item_context_menu(self, event):
#        # Clicking on an item allows you to toggle carried flag and edit details.
#        try:
#            selection_row = selection_col = selected_obj = None
#            selection_row = self.inventory_w.identify_row(event.y)
#            selection_col = self.inventory_w.identify_column(event.x)
#            for selected_obj in self.char_obj.inventory:
#                if selected_obj.id == selection_row:
#                    break
#            else:
#                raise KeyError("Inventory item {} not found".format(selection_row))
#        except:
#            tkMessageBox.showerror("Can't find inventory item", "Internal error finding item {}@{},{}".format(
#                selected_obj, selection_row, selection_col
#            ))
#
#        if selection_col == '#1':
#            selected_obj.carried = not selected_obj.carried
#            self.refresh()
#
#        elif selection_col != '#0':
#            InventoryItemEditor(self, self.char_obj, selected_obj)
#        
#    def _inventory_qty_context_menu(self, event):
#        try:
#            selection_row = selection_col = selected_obj = None
#            selection_row = self.inventory_w.identify_row(event.y)
#            if selection_row.startswith('Q$'):
#                selection_row = selection_row[2:]
#            selection_col = self.inventory_w.identify_column(event.x)
#            for selected_obj in self.char_obj.inventory:
#                if selected_obj.id == selection_row:
#                    break
#            else:
#                raise KeyError("Inventory item {} not found".format(selection_row))
#        except:
#            tkMessageBox.showerror("Can't find inventory item", "Internal error finding item {}@{},{}".format(
#                selected_obj, selection_row, selection_col
#            ))
#
#        if selection_col == '#1':
#            selected_obj.qty = (selected_obj.qty or 0) + 1
#            if (selected_obj.maxqty or 0) < selected_obj.qty:
#                selected_obj.maxqty = selected_obj.qty
#            self.refresh()
#
#        if selection_col == '#2':
#            selected_obj.qty = max(0, (selected_obj.qty or 0) - 1)
#            if (selected_obj.tapqty or 0) > selected_obj.qty:
#                selected_obj.tapqty = selected_obj.qty
#            self.refresh()
#
#    def roll_skill(self, skill_code):
#        skill = self.char_obj.skills[skill_code]
#        d = Dice(1, 20, self.char_obj.skill_mod(skill))
#        d.roll()
#        tkMessageBox.showinfo('Skill Check',
#                'Rolled {} Skill Check: {}\n\nSuccess if DC <= {}\n\n(Rolled {} and got {})'.format(
#                    skill.name,
#                    d.value(),
#                    d.value(),
#                    d.description(),
#                    d.dieHistory
#            ),
#            parent=self.master
#        )
#
#    def roll_save(self, save_type):
#        d = Dice(1, 20, self.char_obj.saving_throw(save_type))
#        d.roll()
#        tkMessageBox.showinfo(
#            'Rolled {} Saving Throw'.format(save_type.upper()),
#            '{} Saving Throw: {}\n\n{}\n\n(Rolled {} and got {})'.format(
#                save_type.upper(),
#                d.value(),
#                'SUCCESS' if d.dieHistory[0] == 20 else
#                'FAILURE' if d.dieHistory[0] ==  1 else
#                'Success if DC <= {}'.format(d.value()),
#                d.description(),
#                d.dieHistory
#            ),
#            parent=self.master
#        )
#
#    def save_file(self):
#        if self.save_file_name is None:
#            self.save_as_file()
#        else:
#            try:
#                self._update_slot_state()
#                self.char_obj.save_file(self.save_file_name, update_instance_data=False)
#            except Exception as err:
#                tkMessageBox.showerror('Error Saving File', 'Unable to write {}: {}'.format(
#                    self.save_file_name, traceback.format_exc(0)))
#
#    def save_as_file(self):
#        if self.save_file_name is None:
#            f_dir = os.getcwd()
#            f_name= None
#        else:
#            f_dir, f_name = os.path.split(self.save_file_name)
#
#        file_name = tkFileDialog.asksaveasfilename(
#                defaultextension='.gcr',
#                filetypes=(('GMA Character Record', '*.gcr'), ('All Files', '*')),
#                initialdir=f_dir,
#                initialfile=f_name,
#                parent=self,
#                title="Save Character File"
#        )
#        if file_name is not None and file_name.strip() != '':
#            self.save_file_name = file_name.strip()
#            self.save_file()
#
#    def blank_postscript(self):
#        pass
#    def save_postscript(self):
#        if self.save_file_name is None:
#            f_dir = os.getcwd()
#            f_name = None
#        else:
#            f_dir, f_name = os.path.split(self.save_file_name)
#            f_root, f_ext = os.path.splitext(f_name)
#            f_name = f_root+'.ps'
#
#        file_name = tkFileDialog.asksaveasfilename(
#            defaultextension='.ps',
#            filetypes=(('PostScript File', '*.ps'), ('All Files', '*')),
#            initialdir=f_dir,
#            initialfile=f_name,
#            parent=self,
#            title="Generate PostScript File"
#        )
#        if file_name is not None and file_name.strip() != '':
#            try:
#                self.char_obj.ps_file(file_name.strip())
#            except Exception as err:
#                tkMessageBox.showerror('Error Generating File', 'Unable to write {}: {}'.format(
#                    file_name, traceback.format_exc(0)))
#
#    def close_window(self):
#        # XXX check for unsaved edits!
#        self.master.destroy()
#
#def valid_id(id):
#    "is id a valid id code (alphanumeric only)?"
#    return id.isalnum()
#
#
#
#
#
#
#
#
#
#
#
#
#
#
#
##        self.close_callback = close_callback
##        self.item = InventoryItem(item_code)
##        self.event_obj = event_obj
##        self.char_obj = char_obj
##
##        if set_title_in is not None:
##            set_title_in.title("Item: {}".format(self.item.name))
##
##        button_bar = ttk.Frame(self)
##        attrs = ttk.Frame(self)
##        self.sublist = {}
##        self.fields = {}
##
##        attrs.grid_columnconfigure(0, pad=1, weight=0)
##        attrs.grid_columnconfigure(1, pad=1, weight=1)
##        attrs.grid_columnconfigure(2, pad=1, weight=0)
##        attrs.grid_columnconfigure(3, pad=1, weight=1)
##        for row,  cols in enumerate((
##                ('Name',              'Category'),
##                ('Cost',              'Code'),
##                ('Weight',            None),
##        )):
##            for col, lab in enumerate(cols):
##                if lab is not None:
##                    self.fields['L$'+lab] = ttk.Label(attrs, text=lab+':')
##                    self.fields['L$'+lab].grid(row=row, column=col*2, sticky=W)
##                    self.fields['V$'+lab] = ttk.Label(attrs, text='')
##                    self.fields['V$'+lab].grid(row=row, column=col*2+1, sticky=W)
##        
##        ttk.Button(button_bar, text="Close", command=self.close).pack(
##            side=RIGHT, anchor=E, pady=5, padx=5)
##
##        attrs.pack(side=TOP, anchor=W, fill=X, expand=True)
##        button_bar.pack(side=BOTTOM, anchor=E, fill=X, expand=True)
##
##        sb = ttk.Scrollbar(self)
##        sb.pack(side=RIGHT, fill=Y)
##        self.text_f = Tkinter.Text(self, yscrollcommand=sb.set, wrap=WORD)
##        sb.config(command=self.text_f.yview)
##        self.text_f.pack(side=LEFT, fill=BOTH, expand=True)
##
##        set_text_tags(self.text_f)
##        self._recalc()
##
##    def _enter_hyperlink(self, event): self.text_f['cursor'] = 'hand2'
##    def _leave_hyperlink(self, event): self.text_f['cursor'] = ''
##    def _disabled(self): tkMessageBox.showerror("Disabled", "Nothing happens.")
##
##    def _recalc(self):
##        self.fields['V$Name']['text'] = self.item.name
##        self.fields['V$Category']['text'] = self.item.category
##        self.fields['V$Cost']['text'] = self.item.str_cost()
##        self.fields['V$Code']['text'] = self.item.code
##        self.fields['V$Weight']['text'] = str_g2lb(self.item.wt)
##        
##        self.text_f['state'] = NORMAL
##        self.text_f.delete(1.0, END)
##        MarkupText(self.item.description).render(
##            TextWidgetFormatter(self.text_f, default_link_type='Item', 
##                event_obj=self.event_obj, char_obj=self.char_obj))
##        self.text_f['state'] = DISABLED
##
##    def close(self):
##        if self.close_callback is not None:
##            self.close_callback()
##
# vi:set ai sm nu ts=4 sw=4 expandtab:
########################################################################
##   _______  _______  _______                 ___       _______        #
##  (  ____ \(       )(  ___  )               /   )     (  __   )       #
##  | (    \/| () () || (   ) |              / /) |     | (  )  |       #
##  | |      | || || || (___) |             / (_) (_    | | /   |       #
##  | | ____ | |(_)| ||  ___  |            (____   _)   | (/ /) |       #
##  | | \_  )| |   | || (   ) |   Game          ) (     |   / | |       #
##  | (___) || )   ( || )   ( |   Master's      | |   _ |  (__) |       #
##  (_______)|/     \||/     \|   Assistant     (_)  (_)(_______)       #
##                                                                      #
#########################################################################
##
## Current Version: 4.0
## Adapted for the Pathfinder RPG, which is what we're playing now 
## (and this software is primarily for our own use in our play group, 
## anyway, but could be generalized later as a stand-alone product).
##
## Copyright (c) 2011 by Steven L. Willoughby, Aloha, Oregon, USA.
## All Rights Reserved.  dba Software Alchemy of Aloha, Oregon.
## Licensed under the terms and conditions of the Open Software License,
## version 3.0.
##
## Based on earlier code (versions before 4.x) by the same
## author, unreleased for the author's personal use; copyright (c)
## 1992-2009.
##
## This product is provided for educational, experimental,
## entertainment, or personal interest use, in accordance with the 
## aforementioned license agreement, ON AN "AS IS" BASIS AND WITHOUT 
## WARRANTY, EITHER EXPRESS OR IMPLIED, INCLUDING, WITHOUT LIMITATION, 
## THE WARRANTIES OF NON-INFRINGEMENT, MERCHANABILITY, OR FITNESS FOR 
## A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY OF THE 
## ORIGINAL WORK IS WITH YOU.  (See the license agreement for full 
## details including disclaimer of warranty and limitation of 
## liability.)
##
#########################################################################
#def debug(msg):
#    #print "DEBUG:", msg
#    pass
#
#import ttk, Tkinter, tkFont
#import tkMessageBox, tkFileDialog
#import traceback
#import re, os.path
#import itertools
#from Tkconstants import *
#
#from   SoftwareAlchemy.GMA.AbilityScore       import AbilityScore
#from   SoftwareAlchemy.GMA.Alignment          import Alignment
#from   SoftwareAlchemy.GMA.Class              import Class
#from   SoftwareAlchemy.GMA.Dice               import Dice
#import SoftwareAlchemy.GMA.GUI.Icons          as     Icons
#from   SoftwareAlchemy.GMA.GUI.ScrollingFrame import ScrollingFrame
#import SoftwareAlchemy.GMA.GUI.Typesetting    as     Typesetting
#from   SoftwareAlchemy.GMA.Feat               import Feat
#from   SoftwareAlchemy.GMA.Formatting         import generate_substitution_list
#from   SoftwareAlchemy.GMA.InventoryItem      import InventoryItem
#from   SoftwareAlchemy.GMA.Race               import Race
#from   SoftwareAlchemy.GMA.Skill              import Skill
#from   SoftwareAlchemy.GMA.Spell              import Spell, SpellCollection
#from   SoftwareAlchemy.Common.MarkupText      import MarkupText
#from   SoftwareAlchemy.Common.RomanNumerals   import to_roman
#from   SoftwareAlchemy.Common.WeightsAndMeasures import str_g2lb, pounds_to_grams, grams_to_pounds
#
#
#class ValidationFailure (Exception): pass
#class InternalSoftwareFault (Exception): pass
#
#def _nonneg_validator(old, new):
#    if new.strip() == '':
#        return True
#    if re.match(r'^[+]?\d+$', new):
#        return True
#    return False
#
#def _int_validator(old, new):
#    if new.strip() == '':
#        return True
#    if re.match(r'^[-+]?\d+$', new):
#        return True
#    return False
#
#def _float_validator(old, new):
#    if new.strip() == '':
#        return True
#    if re.match(r'^[+-]?(\d+(\.(\d+)?)?|\.\d+)$', new):
#        return True
#    return False
#
#class CharacterBasicInfo (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        iv = (self.register(_int_validator), '%s', '%P')
#        self.nn = nn = (self.register(_nonneg_validator), '%s', '%P')
#        
#        nb_f = ttk.Frame(self)
#        name = ttk.Labelframe(nb_f, text="Name", underline=0)
#        back = ttk.Labelframe(nb_f, text="Background", underline=0)
#        stat = ttk.Labelframe(self, text='Stats', underline=0)
#        clas = ttk.Labelframe(self, text='Classes', underline=0)
#        xpts = ttk.Labelframe(self, text='XP', underline=0)
#        buttons = ttk.Frame(self)
#
#        buttons.pack(side=BOTTOM, fill=X, expand=True)
#        name.pack(side=TOP, fill=X, padx=2, pady=2)
#        back.pack(side=BOTTOM, fill=BOTH, padx=2, pady=2)
#        nb_f.pack(side=LEFT, fill=Y)
#        stat.pack(side=LEFT, fill=BOTH, padx=2, pady=2)
#        clas.pack(side=TOP, fill=BOTH, padx=2, pady=2)
#        xpts.pack(side=BOTTOM, fill=X, padx=2, pady=2)
#
#        self.clas = clas
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        self.fields = {}
#        for r, w,  frm,  attr,         label in (
#           (0, 20, name, 'name',       'Character:'),
#           (1, 20, name, 'nickname',   'Nickname:'),
#           (2, 20, name, 'player_name','Player:'),
#           (0, 20, back, 'deity',      'Deity:'),
#           (1, 50, back, 'appearance', 'Appearance:'),
#           (2, 50, back, 'background', 'Background:'),
#           (3, 50, back, '$comments',  'Notes:'),
#           (0,  0, stat, '$race',      'Race:'),
#           (1,  0, stat, '$alignment', 'Alignment:'),
#           (2,  0, stat, '$sex',       'Sex:'),
#           (3,  5, stat, '#age',       'Age:'),
#           (4,  0, stat, '$height',    'Height:'),
#           (5,  0, stat, '$weight',    'Weight:'),
#           (6, 10, stat, 'eyes',       'Eyes:'),
#           (7, 10, stat, 'hair',       'Hair:'),
#           (8, 10, stat, 'skin',       'Skin:'),
#           (0, 10, xpts, '#xp',        'XP:'),
#           (0,  0, clas, ':Level',     'Class'),
#        ):
#            ttk.Label(frm, text=label).grid(row=r, column=0, sticky=W)
#            self.fields[attr] = Tkinter.StringVar()
#
#            if attr[0] == ':':
#                ttk.Label(frm, text=attr[1:]).grid(row=r, column=1, sticky=W)
#
#            elif attr[0] == '#':
#                ttk.Entry(frm, 
#                    textvariable=self.fields[attr],
#                    width=w,
#                    justify=RIGHT,
#                    validate='key', 
#                    validatecommand=nn,
#                ).grid(row=r, column=1, sticky=W)
#                self.fields[attr].set(str(self.char_obj.__getattribute__(attr[1:])))
#
#            elif attr[0] == '$':
#                if attr == '$alignment':
#                    ttk.Combobox(frm,
#                        state='readonly',
#                        values=[v[1] for v in sorted(Alignment.all_alignments())],
#                        textvariable=self.fields[attr]
#                    ).grid(row=r, column=1, sticky=W)
#                    self.fields[attr].set(self.char_obj.alignment.name)
#
#                elif attr == '$comments':
#                    f = ttk.Frame(frm)
#                    f.grid(row=r, column=1, sticky=N+S+E+W)
#                    sb = ttk.Scrollbar(f)
#                    t = Tkinter.Text(f,
#                        width=w,
#                        height=4,
#                        wrap=NONE,
#                        yscrollcommand=sb.set,
#                    )
#                    sb['command'] = t.yview
#                    sb.pack(side=RIGHT, fill=Y, expand=True)
#                    t.pack(fill=BOTH, expand=True)
#                    self.comment_widget = t
#
#                    if 'title' in self.char_obj.comment_blocks:
#                        t.insert(END, '\n'.join(self.char_obj.comment_blocks['title']))
#                    t.see(1.0)
#
#                elif attr == '$height':
#                    f = ttk.Frame(frm)
#                    f.grid(row=r, column=1, sticky=W)
#                    self.fields['$height$in'] = Tkinter.StringVar()
#                    ttk.Entry(f,
#                        textvariable=self.fields[attr],
#                        validate='key',
#                        validatecommand=nn,
#                        width=4,
#                        justify=RIGHT
#                    ).pack(side=LEFT)
#                    ttk.Label(f, text="' ").pack(side=LEFT)
#                    ttk.Entry(f,
#                        textvariable=self.fields['$height$in'],
#                        validate='key',
#                        validatecommand=nn,
#                        width=3,
#                        justify=RIGHT
#                    ).pack(side=LEFT)
#                    ttk.Label(f, text='"').pack(side=LEFT)
#                    ht_in = round(self.char_obj.ht / 2.54)
#                    ht_ft = ht_in // 12
#                    ht_in -= ht_ft * 12
#                    self.fields['$height'].set('{:.0f}'.format(ht_ft))
#                    self.fields['$height$in'].set('{:.0f}'.format(ht_in))
#
#                elif attr == '$race':
#                    ttk.Combobox(frm,
#                        state='readonly',
#                        values=[v[1] for v in sorted(Race.all_races())],
#                        textvariable=self.fields[attr]
#                    ).grid(row=r, column=1, sticky=W)
#                    self.fields[attr].set(self.char_obj.race.name)
#
#                elif attr == '$sex':
#                    ttk.Combobox(frm,
#                        state='readonly',
#                        values=['Female', 'Male'],
#                        textvariable=self.fields[attr]
#                    ).grid(row=r, column=1, sticky=W)
#                    self.fields[attr].set('Female' if self.char_obj.sex_code == 'F' else 'Male')
#
#                elif attr == '$weight':
#                    f = ttk.Frame(frm)
#                    f.grid(row=r, column=1, sticky=W)
#                    ttk.Entry(f,
#                        textvariable=self.fields[attr],
#                        validate='key',
#                        validatecommand=nn,
#                        width=4,
#                        justify=RIGHT
#                    ).pack(side=LEFT)
#                    ttk.Label(f, text='#').pack(side=LEFT)
#                    self.fields['$weight'].set('{:.0f}'.format(round(self.char_obj.wt * 0.0022)))
#
#                else:
#                    raise InternalSoftwareFault('Unsupported field attr {}'.format(attr))
#            else:
#                ttk.Entry(frm,
#                    textvariable=self.fields[attr], 
#                    width=w, 
#                    justify=LEFT
#                ).grid(row=r, column=1, sticky=W)
#                self.fields[attr].set(self.char_obj.__getattribute__(attr) or '')
#
#        self.classvars=[]
#        self.levelvars=[]
#        self.classwidgets=[]
#
#        self.del_button = ttk.Button(clas,
#            style='CharFormMini.Toolbutton',
#            image=Icons.icon_delete,
#            command=self._delete_class,
#        )
#        self.add_button = ttk.Button(clas, 
#            style='CharFormMini.Toolbutton',
#            image=Icons.icon_add, 
#            command=self._add_class
#        )
#
#        for c in self.char_obj.classes:
#            self._add_class()
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#
#    def _add_class(self):
#        self.classvars.append(Tkinter.StringVar())
#        self.levelvars.append(Tkinter.StringVar())
#        r = len(self.classvars)
#
#        c = ttk.Combobox(self.clas,
#            state='readonly',
#            values=[v[1] for v in sorted(Class.all_classes())],
#            textvariable=self.classvars[-1],
#        )
#        c.grid(row=r, column=0, sticky=W)
#
#        l = ttk.Entry(self.clas,
#            textvariable=self.levelvars[r-1],
#            width=3,
#            justify=RIGHT,
#            validate='key',
#            validatecommand=self.nn,
#        )
#        l.grid(row=r, column=1, sticky=W)
#
#        self.classwidgets.append((c,l))
#
#        if len(self.char_obj.classes) >= r:
#            self.classvars[-1].set(self.char_obj.classes[r-1].name)
#            self.levelvars[-1].set(str(self.char_obj.classes[r-1].level))
#        else:
#            self.classvars[-1].set(sorted(Class.all_classes())[0][1])
#            self.levelvars[-1].set('1')
#
#        if r > 1:
#            self.del_button.grid(row=r, column=2, sticky=E)
#        self.add_button.grid(row=r+1, column=2, sticky=E)
#
#    def _delete_class(self):
#        self.del_button.grid_forget()
#        self.add_button.grid_forget()
#
#        if len(self.classvars) > 1:
#            for w in (0, 1):
#                self.classwidgets[-1][w].grid_forget()
#                self.classwidgets[-1][w].destroy()
#            self.classwidgets.pop()
#            self.classvars.pop()
#            self.levelvars.pop()
#
#            r = len(self.classvars)
#            if r > 1:
#                self.del_button.grid(row=r, column=2, sticky=E)
#            self.add_button.grid(row=r+1, column=2, sticky=E)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for k in self.fields:
#            if k[0] == ':':
#                # this was just an on-screen label
#                continue
#
#            v = self.fields[k].get()
#            if k[0] == '#':
#                # non-negative integer value
#                # really, we shouldn't run into this error if the validator worked
#                # but we're paranoid.
#                try:
#                    v = int(v or 0)
#                    assert(v >= 0)
#                except Exception as err:
#                    tkMessageBox.showerror("Value Error", "The value for {} must be a non-negative integer.".format(k[1:]))
#                    return
#
#                self.char_obj.__setattr__(k[1:], v)
#            elif k[0] == '$':
#                # special cases we need to handle specially
#                if k == '$alignment':
#                    self.char_obj.alignment = Alignment(Alignment.code_for(v))
#                elif k == '$comments':
#                    self.char_obj.comment_blocks['title'] = filter(None, self.comment_widget.get(1.0, END).split('\n'))
#                elif k == '$height':
#                    try:
#                        ht_in = int(self.fields['$height$in'].get() or 0)
#                        ht_ft = int(self.fields['$height'].get() or 0)
#                        assert(ht_in >= 0 and ht_ft >= 0)
#                    except Exception as err:
#                        tkMessageBox.showerror("Value Error", "The value for height (both feet and inches) must be a non-negative integers.")
#                        return
#                    self.char_obj.ht = int((ht_ft * 12 + ht_in) * 2.54)
#                elif k == '$height$in':
#                    pass
#                elif k == '$race':
#                    self.char_obj.race = Race(Race.code_for(v))
#                elif k == '$sex':
#                    self.char_obj.sex_code = v[0].upper()
#                elif k == '$weight':
#                    try:
#                        wt = int(v or 0)
#                        assert(wt >= 0)
#                    except Exception as err:
#                        tkMessageBox.showerror('Value Error', 'The value for weight must be an integer number of pounds.')
#                        return
#
#                    self.char_obj.wt = int(round(wt / 0.0022))
#                else:
#                    raise InternalSoftwareFault('Unsupported field attr {}'.format(k))
#            else:
#                # normal string value stored to character attribute named k
#                self.char_obj.__setattr__(k, v)
#
#        # that just leaves the classes and levels to clean up
#        self.classes = [v.get() for v in self.classvars]
#        self.levels  = [int(v.get() or 0) for v in self.levelvars]
#
#        if self.char_obj.classes != self.classes:
#            if len(self.char_obj.classes) > len(self.classes):
#                if tkMessageBox.askokcancel('Confirm Class Change', 
#'''You are reducing the number of character
#classes from {} to {}, which will completely
#remove {}.
#
#Are you sure you want to do this?'''.format(
#    len(self.char_obj.classes), len(self.classes),
#    ', '.join([c.name for c in self.char_obj.classes[len(self.classes):]])
#    ), default=tkMessageBox.CANCEL):
#                    # XXX what other implications propagate out from this?
#                    del self.char_obj.classes[len(self.classes):]
#                else:
#                    tkMessageBox.showinfo('Change Canceled', "Ok, then, I won't change that.")
#
#            for i in range(len(self.classes)):
#                if i >= len(self.char_obj.classes):
#                    if tkMessageBox.askokcancel('Confirm Class Addition',
#'''You are about to add an additional class of
#{} (level {}) to your character.
#
#Are you sure you want to do this?'''.format(self.classes[i], self.levels[i]),
#default=tkMessageBox.CANCEL):
#                        self.char_obj.classes.append(Class(Class.code_for(self.classes[i]), self.levels[i], self.char_obj.special_ability_dict))
#                    else:
#                        tkMessageBox.showinfo('Change Canceled', "Ok, then, I won't change that.")
#                else:
#                    if self.char_obj.classes[i].code != Class.code_for(self.classes[i]) \
#                            or self.char_obj.classes[i].level != self.levels[i]:
#                        if tkMessageBox.askokcancel('Confirm Class Change',
#'''Are you sure you want to change class #{}
#from {} {} to {} {}?'''.format(i+1, 
#    self.char_obj.classes[i].name, self.char_obj.classes[i].level,
#    self.classes[i], self.levels[i]), default=tkMessageBox.CANCEL):
#                            self.char_obj.classes[i] = Class(Class.code_for(self.classes[i]), self.levels[i], self.char_obj.special_ability_dict)
#                        else:
#                            tkMessageBox.showinfo('Change Canceled', "Ok, then, I won't change that.")
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterAbilityScores (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        self.nn = (self.register(_nonneg_validator), '%s', '%P')
#        
#        base = ttk.Labelframe(self, text='Permanent', underline=0)
#        temp = ttk.Labelframe(self, text='Temporary', underline=0)
#        misc = ttk.Labelframe(self, text='Misc.',     underline=0)
#        buttons = ttk.Frame(self)
#
#        buttons.pack(side=BOTTOM, fill=X, expand=True)
#        misc.pack(side=BOTTOM, fill=X, expand=True, padx=2, pady=2)
#        base.pack(side=LEFT, fill=BOTH, padx=2, pady=2)
#        temp.pack(side=LEFT, fill=BOTH, padx=2, pady=2)
#
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        self.fields = {}
#        for r, w,  frm,  attr,         label in (
#           (0, 3, base,  'Bstr',       'Strength:'),
#           (1, 3, base,  'Bdex',       'Dexterity:'),
#           (2, 3, base,  'Bcon',       'Constitution:'),
#           (3, 3, base,  'Bint',       'Intelligence:'),
#           (4, 3, base,  'Bwis',       'Wisdom:'),
#           (5, 3, base,  'Bcha',       'Charisma:'),
#
#           (0, 3, temp,  'Tstr',       ''),
#           (1, 3, temp,  'Tdex',       ''),
#           (2, 3, temp,  'Tcon',       ''),
#           (3, 3, temp,  'Tint',       ''),
#           (4, 3, temp,  'Twis',       ''),
#           (5, 3, temp,  'Tcha',       ''),
#
#           (0, 30, misc,  '$comments',  'Notes:'),
#        ):
#            ttk.Label(frm, text=label).grid(row=r, column=0, sticky=W)
#            self.fields[attr] = Tkinter.StringVar()
#
#            if attr == '$comments':
#                f = ttk.Frame(frm)
#                f.grid(row=r, column=1, sticky=N+S+E+W)
#                sb = ttk.Scrollbar(f)
#                t = Tkinter.Text(f,
#                    width=w,
#                    height=4,
#                    wrap=NONE,
#                    yscrollcommand=sb.set,
#                )
#                sb['command'] = t.yview
#                sb.pack(side=RIGHT, fill=Y, expand=True)
#                t.pack(fill=BOTH, expand=True)
#                self.comment_widget = t
#
#                for a in 'str', 'dex', 'con', 'int', 'wis', 'cha':
#                    if a in self.char_obj.comment_blocks:
#                        t.insert(END, '\n'.join(self.char_obj.comment_blocks[a])+'\n')
#                t.see(1.0)
#
#            else:
#                ttk.Entry(frm, 
#                    textvariable=self.fields[attr],
#                    width=w,
#                    justify=RIGHT,
#                    validate='key', 
#                    validatecommand=self.nn,
#                ).grid(row=r, column=1, sticky=W)
#
#                if attr[0] == 'B':
#                    self.fields[attr].set(str(self.char_obj.ability[attr[1:]].base))
#                else:
#                    self.fields[attr].set(str('' if self.char_obj.ability[attr[1:]].temp is None else self.char_obj.ability[attr[1:]].temp))
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for k in self.fields:
#            v = self.fields[k].get()
#            if k[0] == 'T':
#                if v.strip() == '':
#                    v = None
#                else:
#                    try:
#                        v = int(v)
#                        assert(v >= 0)
#                    except Exception as err:
#                        tkMessageBox.showerror("Value Error", "The value for temporary ability scores must be non-negative integers or completely empty.")
#                        return
#                self.char_obj.ability[k[1:]].temp = v
#
#            elif k[0] == 'B':
#                try:
#                    v = int(v)
#                    assert(v >= 0)
#                except Exception as err:
#                    tkMessageBox.showerror("Value Error", "The value for base ability scores must be non-negative integers.")
#                    return
#                self.char_obj.ability[k[1:]].base = v
#
#            elif k[0] == '$':
#                # special cases we need to handle specially
#                if k == '$comments':
#                    self.char_obj.comment_blocks['str'] = filter(None, self.comment_widget.get(1.0, END).split('\n'))
#                    for a in 'dex', 'con', 'int', 'wis', 'cha':
#                        if a in self.char_obj.comment_blocks:
#                            del self.char_obj.comment_blocks[a]
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#
#class SpellCollectionEditor (ttk.Frame):
#    def __init__(self, parent, char_obj, spell_type):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        root.title("Editing Specification for "+spell_type+" spells")
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.spell_type = spell_type
#        self.parent_widget = parent
#        self.individual_selection = {}
#
#        if spell_type not in self.char_obj.spell_types:
#            # creating it now
#            self.char_obj.spell_types.append(spell_type)
#            self.char_obj.spells[spell_type] = SpellCollection(spell_type)
#            self.char_obj.spell_criteria[spell_type] = {
#                    'all_level': None,
#                    'except':    None,
#            }
#
#        #
#        # check that the whole list makes sense, since we're in here already anyway
#        #
#        typelist = self.char_obj.spells.keys()
#        for st in typelist:
#            coll = self.char_obj.spells[st]
#            if coll.class_code not in [c.code for c in self.char_obj.classes]:
#                tkMessageBox.showerror('Cannot Cast {} Spells'.format(st),
#                        "Your character cannot cast {} spells.  All information about this spell type is removed.".format(st))
#                del self.char_obj.spells[st]
#                self.char_obj.spell_types.remove(st)
#                del self.char_obj.spell_criteria[st]
#
#        if spell_type not in self.char_obj.spells:
#            self._cancel()
#            return
#
#        self.collection = self.char_obj.spells[spell_type]
#        self.criteria = self.char_obj.spell_criteria[spell_type]
#        root.title("Editing Specification for "+self.collection.type_description())
#        nnv = (self.register(_nonneg_validator), '%s', '%P')
#        
#        buttons = ttk.Frame(self)
#        individuals = ttk.Labelframe(self, text="Individual Spell Selection")
#
#        buttons.pack(side=BOTTOM, fill=X, pady=5, expand=False)
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self._cancel).pack(side=LEFT)
#
#        self.fields = {}
#        self.widgets = {}
#        self.fields['up_to'] = Tkinter.StringVar()
#        self.fields['inc_rule'] = Tkinter.IntVar()
#        self.rule_widgets = []
#        self.descriptors = []
#
#        if self.collection.supplimental_type == 'sp':
#            self.fields['inc_rule'].set(0)
#        else:
#            rules = ttk.Labelframe(self, text="Include by Rule")
#            rules.pack(side=TOP, fill=BOTH, expand=False, padx=2, pady=2)
#            ttk.Checkbutton(rules, 
#                text="Include all spells through level:", 
#                variable=self.fields['inc_rule'],
#                command=self._enable_rules,
#            ).grid(row=0, column=0, columnspan=3, sticky=W)
#            f = ttk.Entry(rules, 
#                textvariable=self.fields['up_to'],
#                justify=RIGHT,
#                validate='key',
#                validatecommand=nnv,
#            )
#            f.grid(row=0, column=3, sticky=E+W)
#            self.rule_widgets.append(f)
#
## XXX char_obj.spell_criteria[all_level|except|sp|0..ix] = [...]
## XXX                         int/None   |list  [] []
## XXX None level is "sp" for add_spell
## XXX specials always explicit
## XXX needs to save back in here. the collection list is not the 
## XXX source for read/write; the criteria is.
#            ttk.Label(rules, text="Except:").grid(row=1, column=0, sticky=W)
#            r=c=1
#            old_exc_str = self.criteria.get('except')
#            if old_exc_str is None:
#                old_exclusions = []
#            else:
#                old_exclusions = filter(str.strip, filter(None, self.criteria['except'].split('|')))
#            for key in Spell.all_descriptors():
#                self.fields['D$'+key] = Tkinter.IntVar()
#                self.descriptors.append(key)
#                f = ttk.Checkbutton(rules,
#                    text=key,
#                    variable=self.fields['D$'+key],
#                )
#                if key in old_exclusions:
#                    f.state(['selected'])
#                f.grid(row=r, column=c, sticky=W)
#                self.rule_widgets.append(f)
#                c += 1
#                if c > 3:
#                    c = 1
#                    r += 1
#
#        individuals.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
#        self.level_f = []
#        self.individual_checkbuttons = []
#        if self.collection.supplimental_type == 'sp':
#            f = ttk.Frame(individuals)
#            self._add_spell_tab(None, f)
#        else:
#            nb = ttk.Notebook(individuals)
#            nb.pack(expand=True, fill=BOTH)
#            for sp_level in range(10):
#                f = ttk.Frame(nb)
#                nb.add(f, text=('Level ' if sp_level==0 else '') + to_roman(sp_level))
#                self._add_spell_tab(sp_level, f)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#        self._refresh()
#
#    def _add_spell_tab(self, sp_level, f):
#        sb = ttk.Scrollbar(f, orient=VERTICAL)
#        sf = ScrollingFrame(f, yscrollcommand=sb.set)
#        sb['command'] = sf.yview
#        self.level_f.append(sf)
#        section = 'sp' if sp_level is None else to_roman(sp_level)
#
#        f = self.level_f[-1].scrolled_frame
#        self.individual_checkbuttons.append({})
#        for sp_name in self.collection.each_possible_spell(sp_level or 0):
#            self.individual_selection[sp_name] = Tkinter.IntVar()
#            self.individual_checkbuttons[-1][sp_name] = ttk.Checkbutton(f, 
#                    variable=self.individual_selection[sp_name],
#                    text=sp_name
#            )
#            self.individual_checkbuttons[-1][sp_name].pack(side=TOP, anchor=W, padx=2)
#            if section in self.criteria and sp_name in self.criteria[section]:
#                self.individual_selection[sp_name].set(1)
#            else:
#                self.individual_selection[sp_name].set(0)
#
#        sf.set_scroll_region()
#
#        sb.pack(side=RIGHT, fill=Y)
#        sf.pack(fill=BOTH, expand=True)
#
#    def _refresh(self):
#        all = self.criteria['all_level']
#        if all is not None:
#            self.fields['up_to'].set(str(all))
#            self.fields['inc_rule'].set(1)
#        else:
#            self.fields['up_to'].set('')
#            self.fields['inc_rule'].set(0)
#        self._enable_rules()
#
#
#    def _enable_rules(self):
#        #print "_enable_rules", self.fields['inc_rule'].get()
#        if self.fields['inc_rule'].get():
#            #print "enabling fields"
#            for w in self.rule_widgets:
#                w.state(['!disabled'])
#        else:
#            #print "disabling fields"
#            for w in self.rule_widgets:
#                w.state(['disabled'])
#
#    def _cancel(self):
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#    def _save(self):
#        # first, a little validation
#        if self.fields['inc_rule'].get():
#            up_to_level = self.fields['up_to'].get()
#            if up_to_level is None or up_to_level.strip() == '':
#               if not tkMessageBox.askyesno('Confirm Rule',
#               '''You indicated that you want to include all spells up to a certain level, but did not specify which level.  Do you want me to assume you really did NOT mean to include all spells?
#
#If you answer YES, then ONLY the explicitly-checked spell names will be included, disregarding any rules checked.
#
#If you answer NO, you will be able to correct this and try again.''', default='no'):
#                    return
#            else:
#                try:
#                    up_to_level = min(max(int(up_to_level), 0), 9)
#                except:
#                    tkMessageBox.showerror("Invalid level",
#                    '''You did not specify an integer value for the maximum level of spell you wish to have copied into your character's list.''')
#                    return
#
#                # rule-based inclusion and exclusion
#                self.collection.clear()
#                self.collection.add_up_to_level(up_to_level)
#                except_list = []
#                for exclusion in self.descriptors:
#                    if self.fields['D$'+exclusion].get():
#                        self.collection.remove_type(exclusion)
#                        except_list.append(exclusion)
#
#                self.criteria.clear()
#                self.criteria.update({
#                    'all_level': up_to_level,
#                    'except': '|'.join(except_list) if except_list else None,
#                })
#        else:
#            self.collection.clear()
#            self.criteria.clear()
#            self.criteria.update({
#                'all_level': None,
#                'except': None,
#            })
#
#        # explicit inclusion lists
#        if self.collection.supplimental_type == 'sp':
#            self.criteria['sp'] = []
#            for sp_name, choice in self.individual_checkbuttons[0].items():
#                if choice.instate(['selected']):
#                    self.collection.add_spell(sp_name, None)
#                    self.criteria['sp'].append(sp_name)
#        else:
#            for sp_level in range(10):
#                rom = to_roman(sp_level)
#                for sp_name, choice in self.individual_checkbuttons[sp_level].items():
#                    if choice.instate(['selected']):
#                        if rom not in self.criteria:
#                            self.criteria[rom] = []
#                        self.criteria[rom].append(sp_name)
#                        self.collection.add_spell(sp_name, sp_level)
#
#        self._cancel()
#
#class InventoryItemEditor (ttk.Frame):
#    def _grams_validator(self, old, new):
#        if not _nonneg_validator(old, new): return False
#        g = new or 0
#        lb, ilb, oz = grams_to_pounds(int(g))
#
#        self.fields['$lbs'].set(str(ilb))
#        self.fields['$oz'].set(str(oz))
#        return True
#
#    def _lbs_validator(self, old, new):
#        if not _nonneg_validator(old, new): return False
#        oz = self.fields['$oz'].get() or 0
#        lb = new or 0
#        g = pounds_to_grams(float(lb) + float(oz)/16.0)
#        self.fields['#wt'].set(str(g))
#        return True
#
#    def _oz_validator(self, old, new):
#        if not _nonneg_validator(old, new): return False
#        oz = new or 0
#        lb = self.fields['$lbs'].get() or 0
#        g = pounds_to_grams(float(lb) + float(oz)/16.0)
#        self.fields['#wt'].set(str(g))
#        return True
#
#    def __init__(self, parent, char_obj, item):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.item = item
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        nnv = (self.register(_nonneg_validator), '%s', '%P')
#        flv = (self.register(_float_validator), '%s', '%P')
#        gval = (self.register(self._grams_validator), '%s', '%P')
#        lbval = (self.register(self._lbs_validator), '%s', '%P')
#        ozval = (self.register(self._oz_validator), '%s', '%P')
#        
#        buttons = ttk.Frame(self)
#        basic = ttk.Labelframe(self, text="Basic Information")
#        weight = ttk.Labelframe(self, text="Weight")
#        qty = ttk.Labelframe(self, text="Quantities")
#        desc = ttk.Labelframe(self, text="Details")
#
#        buttons.pack(side=BOTTOM, fill=X, pady=5, expand=False)
#        basic.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
#        weight.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
#        qty.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
#        desc.pack(side=TOP, fill=BOTH, expand=True, padx=2, pady=2)
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self._cancel).pack(side=LEFT)
#        ttk.Button(buttons, text="DELETE", command=self._delete).pack(side=LEFT)
#
#        self.fields = {}
#        self.widgets = {}
#        for r, c, w, s, frm,    validator, attr,         label in (
#           (0, 0, 0, 3, basic,  None,      ':code',    'Type:'),
#           (1, 0,10, 3, basic,  None,      'id',       'ID:'),
#           (2, 0,50, 3, basic,  None,      'name',     'Description:'),
#           (3, 0,10, 3, basic,  None,      'location', 'Location:'),
#           (4, 0,10, 1, basic,  None,      '>cost',    'Cost:'),
#           #(4, 2, 0, 1, basic,  None,      None,       'gp'),
#           #(4, 3, 0, 1, basic,  None,      None,       ' '),
#
#           (0, 0, 0, 8, weight, None,      '?carried', 'Carried (included in character weight load)'),
#           (1, 0,10, 1, weight, gval,      '#wt',      'Weight:'),
#           (1, 2, 5, 1, weight, lbval,     '$lbs',     'g ='),
#           (1, 4, 5, 1, weight, ozval,     '$oz',      'lbs.,'),
#           (1, 6, 0, 1, weight, None,      None,       'oz (each)'),
#           (2, 0,10, 1, weight, None,      '>ttl_g',   None),
#           (2, 2, 5, 1, weight, None,      '>ttl_lbs', 'g ='),
#           (2, 4, 5, 1, weight, None,      '>ttl_oz',  'lbs.,'),
#           (2, 6, 0, 1, weight, None,      None,       'oz (total carried weight)'),
#
#           (0, 0, 0, 2, qty,    None,      '?$has_qty','Has quantity of (expendable) items'),
#           (1, 0, 5, 1, qty,    None,      '#maxqty',   'Maximum Qty:'),
#           (1, 1, 0, 1, qty,    None,      '>maxerr',   None),
#           (2, 0, 5, 1, qty,    None,      '#qty',      'Current Qty:'),
#           (2, 1, 0, 1, qty,    None,      '>qtyerr',   None),
#           (3, 0, 5, 1, qty,    None,      '#tapqty',   'Tapped Qty:'),
#        ):
#            if label is not None and (attr is None or attr[0] != '?'):
#                ttk.Label(frm, text=label).grid(row=r, column=c, sticky=W)
#
#            if attr is not None:
#                self.fields[attr] = Tkinter.StringVar()
#
#                if attr[0] == ':':      # constant field
#                    ttk.Label(frm, textvariable=self.fields[attr]).grid(row=r, column=c+1, sticky=W, columnspan=s)
#
#                elif attr[0] == '>':      # constant field
#                    ttk.Label(frm, textvariable=self.fields[attr]).grid(row=r, column=c+1, sticky=E, columnspan=s)
#
#                elif attr[0] == '?':    # checkbutton
#                    self.fields[attr] = Tkinter.IntVar()
#                    ttk.Checkbutton(frm, text=label, command=self.set_btns, variable=self.fields[attr]).grid(row=r, column=c, sticky=W, columnspan=s)
#
#                elif attr[0] == '#':    # integer input field
#                    self.widgets[attr] = ttk.Entry(frm, 
#                        textvariable=self.fields[attr],
#                        width=w,
#                        justify=RIGHT,
#                        validate='key', 
#                        validatecommand=validator,
#                    )
#                    self.widgets[attr].grid(row=r, column=c+1, sticky=W, columnspan=s)
#
#                elif attr[0] == '!':    # float input field
#                    ttk.Entry(frm, 
#                        textvariable=self.fields[attr],
#                        width=w,
#                        justify=RIGHT,
#                        validate='key', 
#                        validatecommand=validator,
#                    ).grid(row=r, column=c+1, sticky=W, columnspan=s)
#
#                elif attr in ('$lbs', '$oz'):
#                    ttk.Entry(frm, 
#                        textvariable=self.fields[attr],
#                        width=w,
#                        justify=RIGHT,
#                        validate='key', 
#                        validatecommand=validator,
#                    ).grid(row=r, column=c+1, sticky=W, columnspan=s)
#
#                else: # string input field
#                    ttk.Entry(frm, 
#                        textvariable=self.fields[attr],
#                        width=w,
#                        justify=LEFT,
#                    ).grid(row=r, column=c+1, sticky=W, columnspan=s)
#
#        self.widgets['#qty'].bind('<FocusOut>', self.set_btns)
#        self.widgets['#maxqty'].bind('<FocusOut>', self.set_btns)
#        self.widgets['#tapqty'].bind('<FocusOut>', self.set_btns)
#
#        sb = ttk.Scrollbar(desc)
#        sb.pack(side=RIGHT, fill=Y)
#        self.details_w = Tkinter.Text(desc, yscrollcommand=sb.set, height=5, wrap=WORD)
#        sb.config(command=self.details_w.yview)
#        self.details_w.pack(side=LEFT, fill=BOTH, expand=True)
#        Typesetting.set_text_tags(self.details_w)
#        self.pack(side=TOP, expand=True, fill=BOTH)
#        self._refresh()
#
#    def _enter_hyperlink(self, event): self.details_w['cursor'] = 'hand2'
#    def _leave_hyperlink(self, event): self.details_w['cursor'] = ''
#    def _disabled(self): tkMessageBox.showerror("Disabled", "Nothing happens.")
#
#    def _refresh(self):
#        "update fields from object"
#        for k in self.fields:
#            if k == '>cost':
#                self.fields[k].set(self.item.str_cost())
#                continue
#            elif k[0] in '?$>':
#                continue
#            elif k[0] in ':!#':
#                v = self.item.__getattribute__(k[1:])
#            else:
#                v = self.item.__getattribute__(k)
#
#            if v is not None:
#                self.fields[k].set(str(v))
#            else:
#                self.fields[k].set('')
#
#        self.fields['?$has_qty'].set(int(self.item.maxqty is not None or self.item.qty is not None or self.item.tapqty is not None))
#        self.fields['?carried'].set(int(self.item.carried))
#        lb, ilb, oz = grams_to_pounds(self.item.wt)
#        self.fields['$lbs'].set(str(ilb))
#        self.fields['$oz'].set(str(oz))
#        self.set_btns()
#
#        self.details_w['state'] = NORMAL
#        self.details_w.delete(1.0, END)
#        if self.item.description is not None:
#            MarkupText(self.item.description).render(Typesetting.TextWidgetFormatter(
#                    self.details_w, 
#                    default_link_type='Item', 
#                    event_obj=None, 
#                    char_obj=self.char_obj
#                )
#            )
#        self.details_w['state']=DISABLED
#
#    def set_btns(self, event=None):
#        q = bool(self.fields['?$has_qty'].get())
#        for f in '#maxqty', '#qty', '#tapqty':
#            self.widgets[f].configure(state=NORMAL if q else DISABLED)
#            if q and self.fields[f].get().strip() == '':
#                self.fields[f].set('0')
#
#        if q:
#            mq = int(self.fields['#maxqty'].get() or 0)
#            qq = int(self.fields['#qty'].get() or 0)
#            tq = int(self.fields['#tapqty'].get() or 0)
#            if qq < tq:
#                self.fields['>qtyerr'].set("Quantity adjusted to allow for tapped qty")
#                self.fields['#qty'].set('{}'.format(tq))
#                qq = tq
#            else:
#                self.fields['>qtyerr'].set('')
#
#            if mq < qq:
#                self.fields['>maxerr'].set("Max qty adjusted to allow for quantity")
#                self.fields['#maxqty'].set('{}'.format(qq))
#                mq = qq
#            else:
#                self.fields['>maxerr'].set('')
#
#        if self.fields['?carried'].get():
#            self.item.carried = True
#            g = int(self.fields['#wt'].get() or 0) 
#            if q:
#                qty = int(self.fields['#qty'].get() or 0)
#            else:
#                qty = 1
#
#            lbs, ilbs, oz = grams_to_pounds(int(g*qty))
#            self.fields['>ttl_g'].set(str(int(g*qty)))
#            self.fields['>ttl_lbs'].set(str(ilbs))
#            self.fields['>ttl_oz'].set(str(oz))
#        else:
#            self.fields['>ttl_g'].set('0')
#            self.fields['>ttl_lbs'].set('0')
#            self.fields['>ttl_oz'].set('0')
#
#    def _delete(self):
#        "delete this item from the character's inventory"
#        if tkMessageBox.askokcancel('Confirm Deletion', '''Are you sure you want to remove
#{0.name} (ID {0.id})
#permanently from your inventory?
#
#This action cannot be undone!'''.format(self.item), default='cancel'):
#            try:
#                self.char_obj.inventory.remove(self.item)
#            except ValueError:
#                tkMessageBox.showerror('Mysteriously Vanished', '''That item doesn't seem to be in your inventory.  No action taken, but I'm mystified.''')
#
#            self.parent_widget.refresh()
#            self.master.destroy()
#        else:
#            tkMessageBox.showinfo("Canceled", "Ok, then, I won't delete it.")
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        the_id = self.fields['id'].get().strip()
#        if not valid_id(the_id):
#            tkMessageBox.showerror("Invalid ID", '"{}" is not a valid item ID.\nIt must be alphanumeric only.'.format(the_id))
#            return
#        for item in self.char_obj.inventory:
#            if item is not self.item and item.id == the_id:
#                tkMessageBox.showerror("Duplicate ID", '"{}" duplicates the ID of another object\n("{}").'.format(the_id, item.name))
#                return
#        has_qty = bool(self.fields['?$has_qty'].get())
#        for k in self.fields:
#            if k[0] == ':': continue
#            v = self.fields[k].get()
#
#            if k[0] == '!':
#                try:
#                    self.item.__setattr__(k[1:], None if v is None or v.strip()=='' else float(v))
#                except:
#                    tkMessageBox.showerror("Value Error", "The value for {} is not understandable.  It should be a floating point value.".format(k[1:]))
#                    return
#
#            if k[0] == '#':
#                try:
#                    self.item.__setattr__(k[1:], None if v is None or v.strip()=='' else int(v))
#                except:
#                    tkMessageBox.showerror("Value Error", "The value for {} is not understandable.  It should be an integer value.".format(k[1:]))
#                    return
#
#            elif k[0] == '?':
#                if k == '?$has_qty': 
#                    continue
#
#                try:
#                    self.item.__setattr__(k[1:], bool(v or False))
#                except:
#                    tkMessageBox.showerror("Value Error", "The value for {} is not understandable.  It should be a boolean value.".format(k[1:]))
#                    return
#
#            elif k[0] == '$':
#                continue
#
#            else:
#                self.item.__setattr__(k, v)
#
#            if not has_qty:
#                self.qty = self.maxqty = self.tapqty = None
#
#        self._cancel()
#
#    def _cancel(self):
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterSavingThrows (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        mods = ttk.Frame(self)
#        buttons = ttk.Frame(self)
#
#        buttons.pack(side=BOTTOM, fill=X, expand=True)
#        mods.pack(side=BOTTOM, fill=BOTH, expand=True)
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        self.fields = {}
#        for r, w,  frm,  attr,         label in (
#           (0, 50, mods, 'SM0',        'Mods (line 1):'),
#           (1, 50, mods, 'SM1',        'Mods (line 2):'),
#           (2, 50, mods, '$comments',  'Notes:'),
#        ):
#            ttk.Label(frm, text=label).grid(row=r, column=0, sticky=W)
#            self.fields[attr] = Tkinter.StringVar()
#
#            if attr == '$comments':
#                f = ttk.Frame(frm)
#                f.grid(row=r, column=1, sticky=N+S+E+W)
#                sb = ttk.Scrollbar(f)
#                t = Tkinter.Text(f,
#                    width=w,
#                    height=4,
#                    wrap=NONE,
#                    yscrollcommand=sb.set,
#                )
#                sb['command'] = t.yview
#                sb.pack(side=RIGHT, fill=Y, expand=True)
#                t.pack(fill=BOTH, expand=True)
#                self.comment_widget = t
#
#                if 'save' in self.char_obj.comment_blocks:
#                    t.insert(END, '\n'.join(self.char_obj.comment_blocks['save']))
#                t.see(1.0)
#
#            else:
#                ttk.Entry(frm, 
#                    textvariable=self.fields[attr],
#                    width=w,
#                    justify=LEFT,
#                ).grid(row=r, column=1, sticky=W)
#
#        self.fields['SM0'].set(self.char_obj.save_mods[0] if len(self.char_obj.save_mods)>0 else '')
#        self.fields['SM1'].set(self.char_obj.save_mods[1] if len(self.char_obj.save_mods)>1 else '')
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        k = filter(None, self.comment_widget.get(1.0, END).split('\n'))
#        if not k:
#            if 'save' in self.char_obj.comment_blocks:
#                del self.char_obj.comment_blocks['save']
#        else:
#            self.char_obj.comment_blocks['save'] = k
#
#        self.char_obj.save_mods = filter(None, [
#                self.fields['SM0'].get(),
#                self.fields['SM1'].get(),
#        ])
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterSkills (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        skills = ttk.Frame(self)
#        buttons = ttk.Frame(self)
#
#        buttons.pack(side=BOTTOM, fill=X, expand=True)
#        skills.pack(side=BOTTOM, fill=BOTH, expand=True)
#        self.nn = nn = (self.register(_nonneg_validator), '%s', '%P')
#
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#
#        skp_per_level, ttl_skp_per_lev, max_ranks, skp_bonus, total_skp = self.char_obj.skill_points_per_level()
#
#        self.fields = {}
#        maxcols=1
#        for r, w,  frm,    label, attr in (
#           (0,  0, skills, 'Class:', [c.name for c in self.char_obj.classes]),
#           (1,  0, skills, 'Base Points/Level:', ['{}'.format(s) for s in skp_per_level]),
#           (2,  0, skills, '+ Intelligence Modifier:', ['{:+}'.format(self.char_obj.ability['int'].mod()) for s in skp_per_level]),
#           (3,  0, skills, '+ Racial Modifier:', ['{:+}'.format(self.char_obj.race.skill_points) for s in skp_per_level]),
#           (4,  0, skills, '= Total Points/Level:', ['{}'.format(s) for s in ttl_skp_per_lev]),
#           (5,  0, skills, '', '>'),
#           (6,  0, skills, 'x Class Levels:', ['x{}'.format(c.level) for c in self.char_obj.classes]),
#           (7,  0, skills, '= Total Points/Class:', ['={}'.format(c.level*s) for c, s in zip(self.char_obj.classes, ttl_skp_per_lev)]),
#           (8,  0, skills, '', '>'),
#           (9,  3, skills, '+ Bonus Points Taken When Advancing:', '#bonus'),
#           (10, 0, skills, '= Total Skill Points:', '>{}'.format(total_skp)),
#           (11, 0, skills, 'Maximum Ranks per Skill:', '>{}'.format(max_ranks)),
#           (12, 0, skills, 'Skill Point Allocation:', '$points'),
#           (13,50, skills, 'Notes:', '$comments'),
#        ):
#            ttk.Label(frm, text=label).grid(row=r, column=0, sticky=W)
#            if isinstance(attr, (list,tuple)):
#                maxcols = max(maxcols, len(attr))
#                for c,v in enumerate(attr):
#                    ttk.Label(frm, text=v).grid(row=r, column=c+1, sticky=E)
#            elif attr[0] == '>':
#                ttk.Label(frm, text=attr[1:]).grid(row=r, column=1, sticky=W)
#            else:
#                self.fields[attr] = Tkinter.StringVar()
#                if attr == '$comments':
#                    f = ttk.Frame(frm)
#                    f.grid(row=r, column=1, columnspan=maxcols+1, sticky=N+S+E+W)
#                    sb = ttk.Scrollbar(f)
#                    t = Tkinter.Text(f,
#                        width=w,
#                        height=4,
#                        wrap=NONE,
#                        yscrollcommand=sb.set,
#                    )
#                    sb['command'] = t.yview
#                    sb.pack(side=RIGHT, fill=Y, expand=True)
#                    t.pack(fill=BOTH, expand=True)
#                    self.comment_widget = t
#
#                    if 'skills' in self.char_obj.comment_blocks:
#                        t.insert(END, '\n'.join(self.char_obj.comment_blocks['skills']))
#                    t.see(1.0)
#                elif attr == '$points':
#                    f = ttk.Frame(frm)
#                    f.grid(row=r, column=1, columnspan=maxcols+1, sticky=N+S+E+W)
#
#                    r = 0
#                    slist = [x for x in Skill.all_skill_codes()]
#                    skill_count = len(slist)
#                    rows = (skill_count+4) // 5
#                    for skill_code, skill_name in slist:
#                        kk = attr + '$' + skill_code
#                        self.fields[kk] = Tkinter.StringVar()
#                        ttk.Label(f, text=skill_name+":").grid(row=r%rows, column=2*(r//rows), sticky=W)
#                        ttk.Entry(f, 
#                            textvariable=self.fields[kk], 
#                            width=3, 
#                            justify=RIGHT
#                        ).grid(row=r%rows, column=1+2*(r//rows), sticky=W, padx=2)
#                        if skill_code in self.char_obj.skills:
#                            self.fields[kk].set(str(self.char_obj.skills[skill_code].ranks))
#                        else:
#                            self.fields[kk].set('0')
#                        r += 1
#
#                elif attr[0]=='#':
#                    ttk.Entry(frm, 
#                        textvariable=self.fields[attr],
#                        width=w,
#                        justify=RIGHT,
#                        validate='key', 
#                        validatecommand=nn,
#                    ).grid(row=r, column=1, sticky=W)
#
#            for c in range(1, maxcols+1):
#                skills.grid_columnconfigure(c, pad=1, weight=0)
#            skills.grid_columnconfigure(maxcols+1, pad=1, weight=1)
#
#        self.fields['#bonus'].set(str(self.char_obj.skp_bonus))
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for k in self.fields:
#            if k == '$comments':
#                kk = filter(None, self.comment_widget.get(1.0, END).split('\n'))
#                if not kk:
#                    if 'skills' in self.char_obj.comment_blocks:
#                        del self.char_obj.comment_blocks['skills']
#                else:
#                    self.char_obj.comment_blocks['skills'] = kk
#            elif k == '#bonus':
#                try:
#                    self.char_obj.skp_bonus = int(self.fields['#bonus'].get())
#                except:
#                    tkMessageBox.showerror("Value Error", "The value for the skill point bonus must be a non-negative integer.")
#            elif k.startswith('$points$'):
#                try:
#                    ranks = int(self.fields[k].get())
#                except:
#                    tkMessageBox.showerror("Value Error", "The value for the {} skill ranks must be a non-negative integer.".format(k[8:]))
#                    continue
#
#                sc = k[8:]
#                debug('skill {} (field {}) ranks={}'.format(sc, k, ranks))
#                if sc in self.char_obj.skills:
#                    skill = self.char_obj.skills[sc]
#                    if ranks == 0 and skill.trained:
#                        if tkMessageBox.askokcancel('Confirm Skill Deletion',
#                                """\
#You reduced the ranks for the {} skill to zero.
#This skill requires training, so continuing will remove
#this skill from your character.""".format(
#                                    skill.name
#                                )):
#                            skill.ranks = 0
#                            del self.char_obj.skills[sc]
#                        continue
#                    elif ranks == 0 and skill.sub:
#                        if tkMessageBox.askokcancel('Confirm Skill Deletion',
#                                """\
#You reduced the ranks for the {} skill to zero.
#This skill is a specific subclass of a general skill,
#so continuing to remove all ranks will remove it entirely
#from your character.""".format(skill.name)):
#                            skill.ranks=0
#                            del self.char_obj.skills[sc]
#                        continue
#                    skill.ranks = ranks
#                elif ranks > 0:
#                    skill = Skill(sc)
#                    if tkMessageBox.askokcancel('Confirm Skill Addition', 
#                            """\
#You added {} rank{} for the {} skill.  This skill did not
#previously exist for this character.  Continuing will 
#add this skill to your character.""".format(
#                                ranks, 's' if ranks > 1 else '',
#                                skill.name
#                            )):
#                        self.char_obj.skills[sc] = skill
#                        skill.ranks = ranks
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterClassAbilities (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        self.fields={}
#        for c in char_obj.classes:
#            f = ttk.Labelframe(self, text='{} Class Ability Parameters'.format(c.name))
#            f.pack(side=TOP, fill=X, expand=True)
#
#            r=0
#            for a in c.feats:
#                if a.meta_data:
#                    ttk.Label(f, text=a.code).grid(row=r, column=0, sticky=W)
#                    col=1
#                    for i,md in enumerate(a.meta_data):
#                        if 'label' in md:
#                            ttk.Label(f, text=md['label']).grid(row=r, column=col, sticky=W)
#                            col += 1
#                        k = '{}${}'.format(c.code, a.code)
#                        self.fields[k] = Tkinter.StringVar()
#                        if 'values' in md:
#                            ttk.Combobox(f,
#                                    state='readonly',
#                                    values=md['values'],
#                                    textvariable=self.fields[k],
#                            ).grid(row=r, column=col, sticky=W)
#                        else:
#                            ttk.Entry(f, textvariable=self.fields[k]
#                                    ).grid(row=r, column=col, sticky=W)
#                        self.fields[k].set(str(a.extra[i]))
#                r += 1
#
#        buttons = ttk.Frame(self)
#        if not self.fields:
#            ttk.Label(self, text='Your character has no class abilities which require editing.').pack(side=TOP)
#        else:
#            ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#        buttons.pack(side=BOTTOM, expand=True, fill=X)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for c in self.char_obj.classes:
#            for a in c.feats:
#                if a.meta_data:
#                    for i,md in enumerate(a.meta_data):
#                        a.extra[i] = self.fields['{}${}'.format(c.code, a.code)].get()
#                    c.update_feat_data(a.code, a.extra)
#
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterRacialAbilities (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        self.fields={}
#        r=0
#        for a in char_obj.race.ability_adj:
#            if a.meta_data:
#                ttk.Label(f, text=a.code).grid(row=r, column=0, sticky=W)
#                col=1
#                for i,md in enumerate(a.meta_data):
#                    if 'label' in md:
#                        ttk.Label(f, text=md['label']).grid(row=r, column=col, sticky=W)
#                        col += 1
#                    k = '{}${}'.format(c.code, a.code)
#                    self.fields[k] = Tkinter.StringVar()
#                    if 'values' in md:
#                        ttk.Combobox(f,
#                                state='readonly',
#                                values=md['values'],
#                                textvariable=self.fields[k],
#                        ).grid(row=r, column=col, sticky=W)
#                    else:
#                        ttk.Entry(f, textvariable=self.fields[k]
#                                ).grid(row=r, column=col, sticky=W)
#                    self.fields[k].set(str(a.extra[i]))
#            r += 1
#
#        buttons = ttk.Frame(self)
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self.master.destroy).pack(side=LEFT)
#        buttons.pack(side=BOTTOM, expand=True, fill=X)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        for a in self.char_obj.race.ability_adj:
#            if a.meta_data:
#                for i,md in enumerate(a.meta_data):
#                    a.extra[i] = self.fields['{}${}'.format(c.code, a.code)].get()
#                c.update_feat_data(a.code, a.extra)
#
#
#        self.parent_widget.refresh()
#        self.master.destroy()
#
#class CharacterFeats (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        # ensure only one of us is here
#        if parent.feat_w is not None and parent.feat_w.winfo_exists():
#            parent.feat_w.master.deiconify()  # pop to front (including if iconified)
#            return
#
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        parent.feat_w = self     # register for global menus to find us
#        
#        self.fields=[[], []]
#        self.feat_grid=[
#            char_obj.feats[::2],
#            char_obj.feats[1::2]
#        ]
#        self.feat_frames = [ttk.Labelframe(self, text="Left column"),
#                            ttk.Labelframe(self, text="Right column")]
#
#        for c, feat_list in enumerate(self.feat_grid):
#            for r, feat in enumerate(feat_list):
#                self.fields[c].append([])
#                if feat is not None and feat.meta_data is not None:
#                    for value in feat.extra:
#                        self.fields[c][-1].append(Tkinter.StringVar())
#                        self.fields[c][-1][-1].set(str(value))
#
#        buttons = ttk.Frame(self)
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self._cancel).pack(side=LEFT)
#        buttons.pack(side=BOTTOM, expand=True, fill=X)
#        self.feat_frames[0].pack(side=LEFT, expand=True, fill=BOTH)
#        self.feat_frames[1].pack(side=RIGHT, expand=True, fill=BOTH)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#        self._refresh()
#
#    def _refresh(self):
#        for c in (0, 1):
#            old_widgets = self.feat_frames[c].children.values()
#            for w in old_widgets:
#                w.grid_forget()
#                w.destroy()
#
#            r = 0
#            f = self.feat_frames[c]
#
#            for fr, ff in enumerate(self.feat_grid[c]):
#                if ff is None:
#                    ttk.Label(f, text='<<NEW>>', style='CharFormWarning.TLabel').grid(row=r, column=0)
#                    ttk.Label(f, text='(Select from Feats menu)', style='CharFormWarning.TLabel').grid(row=r, column=1, columnspan=5)
#                else:
#                    ttk.Label(f, text=ff.code).grid(row=r, column=0, sticky=W)
#                    if ff.meta_data:
#                        col=1
#                        for i, md in enumerate(ff.meta_data):
#                            if 'label' in md:
#                                ttk.Label(f, text=md['label']).grid(row=r, column=col, sticky=W)
#                                col += 1
#
#                            if 'values' in md:
#                                ttk.Combobox(f,
#                                    state='readonly',
#                                    values=md['values'],
#                                    textvariable=self.fields[c][fr][i],
#                                ).grid(row=r, column=col, sticky=W)
#                            else:
#                                ttk.Entry(f, textvariable=self.fields[c][fr][i]).grid(row=r, column=col, sticky=W)
#                            col += 1
#
#                if r > 0:
#                    ttk.Button(f,
#                        style="CharFormMini.Toolbutton", 
#                        image=Icons.icon_arrow_up,
#                        command=lambda r=fr, c=c: self._shift_feat_up(r,c)
#                    ).grid(row=r, column=97)
#                if fr < len(self.feat_grid[c])-1:
#                    ttk.Button(f,
#                        style="CharFormMini.Toolbutton", 
#                        image=Icons.icon_arrow_down,
#                        command=lambda r=fr, c=c: self._shift_feat_down(r,c)
#                    ).grid(row=r, column=98)
#                ttk.Button(f,
#                    style="CharFormMini.Toolbutton", 
#                    image=Icons.icon_arrow_right if c==0 else Icons.icon_arrow_left,
#                    #text='>' if c==0 else '<',
#                    command=lambda r=fr, c=c: self._shift_feat_column(r,c)
#                ).grid(row=r, column=99)
#                ttk.Button(f,
#                    style="CharFormMini.Toolbutton", 
#                    image=Icons.icon_delete,
#                    command=lambda r=fr, c=c: self._delete_feat(r,c)
#                ).grid(row=r, column=100)
#                r += 1
#                if ff is not None and isinstance(ff.description, (list,tuple)):
#                    for i in range(1, len(ff.description)):
#                        ttk.Label(f, image=Icons.icon_arrow_down).grid(row=r, column=0)
#                        r += 1
#
#            ttk.Button(f,
#                style='CharFormMini.Toolbutton',
#                image=Icons.icon_add,
#                command=lambda c=c: self._add_feat(c),
#            ).grid(row=r, column=100)
#
#    def insert_feat(self, new_feat):
#        "Fill in a place-holder for a new feat, if any.  Returns True if successful."
#        for c, feat_list in enumerate(self.feat_grid):
#            for r, feat in enumerate(feat_list):
#                if feat is None:
#                    self.feat_grid[c][r] = new_feat
#                    if new_feat.meta_data is not None:
#                        for i, md in enumerate(new_feat.meta_data):
#                            self.fields[c][r].append(Tkinter.StringVar())
#                            self.fields[c][r][-1].set(str(new_feat.extra[i]) if 
#                                len(new_feat.extra) > i else '')
#                    self._refresh()
#                    return True
#        return False
#
#    def _shift_feat_up(self, r, c):
#        "Move feat up a row"
#        self.feat_grid[c] = self.feat_grid[c][:r-1] + self.feat_grid[c][r:r+1] + self.feat_grid[c][r-1:r] + self.feat_grid[c][r+1:]
#        self.fields[c] = self.fields[c][:r-1] + self.fields[c][r:r+1] + self.fields[c][r-1:r] + self.fields[c][r+1:]
#        self._refresh()
#
#    def _shift_feat_down(self, r, c):
#        "Move feat down a row"
#        self.feat_grid[c] = self.feat_grid[c][:r] + self.feat_grid[c][r+1:r+2] + self.feat_grid[c][r:r+1] + self.feat_grid[c][r+2:]
#        self.fields[c] = self.fields[c][:r] + self.fields[c][r+1:r+2] + self.fields[c][r:r+1] + self.fields[c][r+2:]
#        self._refresh()
#                    
#    def _shift_feat_column(self, r, c):
#        "Move feat to the other column"
#        self.feat_grid[(c+1)%2].append(self.feat_grid[c][r])
#        self.fields[(c+1)%2].append(self.fields[c][r])
#        del self.feat_grid[c][r]
#        del self.fields[c][r]
#        self._refresh()
#
#    def _add_feat(self, c):
#        "Add new feat slot in column c"
#        self.feat_grid[c].append(None)
#        self.fields[c].append([])
#        self._refresh()
#
#    def _delete_feat(self, r, c):
#        "Delete feat slot in row r of column c"
#        del self.feat_grid[c][r]
#        del self.fields[c][r]
#        self._refresh()
#
#    def _save(self):
#        "Update character object from form data and refresh parent window."
#
#        # update any variables the user typed into the feat objects
#        for c, feat_list in enumerate(self.feat_grid):
#            for r, feat in enumerate(feat_list):
#                if feat is None:
#                    if not tkMessageBox.askokcancel('Pending New Feat Slots',
#                        '''You have a new feat slot which you have not yet filled in with a feat.
#If you continue, the new slot will be lost.  Are you sure you wish to continue and abandon the new slot?'''):
#                        tkMessageBox.showinfo('Aborted', "Save aborted.  Finish filling out the form then click OK again.")
#                        return
#                    tkMessageBox.showinfo("New Slot Abandoned", "Ok, I won't worry about it then.")
#                    continue
#                if feat.meta_data:
#                    feat.extra = []
#                    for i in range(len(feat.meta_data)):
#                        feat.extra.append(self.fields[c][r][i].get())
#
#        # save the new list of feat objects into the character object
#        self.char_obj.feats = []
#        for feat in itertools.chain(*itertools.izip_longest(*self.feat_grid)):
#            if feat is None:
#                feat = Feat('[Blank Line]')
#            self.char_obj.feats.append(feat)
#
#        self.parent_widget.refresh()
#        self._cancel()
#
#    def _cancel(self):
#        self.master.destroy()
#        self.parent_widget.feat_w = None
#
#class PageSetup (ttk.Frame):
#    def __init__(self, parent, char_obj):
#        root = Tkinter.Toplevel()
#        root.transient(parent)
#        ttk.Frame.__init__(self, root)
#        self.char_obj = char_obj
#        self.parent_widget = parent
#        
#        f = ttk.Frame(self)
#        ttk.Label(f, text="These page setup options will be saved with the character.").grid(columnspan=2)
#
#        r=1
#        self.fields = {}
#        f.grid_columnconfigure(0, pad=2)
#        f.grid_columnconfigure(1, pad=2)
#        for label, field in (
#            ('Color Scheme',                'opt_color_scheme'),
#            ('Suppress spell descriptions', '?opt_suppress_spell_desc'),
#            ('Compress descriptive text',   '?opt_compact_text'),
#            ('Print on both sides (duplex)','?opt_duplex'),
#        ):
#            if field[0] == '?':
#                self.fields[field] = Tkinter.IntVar()
#                self.fields[field].set(self.char_obj.__getattribute__(field[1:]))
#                ttk.Checkbutton(f, text=label, variable=self.fields[field]).grid(row=r, columnspan=2, sticky=W)
#            else:
#                ttk.Label(f, text=label).grid(row=r, column=0, sticky=W)
#                self.fields[field] = Tkinter.StringVar()
#                if field == 'opt_color_scheme':
#                    ttk.Combobox(f,
#                        state='readonly',
#                        values=['red', 'green', 'blue', 'violet', 'black'],
#                        textvariable=self.fields[field]
#                    ).grid(row=r, column=1, sticky=W)
#                    self.fields[field].set(self.char_obj.opt_color_scheme)
#            r += 1
#
#        buttons = ttk.Frame(self)
#        ttk.Button(buttons, text='Ok', command=self._save).pack(side=RIGHT)
#        ttk.Button(buttons, text='Cancel', command=self._cancel).pack(side=LEFT)
#        buttons.pack(side=BOTTOM, expand=False, fill=X)
#        f.pack(side=TOP, expand=True, fill=BOTH)
#
#        self.pack(side=TOP, expand=True, fill=BOTH)
#
#    def _save(self):
#        "Update character object from form data"
#
#        for fld in self.fields:
#            if fld[0] == '?':
#                self.char_obj.__setattr__(fld[1:], bool(self.fields[fld].get()))
#            else:
#                self.char_obj.__setattr__(fld, self.fields[fld].get())
#
#        self._cancel()
#
#    def _cancel(self):
#        self.master.destroy()
#
#class CharacterForm (ttk.Frame):
#    def __init__(self, master, char_obj, *args, **kw):
#        ttk.Frame.__init__(self, master, *args, **kw)
#        self.char_obj = char_obj
#        Icons.init()
#
#        self.feat_w = None
#        self.styles = ttk.Style()
#        self.styles.configure('CharFormLabel.TLabel', font='Helvetica 10')
#        self.styles.configure('CharFormValue.TLabel', font='Helvetica 12 bold')
#        self.styles.configure('CharFormWarning.TLabel', 
#                font='Helvetica 11 bold', 
#                foreground='red', 
#        )
#        self.styles.configure('CharFormMini.Toolbutton', padding=0)
#
#        nb = ttk.Notebook(self)
#        nb.enable_traversal()
#        self.fields = {}
#
#        basics = ttk.Frame(nb)
#        nb.add(basics, text='General', underline=0)
#
#        abils = ttk.Frame(nb)
#        nb.add(abils, text='Abilities', underline=0)
#
#        saves = ttk.Frame(nb)
#        nb.add(saves, text='Saving Throws', underline=2)
#
#        combat = ttk.Frame(nb)
#        nb.add(combat, text='Combat', underline=0)
#
#        self.skills_f = ttk.Frame(nb)
#        nb.add(self.skills_f, text='Skills', underline=1)
#
#        sa = ttk.Frame(nb)
#        nb.add(sa, text='Special Abilities', underline=1)
#        self.ca_f = ttk.Labelframe(sa, text="Class Abilities", underline=0)
#        self.ca_f.pack(side=LEFT, fill=BOTH, expand=True, padx=2, pady=2)
#        self.ra_f = ttk.Labelframe(sa, text="Racial Abilities", underline=0)
#        self.ra_f.pack(side=RIGHT, fill=BOTH, expand=True, padx=2, pady=2)
#
#        feats = ttk.Frame(nb)
#        nb.add(feats, text='Feats', underline=0)
#        self.feat_f = [ttk.Labelframe(feats, text='Feats (left column)'),
#                       ttk.Labelframe(feats, text='Feats (right column)')]
#
#        self.feat_f[0].pack(side=LEFT, fill=BOTH, expand=True, padx=2, pady=2)
#        self.feat_f[1].pack(side=RIGHT, fill=BOTH, expand=True, padx=2, pady=2)
#
#        invent = ttk.Frame(nb)
#        nb.add(invent, text='Inventory', underline=0)
#
#        self.spells_f = ttk.Frame(nb)
#        nb.add(self.spells_f, text='Spells', underline=0)
#
#        for frm,   x, y, span, label,         attr in (
#           (basics,0, 0,    3, 'Character:',  '$name'),
#           (basics,0, 1,    1, 'Class:',      '$classes'),
#           (basics,0, 2,    1, 'Favored:',    '$favored'),
#           (basics,0, 3,    1, 'Sex:',        '$sex'),
#
#           (basics,2, 1,    1, 'Level:',      '$levels'),
#           (basics,2, 2,    1, 'Race:',       '$race'),
#           (basics,2, 3,    1, 'Age:',        'age'),
#           (basics,2, 4,    1, 'Eyes:',       'eyes'),
#           (basics,2, 5,    1, 'Hair:',       'hair'),
#           (basics,2, 6,    1, 'Skin:',       'skin'),
#           
#           (basics,4, 0,    1, '',            'id'),
#           (basics,4, 1,    1, 'XP:',         'xp'),
#           (basics,4, 2,    1, 'Alignment:',  '$alignment'),
#           (basics,4, 3,    1, 'Size Code:',  '$size'),
#           (basics,4, 4,    1, 'Height:',     '$height'),
#           (basics,4, 5,    1, 'Weight:',     '$weight'),
#           (basics,4, 6,    1, 'Hit Dice:',   '$HD'),
#
#           (basics,0, 7,    5, 'Appearance:', 'appearance'),
#           (basics,0, 8,    5, 'Background:', 'background'),
#           (basics,0, 9,    5, 'Notes:',      '$comments'),
#
#           (abils, 0, 0,    1, 'Strength:',   '$a$b$str'),
#           (abils, 0, 1,    1, 'Dexterity:',  '$a$b$dex'),
#           (abils, 0, 2,    1, 'Constitution:','$a$b$con'),
#           (abils, 0, 3,    1, 'Intelligence:','$a$b$int'),
#           (abils, 0, 4,    1, 'Wisdom:',     '$a$b$wis'),
#           (abils, 0, 5,    1, 'Charisma:',   '$a$b$cha'),
#
#           (abils, 2, 0,    1, 'Mod:',        '$a$m$str'),
#           (abils, 2, 1,    1, '',            '$a$m$dex'),
#           (abils, 2, 2,    1, '',            '$a$m$con'),
#           (abils, 2, 3,    1, '',            '$a$m$int'),
#           (abils, 2, 4,    1, '',            '$a$m$wis'),
#           (abils, 2, 5,    1, '',            '$a$m$cha'),
#
#           (abils, 4, 0,    1, 'Temp:',       '$a$t$str'),
#           (abils, 4, 1,    1, '',            '$a$t$dex'),
#           (abils, 4, 2,    1, '',            '$a$t$con'),
#           (abils, 4, 3,    1, '',            '$a$t$int'),
#           (abils, 4, 4,    1, '',            '$a$t$wis'),
#           (abils, 4, 5,    1, '',            '$a$t$cha'),
#
#           (abils, 6, 0,    1, 'Mod:',        '$a$M$str'),
#           (abils, 6, 1,    1, '',            '$a$M$dex'),
#           (abils, 6, 2,    1, '',            '$a$M$con'),
#           (abils, 6, 3,    1, '',            '$a$M$int'),
#           (abils, 6, 4,    1, '',            '$a$M$wis'),
#           (abils, 6, 5,    1, '',            '$a$M$cha'),
#
#           (abils, 0, 6,    1, '',            None),
#           (abils, 0, 7,    7, 'Speed:',      '$speed'),
#           (abils, 0, 8,    7, 'Carrying:',   '$carry'),
#           (abils, 0, 9,    7, 'Lifting:',    '$lifting'),
#           (abils, 0,10,    7, 'Push/Drag:',  '$push/drag'),
#
#           (abils, 0,11,    7, 'Notes:',      '$comments.abils'),
#
#           (saves, 0, 0,    1, 'Fortitude:',  '$STfort'),
#           (saves, 0, 1,    1, 'Reflex:',     '$STrefl'),
#           (saves, 0, 2,    1, 'Will:',       '$STwill'),
#
#           (saves, 2, 0,    1, '=',           '$SXfort'),
#           (saves, 2, 1,    1, '=',           '$SXrefl'),
#           (saves, 2, 2,    1, '=',           '$SXwill'),
#
#           (saves, 4, 0,    1, '@roll',       lambda: self.roll_save('fort')),
#           (saves, 4, 1,    1, '@roll',       lambda: self.roll_save('refl')),
#           (saves, 4, 2,    1, '@roll',       lambda: self.roll_save('will')),
#           (saves, 0, 3,    5, '',            None),
#           (saves, 0, 4,    5, 'Mods (line 1):','$SM0'),
#           (saves, 0, 5,    5, 'Mods (line 2):','$SM1'),
#           (saves, 0, 6,    5, '',            None),
#           (saves, 0, 7,    5, 'Notes:',      '$comments.saves'),
#
#
##
## Temporary attack bonus: [____]  Damage: [____]  Saves: [____]  Skills: [____]
##
## Melee  +1 = base+str+size+misc+[___]      Normal    -1 []     Init +3
## Ranged +5 = base+dex+size+misc+[___]      Off-hand  -1 []     =Dex +3
## CMB    +1 = base+str+size+misc+[___]      Two-hand  -1 []     +... +0
##    .    .                                 Bow/sling -1 []     +... +0
##    .    .                                                     +... +0
##    .    .
##
## Weapon Desc      Attack+[_]  Damage+[_]  Threat Crit Range Reach Wt Sz Type  ID
## Weapon Desc      Attack+[_]  Damage+[_]  Threat Crit Range Reach Wt Sz Type  ID
## Weapon Desc      Attack+[_]  Damage+[_]  Threat Crit Range Reach Wt Sz Type  ID
## Weapon Desc      Attack+[_]  Damage+[_]  Threat Crit Range Reach Wt Sz Type  ID
##
#
##
## AC    16  = ...       HP 8/16   Wounds: 5  Non-lethal: 3
## Touch 13  = ...       Heal Rate 1/day
## Flat  13  = ...       DR
## CMD   14  = ...       SR
##   .    .  = ...
##   .    .  = ...
##   .    .  = ...
##
## [] Armor      bonus type mdex chk spl spd wt  id
## [] Armor      bonus type mdex chk spl spd wt  id
## [] Armor      bonus type mdex chk spl spd wt  id
## [] Armor      bonus type mdex chk spl spd wt  id
##
#
##
## Spells
## spells[type] => spell_group (.class_code MUST BE IN CHAR)
#
##
#
#       ):
#            if label == '@roll':
#                ttk.Button(frm, style='CharFormMini.Toolbutton', image=Icons.icon_die_16, command=attr).grid(row=y, column=x)
#            else:
#                ttk.Label(frm, text=label, style='CharFormLabel.TLabel').grid(row=y, column=x, sticky=W)
#                if attr is not None:
#                    self.fields[attr] = ttk.Label(frm, style='CharFormValue.TLabel')
#                    if attr=='id' or attr[:3] == '$a$':
#                        self.fields[attr].grid(row=y, column=x+1, columnspan=span, sticky=E)
#                    else:
#                        self.fields[attr].grid(row=y, column=x+1, columnspan=span, sticky=W)
#
#        basics.columnconfigure(1, weight=2)
#        basics.columnconfigure(3, weight=2)
#        basics.columnconfigure(5, weight=2)
#
#        for f in (self.ca_f, self.ra_f, self.feat_f[0], self.feat_f[1]):
#            f.grid_columnconfigure(0, pad=1, weight=1)
#            f.grid_columnconfigure(1, pad=1, weight=0)
#            f.grid_columnconfigure(2, pad=1, weight=0)
#
#        #
#        # Inventory
#        #
#
#        i_summary = ttk.Frame(invent)
#        i_summary.pack(side=BOTTOM, pady=5)
#
#        ttk.Label(i_summary, text='Total weight:').pack(side=LEFT, padx=2)
#        self.inventory_ttl_wt = ttk.Label(i_summary, text='(calculating)')
#        self.inventory_ttl_wt.pack(side=LEFT, padx=2)
#        self.inventory_ttl_wt_warning = ttk.Label(i_summary, text='')
#        self.inventory_ttl_wt_warning.pack(side=LEFT, padx=2)
#
#        i_scroller = ttk.Scrollbar(invent)
#        i_scroller.pack(side=RIGHT, fill=Y)
#
#        self.inventory_w = ttk.Treeview(invent,
#            columns = ['Carried?', 'Location', 'Weight', 'ID'],
#            selectmode = 'none',
#            yscrollcommand = i_scroller.set,
#        )
#        i_scroller.config(command=self.inventory_w.yview)
#
#        ifont = tkFont.Font(family="Helvetica", size=10)
#        self.inventory_w.tag_configure('row0', background='#ffffff', font=ifont)
#        self.inventory_w.tag_configure('row1', background='#ccccff', font=ifont)
#        self.inventory_w.tag_configure('disabled', foreground='#888888')
#        self.inventory_w.tag_bind('item', '<Button-1>', self._inventory_item_context_menu)
#        self.inventory_w.tag_bind('qty', '<Button-1>', self._inventory_qty_context_menu)
#        for i, heading in enumerate(('Item Description', 'Carried?', 'Location', 'Weight', 'ID')):
#            self.inventory_w.heading('#{}'.format(i), text=heading)
#        for col, anchor, width in (
#            ('#1', W, 'MMMMMM'),
#            ('#2', W, 'MMMMMMMMMM'),
#            ('#3', E, 'MMMMMMM'),
#            ('#4', W, 'MMMMMMMMMM'),
#        ):
#            self.inventory_w.column(col, anchor=anchor, width=ifont.measure(width), stretch=False)
#        self.inventory_w.column('#0', stretch=True)
#        self.inventory_w.pack(side=LEFT, fill=BOTH, expand=True)
#            
#        nb.pack(expand=True, fill=BOTH)
#        self.refresh()
#
#    def refresh(self):
#        carrycap = self.char_obj.carrying_capacity_lbs()
#
#        #
#        # reset skill matrix
#        #
#        old_widgets = self.skills_f.children.values()
#        for w in old_widgets:
#            w.grid_forget()
#            w.destroy()
#
#        allocated_pts = 0
#        skp_per_level, ttl_skp_per_lev, max_ranks, skp_bonus, total_skp = self.char_obj.skill_points_per_level()
#
#        r=0
#        for skill_code in sorted(self.char_obj.skills):
#            skill = self.char_obj.skills[skill_code]
#            allocated_pts += skill.ranks
#            self.char_obj.set_class_skill(skill)
#            ttk.Label(self.skills_f, text='C' if skill.class_skill else '').grid(row=r, column=0)
#            ttk.Label(self.skills_f, text='T' if skill.trained else '').grid(row=r, column=1)
#            ttk.Label(self.skills_f, text='A' if skill.armor else '').grid(row=r, column=2)
#            ttk.Label(self.skills_f, text=skill.name).grid(row=r, column=3, sticky=W)
#            ttk.Label(self.skills_f, text='{:+}'.format(self.char_obj.skill_mod(skill))).grid(row=r, column=4, sticky=E)
#            ttk.Button(self.skills_f, style='CharFormMini.Toolbutton', image=Icons.icon_information, command=lambda s=skill_code: self.display_skill(s)).grid(row=r, column=5)
#            ttk.Button(self.skills_f, style='CharFormMini.Toolbutton', image=Icons.icon_die_16, command=lambda s=skill_code: self.roll_skill(s)).grid(row=r, column=6)
#            ttk.Label(self.skills_f, text=skill.description).grid(row=r, column=7, sticky=W)
#            if skill.ranks > max_ranks:
#                r += 1
#                Tkinter.Label(self.skills_f, text="WARNING: {} SKILL RANKS EXCEEDS MAXIMUM OF {}!".format(
#                    skill.name.upper(),
#                    max_ranks
#                ), foreground='yellow', background='red').grid(row=r, column=0, columnspan=8, sticky=W+E)
#            r += 1
#
#        if allocated_pts != total_skp:
#            r += 1
#            ttk.Label(self.skills_f, text="WARNING: YOU HAVE ALLOCATED {} SKILL POINT{} TOO {}!".format(
#                abs(allocated_pts - total_skp),
#                '' if -1 <= (allocated_pts - total_skp) <= 1 else 'S',
#                'MANY' if allocated_pts > total_skp else 'FEW',
#            ), style="CharFormWarning.TLabel").grid(row=r, column=0, columnspan=8, sticky=W+E)
#
#        #
#        # reset feat list
#        #
#        for ff in (self.ca_f, self.ra_f, self.feat_f[0], self.feat_f[1]):
#            old_widgets = ff.children.values()
#            for w in old_widgets:
#                w.grid_forget()
#                w.destroy()
#
#        vars = generate_substitution_list(
#            abilities = self.char_obj.ability,
#            classes = self.char_obj.classes,
#            deprecated = True,
#            arcane_levels = sum([cc.level for cc in self.char_obj.classes if cc.code in ('S','W')])
#        )
#
#        r=0
#        for ra in self.char_obj.race.ability_adj:
#            for line_item in ra.description_text(vars):
#                ttk.Label(self.ra_f, text=line_item).grid(row=r, column=0, sticky=W)
#                ttk.Label(self.ra_f, text='{}'.format(ra.ref)).grid(row=r, column=1, sticky=E)
#                ttk.Button(self.ra_f,
#                        style='CharFormMini.Toolbutton', 
#                        image=Icons.icon_information,
#                        command=lambda f=ra: self.display_racial_ability(f)
#                ).grid(row=r, column=2)
#                r += 1
#
#        r=0
#        for c in self.char_obj.classes:
#            if len(self.char_obj.classes) > 1:
#                ttk.Label(self.ca_f, 
#                        text='{} {}:'.format(c.name, c.level)
#                ).grid(row=r, sticky=W)
#                r += 1
#            vars = generate_substitution_list(
#                abilities = self.char_obj.ability,
#                classes = self.char_obj.classes,
#                deprecated = True,
#                caster_level = max(0, c.level + c.CL_adj),
#                arcane_levels = sum([cc.level for cc in self.char_obj.classes if cc.code in ('S','W')])
#            )
#            for ff in c.feats:
#                for line_item in ff.description_text(vars):
#                    ttk.Label(self.ca_f, text=line_item).grid(row=r, column=0, sticky=W)
#                    ttk.Label(self.ca_f, text="{}".format(ff.ref)).grid(row=r, column=1, sticky=E)
#                    ttk.Button(self.ca_f, 
#                            style="CharFormMini.Toolbutton",
#                            image=Icons.icon_information,
#                            command=lambda c=c, f=ff: self.display_class_ability(c, f)
#                    ).grid(row=r, column=2)
#                    r += 1
#
#        #
#        # General Feats
#        #
#        vars = generate_substitution_list(
#            abilities=self.char_obj.ability,
#            classes=self.char_obj.classes,
#            deprecated=True,
#            arcane_levels=sum([cc.level for cc in self.char_obj.classes if cc.code in ('S','W')])
#        )
#        r=[0,0]
#        c=0
#        for ff in self.char_obj.feats:
#            if ff is not None:
#                for line_item in ff.description_text(vars):
#                    ttk.Label(self.feat_f[c], text=line_item).grid(row=r[c], column=0, sticky=W)
#                    ttk.Label(self.feat_f[c], text='{}'.format(ff.ref)).grid(row=r[c], column=1, sticky=E)
#                    ttk.Button(self.feat_f[c],
#                        style="CharFormMini.Toolbutton",
#                        image=Icons.icon_information,
#                        command=lambda f=ff: self.display_feat(f)
#                    ).grid(row=r[c], column=2)
#                    r[c] += 1
#            else:
#                ttk.Label(self.feat_f[c], text='').grid(row=r[c])
#                r[c] += 1
#            c = (c + 1) % 2
#        #
#        # various data fields
#        #
#        for k,f in self.fields.iteritems():
#            if k[0] == '$':
#                if k == '$alignment':
#                    f['text'] = self.char_obj.alignment.name
#
#                elif k == '$carry':
#                    f['text'] = 'Light: {0:,}-{1:,}#, Medium: {2:,}-{3:,}#, Heavy: {4:,}-{5:,}#'.format(
#                            0, carrycap[0], 
#                            carrycap[0]+1, carrycap[1], 
#                            carrycap[1]+1, carrycap[2]
#                    )
#
#                elif k == '$classes':
#                    f['text'] = '/'.join([c.name for c in self.char_obj.classes])
#
#                elif k == '$comments':
#                    for kk, sec in (
#                            ('$comments',       'title'),
#                            ('$comments.abils', 'str'),
#                            ('$comments.saves', 'save'),
#                    ):
#                        ff = self.fields[kk]
#                        if sec in self.char_obj.comment_blocks:
#                            ff['text'] = '\n'.join(self.char_obj.comment_blocks[sec])
#                        else:
#                            ff['text'] = ''
#
#                elif k == '$comments.abils': pass
#                elif k == '$comments.saves': pass
#
#                elif k == '$favored':
#                    f['text'] = self.char_obj.classes[0].name   # XXX
#
#                elif k == '$HD':
#                    f['text'] = '/'.join([c.hd_type for c in self.char_obj.classes])
#
#                elif k == '$height':
#                    ht_in = round(self.char_obj.ht / 2.54)
#                    ht_ft = ht_in // 12
#                    ht_in -= ht_ft * 12
#                    f['text'] = '''{:.0f}' {:.0f}"'''.format(ht_ft, ht_in)
#
#                elif k == '$levels':
#                    f['text'] = '/'.join([str(c.level) for c in self.char_obj.classes])
#
#                elif k == '$lifting':
#                    f['text'] = '{:,}#'.format(carrycap[3])
#
#                elif k == '$name':
#                    if self.char_obj.nickname:
#                        f['text'] = '{} ("{}")'.format(self.char_obj.name, self.char_obj.nickname)
#                    else:
#                        f['text'] = self.char_obj.name
#
#                elif k == '$push/drag':
#                    f['text'] = '{:,}#'.format(carrycap[4])
#
#                elif k == '$race':
#                    f['text'] = self.char_obj.race.name
#
#                elif k == '$sex':
#                    f['text'] = 'Male' if self.char_obj.sex_code == 'M' else\
#                                'Female' if self.char_obj.sex_code == 'F' else 'Unknown'
#
#                elif k == '$size':
#                    f['text'] = self.char_obj.race.size_code()
#
#                elif k == '$speed':
#                    f['text'] = "{}' normally, {}' in armor or loaded".format(
#                            self.char_obj.race.speed[0], 
#                            self.char_obj.race.speed[1]
#                    ) 
#
#                elif k == '$SM0':
#                    f['text'] = self.char_obj.save_mods[0] if len(self.char_obj.save_mods) > 0 else ''
#                elif k == '$SM1':
#                    f['text'] = self.char_obj.save_mods[1] if len(self.char_obj.save_mods) > 1 else ''
#                elif k[:3] == '$ST':
#                    f['text'] = "{:+}".format(self.char_obj.saving_throw(k[3:]))
#
#                elif k[:3] == '$SX':
#                    details = self.char_obj.saving_throw_details(k[3:])
#                    f['text'] = '{:+} (class) {:+} ({})'.format(
#                            sum(details[0]),
#                            details[1][1],
#                            details[1][0]
#                    )
#                    if details[2] is not None:
#                        f['text'] += ' {:+} (magic)'.format(details[2])
#                    if details[3] is not None:
#                        f['text'] += ' {:+} (race)'.format(details[3])
#                    if details[4] is not None:
#                        f['text'] += ' {:+} (misc.)'.format(details[4])
#
#                elif k == '$weight':
#                    f['text'] = '{:.0f}#'.format(self.char_obj.wt * 0.0022)
#                elif k[:3] == '$a$':
#                    if k[3:5] == 'b$': f['text'] = str(self.char_obj.ability[k[5:]].base)
#                    if k[3:5] == 'm$': f['text'] = '{:+}'.format(self.char_obj.ability[k[5:]].mod(of=self.char_obj.ability[k[5:]].base))
#                    if k[3:5] == 't$': f['text'] = '' if self.char_obj.ability[k[5:]].temp is None else str(self.char_obj.ability[k[5:]].temp)
#                    if k[3:5] == 'M$': f['text'] = '' if self.char_obj.ability[k[5:]].temp is None else '{:+}'.format(self.char_obj.ability[k[5:]].mod())
#            elif k == 'xp':
#                f['text'] = '{:,}'.format(self.char_obj.xp)
#            else:
#                f['text'] = self.char_obj.__getattribute__(k)
#
#        #
#        # rebuild inventory list
#        #
#        def _tcl_false(v):
#            "a false property in a Tcl object"
#            if v is None or not v: return True
#            s = str(v).lower()
#            if s == 'false' or s == '0' or s == '': return True
#            return False
#
#        old_ilist = self.inventory_w.get_children()
#        if old_ilist:
#            self.char_obj.inventory_closed_IDs = set([id for id in old_ilist if _tcl_false(self.inventory_w.item(id, option='open'))])
#            self.inventory_w.delete(*old_ilist)
#
#        row=0
#        for i, item in enumerate(self.char_obj.inventory):
#            if item.id is None or item.id.strip()=='':
#                item.id = self.assign_item_id(i)
#
#            self.inventory_w.insert('', 1000000, iid=item.id,
#                text=item.name,
#                values=['Yes' if item.carried else 'No',item.location,str_g2lb(item.current_wt()),item.id],
#                tags=['item', 'row{}'.format(row%2)],
#                open=item.id not in self.char_obj.inventory_closed_IDs,
#                image=Icons.icon_box,
#            )
#
#            if item.maxqty is not None:
#                self.inventory_w.insert(item.id, 10000000, iid='Q$'+item.id,
#                    text='Qty: {}{} out of {}'.format(
#                        item.qty if item.qty is not None else 'N/A',
#                        ' (tapped {})'.format(item.tapqty) if item.tapqty else '',
#                        item.maxqty if item.maxqty is not None else 'N/A',
#                    ),
#                    values=['[+1]','[-1]','','',],
#                    tags=['qty', 'row{}'.format(row%2)],
#                    #open=True,
#                )
#            row += 1
#
#        ttlwt = sum([i.current_wt() for i in self.char_obj.inventory])
#        self.inventory_ttl_wt['text'] = str_g2lb(ttlwt)
#        cap_l, cap_m, cap_h, maxlift, maxpush = self.char_obj.carrying_capacity_g()
#        if ttlwt > maxpush:
#            self.inventory_ttl_wt_warning['text'] = '*** EXCEEDS MAXIMUM CARRYING/LIFTING/PUSHING WEIGHT ***'
#        elif ttlwt > maxlift:
#            self.inventory_ttl_wt_warning['text'] = '*** EXCEEDS MAXIMUM CARRYING/LIFTING WEIGHT (May only push/drag) ***'
#        elif ttlwt > cap_h:
#            self.inventory_ttl_wt_warning['text'] = '*** EXCEEDS MAXIMUM CARRYING WEIGHT (May only lift overhead or push/drag) ***'
#        elif ttlwt > cap_m:
#            self.inventory_ttl_wt_warning['text'] = '*** HEAVILY LOADED (ENCUMBERED/SLOWED) ***'
#        elif ttlwt > cap_l:
#            self.inventory_ttl_wt_warning['text'] = '(Medium load)'
#        else:
#            self.inventory_ttl_wt_warning['text'] = '(Light load)'
#
#        #
#        # Spells
#        #
#        # check and rebuild here in case the character changed in a way that affects
#        # spellcasting.
#        #
#        # 
#        # For spontaneous casters:
#        # Level 0: [][][][]...   []
#        #       I: [][][][]...   []
#        #      II: [][][][]...   []
#        #
#        # For those who prepare:
#        # [clear all]
#        # Level 0: [----------------] [i] [prep]
#        #
#        # [prep] button calls up menu of all spells to assign to that slot
#        #  by Level -> alphabet if necessary -> spell
#        # click on spell name to toggle casting status
#        # omit (sp) abilities; they'll be in class ability lists
#
#        self._update_slot_state()
#        old_slist = self.spells_f.children.values()
#        for child in old_slist:
#            child.pack_forget()
#            child.destroy()
#
#        nb = ttk.Notebook(self.spells_f)
#        nb.pack(fill=BOTH, expand=True)
#        for spell_type in sorted(self.char_obj.spell_types):
#            sp = self.char_obj.spells[spell_type]
#            if sp.supplimental_type is not None:
#                continue
#
#            f = ttk.Frame(nb)
#            nb.add(f, text=sp.typename)
#
#            for c in self.char_obj.classes:
#                if sp.class_code == c.code:
#                    casting_class = c
#                    break
#            else:
#                ttk.Label(f, text="You cannot cast {} spells.".format(spell_type)).pack()
#                ttk.Label(f, text="You are not of the required class.").pack()
#                continue
#
#            score = self.char_obj.ability[casting_class.spell_ability].base 
#            DC_mod = self.char_obj.ability[casting_class.spell_ability].mod() 
#            if score < 10:
#                ttk.Label(f, text="You cannot cast {} spells due to your low {} score ({})."
#                        .format(spell_type, casting_class.spell_ability.upper(), score)).pack()
#                continue
#
#            if sp.spontaneous_casting:
#                # In this case, we draw checkboxes for the spell slots
#                # on a single frame, since we don't need to actually assign
#                # specific spells there.
#                #
#                # we keep track of these as a list of levels, with the number
#                # checked as the value
#                #
#
#                slots = self.char_obj.spell_slots[spell_type]
#                for spell_level in range(10):
#                    spd = sp.spells_per_day(spell_level, casting_class.level, score)
#                    skn = sp.spells_known(spell_level, casting_class.level, score)
#                    ttk.Label(f, text=to_roman(spell_level)).grid(row=spell_level)
#                    if spd is not None:
#                        if spd[0] < 0:
#                            ttk.Label(f, text="(at will)").grid(
#                                    row=spell_level, 
#                                    column=1, 
#                                    columnspan=9,
#                                    sticky=W,
#                            )
#                        else:
#                            while len(slots['vars'][spell_level]) < spd[0]:
#                                slots['vars'][spell_level].append(Tkinter.IntVar())
#                            while len(slots['spec_vars'][spell_level]) < spd[1]:
#                                slots['spec_vars'][spell_level].append(Tkinter.IntVar())
#
#                            for i in range(spd[0]):
#                                ttk.Checkbutton(f, 
#                                    variable=slots['vars'][spell_level][i],
#                                ).grid(row=spell_level, column=i+1)
#                                if i < slots['state'][spell_level]:
#                                    slots['vars'][spell_level][i].set(1)
#                                else:
#                                    slots['vars'][spell_level][i].set(0)
#
#                            for i in range(spd[1]):
#                                if i==0: 
#                                    ttk.Label(f, text="|").grid(row=spell_level, column=99)
#                                ttk.Checkbutton(f,
#                                    variable=slots['spec_vars'][spell_level][i],
#                                ).grid(row=spell_level, column=100+i)
#                                if i < slots['spec_state'][spell_level]:
#                                    slots['spec_vars'][spell_level][i].set(1)
#                                else:
#                                    slots['spec_vars'][spell_level][i].set(0)
#
#
#            else:
#                #
#                # for memorized spell slots, we need to record which
#                # spell goes in which slot, AND whether it's cast already
#                # AND allow for any spell to go in any slot (due to metamagic)
#                # BUT reserve special slots for domain/school spells.
#                #
#                # We create a tab for each level, and inside that we have
#                # a list of slots:
#                #
#                # __/Level 0\/I\/II\/III\/IV\/V\/VI\/VII\/VIII\/IX\_______
#                # | Spell Slots Assigned:
#                # |
#                # | [reset all] [clear all]
#                # | [] [___________] [assign] [
#                # |
#                # |_________________________________________________________
#                #
#                level_nb = ttk.Notebook(f)
#                level_nb.pack(fill=BOTH, expand=True)
#                slots = self.char_obj.spell_slots[spell_type]
#
###                for spell_level in range(10):
###                    ff = ttk.Frame(level_nb)
###                    level_nb.add(ff, text="{}{}".format(
###                        'Level ' if spell_level == 0 else '',
###                        to_roman(spell_level)
###                    ))
###
###                    spd = sp.spells_per_day(spell_level, casting_class.level, score)
###                    skn = sp.spells_known(spell_level, casting_class.level, score)
###
###                    if spd is None:
###                        ttk.Label(ff, text="You cannot cast level {} {} spells."
###                                .format(spell_level, spell_type)).pack()
###                        continue
###
###                    subs = self.char_obj.substitution_list(max(0, casting_class.level + casting_class.CL_adj))
###                    ttk.Label(ff, text="LEVEL {} {} SPELL SLOTS (DC {})".format(
###                        to_roman(spell_level), sp.type.upper(), 10 + spell_level + DC_mod
###                    )).grid(row=0, column=0, columnspan=100)
###
###                    ttk.Label(ff, text="Spell Slots:").grid(
###                            row=1,
###                            column=0,
###                            columnspan=3,
###                    )
###                    ttk.Label(ff, text="Domain/Special Slots:").grid(
###                            row=1,
###                            column=3,
###                            columnspan=3)
###
###                    if spd[0] < 0:
###                        ttk.Label(ff, text="(cast at will)").grid(
###                            row=2,
###                            column=0,
###                            columnspan=3)
###                    else:
###                        # For these, vars holds a tuple of the checkmark and spell name
###                        for idx, category in enumerate(('vars','spec_vars')):
###                            while len(slots[category][spell_level]) < spd[idx]:
###                                slots[category][spell_level].append((
###                                    Tkinter.IntVar(), Tkinter.StringVar()))
###
###                        for i in range(spd[0]):
###                            ttk.Checkbutton(ff,
###                                variable=slots['vars'][spell_level][i][0],
###                            ).grid(row=i+2, column=0)
###                            mb = ttk.Menubutton(
###                                textvariable=slots['vars'][spell_level][i][1],
###                                text='xz',
###                            )
###                            mb['menu'] = self._spell_level_menu(mb, spell_type, spell_level)
###                            mb.grid(row=i+2, column=1)
###                            slots['vars'][spell_level][i][1].set('xyzzy')
#                            # spd[1]? XXX
#                            # XXX-XXX 
#
#
#                            # spd[0] spell slots + spd[1] special slots
#                            # skn is -1 for unlimited or # of spells known
#
#        self.update()
#
#    def _spell_level_menu(self, parent, sp_type, sp_lvl):
#        "Create menu of spells of given type, with the given level on top"
#
#        m = Tkinter.Menu(parent, tearoff=False)
#        m.add_command(label='xxx')
#        m.add_command(label='xxx')
#        m.add_separator()
#        for l in range(0):
#            if l != sp_lvl:
#                m.add_cascade(label='Level '+to_roman(l))
#        return m
#
#
#    def _update_slot_state(self):
#        "pull GUI widget states into character object state"
#        for spell_type in self.char_obj.spell_types:
#            sp = self.char_obj.spells[spell_type]
#            if sp.supplimental_type is not None:
#                continue
#
#            if sp.spontaneous_casting:
#                if spell_type not in self.char_obj.spell_slots:
#                    self.char_obj.spell_slots[spell_type] = {
#                            'state':      [0] * 10,
#                            'vars':       [[] for i in range(10)],
#                            'spec_state': [0] * 10,
#                            'spec_vars':  [[] for i in range(10)],
#                    }
#                else:
#                    for spell_level in range(10):
#                        for sublist, substate in ('vars', 'state'), ('spec_vars', 'spec_state'):
#                            if self.char_obj.spell_slots[spell_type][sublist][spell_level]:
#                                self.char_obj.spell_slots[spell_type][substate][spell_level] = sum([
#                                    v.get() for v in self.char_obj.spell_slots[spell_type][sublist][spell_level]
#                                ])
#            else:
#                if spell_type not in self.char_obj.spell_slots:
#                    self.char_obj.spell_slots[spell_type] = {
#                            'state':      [[] for i in range(10)],
#                            'vars':       [[] for i in range(10)],
#                            'spec_state': [[] for i in range(10)],
#                            'spec_vars':  [[] for i in range(10)],
#                    }
#                else:
#                    for spell_level in range(10):
#                        for sublist, substate in ('vars','state'),('spec_vars','spec_state'):
#                            if self.char_obj.spell_slots[spell_type][sublist][spell_level]:
#                                self.char_obj.spell_slots[spell_type][substate][spell_level] =[
#                                    (bool(v[0].get()), v[1].get())
#                                        for v in self.char_obj.spell_slots[spell_level][sublist][spell_level]
#                                ]
#
#    def assign_item_id(self, idx):
#        taken = filter(None, [i.id.strip() if i.id is not None else None for i in self.char_obj.inventory])
#        new_id = None
#        n = 0
#        while new_id is None or new_id in taken:
#            new_id = '{}G{:03d}'.format(self.char_obj.id, n)
#            n += 1
#
#        self.char_obj.inventory[idx].id = new_id
#        return new_id
#
#    def add_inventory(self, item_type): 
#        new_item = InventoryItem(item_type)
#        self.char_obj.inventory.append(new_item)
#        self.assign_item_id(-1)
#        InventoryItemEditor(self, self.char_obj, new_item)
#
#    def edit_basic(self):               CharacterBasicInfo(self, self.char_obj)
#    def edit_abilities(self):           CharacterAbilityScores(self, self.char_obj)
#    def edit_saves(self):               CharacterSavingThrows(self, self.char_obj)
#    def edit_skills(self):              CharacterSkills(self, self.char_obj)
#    def edit_class_abilities(self):     CharacterClassAbilities(self, self.char_obj)
#    def edit_racial_abilities(self):    CharacterRacialAbilities(self, self.char_obj)
#    def edit_feat_list(self):           CharacterFeats(self, self.char_obj)
#    def page_setup(self):               PageSetup(self, self.char_obj)
#    def edit_spell_type(self, sp_type): SpellCollectionEditor(self, self.char_obj, sp_type)
#
#    def display_skill(self, skill_code):
#        Typesetting.display_skill(skill_code, char_obj=self.char_obj)
#
#    def display_class_ability(self, cls, feat):
#        Typesetting.display_class_ability(cls, feat, char_obj=self.char_obj)
#
#    def display_racial_ability(self, feat):
#        Typesetting.display_racial_ability(feat, char_obj=self.char_obj)
#
#    def display_feat(self, feat):
#        if self.feat_w is not None:
#            if self.feat_w.winfo_exists():
#                if self.feat_w.insert_feat(feat):
#                    return
#            else:
#                self.feat_w = None
#
#        Typesetting.display_feat(feat, char_obj=self.char_obj)
#
#    def _inventory_item_context_menu(self, event):
#        # Clicking on an item allows you to toggle carried flag and edit details.
#        try:
#            selection_row = selection_col = selected_obj = None
#            selection_row = self.inventory_w.identify_row(event.y)
#            selection_col = self.inventory_w.identify_column(event.x)
#            for selected_obj in self.char_obj.inventory:
#                if selected_obj.id == selection_row:
#                    break
#            else:
#                raise KeyError("Inventory item {} not found".format(selection_row))
#        except:
#            tkMessageBox.showerror("Can't find inventory item", "Internal error finding item {}@{},{}".format(
#                selected_obj, selection_row, selection_col
#            ))
#
#        if selection_col == '#1':
#            selected_obj.carried = not selected_obj.carried
#            self.refresh()
#
#        elif selection_col != '#0':
#            InventoryItemEditor(self, self.char_obj, selected_obj)
#        
#    def _inventory_qty_context_menu(self, event):
#        try:
#            selection_row = selection_col = selected_obj = None
#            selection_row = self.inventory_w.identify_row(event.y)
#            if selection_row.startswith('Q$'):
#                selection_row = selection_row[2:]
#            selection_col = self.inventory_w.identify_column(event.x)
#            for selected_obj in self.char_obj.inventory:
#                if selected_obj.id == selection_row:
#                    break
#            else:
#                raise KeyError("Inventory item {} not found".format(selection_row))
#        except:
#            tkMessageBox.showerror("Can't find inventory item", "Internal error finding item {}@{},{}".format(
#                selected_obj, selection_row, selection_col
#            ))
#
#        if selection_col == '#1':
#            selected_obj.qty = (selected_obj.qty or 0) + 1
#            if (selected_obj.maxqty or 0) < selected_obj.qty:
#                selected_obj.maxqty = selected_obj.qty
#            self.refresh()
#
#        if selection_col == '#2':
#            selected_obj.qty = max(0, (selected_obj.qty or 0) - 1)
#            if (selected_obj.tapqty or 0) > selected_obj.qty:
#                selected_obj.tapqty = selected_obj.qty
#            self.refresh()
#
#    def roll_skill(self, skill_code):
#        skill = self.char_obj.skills[skill_code]
#        d = Dice(1, 20, self.char_obj.skill_mod(skill))
#        d.roll()
#        tkMessageBox.showinfo('Skill Check',
#                'Rolled {} Skill Check: {}\n\nSuccess if DC <= {}\n\n(Rolled {} and got {})'.format(
#                    skill.name,
#                    d.value(),
#                    d.value(),
#                    d.description(),
#                    d.dieHistory
#            ),
#            parent=self.master
#        )
#
#    def roll_save(self, save_type):
#        d = Dice(1, 20, self.char_obj.saving_throw(save_type))
#        d.roll()
#        tkMessageBox.showinfo(
#            'Rolled {} Saving Throw'.format(save_type.upper()),
#            '{} Saving Throw: {}\n\n{}\n\n(Rolled {} and got {})'.format(
#                save_type.upper(),
#                d.value(),
#                'SUCCESS' if d.dieHistory[0] == 20 else
#                'FAILURE' if d.dieHistory[0] ==  1 else
#                'Success if DC <= {}'.format(d.value()),
#                d.description(),
#                d.dieHistory
#            ),
#            parent=self.master
#        )
#
#    def save_file(self):
#        if self.save_file_name is None:
#            self.save_as_file()
#        else:
#            try:
#                self._update_slot_state()
#                self.char_obj.save_file(self.save_file_name, update_instance_data=False)
#            except Exception as err:
#                tkMessageBox.showerror('Error Saving File', 'Unable to write {}: {}'.format(
#                    self.save_file_name, traceback.format_exc(0)))
#
#    def save_as_file(self):
#        if self.save_file_name is None:
#            f_dir = os.getcwd()
#            f_name= None
#        else:
#            f_dir, f_name = os.path.split(self.save_file_name)
#
#        file_name = tkFileDialog.asksaveasfilename(
#                defaultextension='.gcr',
#                filetypes=(('GMA Character Record', '*.gcr'), ('All Files', '*')),
#                initialdir=f_dir,
#                initialfile=f_name,
#                parent=self,
#                title="Save Character File"
#        )
#        if file_name is not None and file_name.strip() != '':
#            self.save_file_name = file_name.strip()
#            self.save_file()
#
#    def blank_postscript(self):
#        pass
#    def save_postscript(self):
#        if self.save_file_name is None:
#            f_dir = os.getcwd()
#            f_name = None
#        else:
#            f_dir, f_name = os.path.split(self.save_file_name)
#            f_root, f_ext = os.path.splitext(f_name)
#            f_name = f_root+'.ps'
#
#        file_name = tkFileDialog.asksaveasfilename(
#            defaultextension='.ps',
#            filetypes=(('PostScript File', '*.ps'), ('All Files', '*')),
#            initialdir=f_dir,
#            initialfile=f_name,
#            parent=self,
#            title="Generate PostScript File"
#        )
#        if file_name is not None and file_name.strip() != '':
#            try:
#                self.char_obj.ps_file(file_name.strip())
#            except Exception as err:
#                tkMessageBox.showerror('Error Generating File', 'Unable to write {}: {}'.format(
#                    file_name, traceback.format_exc(0)))
#
#    def close_window(self):
#        # XXX check for unsaved edits!
#        self.master.destroy()
#
#def valid_id(id):
#    "is id a valid id code (alphanumeric only)?"
#    return id.isalnum()
