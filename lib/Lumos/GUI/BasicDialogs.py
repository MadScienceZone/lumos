# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS BASIC GUI DIALOGS
# $Header: /tmp/cvsroot/lumos/lib/Lumos/GUI/BasicDialogs.py,v 1.3 2008-12-31 00:25:19 steve Exp $
#
# Lumos Light Orchestration System
# Copyright (c) 2008 by Steven L. Willoughby, Aloha,
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
import wx
import sys
import images

class UndefinedRecordID (Exception): pass

class DataTransferControl (object):
    def __init__(self, collection, recordID=None):
        self.collection = collection
        self.recordID = recordID
        self.oldRecordID = recordID

class DataTransferValidator (wx.PyValidator):
    "Base validator class for moving data from an object to/from dialog."

    def __init__(self, data, fieldID=None, classType=None, dispType=None, fmtString='%s'):
        """
        constructor arguments:
          data:      DataTransferControl object
          fieldID:   key in data.collection[data.recordID] for this field
          classType: class desired for data when stored. [str]
          dispType:  class needed by widget for display [classType]
          fmtString: display format for string fields ['%s']

        If data.recordID is None, it is assumed that we are creating
        a new record.  The field validator (likely a subclass
        of this one) should set data.recordID attribute as part
        of validating that input field to ensure that it is a
        valid destination for saving field data before our
        TransferFromWindow() method is called.

        If fieldID is None, this field contains the recordID
        itself.  

        The collection is a dictionary of objects with unique IDs.
        """

        wx.PyValidator.__init__(self)
        self.data = data
        self.fieldID = fieldID
        self.classType = classType if classType is not None else str
        self.dispType = dispType if dispType is not None else self.classType
        self.fmtString = fmtString

    def Clone(self):
        return DataTransferValidator(self.data, self.fieldID, self.classType, self.dispType, self.fmtString)

    def TransferToWindow(self):
        if self.data.recordID is not None:
            # Existing record; get the data from our storage area
            # (new records don't have data yet to populate the field)
            if self.fieldID is None:
                if self.dispType is str:
                    self.GetWindow().SetValue(self.fmtString % self.data.recordID)
                else:
                    self.GetWindow().SetValue(self.dispType(self.data.recordID))
            elif self.data.recordID in self.data.collection:
                if self.dispType is str:
                    self.GetWindow().SetValue(self.fmtString % self.data.collection[self.data.recordID].__getattribute__(self.fieldID))
                else:
                    self.GetWindow().SetValue(self.dispType(self.data.collection[self.data.recordID].__getattribute__(self.fieldID)))
        return True

    def TransferFromWindow(self):
        # It's up to the other validators to set our
        # recordID if that's being established or changed.

        if self.data.recordID is None:
            raise UndefinedRecordID('Cannot save form; no record ID defined (this is probably a bug in the application)')
            return False  #paranoid much?

        if self.data.recordID not in self.data.collection:
            self.data.collection[self.data.recordID] = self.constructNewTargetObject(self.data.recordID)

        if self.fieldID is not None:
            self.data.collection[self.data.recordID].__setattr__(self.fieldID, self.classType(self.GetWindow().GetValue()))

        # renaming from old value? 
        # we're already saving to the new key, delete the old copy
        if self.data.oldRecordID is not None \
        and self.data.oldRecordID != self.data.recordID \
        and self.data.oldRecordID in self.data.collection:
            del self.data.collection[self.data.oldRecordID]

        return True

    def constructNewTargetObject(self, id):
        raise NotImplementedError('Derived class must define object creation hook')

    def _tagFieldInvalid(self, msg):
        w = self.GetWindow()
        w.SetBackgroundColour('pink')
        w.SetFocus()
        w.Refresh()
        wx.MessageBox(msg, "Field Validation Error")
        return False

    def _tagFieldValid(self):
        w = self.GetWindow()
        w.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOW))
        w.Refresh()
        return True


class UniqueNodeValidator (DataTransferValidator):
    """
    Validate fields which belong to a unique data node in
    the application's data set (like power sources, etc.)
    where the key field can be edited but not to overlap
    another node's ID.
    """

    def __init__(self, data, fieldID=None, classType=None, dispType=None, fmtString='%s'):
        '''
        constructor arguments:
          data:      dictionary of recordID->object
          fieldID:   name of data.collection[data.recordID] attribute for this field
          classType: data field type in data dictionary
          dispType:  field type expected by widget

        If data.recordID is None, it is assumed that we are creating
        a new record.  This can be anything except another ID
        which already exists in the data.collection dictionary.

        If fieldID is None, this field contains the recordID (key)
        itself.  This can be changed (in which case the old data
        record is deleted from the dictionary and re-saved under
        the new key), but not to another key which already 
        exists in data.
        '''
        DataTransferValidator.__init__(self, data, fieldID, classType, dispType, fmtString)

    def Clone(self):
        return UniqueNodeValidator(self.data, self.fieldID, self.classType, self.dispType, self.fmtString)

    def Validate(self, container):
        w = self.GetWindow()
        v = w.GetValue()

        # key fields can't be empty or collide with other existing keys
        # if the key is new or changed, set storageKey to it for saving later
        if self.fieldID is None:
            if v == '':
                return self._tagFieldInvalid('Cannot leave name blank')

            if self.data.oldRecordID is None:
                if v in self.data.collection:
                    return self._tagFieldInvalid('There is already an item named "%s".  Please rename this one.' % v)
                self.data.recordID = v

            elif self.data.oldRecordID != v:
                if v in self.data.collection:
                    return self._tagFieldInvalid('There is already an item named "%s".  Please rename this one or leave it as "%s".' % (v, self.data.oldRecordID))
                self.data.recordID = v
        else:
            # data fields should fit the desired data types
            try:
                self.classType(v)
            except Exception, e:
                return self._tagFieldInvalid('Invalid value entered (%s)' % e)
                
        return self._tagFieldValid()

