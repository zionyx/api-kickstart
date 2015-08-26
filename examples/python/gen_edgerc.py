#! /usr/bin/env python

# This script will generate a ~/.edgerc credentials file based on
# Copy/paste of the "{OPEN} API Administration" output
#
# Usage: python gen_edgerc.py -s <section_name> -f <export_file>

""" Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.

 You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""

import sys, os
import re
import argparse
import ConfigParser
from os.path import expanduser

# This script will create a configuration section with the name of the client in your 
# ~/.edgerc credential store. Many of the sample applications use API specific
# section names for clarity when reviewed during API Bootcamps. For example, the 
# diagnostic tools application expects that section name is set to 'diagnostic_tools'. 
#
# If you wish to use a section name other then 'default', call the script with 
# the desired section name as the '-s' argument.
#
# For example: gen_edgerc.py -s diagnostic-tools

parser = argparse.ArgumentParser(description='After authorizing your client \
	in the {OPEN} API Administration tool, export the credentials and process \
	them with this script.')
parser.add_argument('--config_section', '-s', action='store', 
	help='create new config section with this section name.')
parser.add_argument('--cred_file', '-f', action='store', 
	help='use the exported file from the OPEN API Administration tool.')
args= parser.parse_args()

if args.cred_file:
	with open (os.path.expanduser(args.cred_file), "r") as credFile:
			text = credFile.read()
			credFile.close()
else:
	print "After authorizing your client in the {OPEN} API Administration tool,"
	print "export the credentials and paste the contents of the export file below," 
	print "followed by control-D."
	print
	sys.stdout.write('>>> ')

	# Slurp in creds
	text = sys.stdin.read()

# load the cred data
home = expanduser("~")
fieldlist = text.split()
index = 0
fields = {}

# Parse the cred data
while index < len(fieldlist):
	if (re.search(r':$', fieldlist[index])):
		fields[fieldlist[index]] = fieldlist[index + 1]
	index += 1

# Determine the section name giving precedence to -s value
if args.config_section:
	section_name = args.config_section
	section_name_pretty = args.config_section
else:
	section_name = fields['Name:']
	section_name_pretty = fields['Name:']

# Fix up default sections
if section_name.lower() == "default":
	section_name = "----DEFAULT----"
	section_name_pretty = "default"

# Verify section name
print "This program will create a section from the %s client credentials." % section_name_pretty
print 

# Process the config data
Config = ConfigParser.ConfigParser()
filename = "%s/.edgerc" % home

# If this is a new file, recommend setting the section name to default
if not os.path.isfile(filename):
	print "Creating new %s" % filename
	if section_name_pretty != 'default':
		# Force the first section created to be named default
		section_name = "----DEFAULT----"
		section_name_pretty = "default"
	open(filename, 'a+').close()
	
# First, if we have a 'default' section protect it here
with open (filename, "r+") as myfile:
 	data=myfile.read().replace('default','----DEFAULT----')
	myfile.close()
with open (filename, "w") as myfile:
	myfile.write(data)
	myfile.close()

Config.read(filename)
configfile = open(filename,'w')

if section_name in Config.sections():
	print "Replacing section: %s" % section_name_pretty
	Config.remove_section(section_name)
else:
	print "Creating section: %s" % section_name_pretty

Config.add_section(section_name)
Config.set(section_name,'client_secret',fields['Secret:'])
Config.set(section_name,'host',fields['URL:'].replace('https://',''))
Config.set(section_name,'access_token',fields['Tokens:'])
Config.set(section_name,'client_token',fields['token:'])
Config.set(section_name,'max-body',131072)
Config.write(configfile)

configfile.close()

with open (filename, "r") as myfile:
 	data=myfile.read().replace('----DEFAULT----','default')
	myfile.close()
with open (filename, "w") as myfile:
	myfile.write(data)
	myfile.close()

print "\nDone. Please verify your credentials with the verify_creds.py script."
print	
