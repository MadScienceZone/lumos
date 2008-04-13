import unittest
from Show import Show

class ShowTest (unittest.TestCase):
	def testLoadFile(self):
		g = Show()
		g.load(open('show.conf'))

		self.assertEqual(g.title, "Example Show")
		self.assertEqual(g.description, "This is an example of how to set up a Lumos show.conf file.\nYou should take this file and edit it to reflect\nyour actual show setup.")
		self.assertEqual(sorted(g.powerSources.keys()), ['1', '2a', '2b'])
		self.assertEqual(g.powerSources['1'].amps, 20)
		self.assert_(g.powerSources['1'].gfci)
		self.assertEqual(g.powerSources['2a'].amps, 15)
		self.assert_(not g.powerSources['2a'].gfci)
		self.assertEqual(g.powerSources['2b'].amps, 15.5)
		self.assert_(not g.powerSources['2b'].gfci)

		self.assertEqual(sorted(g.networks.keys()), ['floods', 'misc', 'trees'])
		for key, desc, port, baud, bits, parity, stop, xonxoff, rtscts, units in (
			('floods', 'X10 network for the floodlights.', 
				2, 1200, 8, 'none', 1, False, False, [
					('floodX10', '2b', 'LynX-10/TW523 Controller', None, (
						('A1', 'West flood, blue',  1, 10,   True),
						('A2', 'West flood, green', 1, 10,   True),
						('C1', 'Snowman power',    20, None, False),
					))
				]
			),
			('misc', "Everything that's not a floodlight or a tree.", 
			    1, 9600, 8, 'none', 1, False, False, [
					('a', '2a', '48-Channel SSR Controller', 9),
					('b', '2a', '48-Channel SSR Controller', 10)
				]
			),
			('trees', 'Separate network of controllers for tree displays.', 
				0, 19200, 8, 'none', 1, False, False, [
					('treea1', '1', '48-Channel SSR Controller', 0, (
						(0, 'Tree 1 RED 1', .3, None, True),
						(1, 'Tree 1 RED 2', .3, None, True),
					)),
					('treea2', '1', '48-Channel SSR Controller', 1),
					('treeb1', '1', '48-Channel SSR Controller', 2),
					('treeb2', '1', '48-Channel SSR Controller', 3)
				]
			)
		):
			self.assertEqual(g.networks[key].description, desc)
			self.assertEqual(g.networks[key].port, port)
			self.assertEqual(g.networks[key].baudrate, baud)
			self.assertEqual(g.networks[key].bits, bits)
			self.assertEqual(g.networks[key].parity, parity)
			self.assertEqual(g.networks[key].stop, stop)
			self.assertEqual(g.networks[key].xonxoff, xonxoff)
			self.assertEqual(g.networks[key].rtscts, rtscts)
			self.assertEqual(sorted(g.networks[key].units.keys()), [i[0] for i in units])
			for unit in units:
				self.assertEqual(g.networks[key].units[unit[0]].powerSource.id, unit[1])
				self.assertEqual(g.networks[key].units[unit[0]].type, unit[2])
				if unit[3] is not None:
					self.assertEqual(g.networks[key].units[unit[0]].address, unit[3])
				# channel tests
				if len(unit) > 4:
					self.assertEqual(sorted(g.networks[key].units[unit[0]].channels.keys()), [i[0] for i in unit[4]])
					for channel in unit[4]:
						self.assertEqual(g.networks[key].units[unit[0]].channels[channel[0]].name, channel[1])
						self.assertEqual(g.networks[key].units[unit[0]].channels[channel[0]].load, channel[2])
						if channel[3] is None:
							self.assertEqual(g.networks[key].units[unit[0]].channels[channel[0]].warm, None)
						else:
							self.assertEqual(g.networks[key].units[unit[0]].channels[channel[0]].warm, g.networks[key].units[unit[0]].channels[channel[0]].raw_dimmer_value(channel[3]))
						self.assertEqual(g.networks[key].units[unit[0]].channels[channel[0]].dimmer, channel[4])
