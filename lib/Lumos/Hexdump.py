#
# vi:set ai sm nu ts=4 sw=4 expandtab:
#
import sys

def _bin_hexdump(data: bytes, addr=0, output=sys.stdout):
    o = []
    for idx in range(0, len(data), 16):
        o.append('{0:04X}:'.format(addr+idx))
        for byte in range(16):
            if idx+byte < len(data):
                o.append(' {0:02X}'.format(data[idx+byte]))
            else:
                o.append('   ')
            if byte == 7:
                o.append('   ')
        o.append('   |')

        for byte in range(16):
            if idx+byte < len(data):
                o.append(chr(data[idx+byte]) if 32 <= data[idx+byte] <= 126 else '.')
            else:
                o.append(' ')

            if byte == 7:
                o.append(' ')
        o.append('|\n')

    if 'b' in output.mode:
        output.write(''.join(o).encode())
    else:
        output.write(''.join(o))

def hexdump(data, addr=0, output=sys.stdout):
    # --------------------------------------------------------------------------------
    # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|
    # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|
    # 9999: 99 99 99 99 99 99 99 99   99 99 99 99 99 99 99 99   |........ ........|

    if isinstance(data, (bytes, list)):
        _bin_hexdump(data, addr, output)
        return

    o = []
    for idx in range(0, len(data), 16):
        o.append('{0:04X}:'.format(addr+idx))
        for byte in range(16):
            if idx+byte < len(data):
                o.append(' {0:02X}'.format(ord(data[idx+byte])))
            else:
                o.append('   ')
            if byte == 7:
                o.append('   ')
        o.append('   |')
        for byte in range(16):
            if idx+byte < len(data):
                o.append(data[idx+byte] if ' ' <= data[idx+byte] <= '~' else '.')
            else:
                o.append(' ')

            if byte == 7:
                o.append(' ')
                o.append('|\n')

    if 'b' in output.mode:
        output.write(''.join(o).encode())
    else:
        output.write(''.join(o))
