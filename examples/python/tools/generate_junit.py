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
# To run, call generate_junit.py <test_directory> <classname> <name>
#
# % generate_junit.py test purge ccu

import sys

if len(sys.argv) < 4:
	exit('Usage: %s <test_directory> <classname> <name>' % sys.argv[0])

test_directory = sys.argv[1]
classname = sys.argv[2]
name = sys.argv[3]

with open ('%s/error' % test_directory, 'r') as error_file:
	error_content = error_file.read()

with open ('%s/output' % test_directory, 'r') as output_file:
	output_content = output_file.read()

with open ('%s/test.xml' % test_directory, 'w') as xml_file:
	# For this very simple example, only one test will be used
	xml_file.write('<testsuite tests="1">\n')
	xml_file.write('    <testcase classname="%s" name="%s"' % (classname, name))
	if error_content:
		xml_file.write('>\n')	
		xml_file.write('       <failure type="fail">%s\n       </failure>\n' % error_content)
		xml_file.write('    </testcase>\n')
	else:
		xml_file.write('/>\n')
	xml_file.write('</testsuite>')