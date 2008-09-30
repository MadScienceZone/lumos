# vi:set ai sm nu ts=4 sw=4 expandtab:
import parallel
from Lumos.Network import Network

class ParallelBitNetwork (Network):
    """
    This class describes each parallel-port network of controllers.  
	Unlike ParallelNetwork, though, the interface is designed for
	bit-at-a-time devices such as the Olsen 595, Grinch, etc.

	There are two event methods provided.  send() transmits a
	single bit on pin D0, strobed via the /STROBE pin.  When
	all the bits are sent, call the latch() method to assert
	the /AUTOFEED and /STROBE lines once.  This signals the
	device to latch the shifted bits out to the output channels.
    """
    
    def __init__(self, description=None, port=0, open_device=True):
        """
        Constructor for the ParallelBitNetwork class.

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

    def send(self, bit):
        self.dev.setData(bit)
        self.dev.setDataStrobe(1)
        self.dev.setDataStrobe(0)

	def latch(self):
		raise NotImplementedError("LATCH")

    def close(self):
        self.dev.setDataDir(0)
        self.dev.close()
        self.dev = None

    def __str__(self):
        if self.description is not None: return self.description
        return "ParallelBitNetwork (port %s)" % self.port
