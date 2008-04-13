class Network (object):
    """
    This class describes each network of controllers.  Each network
    driver class derived from this base class describes a type of
    communications interface and protocol for communicating with a
    set of controllers.

    This is a virtual base class from which all actual network drivers
    are derived.
    """
    
    def __init__(self, id, description=None):
        """
        Constructor for the Network class:
            Network(ID, [description], ...)
        
        ID:          The ID tag for this network.

        description: A short description of what this network is 
                     responsible for.

        Derived classes will have additional keyword arguments
        appropriate for the specific kind of hardware they will
        communicate with.
        """
        self.id = id
        self.description = description
        if self.description is None: self.description = 'Network "%s"' % id
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
