# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# LUMOS NETWORK CLASS
# $Header: /usr/local/cvsroot/lumos/lib/Lumos/Network/Network.py,v 1.3 2008/12/31 00:25:19 steve Exp $
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

class DeviceTimeoutError (Exception):
    def __init__(self, read_so_far, *args, **kw):
        Exception.__init__(self, *args, **kw)
        self.read_so_far = read_so_far

class Network (object):
    """
    This class describes each network of controllers.  Each network
    driver class derived from this base class describes a type of
    communications interface and protocol for communicating with a
    set of controllers.

    For now, this is single-threaded.  Output blocks until sent
    to the devices, and input is polled for.  A future version
    of Lumos may implement threaded I/O with asynchronous data
    handling.

    This is a virtual base class from which all actual network drivers
    are derived.
    """
    
    def __init__(self, description=None):
        """
        Constructor for the Network class:
            Network([description], ...)
        
        description: A short description of what this network is 
                     responsible for.

        Derived classes will have additional keyword arguments
        appropriate for the specific kind of hardware they will
        communicate with.
        """
        self.description = self._str(description or 'Unnamed Network')
        self.units = {}

    def set_verbose(self, fileobj):
        """This class does not support this operation, so this method is
        just a place-holder.  Other Network-derived classes may define
        this method."""
        pass

    def add_unit(self, id, unit):
        "Add a new controller unit to the network."
        self.units[id] = unit

    def remove_unit(self, id):
        "Remove a controller"
        del self.units[id]

    def send(self, cmd):
        "Send a command string to the hardware device."
        raise NotImplementedError, "You MUST redefine this method in each Network class."

    def input(self, remaining_f=None, bytes=None, mode_switch=True, timeout=None):
        "Input data from the network."
        # You MAY redefine this method in each Network class.  You MUST if you want
        # it to perform input operations.
        raise NotImplementedError("This network type does not support input.")

    def transmit_mode(self):
        raise NotImplementedError("This network type does not support input.")

    def receive_mode(self):
        raise NotImplementedError("This network type does not support input.")

    def input_waiting(self):
        raise NotImplementedError("This network type does not support input.")

    def divert_output(self):
        raise NotImplementedError("This network type does not support diversion.")

    def end_divert_output(self):
        raise NotImplementedError("This network type does not support diversion.")

    def close(self):
        """Close the network device; no further operations are
        possible for it."""
        raise NotImplementedError, "You MUST redefine this method in each Network class."

    def _bool(self, v):
        "Interpret '1', 'yes', 'true', 'on' as True, '0', 'no', 'false', 'off' as False"
        if isinstance(v, str):
            if v.lower().strip() in ('1', 'yes', 'true', 'on'):
                return True
            if v.lower().strip() in ('0', 'no', 'false', 'off'):
                return False
            raise ValueError("String value {0} is not a recognized Boolean value".format(v))
        return bool(v)

    def _int(self, v): return int(v)
    def _float(self, v): return float(v)
    def _str(self, v): return str(v)

class HardwareNotAvailable (Exception): pass
class NullNetwork (Network):
    """
    This class describes a network which is not supported on this
    machine.  It allows for some testing but mostly is here to
    stand in for the real class long enough to make reasonable
    warnings to the user without crashing the entire application.
    """

    def __init__(self, description=None, nulltype='generic'):
#        Network.__init__(self, description="[Null instance of {0}]".format(description or 'network'))
        Network.__init__(self, description or 'network')
        self.type = nulltype
        self.diversion = None

    def send(self, cmd):
        if self.diversion is not None:
            self.diversion.append(cmd)
        else:
            raise HardwareNotAvailable("Cannot send to {1} network ({0}): support for that device is not found on this computer (install pyserial/pyparallel?)".format(
                self.description, self.type))

    def latch(self):
        raise HardwareNotAvailable("Cannot latch {1} network ({0}): support for that device is not found on this computer (install pyserial/pyparallel?)".format(
            self.description, self.type))

    def divert_output(self):
        if self.diversion is None:
            self.diversion = []

    def end_divert_output(self):
        if self.diversion is None:
            return ''

        output = ''.join(self.diversion)
        self.diversion = None
        return output

    def open(self):
        raise HardwareNotAvailable("Cannot open {1} network ({0}): support for that device is not found on this computer (install pyserial/pyparallel?)".format(
            self.description, self.type))

    def close(self):
        pass

    def __str__(self):
        return self.description
