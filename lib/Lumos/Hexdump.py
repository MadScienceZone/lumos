#
# vi:set ai sm nu ts=4 sw=4 expandtab:
#
import sys

def _bin_hexdump(data: bytes, addr=0, output=sys.stdout):
    for idx in range(0, len(data), 16):
        output.write('{0:04X}:'.format(addr+idx).encode())
        for byte in range(16):
            if idx+byte < len(data):
                output.write(' {0:02X}'.format(data[idx+byte]).encode())
            else:
                output.write(b'   ')
            if byte == 7:
                output.write(b'   ')
        output.write(b'   |')
        for byte in range(16):
            if idx+byte < len(data):
                output.write((chr(data[idx+byte]) if 32 <= data[idx+byte] <= 126 else '.').encode())
            else:
                output.write(b' ')

            if byte == 7:
                output.write(b' ')
        output.write(b'|\n')

def hexdump(data, addr=0, output=sys.stdout):
    # --------------------------------------------------------------------------------
    # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|
    # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|
    # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|

    if isinstance(data, (bytes, list)):
        _bin_hexdump(data, addr, output)
        return

    for idx in range(0, len(data), 16):
        output.write('{0:04X}:'.format(addr+idx).encode())
        for byte in range(16):
            if idx+byte < len(data):
                output.write(' {0:02X}'.format(ord(data[idx+byte])).encode())
            else:
                output.write(b'   ')
            if byte == 7:
                output.write(b'   ')
        output.write(b'   |')
        for byte in range(16):
            if idx+byte < len(data):
                output.write((data[idx+byte] if ' ' <= data[idx+byte] <= '~' else '.').encode())
            else:
                output.write(b' ')

            if byte == 7:
                output.write(b' ')
                output.write(b'|\n')
