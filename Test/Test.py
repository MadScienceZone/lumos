from unittest import TestSuite, findTestCases

def suite():
    modules_to_test = (
      'ChannelTest',
	  'ChannelMapTest',
	  'ControllersTest',
      'ControllerUnitTest',
	  'DeviceTest',
	  'EventTest',
	  'FirecrackerX10ControllerUnitTest',
	  'FireGodControllerUnitTest',
	  'LCheckTest',
	  'LumosTest',
      'LynX10ControllerUnitTest',
      'NetworkTest',
	  'NetworksTest',
	  'Olsen595ControllerUnitTest',
	  'PowerSourceTest',
	  'RenardControllerUnitTest',
	  'ShowTest',
	  'SerialNetworkTest',        # XXX device tests?
	  'ParallelBitNetworkTest',   # XXX device tests?
	  'SequenceTest',
	  'SerialBitNetworkTest',     # XXX device tests?
#     'SpectrumReaderboardUnitTest',
	  'SSR48ControllerUnitTest',
	  'TestNetworkTest',
	  'TestParallelNetworkTest',
	  'VixenSequenceTest',
      'X10ControllerUnitTest'
    )
    suite = TestSuite()
    for module in map(__import__, modules_to_test):
        suite.addTest(findTestCases(module))
    return suite
