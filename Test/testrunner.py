#!/usr/bin/env python3
#
# LUMOS GUI TEST RUNNER
# $Header: /tmp/cvsroot/lumos/Test/testrunner,v 1.3 2008-12-31 00:13:32 steve Exp $
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
#
import sys, unittestgui
#sys.path.append('../lib')
sys.path.insert(0, '../lib')
import Test
import tkinter
import traceback
import string
tk = tkinter

class MyGUI (unittestgui.TkTestRunner):
    def __init__(self, *a, **k):
        unittestgui.TkTestRunner.__init__(self, *a, **k)
        self.SKIP_WARNINGS = []

    def notifyTestFailed(self, test, err):
        self.failCountVar.set(1 + self.failCountVar.get())
        try:
            self.errorListbox.insert(tk.END, "Failure: {0}: {1}".format(test, err[1].message[:100]))
        except:
            self.errorListbox.insert(tk.END, "Failure: {0}: {1}".format(test, str(err[1])[:100]))

        self.errorInfo.append((test, err))

    def notifyTestErrored(self, test, err):
        self.errorCountVar.set(1 + self.errorCountVar.get())
        try:
            self.errorListbox.insert(tk.END, "Error: {0}: {1}".format(test, err[1].message[:100]))
        except:
            self.errorListbox.insert(tk.END, "Error: {0}: {1}".format(test, str(err[1])[:100]))
        self.errorInfo.append((test, err))
    
    def showSelectedError(self):
        selection = self.errorListbox.curselection()
        if not selection: return
        selected = int(selection[0])
        txt = self.errorListbox.get(selected)
        window = tk.Toplevel(self.root)
        window.title(txt)
        window.protocol('WM_DELETE_WINDOW', window.quit)
        test, error = self.errorInfo[selected]
        tk.Label(window, text=str(test),
            foreground="red", justify=tk.LEFT).pack(anchor=tk.W)
        tracebackLines = traceback.format_exception(*error + (10,))
        tracebackText = '\n'.join(tracebackLines)
        tk.Label(window, text=tracebackText, justify=tk.LEFT).pack()
        tk.Button(window, text="Close",
            command=window.quit).pack(side=tk.BOTTOM)
        window.bind('<Key-Return>', lambda e, w=window: w.quit())
        window.mainloop()
        window.destroy()

    def notifyRunning(self):
        Test.reset_accumulated_warnings()
        unittestgui.TkTestRunner.notifyRunning(self)

    def notifyStopped(self):
        if Test.accumulated_warnings() != self.SKIP_WARNINGS:
           self.SKIP_WARNINGS = Test.accumulated_warnings()
           # pop-up warning

        t = sum(i.count for i in self.SKIP_WARNINGS)
        if t:
           self.errorListbox.insert(tk.END, "WARNING: {0} test{1} SKIPPED (not counted as failures); details follow:".format(t, '' if t == 1 else 's'))
           for msg in self.SKIP_WARNINGS:
               self.errorListbox.insert(tk.END, "SKIPPED {1} test{2}: {0}".format(msg.msg, msg.count, '' if msg.count==1 else 's'))

        unittestgui.TkTestRunner.notifyStopped(self)

#unittestgui.main(initialTestName='Test.suite')
root = tk.Tk()
root.title("testrunner (PyUnit)")
runner = MyGUI(root, 'Test.suite')
root.protocol('WM_DELETE_WINDOW', root.quit)
root.mainloop()
