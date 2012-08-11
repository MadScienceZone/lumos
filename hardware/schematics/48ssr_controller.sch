v 20050820 1
C 44600 71600 1 0 0 pic16F877A-1.sym
{
T 48900 80100 5 10 1 1 0 6 1
refdes=U2
}
C 41600 88300 1 0 0 bridge-1.sym
{
T 41800 89300 5 10 1 1 0 0 1
refdes=D0
}
C 38500 88300 1 0 0 fuse-1.sym
{
T 38700 88500 5 10 1 1 0 0 1
refdes=F0
T 38700 87900 5 10 1 1 0 0 1
value=0.25A
T 38500 88300 5 10 0 2 0 0 1
footprint=fuse_holder_3ag
}
C 39800 88000 1 0 0 transformer-2.sym
{
T 39800 89400 5 10 1 1 0 0 1
refdes=T0
T 39800 88000 5 10 0 0 0 0 1
footprint=transformer_mt3115
}
C 48200 89600 1 0 0 5V-plus-1.sym
C 48300 86700 1 0 0 gnd-1.sym
C 48300 89400 1 270 0 led-2.sym
{
T 48200 88900 5 10 1 1 90 0 1
refdes=D1
}
C 59000 87400 1 270 0 rj45-1.sym
{
T 60900 87400 5 10 1 1 270 0 1
refdes=J4
}
C 56400 87400 1 270 0 rj45-1.sym
{
T 58300 87400 5 10 1 1 270 0 1
refdes=J3
}
C 34100 88700 1 0 0 mains-plug-1.sym
{
T 34500 89800 5 10 1 1 0 0 1
refdes=P0
}
C 36500 88100 1 0 0 connector4-1.sym
{
T 36500 89500 5 10 1 1 0 0 1
refdes=J0
}
C 34900 87800 1 90 0 switch-spst-1.sym
{
T 34600 88100 5 10 1 1 90 0 1
refdes=S0
T 34900 87800 5 10 0 0 0 0 1
graphical=1
}
N 38200 88900 38200 88600 4
N 38200 89200 39400 89200 4
N 39400 89200 39400 89300 4
N 39400 89300 39800 89300 4
N 38200 88300 38500 88300 4
N 39400 88300 39400 88100 4
N 39400 88100 39800 88100 4
L 35500 89500 36200 89500 3 0 0 0 -1 -1
L 36200 89500 36200 89200 3 0 0 0 -1 -1
L 36200 89200 36400 89200 3 0 0 0 -1 -1
L 35500 88900 35800 88900 3 0 0 0 -1 -1
L 35800 88900 36400 88900 3 0 0 0 -1 -1
L 34900 88600 36000 88600 3 0 0 0 -1 -1
L 36000 88600 36400 88600 3 0 0 0 -1 -1
L 36400 88300 36200 88300 3 0 0 0 -1 -1
L 36200 88300 36200 87800 3 0 0 0 -1 -1
L 36200 87800 34900 87800 3 0 0 0 -1 -1
N 41300 89300 41500 89300 4
N 41500 89300 41500 89000 4
N 41500 89000 41600 89000 4
N 41300 88100 41500 88100 4
N 41500 88100 41500 88500 4
N 41500 88500 41600 88500 4
C 45000 88800 1 0 0 lm7805-1.sym
{
T 46300 89800 5 10 1 1 0 6 1
refdes=U0
}
C 47000 87800 1 90 0 capacitor-1.sym
{
T 46500 88000 5 10 1 1 90 0 1
refdes=C2
T 47000 87800 5 10 1 1 0 0 1
value=0.1uF
}
C 45000 87800 1 90 0 capacitor-1.sym
{
T 44500 88000 5 10 1 1 90 0 1
refdes=C1
T 45000 87800 5 10 1 1 0 0 1
device=0.33uF
}
C 43500 88600 1 270 0 capacitor-2.sym
{
T 43400 88000 5 10 1 1 90 0 1
refdes=C0
T 43800 87800 5 10 1 1 0 0 1
value=1800uF
}
N 42800 89000 43000 89000 4
N 43000 89000 43000 89400 4
N 43000 89400 45000 89400 4
N 44800 88700 44800 89400 4
N 42800 88500 43000 88500 4
N 43000 88500 43000 87000 4
N 45800 88800 45800 87000 4
N 46800 87800 46800 87000 4
N 46600 89400 48400 89400 4
N 46800 88700 46800 89400 4
C 48300 88300 1 270 0 resistor-1.sym
{
T 48200 87600 5 10 1 1 90 0 1
refdes=R0
T 48500 87400 5 10 1 1 0 0 1
value=220
}
N 48400 89600 48400 89400 4
N 48400 88500 48400 88300 4
N 44800 87800 44800 87000 4
N 48400 87400 48400 87000 4
T 33500 89100 9 10 1 0 0 0 1
120V AC
T 34300 88000 9 10 1 0 90 0 1
Power
C 39900 83400 1 0 0 H11AA1-1.sym
{
T 41700 85900 5 10 1 1 0 6 1
refdes=U1
}
C 38500 84800 1 90 0 resistor-1.sym
{
T 38200 85000 5 10 1 1 90 0 1
refdes=R2
T 38500 84800 5 10 1 1 0 0 1
value=15K
}
N 39900 83600 38400 83600 4
N 38400 83600 38400 84800 4
N 38400 85700 38400 89200 4
N 43700 88600 43700 89400 4
N 43700 87700 43700 87000 4
C 52800 81800 1 0 0 SN75176-1.sym
{
T 54050 81850 5 10 1 1 0 0 1
refdes=U4
}
C 44300 80000 1 0 0 5V-plus-1.sym
C 49400 70700 1 0 0 gnd-1.sym
N 44500 79600 44700 79600 4
N 44700 79200 44500 79200 4
N 44500 79200 44500 80000 4
N 49200 72400 49500 72400 4
N 49500 72400 49500 71000 4
N 49200 72000 49500 72000 4
N 42500 85300 42500 75200 4
N 42500 75200 44700 75200 4
C 42000 82700 1 0 0 gnd-1.sym
N 42100 83000 42100 84400 4
N 42100 84400 42000 84400 4
C 53100 86100 1 90 0 resistor-1.sym
{
T 52800 86300 5 10 1 1 90 0 1
refdes=R14
T 53100 86100 5 10 1 1 0 0 1
value=27K
}
C 52800 87500 1 0 0 5V-plus-1.sym
N 53000 87500 53000 87000 4
N 49200 77200 50500 77200 4
C 37000 71900 1 0 0 connector5-1.sym
{
T 37100 73600 5 10 1 1 0 0 1
refdes=J5
}
N 38700 72100 40500 72100 4
N 40500 72100 40500 72800 4
N 40500 72800 44700 72800 4
N 38700 72400 44700 72400 4
N 38700 72700 39700 72700 4
N 39700 72700 39700 78800 4
N 38700 78800 44700 78800 4
C 39100 71200 1 0 0 gnd-1.sym
C 39000 74000 1 0 0 5V-plus-1.sym
N 39200 73300 39200 74000 4
N 39200 73300 38700 73300 4
N 38700 73000 39200 73000 4
N 39200 73000 39200 71500 4
C 38900 77600 1 90 0 capacitor-1.sym
{
T 38400 77800 5 10 1 1 90 0 1
refdes=C3
T 38800 77800 5 10 1 1 0 0 1
value=0.1uF
}
C 38800 79100 1 90 0 resistor-1.sym
{
T 38500 79300 5 10 1 1 90 0 1
refdes=R3
T 38800 79100 5 10 1 1 0 0 1
value=33K
}
N 38700 78500 38700 79100 4
N 38700 80000 38700 80300 4
C 38600 77200 1 0 0 gnd-1.sym
N 38700 77600 38700 77500 4
C 38500 80300 1 0 0 5V-plus-1.sym
U 43000 78500 43000 61000 10 -1
U 43000 61000 51500 61000 10 0
U 51500 61000 51500 79700 10 -1
N 44700 78000 43200 78000 4
{
T 44100 78100 5 10 1 1 0 0 1
netname=SSR13
}
C 43200 78000 1 180 0 busripper-1.sym
N 44700 77600 43200 77600 4
{
T 44100 77700 5 10 1 1 0 0 1
netname=SSR14
}
C 43200 77600 1 180 0 busripper-1.sym
N 44700 77200 43200 77200 4
{
T 44100 77300 5 10 1 1 0 0 1
netname=SSR15
}
C 43200 77200 1 180 0 busripper-1.sym
N 44700 74800 43200 74800 4
{
T 44100 74900 5 10 1 1 0 0 1
netname=SSR16
}
C 43200 74800 1 180 0 busripper-1.sym
N 44700 74400 43200 74400 4
{
T 44100 74500 5 10 1 1 0 0 1
netname=SSR8
}
C 43200 74400 1 180 0 busripper-1.sym
N 44700 74000 43200 74000 4
{
T 44100 74100 5 10 1 1 0 0 1
netname=SSR9
}
C 43200 74000 1 180 0 busripper-1.sym
N 44700 73600 43200 73600 4
{
T 44100 73700 5 10 1 1 0 0 1
netname=SSR10
}
C 43200 73600 1 180 0 busripper-1.sym
N 44700 73200 43200 73200 4
{
T 44100 73300 5 10 1 1 0 0 1
netname=SSR11
}
C 43200 73200 1 180 0 busripper-1.sym
N 49200 79600 51300 79600 4
{
T 49300 79700 5 10 1 1 0 0 1
netname=SSR4
}
C 51300 79600 1 270 0 busripper-1.sym
N 49200 79200 51300 79200 4
{
T 49300 79300 5 10 1 1 0 0 1
netname=SSR19
}
C 51300 79200 1 270 0 busripper-1.sym
N 49200 78800 51300 78800 4
{
T 49300 78900 5 10 1 1 0 0 1
netname=SSR3
}
C 51300 78800 1 270 0 busripper-1.sym
N 49200 78400 51300 78400 4
{
T 49300 78500 5 10 1 1 0 0 1
netname=SSR2
}
C 51300 78400 1 270 0 busripper-1.sym
N 49200 78000 51300 78000 4
{
T 49300 78100 5 10 1 1 0 0 1
netname=SSR21
}
C 51300 78000 1 270 0 busripper-1.sym
N 49200 77600 51300 77600 4
{
T 49300 77700 5 10 1 1 0 0 1
netname=SSR20
}
C 51300 77600 1 270 0 busripper-1.sym
N 49200 76400 51300 76400 4
{
T 49400 76500 5 10 1 1 0 0 1
netname=SSR1
}
C 51300 76400 1 270 0 busripper-1.sym
N 49200 76000 51300 76000 4
{
T 49400 76100 5 10 1 1 0 0 1
netname=SSR0
}
C 51300 76000 1 270 0 busripper-1.sym
N 49200 75600 51300 75600 4
{
T 49400 75700 5 10 1 1 0 0 1
netname=SSR23
}
C 51300 75600 1 270 0 busripper-1.sym
N 49200 75200 51300 75200 4
{
T 49400 75300 5 10 1 1 0 0 1
netname=SSR22
}
C 51300 75200 1 270 0 busripper-1.sym
N 49200 74800 51300 74800 4
{
T 49400 74900 5 10 1 1 0 0 1
netname=SSR18
}
C 51300 74800 1 270 0 busripper-1.sym
N 49200 74400 51300 74400 4
{
T 49400 74500 5 10 1 1 0 0 1
netname=SSR5
}
C 51300 74400 1 270 0 busripper-1.sym
N 49200 74000 51300 74000 4
{
T 49400 74100 5 10 1 1 0 0 1
netname=SSR17
}
C 51300 74000 1 270 0 busripper-1.sym
N 49200 73600 51300 73600 4
{
T 49400 73700 5 10 1 1 0 0 1
netname=SSR6
}
C 51300 73600 1 270 0 busripper-1.sym
N 46400 67100 43200 67100 4
{
T 44800 67200 5 10 1 1 0 0 1
netname=SSR11
}
C 43200 67100 1 180 0 busripper-1.sym
N 46400 66700 43200 66700 4
{
T 44800 66800 5 10 1 1 0 0 1
netname=SSR10
}
C 43200 66700 1 180 0 busripper-1.sym
N 46400 66300 43200 66300 4
{
T 44800 66400 5 10 1 1 0 0 1
netname=SSR9
}
C 43200 66300 1 180 0 busripper-1.sym
N 46400 65900 43200 65900 4
{
T 44800 66000 5 10 1 1 0 0 1
netname=SSR8
}
C 43200 65900 1 180 0 busripper-1.sym
N 47800 67100 51300 67100 4
{
T 49100 67200 5 10 1 1 0 0 1
netname=SSR12
}
C 51300 67100 1 270 0 busripper-1.sym
N 47800 66700 51300 66700 4
{
T 49100 66800 5 10 1 1 0 0 1
netname=SSR13
}
C 51300 66700 1 270 0 busripper-1.sym
N 47800 65900 51300 65900 4
{
T 49100 66000 5 10 1 1 0 0 1
netname=SSR15
}
C 51300 65900 1 270 0 busripper-1.sym
N 47800 66300 51300 66300 4
{
T 49100 66400 5 10 1 1 0 0 1
netname=SSR14
}
C 51300 66300 1 270 0 busripper-1.sym
N 46400 62300 43200 62300 4
{
T 44800 62400 5 10 1 1 0 0 1
netname=SSR0
}
C 43200 62300 1 180 0 busripper-1.sym
N 46400 62700 43200 62700 4
{
T 44800 62800 5 10 1 1 0 0 1
netname=SSR1
}
C 43200 62700 1 180 0 busripper-1.sym
N 46400 63100 43200 63100 4
{
T 44800 63200 5 10 1 1 0 0 1
netname=SSR2
}
C 43200 63100 1 180 0 busripper-1.sym
N 46400 63500 43200 63500 4
{
T 44800 63600 5 10 1 1 0 0 1
netname=SSR3
}
C 43200 63500 1 180 0 busripper-1.sym
N 46400 63900 43200 63900 4
{
T 44800 64000 5 10 1 1 0 0 1
netname=SSR4
}
C 43200 63900 1 180 0 busripper-1.sym
N 46400 64300 43200 64300 4
{
T 44800 64400 5 10 1 1 0 0 1
netname=SSR5
}
C 43200 64300 1 180 0 busripper-1.sym
N 46400 64700 43200 64700 4
{
T 44800 64800 5 10 1 1 0 0 1
netname=SSR6
}
C 43200 64700 1 180 0 busripper-1.sym
N 46400 65500 43200 65500 4
{
T 44800 65600 5 10 1 1 0 0 1
netname=SSR7
}
C 43200 65500 1 180 0 busripper-1.sym
N 47800 62300 51300 62300 4
{
T 49100 62400 5 10 1 1 0 0 1
netname=SSR23
}
C 51300 62300 1 270 0 busripper-1.sym
N 47800 62700 51300 62700 4
{
T 49100 62800 5 10 1 1 0 0 1
netname=SSR22
}
C 51300 62700 1 270 0 busripper-1.sym
N 47800 63100 51300 63100 4
{
T 49100 63200 5 10 1 1 0 0 1
netname=SSR21
}
C 51300 63100 1 270 0 busripper-1.sym
N 47800 63500 51300 63500 4
{
T 49100 63600 5 10 1 1 0 0 1
netname=SSR20
}
C 51300 63500 1 270 0 busripper-1.sym
N 47800 63900 51300 63900 4
{
T 49100 64000 5 10 1 1 0 0 1
netname=SSR19
}
C 51300 63900 1 270 0 busripper-1.sym
N 47800 64300 51300 64300 4
{
T 49100 64400 5 10 1 1 0 0 1
netname=SSR18
}
C 51300 64300 1 270 0 busripper-1.sym
N 47800 64700 51300 64700 4
{
T 49100 64800 5 10 1 1 0 0 1
netname=SSR17
}
C 51300 64700 1 270 0 busripper-1.sym
N 47800 65500 51300 65500 4
{
T 49100 65600 5 10 1 1 0 0 1
netname=SSR16
}
C 51300 65500 1 270 0 busripper-1.sym
C 45600 65100 1 0 0 5V-plus-1.sym
C 48300 64800 1 0 0 gnd-1.sym
N 44700 78400 43200 78400 4
{
T 44100 78500 5 10 1 1 0 0 1
netname=SSR12
}
C 43200 78400 1 180 0 busripper-1.sym
C 41900 75400 1 90 0 crystal-1.sym
{
T 41600 75600 5 10 1 1 90 0 1
refdes=X0
T 41400 75400 5 10 1 1 90 0 1
value=20MHz
}
C 40600 76000 1 0 0 capacitor-1.sym
{
T 40800 76500 5 10 1 1 0 0 1
refdes=C4
T 41200 76300 5 10 1 1 0 0 1
value=22pF
}
C 40600 75000 1 0 0 capacitor-1.sym
{
T 40800 75500 5 10 1 1 0 0 1
refdes=C5
T 41200 74900 5 10 1 1 0 0 1
value=22pF
}
C 43400 75500 1 0 0 resistor-1.sym
{
T 43600 75800 5 10 1 1 0 0 1
refdes=R5
T 44000 75800 5 10 1 1 0 0 1
value=330
}
C 40300 74500 1 0 0 gnd-1.sym
N 44700 75600 44300 75600 4
N 44700 76000 42100 76000 4
N 42100 76000 42100 76200 4
N 41800 76200 41800 76100 4
N 43400 75600 42100 75600 4
N 42100 75600 42100 75200 4
N 41800 75200 41800 75400 4
N 41500 75200 42100 75200 4
N 41500 76200 42100 76200 4
N 40600 76200 40400 76200 4
N 40400 76200 40400 74800 4
N 40600 75200 40400 75200 4
C 41500 77300 1 180 0 led-2.sym
{
T 41000 77500 5 10 1 1 180 0 1
refdes=D2
}
C 43400 71800 1 270 0 led-2.sym
{
T 43700 71000 5 10 1 1 270 0 1
refdes=D3
}
C 50900 72200 1 270 0 led-2.sym
{
T 51200 71400 5 10 1 1 270 0 1
refdes=D5
}
C 50500 72200 1 270 0 led-2.sym
{
T 50800 71400 5 10 1 1 270 0 1
refdes=D4
}
C 43500 71900 1 0 0 resistor-1.sym
{
T 43700 72200 5 10 1 1 0 0 1
refdes=R6
T 44100 72200 5 10 1 1 0 0 1
value=220
}
C 43400 76300 1 0 0 resistor-1.sym
{
T 43600 76600 5 10 1 1 0 0 1
refdes=R4
T 44000 76600 5 10 1 1 0 0 1
value=220
}
C 49400 73100 1 0 0 resistor-1.sym
{
T 49600 73300 5 10 1 1 0 0 1
refdes=R8
T 50100 73300 5 10 1 1 0 0 1
value=220
}
C 49400 72700 1 0 0 resistor-1.sym
{
T 49600 72900 5 10 1 1 0 0 1
refdes=R7
T 50100 72900 5 10 1 1 0 0 1
value=220
}
N 44700 76800 43200 76800 4
{
T 44100 76900 5 10 1 1 0 0 1
netname=SSR7
}
C 43200 76800 1 180 0 busripper-1.sym
C 40300 76800 1 0 0 gnd-1.sym
N 44700 76400 44300 76400 4
N 43400 76400 42200 76400 4
N 42200 76400 42200 77200 4
N 42200 77200 41500 77200 4
N 40400 77100 40400 77200 4
N 40400 77200 40600 77200 4
C 43400 70500 1 0 0 gnd-1.sym
N 43500 70800 43500 70900 4
N 43500 71800 43500 72000 4
N 44400 72000 44700 72000 4
C 50500 70700 1 0 0 gnd-1.sym
C 50900 70700 1 0 0 gnd-1.sym
N 49200 72800 49400 72800 4
N 49200 73200 49400 73200 4
N 50300 73200 51000 73200 4
N 51000 73200 51000 72200 4
N 50300 72800 50600 72800 4
N 50600 72800 50600 72200 4
N 50600 71300 50600 71000 4
N 51000 71300 51000 71000 4
N 50200 82500 50200 76800 4
N 50200 76800 49200 76800 4
C 53500 81400 1 0 0 gnd-1.sym
N 53600 81800 53600 81700 4
N 54300 82900 54300 83300 4
C 53400 84000 1 0 0 5V-plus-1.sym
N 53600 84000 53600 83800 4
N 52500 83100 52800 83100 4
N 57200 86500 57200 82700 4
N 57200 82700 54300 82700 4
N 54300 82300 57400 82300 4
N 57400 82300 57400 86500 4
N 60000 86500 60000 85600 4
N 60000 85600 57400 85600 4
N 59800 86500 59800 85800 4
N 59800 85800 57200 85800 4
N 56800 86500 56800 86000 4
N 59400 86000 59400 86500 4
C 56500 85500 1 0 0 gnd-1.sym
N 56600 85800 56600 86500 4
N 53000 86100 53000 85300 4
C 60500 71600 1 0 0 pic16F877A-1.sym
{
T 64800 80100 5 10 1 1 0 6 1
refdes=U3
}
C 60200 80000 1 0 0 5V-plus-1.sym
C 65300 70700 1 0 0 gnd-1.sym
N 60400 79600 60600 79600 4
N 60600 79200 60400 79200 4
N 60400 79200 60400 80000 4
N 65100 72400 65400 72400 4
N 65400 72400 65400 71000 4
N 65100 72000 65400 72000 4
C 52600 71900 1 0 0 connector5-1.sym
{
T 52700 73600 5 10 1 1 0 0 1
refdes=J6
}
N 54300 72100 56000 72100 4
N 56000 72100 56000 72800 4
N 56000 72800 60600 72800 4
N 54300 72400 60600 72400 4
N 54300 72700 55300 72700 4
N 55300 72700 55300 78800 4
N 54200 78800 60600 78800 4
C 54700 71200 1 0 0 gnd-1.sym
C 54600 74000 1 0 0 5V-plus-1.sym
N 54800 73300 54800 74000 4
N 54800 73300 54300 73300 4
N 54300 73000 54800 73000 4
N 54800 73000 54800 71500 4
C 54400 77600 1 90 0 capacitor-1.sym
{
T 53900 77800 5 10 1 1 90 0 1
refdes=C8
T 54300 77700 5 10 1 1 0 0 1
value=0.1uF
}
C 54300 79100 1 90 0 resistor-1.sym
{
T 54000 79300 5 10 1 1 90 0 1
refdes=R9
T 54300 79100 5 10 1 1 0 0 1
value=33K
}
N 54200 78500 54200 79100 4
N 54200 80000 54200 80300 4
C 54100 77200 1 0 0 gnd-1.sym
N 54200 77600 54200 77500 4
C 54000 80300 1 0 0 5V-plus-1.sym
U 58900 78500 58900 61000 10 -1
U 58900 61000 67400 61000 10 0
U 67400 61000 67400 79700 10 -1
N 60600 78000 59100 78000 4
{
T 59900 78100 5 10 1 1 0 0 1
netname=SSR37
}
C 59100 78000 1 180 0 busripper-1.sym
N 60600 77600 59100 77600 4
{
T 59900 77700 5 10 1 1 0 0 1
netname=SSR38
}
C 59100 77600 1 180 0 busripper-1.sym
N 60600 77200 59100 77200 4
{
T 59900 77300 5 10 1 1 0 0 1
netname=SSR39
}
C 59100 77200 1 180 0 busripper-1.sym
N 60600 74800 59100 74800 4
{
T 59900 74900 5 10 1 1 0 0 1
netname=SSR40
}
C 59100 74800 1 180 0 busripper-1.sym
N 60600 74400 59100 74400 4
{
T 59900 74500 5 10 1 1 0 0 1
netname=SSR32
}
C 59100 74400 1 180 0 busripper-1.sym
N 60600 74000 59100 74000 4
{
T 59900 74100 5 10 1 1 0 0 1
netname=SSR33
}
C 59100 74000 1 180 0 busripper-1.sym
N 60600 73600 59100 73600 4
{
T 59900 73700 5 10 1 1 0 0 1
netname=SSR34
}
C 59100 73600 1 180 0 busripper-1.sym
N 60600 73200 59100 73200 4
{
T 59900 73300 5 10 1 1 0 0 1
netname=SSR35
}
C 59100 73200 1 180 0 busripper-1.sym
N 65100 79600 67200 79600 4
{
T 65200 79700 5 10 1 1 0 0 1
netname=SSR28
}
C 67200 79600 1 270 0 busripper-1.sym
N 65100 79200 67200 79200 4
{
T 65200 79300 5 10 1 1 0 0 1
netname=SSR43
}
C 67200 79200 1 270 0 busripper-1.sym
N 65100 78800 67200 78800 4
{
T 65200 78900 5 10 1 1 0 0 1
netname=SSR27
}
C 67200 78800 1 270 0 busripper-1.sym
N 65100 78400 67200 78400 4
{
T 65200 78500 5 10 1 1 0 0 1
netname=SSR26
}
C 67200 78400 1 270 0 busripper-1.sym
N 65100 78000 67200 78000 4
{
T 65200 78100 5 10 1 1 0 0 1
netname=SSR45
}
C 67200 78000 1 270 0 busripper-1.sym
N 65100 77600 67200 77600 4
{
T 65200 77700 5 10 1 1 0 0 1
netname=SSR44
}
C 67200 77600 1 270 0 busripper-1.sym
N 65100 76400 67200 76400 4
{
T 65200 76500 5 10 1 1 0 0 1
netname=SSR25
}
C 67200 76400 1 270 0 busripper-1.sym
N 65100 76000 67200 76000 4
{
T 65200 76100 5 10 1 1 0 0 1
netname=SSR24
}
C 67200 76000 1 270 0 busripper-1.sym
N 65100 75600 67200 75600 4
{
T 65200 75700 5 10 1 1 0 0 1
netname=SSR47
}
C 67200 75600 1 270 0 busripper-1.sym
N 65100 75200 67200 75200 4
{
T 65200 75300 5 10 1 1 0 0 1
netname=SSR46
}
C 67200 75200 1 270 0 busripper-1.sym
N 65100 74800 67200 74800 4
{
T 65200 74900 5 10 1 1 0 0 1
netname=SSR42
}
C 67200 74800 1 270 0 busripper-1.sym
N 65100 74400 67200 74400 4
{
T 65200 74500 5 10 1 1 0 0 1
netname=SSR29
}
C 67200 74400 1 270 0 busripper-1.sym
N 65100 74000 67200 74000 4
{
T 65200 74100 5 10 1 1 0 0 1
netname=SSR41
}
C 67200 74000 1 270 0 busripper-1.sym
N 65100 73600 67200 73600 4
{
T 65200 73700 5 10 1 1 0 0 1
netname=SSR30
}
C 67200 73600 1 270 0 busripper-1.sym
N 62300 67100 59100 67100 4
{
T 60600 67200 5 10 1 1 0 0 1
netname=SSR35
}
C 59100 67100 1 180 0 busripper-1.sym
N 62300 66700 59100 66700 4
{
T 60600 66800 5 10 1 1 0 0 1
netname=SSR34
}
C 59100 66700 1 180 0 busripper-1.sym
N 62300 66300 59100 66300 4
{
T 60600 66400 5 10 1 1 0 0 1
netname=SSR33
}
C 59100 66300 1 180 0 busripper-1.sym
N 62300 65900 59100 65900 4
{
T 60600 66000 5 10 1 1 0 0 1
netname=SSR32
}
C 59100 65900 1 180 0 busripper-1.sym
N 63700 67100 67200 67100 4
{
T 65000 67200 5 10 1 1 0 0 1
netname=SSR36
}
C 67200 67100 1 270 0 busripper-1.sym
N 63700 66700 67200 66700 4
{
T 65000 66800 5 10 1 1 0 0 1
netname=SSR37
}
C 67200 66700 1 270 0 busripper-1.sym
N 63700 65900 67200 65900 4
{
T 65000 66000 5 10 1 1 0 0 1
netname=SSR39
}
C 67200 65900 1 270 0 busripper-1.sym
N 63700 66300 67200 66300 4
{
T 65000 66400 5 10 1 1 0 0 1
netname=SSR38
}
C 67200 66300 1 270 0 busripper-1.sym
N 62300 62300 59100 62300 4
{
T 60600 62400 5 10 1 1 0 0 1
netname=SSR24
}
C 59100 62300 1 180 0 busripper-1.sym
N 62300 62700 59100 62700 4
{
T 60600 62800 5 10 1 1 0 0 1
netname=SSR25
}
C 59100 62700 1 180 0 busripper-1.sym
N 62300 63100 59100 63100 4
{
T 60600 63200 5 10 1 1 0 0 1
netname=SSR26
}
C 59100 63100 1 180 0 busripper-1.sym
N 62300 63500 59100 63500 4
{
T 60600 63600 5 10 1 1 0 0 1
netname=SSR27
}
C 59100 63500 1 180 0 busripper-1.sym
N 62300 63900 59100 63900 4
{
T 60600 64000 5 10 1 1 0 0 1
netname=SSR28
}
C 59100 63900 1 180 0 busripper-1.sym
N 62300 64300 59100 64300 4
{
T 60600 64400 5 10 1 1 0 0 1
netname=SSR29
}
C 59100 64300 1 180 0 busripper-1.sym
N 62300 64700 59100 64700 4
{
T 60600 64800 5 10 1 1 0 0 1
netname=SSR30
}
C 59100 64700 1 180 0 busripper-1.sym
N 62300 65500 59100 65500 4
{
T 60600 65600 5 10 1 1 0 0 1
netname=SSR31
}
C 59100 65500 1 180 0 busripper-1.sym
N 63700 62300 67200 62300 4
{
T 65000 62400 5 10 1 1 0 0 1
netname=SSR47
}
C 67200 62300 1 270 0 busripper-1.sym
N 63700 62700 67200 62700 4
{
T 65000 62800 5 10 1 1 0 0 1
netname=SSR46
}
C 67200 62700 1 270 0 busripper-1.sym
N 63700 63100 67200 63100 4
{
T 65000 63200 5 10 1 1 0 0 1
netname=SSR45
}
C 67200 63100 1 270 0 busripper-1.sym
N 63700 63500 67200 63500 4
{
T 65000 63600 5 10 1 1 0 0 1
netname=SSR44
}
C 67200 63500 1 270 0 busripper-1.sym
N 63700 63900 67200 63900 4
{
T 65000 64000 5 10 1 1 0 0 1
netname=SSR43
}
C 67200 63900 1 270 0 busripper-1.sym
N 63700 64300 67200 64300 4
{
T 65000 64400 5 10 1 1 0 0 1
netname=SSR42
}
C 67200 64300 1 270 0 busripper-1.sym
N 63700 64700 67200 64700 4
{
T 65000 64800 5 10 1 1 0 0 1
netname=SSR41
}
C 67200 64700 1 270 0 busripper-1.sym
N 63700 65500 67200 65500 4
{
T 65000 65600 5 10 1 1 0 0 1
netname=SSR40
}
C 67200 65500 1 270 0 busripper-1.sym
C 61400 65100 1 0 0 5V-plus-1.sym
C 64300 64800 1 0 0 gnd-1.sym
N 60600 78400 59100 78400 4
{
T 59900 78500 5 10 1 1 0 0 1
netname=SSR36
}
C 59100 78400 1 180 0 busripper-1.sym
C 57400 75400 1 90 0 crystal-1.sym
{
T 57100 75600 5 10 1 1 90 0 1
refdes=X1
T 56900 75400 5 10 1 1 90 0 1
value=20MHz
}
C 56100 76000 1 0 0 capacitor-1.sym
{
T 56300 76500 5 10 1 1 0 0 1
refdes=C6
T 56000 75900 5 10 1 1 0 0 1
value=22pF
}
C 56100 75000 1 0 0 capacitor-1.sym
{
T 56300 75500 5 10 1 1 0 0 1
refdes=C7
T 56000 74900 5 10 1 1 0 0 1
value=22pF
}
C 59300 75500 1 0 0 resistor-1.sym
{
T 59500 75800 5 10 1 1 0 0 1
refdes=R10
T 59900 75800 5 10 1 1 0 0 1
value=330
}
C 55800 74500 1 0 0 gnd-1.sym
N 60600 75600 60200 75600 4
N 60600 76000 57600 76000 4
N 57600 76000 57600 76200 4
N 57300 76200 57300 76100 4
N 59300 75600 57600 75600 4
N 57600 75600 57600 75200 4
N 57300 75200 57300 75400 4
N 57000 75200 57600 75200 4
N 57000 76200 57600 76200 4
N 56100 76200 55900 76200 4
N 55900 76200 55900 74800 4
N 56100 75200 55900 75200 4
C 59300 71800 1 270 0 led-2.sym
{
T 59600 71000 5 10 1 1 270 0 1
refdes=D6
}
C 66800 72200 1 270 0 led-2.sym
{
T 67100 71400 5 10 1 1 270 0 1
refdes=D8
}
C 66400 72200 1 270 0 led-2.sym
{
T 66700 71400 5 10 1 1 270 0 1
refdes=D7
}
C 59400 71900 1 0 0 resistor-1.sym
{
T 59600 72200 5 10 1 1 0 0 1
refdes=R11
T 60000 72200 5 10 1 1 0 0 1
value=220
}
C 65300 73100 1 0 0 resistor-1.sym
{
T 65500 73400 5 10 1 1 0 0 1
refdes=R13
T 66000 73400 5 10 1 1 0 0 1
value=220
}
C 65300 72700 1 0 0 resistor-1.sym
{
T 65500 72900 5 10 1 1 0 0 1
refdes=R12
T 66000 72900 5 10 1 1 0 0 1
value=220
}
N 60600 76800 59100 76800 4
{
T 59900 76900 5 10 1 1 0 0 1
netname=SSR31
}
C 59100 76800 1 180 0 busripper-1.sym
C 59300 70500 1 0 0 gnd-1.sym
N 59400 70800 59400 70900 4
N 59400 71800 59400 72000 4
N 60300 72000 60600 72000 4
C 66400 70700 1 0 0 gnd-1.sym
C 66800 70700 1 0 0 gnd-1.sym
N 65100 72800 65300 72800 4
N 65100 73200 65300 73200 4
N 66200 73200 66900 73200 4
N 66900 73200 66900 72200 4
N 66200 72800 66500 72800 4
N 66500 72800 66500 72200 4
N 66500 71300 66500 71000 4
N 66900 71300 66900 71000 4
N 66200 76800 65100 76800 4
N 60600 76400 58500 76400 4
N 58500 76400 58500 83100 4
N 58500 83100 54300 83100 4
N 65100 77200 66500 77200 4
N 66500 77200 66500 84800 4
N 66500 84800 52500 84800 4
N 52500 83100 52500 84800 4
N 50500 77200 50500 81000 4
N 50500 81000 66200 81000 4
N 66200 81000 66200 76800 4
N 58100 75200 60600 75200 4
N 58100 75200 58100 85300 4
N 42000 85300 58100 85300 4
N 50200 82500 52800 82500 4
T 68900 57600 9 20 1 0 0 0 1
48-CHANNEL SSR CONTROLLER
T 68800 56800 9 10 1 0 0 0 1
1
T 70200 56800 9 10 1 0 0 0 1
1
T 68800 57100 9 10 1 0 0 0 1
48SSR_CONTROLLER.SCH
T 72600 57100 9 10 1 0 0 0 1
3.1       5-DEC-2006
T 72600 56800 9 10 1 0 0 0 1
STEVE WILLOUGHBY
C 42900 86700 1 0 0 gnd-1.sym
C 43600 86700 1 0 0 gnd-1.sym
C 44700 86700 1 0 0 gnd-1.sym
C 45700 86700 1 0 0 gnd-1.sym
C 46700 86700 1 0 0 gnd-1.sym
T 36800 89500 9 10 1 0 0 0 1
POWER
T 40900 89400 9 10 1 0 0 0 1
8V
T 56900 87700 9 10 1 0 0 0 1
RS-485 IN
T 59400 87700 9 10 1 0 0 0 1
RS-485 OUT
T 53000 73600 9 10 1 0 0 0 1
ICSP
T 37500 73600 9 10 1 0 0 0 1
ICSP
T 47300 67400 9 10 1 0 0 0 1
TO SSR BOARD 0
T 63300 67400 9 10 1 0 0 0 1
TO SSR BOARD 1
T 63700 71400 9 10 1 0 0 0 1
SLAVE CPU
T 47700 71400 9 10 1 0 0 0 1
MASTER CPU
T 35000 64600 9 10 1 0 0 0 1
7
T 35400 64600 9 10 1 0 0 0 1
6
T 35800 64600 9 10 1 0 0 0 1
5
T 36200 64600 9 10 1 0 0 0 1
4
T 36600 64600 9 10 1 0 0 0 1
3
T 37000 64600 9 10 1 0 0 0 1
2
T 37400 64600 9 10 1 0 0 0 1
1
T 37800 64600 9 10 1 0 0 0 1
0
T 34652 64234 9 10 1 0 0 0 1
A
T 34652 63834 9 10 1 0 0 0 1
B
T 34652 63434 9 10 1 0 0 0 1
C
T 34652 63034 9 10 1 0 0 0 1
D
T 34652 62634 9 10 1 0 0 0 1
E
T 35700 64200 9 10 1 0 0 0 1
Act
T 36200 64200 9 10 1 0 0 0 1
7
T 36600 64200 9 10 1 0 0 0 1
15
T 37000 64200 9 10 1 0 0 0 1
14
T 37400 64200 9 10 1 0 0 0 1
13
T 37800 64200 9 10 1 0 0 0 1
12
T 34900 63800 9 10 1 0 0 0 1
PD
T 35300 63800 9 10 1 0 0 0 1
PC
T 35800 63800 9 10 1 0 0 0 1
11
T 36200 63800 9 10 1 0 0 0 1
10
T 36600 63800 9 10 1 0 0 0 1
9
T 37000 63800 9 10 1 0 0 0 1
8
T 37400 63800 9 10 1 0 0 0 1
16
T 37800 63800 9 10 1 0 0 0 1
ZC
T 34900 63400 9 10 1 0 0 0 1
Rx
T 35300 63400 9 10 1 0 0 0 1
Tx
T 35800 63400 9 10 1 0 0 0 1
20
T 36200 63400 9 10 1 0 0 0 1
21
T 36600 63400 9 10 1 0 0 0 1
2
T 37000 63400 9 10 1 0 0 0 1
3
T 37800 63400 9 10 1 0 0 0 1
4
T 37400 63400 9 10 1 0 0 0 1
19
T 34900 63000 9 10 1 0 0 0 1
6
T 35300 63000 9 10 1 0 0 0 1
17
T 35800 63000 9 10 1 0 0 0 1
5
T 36200 63000 9 10 1 0 0 0 1
18
T 36600 63000 9 10 1 0 0 0 1
22
T 37000 63000 9 10 1 0 0 0 1
23
T 37400 63000 9 10 1 0 0 0 1
0
T 37800 63000 9 10 1 0 0 0 1
1
T 37000 62600 9 10 1 0 0 0 1
R
T 37400 62600 9 10 1 0 0 0 1
Y
T 37800 62600 9 10 1 0 0 0 1
G
L 34600 64800 38100 64800 3 20 0 0 -1 -1
L 38100 64800 38100 62500 3 20 0 0 -1 -1
L 38100 62500 34600 62500 3 20 0 0 -1 -1
L 34600 64800 34600 62500 3 20 0 0 -1 -1
L 34800 64800 34800 62500 3 20 0 0 -1 -1
L 35200 64800 35200 62500 3 0 0 0 -1 -1
L 35600 64800 35600 62500 3 0 0 0 -1 -1
L 36100 64800 36100 62500 3 0 0 0 -1 -1
L 36500 64800 36500 62500 3 0 0 0 -1 -1
L 36900 64800 36900 62500 3 0 0 0 -1 -1
L 37300 64800 37300 62500 3 0 0 0 -1 -1
L 37700 64800 37700 62500 3 0 0 0 -1 -1
L 34600 64500 38100 64500 3 20 0 0 -1 -1
L 34600 64100 38100 64100 3 0 0 0 -1 -1
L 34600 63700 38100 63700 3 0 0 0 -1 -1
L 34600 63300 38100 63300 3 0 0 0 -1 -1
L 34600 62800 38100 62800 3 0 0 0 -1 -1
T 40400 86800 9 10 1 0 0 0 3
DISREGARD PIN
NUMBERS ON THESE
PARTS
L 41600 87600 42000 88000 3 0 0 0 -1 -1
L 42000 88000 41900 87800 3 0 0 0 -1 -1
L 42000 88000 41800 87900 3 0 0 0 -1 -1
L 40900 87600 40600 87900 3 0 0 0 -1 -1
L 40600 87900 40700 87700 3 0 0 0 -1 -1
L 40600 87900 40800 87800 3 0 0 0 -1 -1
T 32400 58000 9 24 1 0 0 0 1
WARNING
T 32400 57300 9 12 1 0 0 0 2
THIS DESIGN IS *EXPERIMENTAL* AND IS FOR EDUCATIONAL/HOBBYIST PURPOSES ONLY.  NOT GUARANTEED TO WORK, OR EVEN TO NOT EXPLODE IN A FIREBALL ONCE PLUGGED IN :)
*** USE ENTIRELY AT YOUR OWN RISK ***
C 39700 84800 1 90 0 resistor-1.sym
{
T 39400 85000 5 10 1 1 90 0 1
refdes=R1
T 39700 84800 5 10 1 1 0 0 1
value=15K
}
N 39600 84500 39900 84500 4
N 39600 84500 39600 84800 4
N 39600 85700 39600 88100 4
T 48600 88300 9 10 1 0 0 0 2
POWER
(GREEN)
T 41200 77400 9 10 1 0 0 0 2
ACTIVE
(AMBER)
T 43900 71200 9 10 1 0 0 0 2
STATUS
(GREEN)
T 49700 71200 9 10 1 0 0 0 2
STATUS
(AMBER)
T 50700 70000 9 10 1 0 0 0 2
STATUS
(RED)
N 46400 65100 45800 65100 4
N 47800 65100 48400 65100 4
C 43600 79800 1 90 0 capacitor-1.sym
{
T 43100 80000 5 10 1 1 90 0 1
refdes=C10
T 43500 80000 5 10 1 1 0 0 1
value=0.01uF
}
C 43300 79200 1 0 0 gnd-1.sym
C 43200 81000 1 0 0 5V-plus-1.sym
N 43400 81000 43400 80700 4
N 43400 79800 43400 79500 4
C 51800 83400 1 90 0 capacitor-1.sym
{
T 51300 83600 5 10 1 1 90 0 1
refdes=C9
T 51700 83600 5 10 1 1 0 0 1
value=0.01uF
T 51800 83400 5 10 0 0 0 0 1
footprint=RCY100
}
C 51500 82800 1 0 0 gnd-1.sym
C 51400 84600 1 0 0 5V-plus-1.sym
N 51600 84600 51600 84300 4
N 51600 83400 51600 83100 4
T 59900 71100 9 10 1 0 0 0 2
STATUS
(GREEN)
T 65500 71300 9 10 1 0 0 0 2
STATUS
(AMBER)
T 66600 70100 9 10 1 0 0 0 2
STATUS
(RED)
N 61600 65100 62300 65100 4
N 64400 65100 63700 65100 4
C 67400 81000 1 90 0 capacitor-1.sym
{
T 66900 81200 5 10 1 1 90 0 1
refdes=C11
T 67300 81200 5 10 1 1 0 0 1
value=0.01uF
}
C 67100 80400 1 0 0 gnd-1.sym
C 67000 82200 1 0 0 5V-plus-1.sym
N 67200 82200 67200 81900 4
N 67200 81000 67200 80700 4
C 31700 56500 1 0 0 title-bordered-E.sym
L 34600 62100 38100 62100 3 20 0 0 -1 -1
L 38100 62100 38100 59800 3 20 0 0 -1 -1
L 38100 59800 34600 59800 3 20 0 0 -1 -1
L 34600 62100 34600 59800 3 20 0 0 -1 -1
L 34800 62100 34800 59800 3 20 0 0 -1 -1
L 35200 62100 35200 59800 3 0 0 0 -1 -1
L 35600 62100 35600 59800 3 0 0 0 -1 -1
L 36100 62100 36100 59800 3 0 0 0 -1 -1
L 36500 62100 36500 59800 3 0 0 0 -1 -1
L 36900 62100 36900 59800 3 0 0 0 -1 -1
L 37300 62100 37300 59800 3 0 0 0 -1 -1
L 37700 62100 37700 59800 3 0 0 0 -1 -1
L 34600 61800 38100 61800 3 20 0 0 -1 -1
L 34600 61400 38100 61400 3 0 0 0 -1 -1
L 34600 61000 38100 61000 3 0 0 0 -1 -1
L 34600 60600 38100 60600 3 0 0 0 -1 -1
L 34600 60100 38100 60100 3 0 0 0 -1 -1
T 35000 61900 9 10 1 0 0 0 1
7
T 35400 61900 9 10 1 0 0 0 1
6
T 35800 61900 9 10 1 0 0 0 1
5
T 36200 61900 9 10 1 0 0 0 1
4
T 36600 61900 9 10 1 0 0 0 1
3
T 37000 61900 9 10 1 0 0 0 1
2
T 37400 61900 9 10 1 0 0 0 1
1
T 37800 61900 9 10 1 0 0 0 1
0
T 34652 61534 9 10 1 0 0 0 1
A
T 34652 61134 9 10 1 0 0 0 1
B
T 34652 60734 9 10 1 0 0 0 1
C
T 34652 60334 9 10 1 0 0 0 1
D
T 34652 59934 9 10 1 0 0 0 1
E
T 35700 61500 9 10 1 0 0 0 1
T/R
T 36200 61500 9 10 1 0 0 0 1
31
T 36600 61500 9 10 1 0 0 0 1
39
T 37000 61500 9 10 1 0 0 0 1
38
T 37400 61500 9 10 1 0 0 0 1
37
T 37800 61500 9 10 1 0 0 0 1
36
T 34900 61100 9 10 1 0 0 0 1
PD
T 35300 61100 9 10 1 0 0 0 1
PC
T 35800 61100 9 10 1 0 0 0 1
35
T 36200 61100 9 10 1 0 0 0 1
34
T 36600 61100 9 10 1 0 0 0 1
33
T 37000 61100 9 10 1 0 0 0 1
32
T 37400 61100 9 10 1 0 0 0 1
40
T 37800 61100 9 10 1 0 0 0 1
ZC
T 34900 60700 9 10 1 0 0 0 1
Rx
T 35300 60700 9 10 1 0 0 0 1
Tx
T 35800 60700 9 10 1 0 0 0 1
44
T 36200 60700 9 10 1 0 0 0 1
45
T 36600 60700 9 10 1 0 0 0 1
26
T 37000 60700 9 10 1 0 0 0 1
27
T 37800 60700 9 10 1 0 0 0 1
28
T 37400 60700 9 10 1 0 0 0 1
43
T 34900 60300 9 10 1 0 0 0 1
30
T 35300 60300 9 10 1 0 0 0 1
41
T 35800 60300 9 10 1 0 0 0 1
29
T 36200 60300 9 10 1 0 0 0 1
42
T 36600 60300 9 10 1 0 0 0 1
46
T 37000 60300 9 10 1 0 0 0 1
47
T 37400 60300 9 10 1 0 0 0 1
24
T 37800 60300 9 10 1 0 0 0 1
25
T 37000 59900 9 10 1 0 0 0 1
R
T 37400 59900 9 10 1 0 0 0 1
Y
T 37800 59900 9 10 1 0 0 0 1
G
T 34600 64900 9 10 1 0 0 0 1
MASTER CPU PORT ASSIGNMENTS
T 34600 62200 9 10 1 0 0 0 1
SLAVE CPU PORT ASSIGNMENTS
L 34900 64300 35100 64500 3 0 0 0 -1 -1
L 34900 64300 34800 64200 3 0 0 0 -1 -1
L 34800 64100 35200 64500 3 0 0 0 -1 -1
L 34900 64100 35300 64500 3 0 0 0 -1 -1
L 35000 64100 35400 64500 3 0 0 0 -1 -1
L 35100 64100 35500 64500 3 0 0 0 -1 -1
L 35200 64100 35600 64500 3 0 0 0 -1 -1
L 35300 64100 35600 64400 3 0 0 0 -1 -1
L 35400 64100 35600 64300 3 0 0 0 -1 -1
L 35600 64100 35600 64200 3 0 0 0 -1 -1
L 34800 64400 34900 64500 3 0 0 0 -1 -1
L 34800 64300 35000 64500 3 0 0 0 -1 -1
L 34900 61600 35100 61800 3 0 0 0 -1 -1
L 34900 61600 34800 61500 3 0 0 0 -1 -1
L 34800 61400 35200 61800 3 0 0 0 -1 -1
L 34900 61400 35300 61800 3 0 0 0 -1 -1
L 35000 61400 35400 61800 3 0 0 0 -1 -1
L 35100 61400 35500 61800 3 0 0 0 -1 -1
L 35200 61400 35600 61800 3 0 0 0 -1 -1
L 35300 61400 35600 61700 3 0 0 0 -1 -1
L 35400 61400 35600 61600 3 0 0 0 -1 -1
L 35500 61400 35600 61500 3 0 0 0 -1 -1
L 34800 61700 34900 61800 3 0 0 0 -1 -1
L 34800 61600 35000 61800 3 0 0 0 -1 -1
L 34800 62700 34900 62800 3 0 0 0 -1 -1
L 35100 62500 35200 62600 3 0 0 0 -1 -1
L 34800 62600 35000 62800 3 0 0 0 -1 -1
L 35000 62500 35200 62700 3 0 0 0 -1 -1
L 34800 62500 35100 62800 3 0 0 0 -1 -1
L 34900 62500 35200 62800 3 0 0 0 -1 -1
L 35200 62700 35300 62800 3 0 0 0 -1 -1
L 35500 62500 35600 62600 3 0 0 0 -1 -1
L 35200 62600 35400 62800 3 0 0 0 -1 -1
L 35400 62500 35600 62700 3 0 0 0 -1 -1
L 35200 62500 35500 62800 3 0 0 0 -1 -1
L 35300 62500 35600 62800 3 0 0 0 -1 -1
L 35700 62700 35800 62800 3 0 0 0 -1 -1
L 36000 62500 36100 62600 3 0 0 0 -1 -1
L 35700 62600 35900 62800 3 0 0 0 -1 -1
L 35900 62500 36100 62700 3 0 0 0 -1 -1
L 35700 62500 36000 62800 3 0 0 0 -1 -1
L 35800 62500 36100 62800 3 0 0 0 -1 -1
L 36100 62700 36200 62800 3 0 0 0 -1 -1
L 36400 62500 36500 62600 3 0 0 0 -1 -1
L 36100 62600 36300 62800 3 0 0 0 -1 -1
L 36300 62500 36500 62700 3 0 0 0 -1 -1
L 36100 62500 36400 62800 3 0 0 0 -1 -1
L 36200 62500 36500 62800 3 0 0 0 -1 -1
L 36500 62700 36600 62800 3 0 0 0 -1 -1
L 36800 62500 36900 62600 3 0 0 0 -1 -1
L 36500 62600 36700 62800 3 0 0 0 -1 -1
L 36700 62500 36900 62700 3 0 0 0 -1 -1
L 36500 62500 36800 62800 3 0 0 0 -1 -1
L 36600 62500 36900 62800 3 0 0 0 -1 -1
L 35600 62700 35700 62800 3 0 0 0 -1 -1
L 35900 62500 36000 62600 3 0 0 0 -1 -1
L 35600 62600 35800 62800 3 0 0 0 -1 -1
L 35800 62500 36000 62700 3 0 0 0 -1 -1
L 35600 62500 35900 62800 3 0 0 0 -1 -1
L 35700 62500 36000 62800 3 0 0 0 -1 -1
L 34800 60000 34900 60100 3 0 0 0 -1 -1
L 35100 59800 35200 59900 3 0 0 0 -1 -1
L 34800 59900 35000 60100 3 0 0 0 -1 -1
L 35000 59800 35200 60000 3 0 0 0 -1 -1
L 34800 59800 35100 60100 3 0 0 0 -1 -1
L 34900 59800 35200 60100 3 0 0 0 -1 -1
L 35200 60000 35300 60100 3 0 0 0 -1 -1
L 35500 59800 35600 59900 3 0 0 0 -1 -1
L 35200 59900 35400 60100 3 0 0 0 -1 -1
L 35400 59800 35600 60000 3 0 0 0 -1 -1
L 35200 59800 35500 60100 3 0 0 0 -1 -1
L 35300 59800 35600 60100 3 0 0 0 -1 -1
L 35600 60000 35700 60100 3 0 0 0 -1 -1
L 35900 59800 36000 59900 3 0 0 0 -1 -1
L 35600 59900 35800 60100 3 0 0 0 -1 -1
L 35800 59800 36000 60000 3 0 0 0 -1 -1
L 35600 59800 35900 60100 3 0 0 0 -1 -1
L 35700 59800 36000 60100 3 0 0 0 -1 -1
L 36000 60000 36100 60100 3 0 0 0 -1 -1
L 36300 59800 36400 59900 3 0 0 0 -1 -1
L 36000 59900 36200 60100 3 0 0 0 -1 -1
L 36200 59800 36400 60000 3 0 0 0 -1 -1
L 36000 59800 36300 60100 3 0 0 0 -1 -1
L 36100 59800 36400 60100 3 0 0 0 -1 -1
L 36400 60000 36500 60100 3 0 0 0 -1 -1
L 36700 59800 36800 59900 3 0 0 0 -1 -1
L 36400 59900 36600 60100 3 0 0 0 -1 -1
L 36600 59800 36800 60000 3 0 0 0 -1 -1
L 36400 59800 36700 60100 3 0 0 0 -1 -1
L 36500 59800 36800 60100 3 0 0 0 -1 -1
L 36500 60000 36600 60100 3 0 0 0 -1 -1
L 36800 59800 36900 59900 3 0 0 0 -1 -1
L 36500 59900 36700 60100 3 0 0 0 -1 -1
L 36700 59800 36900 60000 3 0 0 0 -1 -1
L 36500 59800 36800 60100 3 0 0 0 -1 -1
L 36600 59800 36900 60100 3 0 0 0 -1 -1
L 35900 61700 36000 61700 3 0 0 0 -1 -1
L 34800 64100 35600 64100 3 15 0 0 -1 -1
L 35600 64100 35600 63700 3 15 0 0 -1 -1
L 35600 63700 34800 63700 3 15 0 0 -1 -1
L 34800 61400 35600 61400 3 15 0 0 -1 -1
L 35600 61400 35600 61000 3 15 0 0 -1 -1
L 35600 61000 34800 61000 3 15 0 0 -1 -1
L 34800 61000 35600 61000 3 15 0 0 -1 -1
L 35600 61000 35600 60600 3 15 0 0 -1 -1
L 35600 60600 34800 60600 3 15 0 0 -1 -1
L 34800 63700 35600 63700 3 15 0 0 -1 -1
L 35600 63700 35600 63300 3 15 0 0 -1 -1
L 35600 63300 34800 63300 3 15 0 0 -1 -1
L 37700 64100 37700 63700 3 15 0 0 -1 -1
L 37700 64100 38100 64100 3 15 0 0 -1 -1
L 37700 63700 38100 63700 3 15 0 0 -1 -1
L 37700 61400 38100 61400 3 15 0 0 -1 -1
L 37700 61000 38100 61000 3 15 0 0 -1 -1
L 37700 61400 37700 61000 3 15 0 0 -1 -1
L 36100 64500 36100 64100 3 15 0 0 -1 -1
L 35600 64500 35600 64100 3 15 0 0 -1 -1
L 35600 61800 35600 61400 3 15 0 0 -1 -1
L 36100 61800 36100 61400 3 15 0 0 -1 -1
L 35600 61400 36100 61400 3 15 0 0 -1 -1
L 35600 64100 36100 64100 3 15 0 0 -1 -1
L 36900 62800 38100 62800 3 15 0 0 -1 -1
L 36900 60100 38100 60100 3 15 0 0 -1 -1
L 36900 62800 36900 62500 3 15 0 0 -1 -1
L 36900 60100 36900 59800 3 15 0 0 -1 -1
N 59200 86000 59200 86500 4
N 56600 86000 59400 86000 4
C 46400 62000 1 0 0 header26-1.sym
{
T 47000 67400 5 10 1 1 0 0 1
refdes=J1
}
C 62300 62000 1 0 0 header26-1.sym
{
T 62900 67400 5 10 1 1 0 0 1
refdes=J2
}
T 32400 56900 9 10 1 0 0 0 1
CVS: $Id: 48ssr_controller.sch,v 1.1.1.1 2007/06/13 04:34:28 steve Exp $
T 67900 58400 9 10 1 0 0 0 2
3.1: No changes; version number sync with PCB 
(Corrected some layout and tooling issues)
T 67900 58900 9 10 1 0 0 0 1
3.0: Total redesign; split into separate controller and relay boards.
T 67900 59100 9 10 1 0 0 0 1
REVISION HISTORY FROM 3.0:
