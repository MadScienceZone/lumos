# vi:set ai sm nu ts=4 sw=4 expandtab:
import serial
from Lumos.Network import Network

class SerialBitNetwork (Network):
    """
    This class describes each serial network of controllers.  
	As opposed to the SerialNetwork class, this is for bit-
	at-a-time interfaces such as the X-10 CM17A "Firecracker"
	interface. 

	With an open port, sending bytes is accomplished by toggling
	the states of the serial port control lines XXX and XXX.
    """
    
    def __init__(self, description=None, port=0, open_device=True):
        """
        Constructor for the SerialBitNetwork class.

        description: A short description of what this network is 
                     responsible for.

        port:        The system designation for the serial device 
                     connecting the host computer to the network.  
                     Can be system-specific like "COM1" or 
                     "/dev/ttyS1", or can be a simple integer--0 
                     should be the "first" serial port on your 
                     system, 1 the next, etc.  [0]

        open_device: Boolean: whether to actually open the serial 
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
        self.dev = serial.Serial(port=self.port)

    def send(self, cmd):
		raise NotImplementedError("SEND")

    def close(self):
        self.dev.close()
        self.dev = None

    def __str__(self):
        if self.description is not None: return self.description
        return "SerialBitNetwork (port %s)" % self.port
