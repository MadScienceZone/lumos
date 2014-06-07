;-----------------------------------------------------------------------------
; I/O PORT ASSIGNMENTS
;-----------------------------------------------------------------------------
;
;          7   6   5   4   3   2   1   0
; PORT RA --- ---  A   B   C   D   X   L     QSCC
; PORT RA --- --- L2  X2  X0  L0  X1  L1     QSRC
;          <OSC>   I   I   I   I   I   I
;
;          7   6   5   4   3   2   1   0
; PORT RB AL  BL  CL  DL  FR  FG  FB  FW     QSCC
; PORT RB X1R X1G X1B L1R X2R X2G X2B X4R    QSRC
;          O   O   O   O   O   O   O   O 
;
;          7   6   5   4   3_  2   1   0
; PORT RC --- --- PS0 PS1 T/R XR  XG  XB     QSCC
;          <I/O>   O   O   O_  O   O   O
; PORT RC --- --- L4  X3  T/R X0R X0G X0B    QSRC
;          <I/O>   I   I   O   O   O   O
;
;          7   6   5   4   3   2   1   0
; PORT RD D7  D6  D5  D4  D3  D2  D1  D0     QSCC
;          O   O   O   O   O   O   O   O
; PORT RD X3R X3G X3B X4  X4G L4R X4B L3     QSRC
;          O   O   O   I   O   O   O   I
;
;          7   6   5   4   3   2   1   0
; PORT RE /////////////////// LR  LG  LY     QSCC
; PORT RE /////////////////// L0R L3R L2R    QSRC
;                              O   O   O
;      
