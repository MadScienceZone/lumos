@rem Split out the three individual ROM versions from the main source file.
@filesplitter.py -r -t master 48ctl-master.asm -t slave 48ctl-slave-877.asm -p 877 48ctlrom.asm
@filesplitter.py -r -t master XXX-DONT-USE-XXX -t slave 48ctl-slave-777.asm -p 777 48ctlrom.asm
