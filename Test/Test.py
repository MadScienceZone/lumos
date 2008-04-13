from unittest import TestSuite, findTestCases

def suite():
	modulesToTest = ('LCheckTest', 'ChannelTest', 'ControllerUnitTest', 
	                 'FirecrackerX10ControllerUnitTest', 'NetworkTest', 
					 'PowerSourceTest', 'ShowTest', 
					 'SpectrumReaderboardUnitTest', 'SSR48ControllerUnitTest')
	suite = TestSuite()
	for module in map(__import__, modulesToTest):
		suite.addTest(findTestCases(module))
	return suite
