# Simple script to generate credentials file based on
# Copy/paste of the mahina output

import sys
import re
import ConfigParser
from os.path import expanduser

if len(sys.argv) > 1:
	section_name = sys.argv[1]
else:
	section_name = "diagnostic_tools"

print "Please paste the credentials file information here, followed by control-D"
print "Section name will be %s" % section_name
print "If you wish to use a different section name, call the script with %s 'section_name'" % sys.argv[0]

text = sys.stdin.read()
home = expanduser("~")

fieldlist = text.split()
index = 0

fields = {}

while index < len(fieldlist):
	if (re.search(r':$', fieldlist[index])):
		fields[fieldlist[index]] = fieldlist[index + 1]

	index += 1

Config = ConfigParser.ConfigParser()
filename = "%s/.edgerc" % home
open(filename, 'a').close()
Config.read(filename)

configfile = open(filename,'w')
if section_name in Config.sections():
	Config.remove_section(section_name)
Config.add_section(section_name)
Config.set(section_name,'client_secret',fields['Secret:'])
Config.set(section_name,'host',fields['URL:'].replace('https://',''))
Config.set(section_name,'access_token',fields['Tokens:'])
Config.set(section_name,'client_token',fields['token:'])
Config.write(configfile)	
