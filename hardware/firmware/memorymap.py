#!/usr/bin/env python
# vi:set ai sm nu ts=4 sw=4 expandtab:
#
# Read in the MPLAB X memory allocation information and create
# a graphical memory map image for the assembled firmware.
#
# locations starting at 0x300000 are the config fuses
#
# input format:
# MPLINK 4.50, Linker
# Linker Map File - Created Sat Mar 28 01:54:48 2015
# 
import re
import textwrap

class MemoryMap (object):
    skip_pattern = re.compile(r'^\s*$')
    state_patterns = (
        re.compile(r'^\s*Section Info\s*$'),
        re.compile(r'^\s*Section\s*Type\s*Address\s*Location\s*Size\(Bytes\)\s*$'),
        re.compile(r'^[- ]+$'),
        re.compile(r'^\s*([./\w]+)\s+(code|romdata|udata)\s+0x([0-9A-Fa-f]+)\s+(program|data)\s+0x([0-9A-Fa-f]+)\s*$'),
        re.compile(r'^\s*Program Memory Usage\s*$'),
        re.compile(r'^\s*Start\s+End\s*$'),
        re.compile(r'^[- ]+$'),
        re.compile(r'^\s*0x([0-9A-Fa-f]+)\s*0x([0-9a-fA-F]+)\s*$'),
        re.compile(r'^\s*\d+ out of \d+ program addresses used, program memory utilization is \d+%\s*$'),
        re.compile(r'^\s*Symbols.*Sorted by Name\s*$'),
        re.compile(r'^\s*Name\s+Address\s+Location\s+Storage\s+File\s*$'),
        re.compile(r'^[- ]+$'),
        re.compile(r'^\s*([./\w]+)\s*0x([0-9A-Fa-f]+)\s*(program|data)\s*(static|extern)\s*(.*?)\s*$'),
        re.compile(r'^\s*Symbols - Sorted by Address\s*$'),
        re.compile(r'^\s*Name\s+Address\s+Location\s+Storage\s+File\s*$'),
        re.compile(r'^[- ]+$'),
        re.compile(r'^\s*([./\w]+)\s*0x([0-9A-Fa-f]+)\s*(program|data)\s*(static|extern)\s*(.*?)\s*$'),
    )

    def __init__(self):
        self.banks = {
            'program':  MemoryBank('program'),
            'data':     MemoryBank('data')
        }

#              ________________________________  ___________
#  0x00000000 | symbol                         | section
#  0x00000000 | symbol                         | 
#  0x00000000 |________________________________| ___________ 
#
    def render_map(self, fileobj, descriptions):
        self.render_program(fileobj, descriptions)
        self.render_data(fileobj)

    def render_program(self, fileobj, descriptions, include_symbols=False):
        last_addr = -1
        fileobj.write('          ______________________________\n')
        for block_address in sorted(self.banks['program'].by_address):
            if block_address >= 0x300000:
                break
            if last_addr >= 0 and block_address != last_addr + 1:
                fileobj.write('    :     ______________________________\n')
            block = self.banks['program'].by_address[block_address]
            if not include_symbols:
                symbols = []
            else:
                symbols = sorted(block.symbol_table, key=lambda sym: sym.address)
            section_label = block.name
            if block.name in descriptions:
                for desc_line in textwrap.wrap(descriptions[block.name], 28):
                    if section_label:
                        fileobj.write('{0:08X} | {1:28.28s} | {2}\n'.format(
                            block.address, desc_line, section_label))
                    else:
                        fileobj.write('         | {0:28.28s} |\n'.format(
                            desc_line))
                    section_label = ''

            if section_label and (not symbols or symbols[0].address > block_address):
                fileobj.write('{0:08X} | {1:28.28s} | {2}\n'.format(
                    block_address, '', section_label))

            for symbol in symbols:
                fileobj.write('{0:08X} | {1:28.28s} | {2}\n'.format(
                    symbol.address, symbol.name, section_label))
                section_label = ''
                
            last_addr = block.address + block.size - 1
            fileobj.write('{0:08X} |______________________________|\n'.format(last_addr))
