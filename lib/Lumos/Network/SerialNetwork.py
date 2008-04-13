import serial
from Network import Network

class SerialNetwork (Network):
    """
    This class describes each serial network of controllers.  
    Typically this will be a serial port on the host computer, 
    and attached to that serial port will be one or more 
    controller devices.  Commands are sent as a sequence of
    bytes sent at a particular baud rate and flow control.
    """
    
    def __init__(self, id, description=None, port=0, baudrate=9600, bits=8, parity='none', stop=1, xonxoff=False, rtscts=False):
        """
        Constructor for the Network class:
            Network(ID, [description], [port], [baudrate], [bits], [parity], [stop],
                [xonxoff], [rtscts])
        
        ID:          The ID tag for this network

        description: A short description of what this network is 
                     responsible for.

        port:        The system designation for the serial device 
                     connecting the host computer to the network.  
                     Can be system-specific like "COM1" or 
                     "/dev/ttyS1", or can be a simple integer--0 
                     should be the "first" serial port on your 
                     system, 1 the next, etc.  [0]

        baudrate:    The integer number of bits/sec this network 
                     needs to run at.  [9600]

        bits:        7 or 8; the number of data bits per byte 
                     transmitted.  [8]

        parity:      One of: 'none', 'even', 'odd'.  ['none']

        stop:        1 or 2; the number of stop bits.  [1]

        xonxoff:     Boolean; whether to use XON/XOFF flow control.
                     [False]

        rtscts:      Boolean; whether to use RTS/CTS flow control.
                     [False]
        """
        
        Network.__init__(self, id, description)
        
        self.port = port
        self.baudrate = int(baudrate)
        self.bits = int(bits)
        self.parity = parity
        self.stop = int(stop)
        self.xonxoff = bool(xonxoff)
        self.rtscts = bool(rtscts)

        if self.parity not in ('none', 'even', 'odd'):
            raise ValueError, "'%s' is not a valid parity type (network %s)" % (parity, id)
		# conform to PySerial values
		self.parity = {
			'none': 'N',
			'even': 'E',
			'odd':  'O'
		}[self.parity]

		if self.parity not in serial.PARITIES:
			raise ValueError, "IMPLEMENTATION BUG: parity %s does not match to serial parity label" % parity

        if self.bits not in serial.BYTESIZES:
            raise ValueError, "%d is not a valid number of bits per byte (network %s)" % (self.bits, id)

        if self.stop not in serial.STOPBITS:
            raise ValueError, "%d is not a valid number of stop bits (network %s)" % (self.stop, id)

		if self.baudrate not in serial.BAUDRATES:
            raise ValueError, "%d is not a valid baud rate (network %s)" % (self.baudrate, id)

        # If the port can be a simple integer, make it so.
        try:
            self.port = int(self.port)
        except:
            pass

        self.dev = serial.Serial(
			port=self.port, 
			baudrate=self.baudrate, 
			bytesize=self.bits, 
			parity=self.parity, 
			stopbits=self.stop, 
			xonxoff=self.xonxoff, 
			rtscts=self.rtscts)

    def send(self, cmd):
        raise self.dev.write(cmd)

    def close(self):
		self.dev.close()
