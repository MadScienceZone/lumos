# vi:set ai sm nu ts=4 sw=4 expandtab:

class PowerSource (object):
    """
    This class describes each power source from which we draw power to run the
    controller loads.  The main reason we define these is so we can keep track
    of the current load we're pulling at any given time.
    """
    
    def __init__(self, id, amps=0, gfci=False):
        """
        Constructor for the PowerSource class:
            PowerSource([amps], [gfci=False])
        
        amps: The current rating AVAILABLE TO US from this power source
        (i.e., if there is anything else on that circuit, subtract its
        load from the circuit capacity first, so this number reflects the
        total number of amps that we can pull at any given time.)

        gfci: Whether or not the circuit has GFCI protection.  The default
        is False (no GFCI protection).
        """
        self.id = id

        try:
            self.amps = float(amps)
        except:
            raise ValueError, "amps must be a numeric value"

        if isinstance(gfci, bool):
            self.gfci = gfci
        else:
            raise ValueError, "gfci value must be a boolean"
