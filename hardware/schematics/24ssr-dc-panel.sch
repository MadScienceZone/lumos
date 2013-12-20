v 20110115 2
C 40000 40000 0 0 0 title-B.sym
C 40600 47000 1 0 0 connector5-1.sym
{
T 42400 48500 5 10 0 0 0 0 1
device=CONNECTOR_5
T 40700 48700 5 10 1 1 0 0 1
refdes=ICSP #0
}
C 43600 47200 1 0 0 switch-pushbutton-no-1.sym
{
T 45000 47200 5 10 1 1 0 0 1
refdes=OPTION
T 44000 47800 5 10 0 0 0 0 1
device=SWITCH_PUSHBUTTON_NO
}
C 43600 47800 1 0 0 switch-pushbutton-no-1.sym
{
T 45000 47800 5 10 1 1 0 0 1
refdes=RESET
T 44000 48400 5 10 0 0 0 0 1
device=SWITCH_PUSHBUTTON_NO
}
C 50500 48700 1 0 0 resistor-1.sym
{
T 50800 49100 5 10 0 0 0 0 1
device=RESISTOR
T 51400 48900 5 10 1 1 0 0 1
value=220
}
C 49600 49000 1 180 0 led-3.sym
{
T 48650 48350 5 10 0 0 180 0 1
device=LED
}
C 51800 47400 1 0 0 ground.sym
T 40300 49200 9 10 1 0 0 0 2
RETRO-FIT OF FRONT PANEL CONTROLS
ON OLDER 48-CHANNEL CONTROLLER BOARDS
C 42300 48300 1 0 0 resistor-1.sym
{
T 42600 48700 5 10 0 0 0 0 1
device=RESISTOR
T 42500 48600 5 10 0 1 0 0 1
refdes=R?
T 42600 48600 5 10 1 1 0 0 1
value=10K
}
N 42300 48100 44900 48100 4
N 42300 47800 43600 47800 4
N 42300 47200 43600 47200 4
N 44600 47200 44900 47200 4
N 44900 47200 44900 48100 4
N 44600 47800 44900 47800 4
N 43200 48400 43300 48400 4
N 43300 48400 43300 47200 4
N 42300 47500 43000 47500 4
N 43000 47500 43000 46500 4
T 43000 46200 9 10 1 0 0 0 1
\_PWR\_ OUTPUT (00-23)
C 47000 47700 1 0 0 connector4-1.sym
{
T 48800 48600 5 10 0 0 0 0 1
device=CONNECTOR_4
T 47000 49100 5 10 1 1 0 0 1
refdes=J16
}
C 49600 48400 1 180 0 led-3.sym
{
T 48650 47750 5 10 0 0 180 0 1
device=LED
}
C 50500 48700 1 180 0 led-3.sym
{
T 49550 48050 5 10 0 0 180 0 1
device=LED
}
C 50500 48100 1 180 0 led-3.sym
{
T 49550 47450 5 10 0 0 180 0 1
device=LED
}
N 48700 47900 49600 47900 4
N 49600 48500 48700 48500 4
C 50500 48400 1 0 0 resistor-1.sym
{
T 50800 48800 5 10 0 0 0 0 1
device=RESISTOR
T 51400 48600 5 10 1 1 0 0 1
value=220
}
C 50500 48100 1 0 0 resistor-1.sym
{
T 50800 48500 5 10 0 0 0 0 1
device=RESISTOR
T 51400 48300 5 10 1 1 0 0 1
value=220
}
C 50500 47800 1 0 0 resistor-1.sym
{
T 50800 48200 5 10 0 0 0 0 1
device=RESISTOR
T 51400 48000 5 10 1 1 0 0 1
value=220
}
N 49600 48800 50500 48800 4
N 50500 48200 49600 48200 4
N 51400 48800 52000 48800 4
N 52000 48800 52000 47700 4
N 51400 48500 52000 48500 4
N 51400 48200 52000 48200 4
N 51400 47900 52000 47900 4
T 46800 48700 9 10 1 0 0 0 1
\_D\_
T 46800 48400 9 10 1 0 0 0 1
\_C\_
T 46800 48100 9 10 1 0 0 0 1
\_B\_
T 46800 47800 9 10 1 0 0 0 1
\_A\_
T 52100 48700 9 10 1 0 0 0 1
STATUS (YELLOW)
T 52100 48100 9 10 1 0 0 0 1
STATUS (GREEN)
T 52100 47800 9 10 1 0 0 0 1
STATUS (RED)
T 52100 48400 9 10 1 0 0 0 1
ACTIVITY
T 46900 49500 9 10 1 0 0 0 1
EXTERNAL (FRONT PANEL) STATUS LED CONNECTIONS VIA J16
C 47000 44400 1 0 0 connector5-1.sym
{
T 48800 45900 5 10 0 0 0 0 1
device=CONNECTOR_5
T 47100 46100 5 10 1 1 0 0 1
refdes=ICSP
}
C 50000 44600 1 0 0 switch-pushbutton-no-1.sym
{
T 51400 44600 5 10 1 1 0 0 1
refdes=OPTION
T 50400 45200 5 10 0 0 0 0 1
device=SWITCH_PUSHBUTTON_NO
}
C 50000 45200 1 0 0 switch-pushbutton-no-1.sym
{
T 51400 45200 5 10 1 1 0 0 1
refdes=RESET
T 50400 45800 5 10 0 0 0 0 1
device=SWITCH_PUSHBUTTON_NO
}
N 48700 45500 51300 45500 4
N 48700 45200 50000 45200 4
N 48700 44600 50000 44600 4
N 51000 44600 51300 44600 4
N 51300 44600 51300 45500 4
N 51000 45200 51300 45200 4
T 46900 46400 9 10 1 0 0 0 1
EXTERNAL (FRONT PANEL) BUTTON CONNECTIONS VIA ICSP HEADER
T 50000 40900 9 10 1 0 0 0 2
LUMOS 24-CHANNEL DC SSR CONTROLLER EXTERNAL CONNECTIONS
AND OLDER BOARD RETRO-FIT
T 50000 40400 9 10 1 0 0 0 1
24ssr-dc-panel.sch
T 50000 40100 9 10 1 0 0 0 1
4
T 51600 40100 9 10 1 0 0 0 1
4
T 54000 40100 9 10 1 0 0 0 1
STEVE WILLOUGHBY
T 54000 40400 9 10 1 0 0 0 1
1.0.7 16-SEP-2012
C 40600 44200 1 0 0 connector5-1.sym
{
T 42400 45700 5 10 0 0 0 0 1
device=CONNECTOR_5
T 40700 45900 5 10 1 1 0 0 1
refdes=ICSP #1
}
N 42300 44700 43000 44700 4
N 43000 44000 43000 44700 4
T 43000 43700 9 10 1 0 0 0 1
\_PWR\_ OUTPUT (24-47)
N 42500 47800 42500 45000 4
N 42500 45000 42300 45000 4
C 42800 41800 1 0 0 interpage_from-1.sym
{
T 43100 42400 5 10 0 0 0 0 1
device=interpage_from
T 43300 41950 5 10 1 1 0 0 1
pages=\_SSR0
}
C 42800 41400 1 0 0 interpage_from-1.sym
{
T 43100 42000 5 10 0 0 0 0 1
device=interpage_from
T 43300 41550 5 10 1 1 0 0 1
pages=\_SSR1
}
C 42800 41000 1 0 0 interpage_from-1.sym
{
T 43100 41600 5 10 0 0 0 0 1
device=interpage_from
T 43300 41150 5 10 1 1 0 0 1
pages=\_SSR2
}
C 42800 40600 1 0 0 interpage_from-1.sym
{
T 43100 41200 5 10 0 0 0 0 1
device=interpage_from
T 43300 40750 5 10 1 1 0 0 1
pages=\_SSR3
}
C 40700 40500 1 0 0 connector5-1.sym
{
T 42500 42000 5 10 0 0 0 0 1
device=CONNECTOR_5
T 40800 42200 5 10 1 1 0 0 1
refdes=J18 LOGIC OUTPUTS
}
N 42800 42000 42400 42000 4
N 42400 42000 42400 41900 4
N 42800 41600 42400 41600 4
N 42800 41200 42400 41200 4
N 42400 41200 42400 41300 4
N 42800 41000 42400 41000 4
N 42800 40800 42800 41000 4
C 42200 40400 1 0 0 ground.sym
T 40800 42500 9 10 1 0 0 0 1
OPTIONAL LOGIC-LEVEL OUTPUT BLOCK