#class DictStorageDialogBox (wx.Dialog):
#    def __init__(self, title, directions, fields, record, recordID=None):
#        wx.Dialog.__init__(self, None, -1, title)
#
#        ctrl = DataTransferControl(record, recordID)
#        sizer = wx.BoxSizer(wx.VERTICAL)
#        sizer.Add(wx.StaticText(self, -1, directions), 0, wx.ALL, 5)
#        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)
#
#        fgs = wx.FlexGridSizer(3, 2, 5, 5) #XXX
#
#        for field, label, ftype, extra in fields:
#            fgs.Add(wx.StaticText(self, -1, label), 0, wx.ALIGN_RIGHT)
#            if field is None:
#                fgs.Add(wx.TextCtrl(self, validator=UniqueNodeValidator(ctrl)), 0, wx.EXPAND)
#            elif ftype == 'string':
#                fgs.Add(wx.TextCtrl(self, validator=UniqueNodeValidator(ctrl, field)), 0, wx.EXPAND)
#            elif ftype == 'float':
#                fgs.Add(wx.TextCtrl(self, validator=UniqueNodeValidator(ctrl, field, classType=float, dispType=str)), 0, wx.EXPAND)
#            elif ftype == 'checkbox':
#                fgs.Add(wx.CheckBox(self, -1, extra[0], validator=UniqueNodeValidator(ctrl, field, classType=bool)), 0, wx.EXPAND)
#            else:
#                raise NotImplementedError('Unimplemented dialog field type "%s" (This is probably an application bug)' % ftype)
#
#        fgs.AddGrowableCol(1)
#        sizer.Add(fgs, 0, wx.EXPAND | wx.ALL, 5)
#
#        okay = wx.Button(self, wx.ID_OK)
#        okay.SetDefault()
#        cancel = wx.Button(self, wx.ID_CANCEL)
#        btns = wx.StdDialogButtonSizer()
#        btns.AddButton(okay)
#        btns.AddButton(cancel)
#        btns.Realize()
#        sizer.Add(btns, 0, wx.EXPAND | wx.ALL, 5)
#
#        self.SetSizer(sizer)
#        sizer.Fit(self)

class ObjectStorageDialogBox (wx.Dialog):
    def __init__(self, title, directions, fields, record, recordID=None, validatorClass=None):
        wx.Dialog.__init__(self, None, -1, title)

        self.validatorClass = validatorClass or UniqueNodeValidator

        ctrl = DataTransferControl(record, recordID)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(wx.StaticText(self, -1, directions), 0, wx.ALL, 5)
        sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        fgs = wx.FlexGridSizer(len(fields), 2, 5, 5)

        for label, flags, field, ftype, extra in fields:
            fgs.Add(wx.StaticText(self, -1, label), 0, wx.ALIGN_RIGHT)
            if field is None:
                fgs.Add(wx.TextCtrl(self, validator=self.validatorClass(ctrl)), 0, wx.EXPAND)
            elif ftype == 'string':
                fgs.Add(wx.TextCtrl(self, validator=self.validatorClass(ctrl, field)), 0, wx.EXPAND)
            elif ftype == 'float':
                fgs.Add(wx.TextCtrl(self, validator=self.validatorClass(ctrl, field, classType=float, dispType=str)), 0, wx.EXPAND)
            elif ftype == 'checkbox':
                fgs.Add(wx.CheckBox(self, -1, extra[0], validator=self.validatorClass(ctrl, field, classType=bool)), 0, wx.EXPAND)
            else:
                raise NotImplementedError('Unimplemented dialog field type "%s" (This is probably an application bug)' % ftype)

        fgs.AddGrowableCol(1)
        sizer.Add(fgs, 0, wx.EXPAND | wx.ALL, 5)

        okay = wx.Button(self, wx.ID_OK)
        okay.SetDefault()
        cancel = wx.Button(self, wx.ID_CANCEL)
        btns = wx.StdDialogButtonSizer()
        btns.AddButton(okay)
        btns.AddButton(cancel)
        btns.Realize()
        sizer.Add(btns, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)
        sizer.Fit(self)

