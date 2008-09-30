# vi:set ai sm nu ts=4 sw=4 expandtab:
import parallel
from Lumos.Network import Network

class ParallelNetwork (Network):
    """
    This class describes each parallel-port network of controllers.  
    Typically this will be a parallel port on the host computer, 
    and attached to that parallel port will be one or more 
    controller devices.  Commands are sent as a sequence of
    bytes using the standard control bits (STROBE, etc).
    """
    
    def __init__(self, description=None, port=0, open_device=True):
        """
        Constructor for the ParallelNetwork class.

        description: A short description of what this network is 
                     responsible for.

        port:        The system designation for the parallel device 
                     connecting the host computer to the network.  
                     Can be system-specific like "LPT1" or 
                     "/dev/lp0", or can be a simple integer--0 
                     should be the "first" parallel port on your 
                     system, 1 the next, etc.  [0]

        open_device: Boolean: whether to actually open the parallel 
                     device upon construction.  If you don't let it
                     open here, you'll need to call the open()
                     method later.  [True]
        """
        
        Network.__init__(self, description)
        
        self.port = port

        # If the port can be a simple integer, make it so.
        try:
            self.port = int(self.port)
        except:
            pass

        self.dev = None
        if open_device:
            self.open()

    def open(self):
        self.dev = parallel.Parallel(port=self.port)
        self.dev.setDataDir(1)
        self.dev.setDataStrobe(0)

    def send(self, cmd):
        self.dev.setData(cmd)
        self.dev.setDataStrobe(1)
        self.dev.setDataStrobe(0)

    def close(self):
        self.dev.setDataDir(0)
        self.dev.close()
        self.dev = None

    def __str__(self):
        if self.description is not None: return self.description
        return "ParallelNetwork (port %s)" % self.port
