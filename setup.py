#!/usr/bin/env python
#
# Setup script for installing Lumos on your system.
# To install, run:
#
#    setup.py install
#

from distutils.core import setup

setup(
	name = 'Lumos',
	version = '0.3a1',
	description = 'Light Orchestration System (SSR Sequencing Control)',
	long_description = '''
		Lumos ("Light Orchestration System") is a software application for
		creating and playing pattern sequences for light displays (such as
		elaborate Christmas light shows, either free-running or synchronized
		to music).
	''',
	author = 'Steve Willoughby',
	author_email = 'support@alchemy.com',
	url = 'http://lumos.sourceforge.net',
	packages = [
		'Lumos', 
		'Lumos.Device', 
		'Lumos.Extras', 
		'Lumos.Network',
	],
	scripts = [
		'dist_bin/lcheck', 
		'dist_bin/lplay', 
		'dist_bin/vixen2lumos',
	],
	package_dir = {'': 'lib'},
	requires = [
		'parallel',
		'serial', 
	],
	provides = ['Lumos'],
)
