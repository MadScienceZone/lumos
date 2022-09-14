@echo off
rem
rem Flash the SSR program to the device using XWISP.
rem
rem The serial port is usually #3 on my system.
rem The valid files are "master", "slave-877", and "slave-777"
rem
if "%1" == "-h" goto usage
if "%1" == "" goto usage
if "%2" == "" goto usage

"c:\program files\xwisp\xwisp.py" PORT %1 GO \ssr\48ctl-%2.hex FUSES FILE
goto end
:usage
echo Usage: flash-rom port# master/slave-777/slave-877
:end
