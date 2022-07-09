# Lumos Firmware
This directory contains the firmware (PIC18 assembly) for the various
Lumos control boards.

It's been years since I've assembled this code, so it's entirely
possible that the code may need some tweaking to assemble with current
Microchip software.

Any reference to "quiz show" boards should be ignored. There was a time
I was planning to build quiz show game devices which were based on the Lumos
boards, using a variant of this firmware. However, I ended up going in a
different direction with those, basing them on Arduino microcontrollers,
although the firmware developed (in the Arduino variant of C++) for them
is protocol-compatible with Lumos, so the quiz show devices can coexist with,
and interact with, Lumos controllers on the same RS-485 network.
