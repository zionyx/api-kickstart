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
# To run, call generate_junit.py <classname> <scriptname>
#
# % generate_junit.py test purge ccu

import sys, glob, re

if len(sys.argv) < 4:
	exit('Usage: %s <test_directory> <classname> <scriptname>' % sys.argv[0])

test_directory = sys.argv[1]
classname = sys.argv[2]
scriptname = sys.argv[3]

error_results = {}
output_results = []

for file in glob.glob("scriptname.*"):
	if match("error", file):
		with open ('file, 'r') as error_file:
			error_results[file] = error_file.read()	

	if match("output", file):
		with open ('file, 'r') as output_file:
			output_content = output_file.read()
			output_results[file] = output_file.read()

with open ('test.xml', 'w') as xml_file:
	# One test per script
	xml_file.write('<testsuite tests="%d">\n' % len(output_results.keys())
	for key in output_results:
		xml_file.write('    <testcase classname="%s" name="%s"' % (classname, name))
		if key in error_content:
			xml_file.write('>\n')	
			xml_file.write('       <failure type="fail">%s\n       </failure>\n' % error_content[key])
			xml_file.write('    </testcase>\n')
		else:
			xml_file.write('/>\n')
		xml_file.write('</testsuite>')