#            section_label = block.name
#
#            if not symbols or symbols[0].address > block_address:
#                fileobj.write('{0:08X} | {1:28.28s} | {2}\n'.format(
#                    block_address, '', section_label))
#            for symbol in symbols:
#                fileobj.write('{0:08X} | {1:28.28s} | {2}\n'.format(
#                    symbol.address, symbol.name, section_label))
#                section_label = ''
#                
#            last_addr = block.address + block.size - 1
#            fileobj.write('{0:08X} |______________________________|\n'.format(last_addr))
                
    def render_data(self, fileobj, include_symbols=True):
        last_addr = -1
        fileobj.write('     ______________________________\n')
        for block_address in sorted(self.banks['data'].by_address):
#            if block_address >= 0x300000:
#                break
            if last_addr >= 0 and block_address != last_addr + 1:
                fileobj.write(' :   ______________________________\n')
            block = self.banks['data'].by_address[block_address]
            if not include_symbols:
                symbols = []
            else:
                symbols = sorted(block.symbol_table, key=lambda sym: sym.address)
            section_label = block.name
            if block.name in descriptions:
                for desc_line in textwrap.wrap(descriptions[block.name], 28):
                    if section_label:
                        fileobj.write('{0:03X} | {1:28.28s} | {2}\n'.format(
                            block.address, desc_line, section_label))
                    else:
                        fileobj.write('    | {0:28.28s} |\n'.format(
                            desc_line))
                    section_label = ''

            if section_label and (not symbols or symbols[0].address > block_address):
                fileobj.write('{0:03X} | {1:28.28s} | {2}\n'.format(
                    block_address, '', section_label))
                section_label = ''

            for symbol in symbols:
                if section_label:
                    fileobj.write('{0:03X} | {1:03X} {2:24.24s} | {3}\n'.format(
                        block_address, symbol.address, symbol.name, section_label))
                    section_label = ''
                else:
                    fileobj.write('    | {0:03X} {1:24.24s} |\n'.format(
                        symbol.address, symbol.name))
                
            last_addr = block.address + block.size - 1
            fileobj.write('{0:03X} |______________________________|\n'.format(last_addr))
                
            
    def read(self, fileobj):
        state=0

        for line in fileobj:
            if self.skip_pattern.match(line):
                continue

            match = self.state_patterns[state].match(line)
#0                           Section Info
#1       Section       Type    Address   Location Size(Bytes)
#2      ---------  ---------  ---------  ---------  ---------
#3     <name>		{code|romdata|udata} <0xhex> {program|data} <0xhex>
#4                               Program Memory Usage 
#5                               Start         End      
#6                           ---------   ---------      
#7                            0x000000    0x00000d      
#8             7708 out of 16664 program addresses used, program memory utilization is 46%
#9                   Symbols - Sorted by Name
#10     Name    Address   Location    Storage File                     
#11   ---------  ---------  ---------  --------- ---------                
#12	<name> <hex> {program|data} {static|extern} <path>
#13                    Symbols - Sorted by Address
#14      Name    Address   Location    Storage File                     
#15   ---------  ---------  ---------  --------- ---------                
#16	<name> <hex> {program|data} {static|extern} <path>

            if state == 3:  # read section information records
                if not match:
                    state += 1      # and fall through to code below
                else:
                    addr = int(match.group(3), 16)
                    self.banks[match.group(4)].add(MemoryBlock(match.group(1), match.group(2), addr, match.group(4), int(match.group(5), 16)))

            if state == 6:
                for bank in self.banks.values():
                    bank.clear_checks()

            if state == 7:
                if not match:
                    state += 1
                else:
                    self.banks['program'].check_addr_range(
                        int(match.group(1), 16), 
                        int(match.group(2), 16)
                    )

            if state == 11:
                errors = self.banks['program'].check_addr_range_done()
                if errors:
                    raise ValueError('Aborting after {0} cross-reference error{1}'.format(errors, '' if errors==1 else 's'))
                self.banks['program'].clear_checks()

            if state == 12:
                if not match:
                    state += 1
                else:
                    name, start, loc, storage, file = (
                        match.group(1),
                        int(match.group(2), 16),
                        match.group(3),
                        match.group(4),
                        match.group(5),
                    )
                    #self.banks[loc].check_name(name, start)
                    self.banks[loc].define_name(name, start, storage, file)

            if state == 15:
