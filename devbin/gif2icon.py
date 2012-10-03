#!/usr/bin/python2.7
# vi:set ai sm nu ts=4 sw=4 expandtab:

import base64
import argparse
import os.path
from   glob import glob

parser = argparse.ArgumentParser(description='Convert GIF files for icons to source code')
parser.add_argument('iconfiles', metavar='FILE', nargs='+',
    help="Input GIF files"), #type=argparse.FileType('rb'))
parser.add_argument('-o', '--output', default="icons.py", type=argparse.FileType('w'), help="Source file to create")

args = parser.parse_args()

args.output.write("def init():\n")

for pattern in args.iconfiles:
    for filename in glob(pattern):
        with open(filename, 'rb') as in_file:
            args.output.write("""
    global icon_{0}
    icon_{0} = Tkinter.PhotoImage(data='''
{1}
''')
""".format(
        os.path.splitext(os.path.basename(in_file.name))[0],
        base64.b64encode(in_file.read()),
    ))

args.output.close()
