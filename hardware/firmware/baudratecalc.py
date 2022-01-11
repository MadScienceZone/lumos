#!/usr/bin/python
#
# Calculate PIC18 baud rate options
#

import sys

def baudrate(baud, div, Fosc):
	"given baud rate, divisor, clock -> (SPBRG value, error)"
	X = int(((Fosc/baud)/div)-1)
	return (X, (Fosc/(div*(X+1)) - baud) / baud)

Fosc = int(sys.argv[2]) if len(sys.argv) > 2 else 40000000
baud = int(sys.argv[1]) if len(sys.argv) > 1 else 9600

print("For desired baud rate of {:,d} at Fosc={:,d}:".format(baud, Fosc))
print("BRG16 BRGH SPBRGH SPBRG Error      Actual")
for b16, bh, div in (
		(0, 0, 64),
		(0, 1, 16),
		(1, 0, 16),
		(1, 1, 4)
):
	b, e = baudrate(baud, div, Fosc)
	print("{:5d} {:4d}   {:#04x}  {:#04x} {:10.6%} {:.4f}".format(b16, bh, (b>>8)&0xff, b&0xff, e, baud+(baud*e)))

