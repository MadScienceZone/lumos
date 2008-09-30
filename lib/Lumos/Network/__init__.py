# vi:set ai sm nu ts=4 sw=4 expandtab:
class Network (object):
    """
    This class describes each network of controllers.  Each network
    driver class derived from this base class describes a type of
    communications interface and protocol for communicating with a
    set of controllers.

    This is a virtual base class from which all actual network drivers
    are derived.
    """
    
    def __init__(self, description=None):
        """
        Constructor for the Network class
        description: A short description of what this network is 
                     responsible for.

        Derived classes will have additional keyword arguments
        appropriate for the specific kind of hardware they will
        communicate with.
        """
        self.description = description
        self.units = {}

    def add_unit(self, id, unit):
        "Add a new controller unit to the network."
        self.units[id] = unit

    def send(self, cmd):
        "Send a command string to the hardware device."
        raise NotImplementedError, "You MUST redefine this method in each Network class."

    def close(self):
        """Close the network device; no further operations are
        possible for it."""
        raise NotImplementedError, "You MUST redefine this method in each Network class."
