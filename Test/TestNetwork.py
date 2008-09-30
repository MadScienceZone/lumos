# vi:set ai sm nu ts=4 sw=4 expandtab:
from Lumos.Network import Network
from quopri        import encodestring
import sys

class TestNetwork (Network):
    """
    This is a network type for debugging purposes.  Instead of talking
    to an external device, it simply prints its commands to stdout.
    """
    def __init__(self, description='test network', **kwargs):
        self.units = {}
        self.description = description
        self.buffer = ''
        self.closed = False
        self.args = kwargs
        for key in 'port', 'baudrate', 'bits':
            if key in self.args:
                try:
                    self.args[key] = int(self.args[key])
                except:
                    pass

    def send(self, cmd):
        "Send a command string to the hardware device."
        if self.closed: raise ValueError, "Device already closed!"
        if cmd:
            self.buffer += encodestring(cmd)

    def close(self):
        """Close the network device; no further operations are
        possible for it."""
        if self.closed: raise ValueError, "Device already closed!"
        self.closed = True

    def reset(self):
        "Reset output buffer for easier testing (of isolated events)"
        self.buffer = ''

class TestParallelNetwork (TestNetwork):
    def send(self, bit):
        if   bit == 0: self.buffer += '0'
        elif bit == 1: self.buffer += '1'
        else:
            raise ValueError('Parallel Network given bogus value %s' % bit)

    def latch(self):
        self.buffer += 'X'