#                errors = 0
                for loc in self.banks:
#                    errors += self.banks[loc].check_name_done()
                    self.banks[loc].clear_checks()
#                if errors:
#                    raise ValueError('Aborting after {0} cross-reference error{1}'.format(errors, '' if errors==1 else 's'))
#

            if state == 16:
                if not match:
                    state += 1
                else:
                    name, start, loc, storage, file = (
                        match.group(1),
                        int(match.group(2), 16),
                        match.group(3),
                        match.group(4),
                        match.group(5),
                    )
                    self.banks[loc].check_addr(name, start, storage, file)

            if state == 17:
                raise ValueError("Extra text after end of map data: {0}".format(line))

            if state in (0,1,2,4,5,6,8,9,10,11,13,14,15):    # wait for start of our data
                # re-match in case we shifted to this state by a previous
                # failure in a working state
                match = self.state_patterns[state].match(line)
                if match:
                    state += 1
                    continue
                elif state > 0:
                    raise ValueError('Unexpected input line in state {0}: {1}'.format(state, line))
        
        if state < 16:
            raise ValueError("Unexpected end of map data in state {0}".format(state))
                    
        errors = 0
        for loc in self.banks:
            errors += self.banks[loc].check_addr_done()
        if errors:
            raise ValueError('Aborting after {0} cross-reference error{1}'.format(errors, '' if errors==1 else 's'))

                
class MemoryBank (object):
    def __init__(self, name):
        self.by_address = {}
        self.by_name = {}
        self.name = name
        self.checked = {}
        self.symbol_table = {}

    def clear_checks(self):
        self.addr_checked = dict([(k,False) for k in self.by_address.keys()])
        self.name_checked = dict([(k,False) for k in self.symbol_table.keys()])

    def check_addr(self, name, addr, storage, filename):
        if name not in self.symbol_table:
            raise ValueError('Symbol "{0}" not found while cross-checking {1} symbol table'.format(name, self.name))

        symbol = self.symbol_table[name]
        for block_address in sorted(self.by_address):
            block = self.by_address[block_address]
            if block_address <= symbol.address < block_address + block.size:
                break
        else:
            raise ValueError('Cannot find a block containing symbol "{0}" at address {1:#08x}'.format(name, symbol.address))
        
        if name not in [s.name for s in block.symbol_table]:
            raise ValueError('Symbol "{0}" should be in {1} block {2:#08x} but does not appear in the symbol table there.'.format(name, self.name, block.address))

        if addr != symbol.address:
            raise ValueError('Symbol "{0}" ({1}@{2:#08x}) should be at {3:#08x}?'.format(name, self.name, symbol.address, addr))

        if storage != symbol.storage:
            raise ValueError('Symbol "{0}" ({1}@{2:#08x}) storage class is {3} should be {4}?'.format(name, self.name, symbol.address, symbol.storage, storage))

        if filename != symbol.filename:
            raise ValueError('Symbol "{0}" ({1}@{2:#08x}) filename is {3} should be {4}?'.format(name, self.name, symbol.address, symbol.filename, filename))

        if name not in self.name_checked:
            raise ValueError('Symbol "{0}" not previously defined or failure in checking system'.format(name))

        self.name_checked[name] = True
        #print "self.name_checked[",name,"] = True"

    def check_addr_range(self, addr, end):
        if addr not in self.addr_checked:
            raise ValueError('Program block starting at {0:#08x} not previously defined'.format(addr))
        start = addr
        while True:
            block = self.by_address[start]
            if block.address != start:
                raise ValueError('Program block starting at {0:#08x} object start address is {1:#08x} (internal error)'.format(addr, block.address))
            endpoint = block.address + block.size - 1
            if endpoint > end:
                raise ValueError('Program memory block {0:#08x}-{1:#08x} contains overlapping block {2:#08x}-{3:#08x} ("{4}")'.format(
                    addr, end, block.address, endpoint, block.name
                ))
            self.addr_checked[block.address] = True
            if endpoint == end:
                break

            start = endpoint + 1
            if start not in self.by_address:
                raise ValueError('Program memory block {0:#08x}-{1:#08x} doesn\'t have a block at {2:#08x}.'.format(addr, end, start))

    def check_addr_done(self):
        errors = 0
        for name in self.name_checked:
            if not self.name_checked[name]:
                print '{0} symbol "{1}" not found in cross-reference check'.format(self.name, name)
                errors += 1
        return errors
        
    def check_addr_range_done(self):
        errors = 0
        for addr in self.addr_checked:
            if not self.addr_checked[addr]:
                print '{0} block {1:#08x} ({2} @{3:#08x}-{4:#08x}) not found in cross-reference check'.format(
                    self.name, addr, self.by_address[addr].name,
                    self.by_address[addr].address,
                    self.by_address[addr].address + 
                        self.by_address[addr].size - 1,
                )
                errors += 1
        return errors
            