class ObjectDictStorageDialogBox (wx.Dialog):
    "Displays the contents of a dictionary of objects in an editible table."

    def __init__(self, title, directions, fields, itemDirections, itemFields, objDict, validatorClass=None):
        """
        Constructor for ObjectDictStorageDialogBox.  Arguments:
        title        - dialog box frame title
        directions   - explanatory paragraph at top of frame
        fields       - list of data columns for table.  This is a tuple
                       of column descriptions, where each description is
                       a tuple of:
                          column title,
                          formatting bits,
                          attribute name from object to display here or None
                          if this is the id (dict key) field itself,
                          printf-style format for displaying that attribute
        itemDirections-explanatory paragraph for editing individual objects
        itemFields   - as fields but for individual instance editor dialog.  In this
                       case the tuple for each column is:
                          field title,
                          formatting bits,
                          attribute name from object or None for id field,
                          field type name (string/float,checkbox),
                          tuple of extra parameters based on field type
                            (checkbox: checkbox's label)
        objDict      - dictionary of {id -> object_instance, ...}
        validatorClass - class to validate/transfer instances
        """
        wx.Dialog.__init__(self, None, -1, title) #, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.fields = fields
        self.objDict = objDict
        self.itemDirections = itemDirections if itemDirections is not None else directions
        self.itemFields = itemFields if itemFields is not None else self.fields
        self.validatorClass = validatorClass

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(wx.StaticText(self, -1, directions), 0, wx.ALL, 5)
        self.sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 5)

        self.list = wx.ListCtrl(self, -1, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES)
        self.sizer.Add(self.list, 10, wx.EXPAND | wx.ALL , 5)

        for idx, fdesc in enumerate(fields):
            self.list.InsertColumn(idx, fdesc[0], format=fdesc[1])
            self.list.SetColumnWidth(idx, wx.LIST_AUTOSIZE_USEHEADER)

        self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnEditItem, self.list)
        self.Bind(wx.EVT_LIST_KEY_DOWN, self.OnKeyPress, self.list)

        add  = wx.Button(self, wx.ID_ADD)
        dele = wx.Button(self, wx.ID_DELETE)
        self.Bind(wx.EVT_BUTTON, self.OnInsertItem, add)
        self.Bind(wx.EVT_BUTTON, self.OnDeleteItems, dele)

        listbtns = wx.BoxSizer(wx.HORIZONTAL)
        listbtns.Add(add)
        listbtns.Add(dele)
        self.sizer.Add(listbtns, 0, wx.EXPAND | wx.ALL, 5)

        okay = wx.Button(self, wx.ID_OK)
        okay.SetDefault()

        btns = wx.StdDialogButtonSizer()
        btns.AddButton(okay)
        btns.Realize()
        self.sizer.Add(btns, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(self.sizer)
        self.ReloadDict()
        self.sizer.Fit(self)

    def IterSelectedItems(self):
        i = self.list.GetFirstSelected()
        while i != -1:
            yield self.list.GetItem(i)
            i = self.list.GetNextSelected(i)
    
    def OnEditItem(self, event):
        "Edit the item in a dialog box."
        itemID = event.GetItem().GetText()
        obj = self.objDict[itemID]
        d = ObjectStorageDialogBox('Editing "%s"' % itemID, self.itemDirections, self.itemFields, self.objDict, itemID, self.validatorClass)
        d.ShowModal()
        d.Destroy()
        self.ReloadDict()


    def OnKeyPress(self, event):
        key = event.GetKeyCode()
        if key == 127:    # DELETE
            self.OnDeleteItems(event)
        elif key == 322:  # INSERT
            self.OnInsertItem(event)
        else:
            event.Skip()

    def OnDeleteItems(self, event):
        qty = self.list.GetSelectedItemCount()
        if qty > 0:
            if qty == 1:
                prompt = 'Are you sure you wish to delete "%s"?' % \
                    self.list.GetItem(self.list.GetFirstSelected()).GetText()
            else:
                prompt = 'Are you sure you wish to delete the %d selected items?' % qty

            confirm = wx.MessageDialog(self, prompt, "Confirm Deletion", wx.YES_NO | wx.ICON_QUESTION)
            result = confirm.ShowModal()
            confirm.Destroy()
            if result == wx.ID_YES:
                for item in self.IterSelectedItems():
                    del self.objDict[item.GetText()]
                self.ReloadDict()
        else:
            alert = wx.MessageDialog(self, "You need to select one or more list items, then press DEL to delete them.",
                'Deletion Error', wx.OK | wx.ICON_ERROR)
            alert.ShowModal()
            alert.Destroy()

    def OnInsertItem(self, event):
        d = ObjectStorageDialogBox('Creating New Item', self.itemDirections, self.itemFields, self.objDict, None, self.validatorClass)
        d.ShowModal()
        d.Destroy()
        self.ReloadDict()

    def ReloadDict(self):
        "Reload the contents of the object dictionary on the displayed list."
        self.list.DeleteAllItems()
        for objID in sorted(self.objDict):
            obj = self.objDict[objID]
            self.list.Append([fld[3] % (obj.__getattribute__(fld[2]) if fld[2] is not None else objID) for fld in self.fields])

