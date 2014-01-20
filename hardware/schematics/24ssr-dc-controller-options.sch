v 20110115 2
C 40000 40000 0 0 0 title-B.sym
C 56100 49600 1 180 0 DB9-1.sym
{
T 55100 46700 5 10 0 0 180 0 1
device=DB9
T 55900 46400 5 10 1 1 180 0 1
refdes=J15
}
C 52800 50100 1 0 0 capacitor-2.sym
{
T 53000 50800 5 10 0 0 0 0 1
device=POLARIZED_CAPACITOR
T 53000 50600 5 10 1 1 0 0 1
refdes=C13
T 53000 51000 5 10 0 0 0 0 1
symversion=0.1
T 52800 50100 5 10 1 1 0 0 1
value=1uF
}
C 41400 41300 1 0 0 connector4-1.sym
{
T 43200 42200 5 10 0 0 0 0 1
device=CONNECTOR_4
T 41400 42700 5 10 1 1 0 0 1
refdes=J16
}
C 45800 42200 1 0 0 interpage_to-1.sym
{
T 46100 42800 5 10 0 0 0 0 1
device=interpage_to
T 47100 42400 5 10 1 1 0 0 1
pages=TO U9, PIN 9
}
C 45800 41700 1 0 0 interpage_to-1.sym
{
T 46100 42300 5 10 0 0 0 0 1
device=interpage_to
T 47100 41900 5 10 1 1 0 0 1
pages=TO U9, PIN 7
}
C 45800 41200 1 0 0 interpage_to-1.sym
{
T 46100 41800 5 10 0 0 0 0 1
device=interpage_to
T 47100 41400 5 10 1 1 0 0 1
pages=TO U9, PIN 8
}
C 45800 40700 1 0 0 interpage_to-1.sym
{
T 46100 41300 5 10 0 0 0 0 1
device=interpage_to
T 47100 40900 5 10 1 1 0 0 1
pages=TO U9, PIN 10
}
C 43800 42700 1 0 0 resistorpack6-1.sym
{
T 43900 44100 5 10 0 0 0 0 1
device=RESISTORPACK_6
T 43900 43900 5 10 1 1 0 0 1
refdes=R59
T 44700 43900 5 10 1 1 0 0 1
value=10K
}
C 52500 43900 1 0 0 ground.sym
N 43100 42400 45800 42400 4
N 45800 41900 43500 41900 4
N 43500 41900 43500 42100 4
N 45800 41400 43300 41400 4
N 43300 41400 43300 41800 4
N 43100 42100 43500 42100 4
N 43300 41800 43100 41800 4
N 45800 40900 43100 40900 4
N 43100 40900 43100 41500 4
N 43900 42700 43900 42400 4
N 44200 42700 44200 40400 4
N 44500 42700 44500 41900 4
N 44800 42700 44800 41400 4
C 45700 44200 1 0 0 5V-plus-1.sym
N 45900 44200 45900 43800 4
N 45900 43800 45600 43800 4
T 40500 42300 9 10 1 0 0 0 1
\_INPUT D\_
T 40500 42000 9 10 1 0 0 0 1
\_INPUT C\_
T 40500 41700 9 10 1 0 0 0 1
\_INPUT B\_
T 40500 41400 9 10 1 0 0 0 1
\_INPUT A\_
C 53600 49900 1 0 0 ground.sym
N 53700 50300 54900 50300 4
N 53800 50300 53800 50200 4
N 52400 50000 52400 50500 4
N 52400 50300 52800 50300 4
C 52200 50500 1 0 0 5V-plus-1.sym
T 56200 46800 9 10 1 0 0 0 1
DCD
T 56200 47100 9 10 1 0 0 0 1
DSR
T 56200 47400 9 10 1 0 0 0 1
RxD
T 56200 47700 9 10 1 0 0 0 1
RTS
T 56200 48000 9 10 1 0 0 0 1
TxD
T 56200 48300 9 10 1 0 0 0 1
CTS
T 56200 48600 9 10 1 0 0 0 1
DTR
T 56200 48900 9 10 1 0 0 0 1
RI
T 56200 49200 9 10 1 0 0 0 1
GND
N 54900 49300 54900 50300 4
N 53600 47100 54100 47100 4
N 54100 47100 54100 46300 4
N 54100 46300 53600 46300 4
N 51000 46800 50600 46800 4
N 50600 46800 50600 44700 4
N 50600 44700 53800 44700 4
N 53800 44700 53800 47400 4
N 53800 47400 53600 47400 4
N 53600 46600 54300 46600 4
N 54300 46600 54300 44500 4
N 54300 44500 50800 44500 4
N 50800 44500 50800 46500 4
N 50800 46500 51000 46500 4
N 52200 44900 52700 44900 4
N 52700 44900 52700 44200 4
C 50500 49400 1 180 0 interpage_to-1.sym
{
T 50200 48800 5 10 0 0 180 0 1
device=interpage_to
T 49200 49200 5 10 1 1 180 0 1
pages=TO U9, PIN 25
}
C 50500 49000 1 180 0 interpage_to-1.sym
{
T 50200 48400 5 10 0 0 180 0 1
device=interpage_to
T 49200 48800 5 10 1 1 180 0 1
pages=TO U9, PIN 26
}
T 40200 43200 9 10 1 0 0 0 2
SENSOR INPUT OPTION:
Omit D9-D12, R58, R60, substitute these.
T 47600 50200 9 10 1 0 0 0 2
RS-232 COMMUNICATIONS OPTION:
Omit U10, J12, J13; substitute these instead.
T 54900 45900 9 10 1 0 0 0 1
RS-232 TO COMPUTER
T 50200 40800 9 11 1 0 0 0 2
24-CHANNEL DC SSR RELAY BOARD
(OPTIONAL MODS TO INTEGRATED CONTROLLER)
T 50200 40400 9 10 1 0 0 0 1
24ssr-dc-controller-options.sch
T 50200 40100 9 10 1 0 0 0 1
3
T 52000 40100 9 10 1 0 0 0 1
4
T 54100 40400 9 10 1 0 0 0 1
1.0.7 16-SEP-2012
T 54100 40100 9 10 1 0 0 0 1
STEVE WILLOUGHBY
C 51000 44900 1 0 0 max233-DIP.sym
{
T 51300 50700 5 10 0 0 0 0 1
device=MAX232
T 53300 49800 5 10 1 1 0 6 1
refdes=U12
T 51300 50500 5 10 0 0 0 0 1
footprint=SO20
T 51300 51500 5 10 0 0 0 0 1
symversion=1.0
}
N 50500 48800 51000 48800 4
N 51000 49200 50500 49200 4
T 49700 48700 9 10 1 0 0 0 1
RX
T 49700 49100 9 10 1 0 0 0 1
TX
N 54900 47500 54000 47500 4
N 54000 47500 54000 49200 4
N 54000 49200 53600 49200 4
N 53600 48800 54200 48800 4
N 54200 48100 54200 48800 4
N 54900 48100 54200 48100 4
N 54600 47800 54600 48400 4
N 54600 48400 54900 48400 4
N 54600 47800 54900 47800 4
N 54400 47200 54900 47200 4
N 54400 47200 54400 48700 4
N 54400 48700 54900 48700 4
N 45100 42700 45100 40900 4
C 45800 40200 1 0 0 interpage_to-1.sym
{
T 46100 40800 5 10 0 0 0 0 1
device=interpage_to
T 47100 40400 5 10 1 1 0 0 1
pages=TO S1 (REPLACES R58)
}
N 44200 40400 45800 40400 4
T 40500 50600 9 10 1 0 0 0 1
PROGRAMMING REFERENCE (I/O Port Assignments)
T 40800 49700 9 10 1 0 0 0 1
RA
T 40800 49200 9 10 1 0 0 0 1
RB
T 40800 48700 9 10 1 0 0 0 1
RC
T 40800 48200 9 10 1 0 0 0 1
RD
T 40800 47700 9 10 1 0 0 0 1
RE
T 42700 48200 9 10 1 0 0 0 1
\_7\_
T 42200 48200 9 10 1 0 0 0 1
\_6\_
T 41700 48200 9 10 1 0 0 0 1
\_5\_
T 44700 49150 9 10 1 0 0 0 1
\_4\_
T 44200 49150 9 10 1 0 0 0 1
\_3\_
T 43700 49150 9 10 1 0 0 0 1
\_2\_
T 43200 49150 9 10 1 0 0 0 1
\_1\_
T 42700 49150 9 10 1 0 0 0 1
\_0\_
L 40500 49500 45500 49500 3 0 0 0 -1 -1
L 45500 49000 40500 49000 3 0 0 0 -1 -1
L 40500 48500 45500 48500 3 0 0 0 -1 -1
L 45500 48000 40500 48000 3 0 0 0 -1 -1
L 40500 47500 45500 47500 3 0 0 0 -1 -1
L 40500 50000 45500 50000 3 0 0 0 -1 -1
L 40500 50500 40500 47500 3 0 0 0 -1 -1
L 41450 50500 41450 47500 3 0 0 0 -1 -1
L 40500 50050 45500 50050 3 0 0 0 -1 -1
L 40500 50500 45500 50500 3 0 0 0 -1 -1
L 45500 50500 45500 47500 3 0 0 0 -1 -1
L 45000 47500 45000 50500 3 0 0 0 -1 -1
L 44500 50500 44500 47500 3 0 0 0 -1 -1
L 44000 47500 44000 50500 3 0 0 0 -1 -1
L 43500 50400 43500 47600 3 0 0 0 -1 -1
L 43500 47500 43500 47600 3 0 0 0 -1 -1
L 43500 50300 43500 50500 3 0 0 0 -1 -1
L 43000 50500 43000 47500 3 0 0 0 -1 -1
L 42500 47500 42500 50500 3 0 0 0 -1 -1
L 42000 50500 42000 47500 3 0 0 0 -1 -1
L 41500 50500 41500 47500 3 0 0 0 -1 -1
L 41600 50000 41500 49900 3 0 0 0 -1 -1
L 41700 50000 41500 49800 3 0 0 0 -1 -1
L 41500 49700 41800 50000 3 0 0 0 -1 -1
L 41900 50000 41500 49600 3 0 0 0 -1 -1
L 41500 49500 42000 50000 3 0 0 0 -1 -1
L 42000 49900 41600 49500 3 0 0 0 -1 -1
L 41700 49500 42000 49800 3 0 0 0 -1 -1
L 42000 49700 41800 49500 3 0 0 0 -1 -1
L 41900 49500 42000 49600 3 0 0 0 -1 -1
L 42000 49900 42100 50000 3 0 0 0 -1 -1
L 42200 50000 42000 49800 3 0 0 0 -1 -1
L 42000 49700 42300 50000 3 0 0 0 -1 -1
L 42400 50000 42000 49600 3 0 0 0 -1 -1
L 42000 49500 42500 50000 3 0 0 0 -1 -1
L 42500 49900 42100 49500 3 0 0 0 -1 -1
L 42200 49500 42500 49800 3 0 0 0 -1 -1
L 42500 49700 42300 49500 3 0 0 0 -1 -1
L 42400 49500 42500 49600 3 0 0 0 -1 -1
L 41600 49000 41500 48900 3 0 0 0 -1 -1
L 41500 48800 41700 49000 3 0 0 0 -1 -1
L 41800 49000 41500 48700 3 0 0 0 -1 -1
L 41500 48600 41900 49000 3 0 0 0 -1 -1
L 42000 49000 41500 48500 3 0 0 0 -1 -1
L 41600 48500 42000 48900 3 0 0 0 -1 -1
L 42000 48800 41700 48500 3 0 0 0 -1 -1
L 41800 48500 42000 48700 3 0 0 0 -1 -1
L 42000 48600 41900 48500 3 0 0 0 -1 -1
L 42000 48900 42100 49000 3 0 0 0 -1 -1
L 42200 49000 42000 48800 3 0 0 0 -1 -1
L 42000 48700 42300 49000 3 0 0 0 -1 -1
L 42400 49000 42000 48600 3 0 0 0 -1 -1
L 42000 48500 42500 49000 3 0 0 0 -1 -1
L 42500 48900 42100 48500 3 0 0 0 -1 -1
L 42200 48500 42500 48800 3 0 0 0 -1 -1
L 42500 48700 42300 48500 3 0 0 0 -1 -1
L 42400 48500 42500 48600 3 0 0 0 -1 -1
L 41500 47900 41600 48000 3 0 0 0 -1 -1
L 41700 48000 41500 47800 3 0 0 0 -1 -1
L 41500 47700 41800 48000 3 0 0 0 -1 -1
L 41900 48000 41500 47600 3 0 0 0 -1 -1
L 41500 47500 42000 48000 3 0 0 0 -1 -1
L 42100 48000 41600 47500 3 0 0 0 -1 -1
L 41700 47500 42200 48000 3 0 0 0 -1 -1
L 42300 48000 41800 47500 3 0 0 0 -1 -1
L 41900 47500 42400 48000 3 0 0 0 -1 -1
L 42000 47500 42500 48000 3 0 0 0 -1 -1
L 42600 48000 42100 47500 3 0 0 0 -1 -1
L 42200 47500 42700 48000 3 0 0 0 -1 -1
L 42800 48000 42300 47500 3 0 0 0 -1 -1
L 42400 47500 42900 48000 3 0 0 0 -1 -1
L 43100 47500 43600 48000 3 0 0 0 -1 -1
L 43500 48000 43000 47500 3 0 0 0 -1 -1
L 43300 48000 42800 47500 3 0 0 0 -1 -1
L 42900 47500 43400 48000 3 0 0 0 -1 -1
L 42700 47500 43200 48000 3 0 0 0 -1 -1
L 43000 48000 42500 47500 3 0 0 0 -1 -1
L 42600 47500 43100 48000 3 0 0 0 -1 -1
L 43800 47500 44000 47700 3 0 0 0 -1 -1
L 44000 47800 43700 47500 3 0 0 0 -1 -1
L 44000 48000 43500 47500 3 0 0 0 -1 -1
L 43600 47500 44000 47900 3 0 0 0 -1 -1
L 43400 47500 43900 48000 3 0 0 0 -1 -1
L 43700 48000 43200 47500 3 0 0 0 -1 -1
L 43300 47500 43800 48000 3 0 0 0 -1 -1
L 43900 47500 44000 47600 3 0 0 0 -1 -1
L 42500 49750 43000 49750 3 0 0 0 -1 -1
T 42600 49800 9 10 1 0 0 0 1
ACT
T 45200 47550 9 10 1 0 0 0 1
\_B\_*
T 43150 49700 9 10 1 0 0 0 1
\_19\_
T 43650 49700 9 10 1 0 0 0 1
\_20\_
T 44150 49700 9 10 1 0 0 0 1
\_21\_
T 44650 49700 9 10 1 0 0 0 1
\_22\_
T 45150 49700 9 10 1 0 0 0 1
\_23\_
T 42050 49150 9 10 1 0 0 0 1
\_OPT\_*
T 41550 49150 9 10 1 0 0 0 1
\_PWR\_
T 42700 48700 9 10 1 0 0 0 1
\_9\_
T 43150 48700 9 10 1 0 0 0 1
\_10\_
T 43650 48200 9 10 1 0 0 0 1
\_11\_
T 44150 48200 9 10 1 0 0 0 1
\_12\_
T 43650 48700 9 10 1 0 0 0 1
\_15\_
T 44150 48700 9 10 1 0 0 0 1
\_16\_
T 44650 48700 9 10 1 0 0 0 1
\_17\_
T 45150 48700 9 10 1 0 0 0 1
\_18\_
T 43200 48200 9 10 1 0 0 0 1
\_8\_
T 44650 48200 9 10 1 0 0 0 1
\_13\_
T 45150 48200 9 10 1 0 0 0 1
\_14\_
L 44000 47750 45500 47750 3 0 0 0 -1 -1
T 44200 47550 9 10 1 0 0 0 1
\_A\_*
T 42700 49550 9 10 1 0 0 0 1
\_C\_*
T 44700 47550 9 10 1 0 0 0 1
\_D\_*
T 44050 47800 9 10 1 0 0 0 1
RED
T 44550 47800 9 10 1 0 0 0 1
YEL
T 45050 47800 9 10 1 0 0 0 1
GRN
T 41700 50200 9 10 1 0 0 0 1
7
T 42200 50200 9 10 1 0 0 0 1
6
T 42700 50200 9 10 1 0 0 0 1
5
T 43200 50200 9 10 1 0 0 0 1
4
T 43700 50200 9 10 1 0 0 0 1
3
T 44200 50200 9 10 1 0 0 0 1
2
T 44700 50200 9 10 1 0 0 0 1
1
T 45200 50200 9 10 1 0 0 0 1
0
T 45100 49150 9 10 1 0 0 0 1
T/\_R\_
T 45000 47300 9 10 1 0 0 0 1
*Inputs
C 45800 44400 1 0 0 max489-1.sym
{
T 47450 46700 5 10 0 0 0 0 1
device=MAX489
T 47050 44950 5 10 1 1 0 0 1
refdes=U13
T 47450 46500 5 10 0 0 0 0 1
footprint=SO14
}
C 45400 46400 1 180 0 interpage_to-1.sym
{
T 44100 46200 5 10 1 1 180 0 1
pages=TO U9, PIN 25
T 45100 45800 5 10 0 0 180 0 1
device=interpage_to
}
C 45400 45600 1 180 0 interpage_to-1.sym
{
T 44100 45400 5 10 1 1 180 0 1
pages=TO U9, PIN 26
T 45100 45000 5 10 0 0 180 0 1
device=interpage_to
}
T 44600 45300 9 10 1 0 0 0 1
RX
T 44600 46100 9 10 1 0 0 0 1
TX
C 45400 46000 1 180 0 interpage_to-1.sym
{
T 44100 45800 5 10 1 1 180 0 1
pages=TO U9, PIN 33
T 45100 45400 5 10 0 0 180 0 1
device=interpage_to
}
T 44600 45700 9 10 1 0 0 0 1
T/\_R\_
N 45400 46200 45800 46200 4
C 46400 47100 1 0 0 5V-plus-1.sym
N 46600 47100 46600 46900 4
C 46500 44400 1 0 0 ground.sym
N 46500 44800 46700 44800 4
N 46700 44700 46700 44900 4
N 46500 44800 46500 44900 4
C 47500 46000 1 0 0 interpage_to-1.sym
{
T 48700 46200 5 10 1 1 0 0 1
pages=TO J12, PIN 2
T 47800 46600 5 10 0 0 0 0 1
device=interpage_to
}
C 47500 45600 1 0 0 interpage_to-1.sym
{
T 48700 45800 5 10 1 1 0 0 1
pages=TO J12, PIN 5
T 47800 46200 5 10 0 0 0 0 1
device=interpage_to
}
C 47500 45200 1 0 0 interpage_to-1.sym
{
T 48700 45400 5 10 1 1 0 0 1
pages=TO J12, PIN 4
T 47800 45800 5 10 0 0 0 0 1
device=interpage_to
}
C 47500 46400 1 0 0 interpage_to-1.sym
{
T 48700 46600 5 10 1 1 0 0 1
pages=TO J12, PIN 1
T 47800 47000 5 10 0 0 0 0 1
device=interpage_to
}
N 47300 45400 47500 45400 4
N 47500 45800 47300 45800 4
N 47500 46200 47500 46000 4
N 47300 46400 47500 46400 4
N 47500 46400 47500 46600 4
T 48000 46500 9 10 1 0 0 0 1
Y (+)
T 48000 46100 9 10 1 0 0 0 1
Z (-)
T 48000 45700 9 10 1 0 0 0 1
A (+)
T 48000 45300 9 10 1 0 0 0 1
B (-)
N 47300 46000 47500 46000 4
T 42900 46600 9 10 1 0 0 0 2
FULL DUPLEX RS-485 OPTION:
Omit U10, substitute U13.
T 40500 50100 9 10 1 0 0 0 1
PORT
T 41400 50200 9 10 1 0 90 0 1
BIT
L 40500 50500 41450 50050 3 0 0 0 -1 -1
C 50500 41700 1 0 0 rj45-1.sym
{
T 50500 44600 5 10 0 0 0 0 1
device=RJ45
T 50500 44400 5 10 0 0 0 0 1
footprint=RJ45
}
C 51750 43000 1 0 0 resistor-1.sym
{
T 52050 43400 5 10 0 0 0 0 1
device=RESISTOR
T 53000 43100 5 10 1 1 0 0 1
value=120
}
C 51750 42600 1 0 0 resistor-1.sym
{
T 52050 43000 5 10 0 0 0 0 1
device=RESISTOR
}
N 51400 42700 51750 42700 4
N 51400 42500 52800 42500 4
N 51400 42300 53000 42300 4
N 53000 42300 53000 42900 4
N 52800 42500 52800 42700 4
N 52800 42700 52650 42700 4
T 51450 43500 9 10 1 0 0 0 1
TERMINATOR (plug into last RS-485 OUT jack in chain)
T 53000 42700 5 10 1 1 0 0 1
value=120
N 51400 42900 53000 42900 4
N 51400 43100 51750 43100 4
N 53000 43100 53000 43300 4
N 53000 43300 51400 43300 4
N 53000 43100 52650 43100 4
N 45800 45900 45600 45900 4
N 45600 45400 45600 45900 4
N 45600 45400 45800 45400 4
N 45400 45800 45600 45800 4
N 45800 45600 45400 45600 4
N 45400 45600 45400 45400 4