#    def check_name(self, name, addr):
#        if name not in self.name_checked:
#            raise ValueError('{0} memory block "{1}" not previously defined'.format(self.name, name))
#        block = self.by_name[name]
#        if block.address != addr:
#            raise ValueError('{0} memory block "{1}" starting at {2:#08x} object start address is {3:#08x} (internal error)'.format(self.name, name, addr, block.address))
#
#        self.name_checked[name] = True

    def add(self, block):
        if block.address in self.by_address:
            raise ValueError('Duplicate starting address {0} in memory bank "{1}"'.format(block.address, self.name))

        self.by_address[block.address] = block
        self.by_name[block.name] = block

    def define_name(self, name, start, storage, file):
        if name in self.symbol_table:
            raise ValueError('Symbol "{0}" already defined at {1} memory location {2:#08x}'.format(name, self.name, self.symbol_table[name].address))

        for block_address in sorted(self.by_address):
            if block_address <= start < block_address + self.by_address[block_address].size:
                symbol_block = self.by_address[block_address]
                new_symbol = Symbol(name, start, storage, file, symbol_block)
                self.symbol_table[name] = new_symbol
                symbol_block.add_symbol(new_symbol)
                break
        else:
            raise ValueError("Can't find a {0} block in which to store symbol \"{1}\"".format(self.name, name))

    def get(self, address=None, name=None):
        if address is not None:
            return self.by_address[address]
        if name is not None:
            return self.by_name[name]
        raise ValueError("MemoryBank ({0}) get with no search value".format(self.name))

class MemoryBlock (object):
    def __init__(self, name, type, address, location, size):
        self.name = name
        self.type = type
        self.address = address
        self.location = location
        self.size = size
        self.symbol_table = []

    def add_symbol(self, symbol):
        self.symbol_table.append(symbol)

class Symbol (object):
    def __init__(self, name, address, storage, filename, memory_block):
        self.name = name
        self.address = address
        self.storage = storage
        self.filename = filename
        self.memory_block = memory_block
                
import sys
if len(sys.argv) != 4:
    sys.stderr.write("Usage: {0} input descriptions output\n".format(sys.argv[0]))
    sys.exit(1)

map = MemoryMap()
with open(sys.argv[1]) as infile:
    map.read(infile)

descriptions = {}
with open(sys.argv[2]) as descfile:
    for line in descfile:
        name, desc = line.split(None, 1)
        descriptions[name] = desc.strip()

with open(sys.argv[3], 'w') as outfile:
    map.render_map(outfile, descriptions)
