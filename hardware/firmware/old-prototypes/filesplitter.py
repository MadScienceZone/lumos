#!/usr/bin/python
# 
# Split up source files into multiple versions
# by using lines containing the special tokens:
#   @@--token--@@   output ONLY to "token" file
#   @@--END--@@     end diversion
#
# The token (or END) is matched regardless of case.
# 
# This is enabled by specifying an output filename
# for each token using the option:
#   -t token filename
#
# Further, processor-specific tokens may be 
# given, which apply to ALL diversions.
# These have the form @@P=ID@@.  Any line
# of this type with a different ID than the
# defined processor (default ID=877) is
# discarded.
#
# The lines containing the dividing markers are
# discarded completely.
#
# Additionally, the special tokens @@REL and @@DEV
# mark lines which are release code and development
# code.  Any line containing @@REL is completely 
# deleted from the output.  If the -r option is
# given, then the @@REL lines are kept in but the
# @@DEV lines are deleted.
#
# And finally, lines containing @@XXX are only 
# kept in the source file and not passed to ANY
# output file.
#

import optparse
import sys
import re

diversionOutput = {}
mainOutput = None

def token(option, opt_str, value, parser):
	key = value[0].lower()
	if key in diversionOutput:
		raise KeyError, "Diversion target '%s' already defined" % value[0]
	diversionOutput[key] = open(value[1], "w")

parser = optparse.OptionParser()
parser.add_option('-r', action='store_true', dest='release', help='Generate release code')
parser.add_option('-t', action='callback', callback=token, help='Specify diversion token and file', metavar='TOKEN FILE', nargs=2, type='string')
parser.add_option('-o', action='store',      dest='output',  help='Output filename', metavar='PATH')
parser.add_option('-p', action='store',      dest='proc',    help='Processor type',  metavar='ID')
parser.add_option('-v', action='store_true', dest='verbose', help='Verbose output')
parser.set_defaults(proc='877')
(options, files) = parser.parse_args()

if options.output is None:
	if len(diversionOutput) == 0:
		print >> sys.stderr, "No output stream specified"
		sys.exit(1)
else:
	mainOutput = open(options.output, "w")

if len(files) != 1:
	print >> sys.stderr, "Exactly one input filename is required."
	sys.exit(1)

mainInput = open(files[0], "r")

tok_re = re.compile(r'@@--(\w+)--@@')
proc_re= re.compile(r'@@P=(\w+)@@')
divertTo = None

for line in mainInput:
	line = line.rstrip()
	if line.find('@@REL') >= 0 and not options.release: continue
	if line.find('@@DEV') >= 0 and     options.release: continue
	if line.find('@@XXX') >= 0:                         continue

	match = proc_re.search(line)
	if match is not None:
		if match.group(1).lower() != options.proc.lower(): 
			if options.verbose:
				print "Excluded", line
			continue
		elif options.verbose:
			print "Included", line

	match = tok_re.search(line)
	if match is not None:
		dt = match.group(1).lower()
		if dt == 'end':
			divertTo = None
		elif dt in diversionOutput:
			divertTo = diversionOutput[dt]
		else:
			print >> sys.stderr, "Warning: File refers to diversion target '%s' which has no output file. (IGNORED)" % dt
		continue

	if mainOutput is not None:
		print >> mainOutput, line

	if divertTo is None:
		# send to all outputs
		for k in diversionOutput:
			print >> diversionOutput[k], line
	else:
		print >> divertTo, line
