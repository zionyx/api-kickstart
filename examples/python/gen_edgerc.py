# Simple script to generate credentials file based on
# Copy/paste of the "{OPEN} API Administration" output
# Usage: python gen_edgerc.py <section_name>

import sys
import re
import ConfigParser
from os.path import expanduser

# For the sample diagnostic tools application the section name is set to 
# diagnostic_tools. If you wish to use a different section name, call the  
# script with a new section name as the argument.
if len(sys.argv) > 1:
	section_name = sys.argv[1]
else:
	section_name = "diagnostic_tools"

print "After authorizing your client in the {OPEN} API Administration tool,"
print "export the credentials and paste the contents of the export file below," 
print "followed by control-D."
sys.stdout.write('>>> ')

# Slurp in config
text = sys.stdin.read()

# Parse the config data
home = expanduser("~")
fieldlist = text.split()
index = 0
fields = {}

while index < len(fieldlist):
	if (re.search(r':$', fieldlist[index])):
		fields[fieldlist[index]] = fieldlist[index + 1]
	index += 1

# Process the config data
Config = ConfigParser.ConfigParser()
filename = "%s/.edgerc" % home
open(filename, 'a').close()
Config.read(filename)
configfile = open(filename,'w')

if section_name in Config.sections():
	print "\n\nReplacing section: %s" % section_name
	Config.remove_section(section_name)
else:
	print "\n\nCreating section: %s" % section_name

Config.add_section(section_name)
Config.set(section_name,'client_secret',fields['Secret:'])
Config.set(section_name,'host',fields['URL:'].replace('https://',''))
Config.set(section_name,'access_token',fields['Tokens:'])
Config.set(section_name,'client_token',fields['token:'])
Config.write(configfile)	
