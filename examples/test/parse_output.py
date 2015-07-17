# This command generates a valid xml file for junit parsing in Jenkins
# It is designed to create the minimum valid xml file for the purpose, as demonstrated here:
#<testsuite tests="3">
#    <testcase classname="foo1" name="ASuccessfulTest"/>
#    <testcase classname="foo2" name="AnotherSuccessfulTest"/>
#    <testcase classname="foo3" name="AFailingTest">
#        <failure type="NotEnoughFoo"> details about failure </failure>
#    </testcase>
#</testsuite>
#
#
# To run, call parse_output.py <scriptname> <dig>
#
# % generate_junit.py diagnostic_tools dig

import sys, glob, re
from datetime import time

if len(sys.argv) < 3:
	exit('Usage: %s <scriptname_base> <classname>' % sys.argv[0])

scriptname = sys.argv[1]
name = sys.argv[2]

error_results = {}
output_results = {}

for file in glob.glob("%s.*.*" % scriptname):
	if "error" in file:
		with open (file, 'r') as error_file:
			error_results[file] = error_file.read()	

	if "output" in file:
		print "Found an output"
		with open (file, 'r') as output_file:
			output_content = output_file.read()
			output_results[file] = output_file.read()

with open ('test.xml', 'w') as xml_file:
	# One test per script
	xml_file.write('<testsuite tests="%d">\n' % len(output_results))
	for key in output_results:
		xml_file.write('    <testcase classname="%s" name="%s"' % (key, name))
		if key in error_results:
			xml_file.write('>\n')	
			xml_file.write('       <failure type="fail">%s\n       </failure>\n' % error_content[key])
			xml_file.write('    </testcase>\n')
		else:
			xml_file.write('/>\n')
	xml_file.write('</testsuite>\n')
	xml_file.close()
time.sleep(5)
