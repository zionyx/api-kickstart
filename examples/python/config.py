# Python edgegrid module
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

import ConfigParser,os,sys
import argparse
import httplib
import urllib
import urllib2
import logging
import uuid
import hashlib
import hmac
import base64
import re
import json
from sets import Set
from time import gmtime, strftime
from urlparse import urlparse, parse_qsl, urlunparse

if sys.version_info[0] != 2 or sys.version_info[1] < 7:
    print("This script requires Python version 2.7")
    sys.exit(1)

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(description='Process command line options.')

class EdgeGridConfig():

    def __init__(self, config_values, configuration):

        parser.add_argument('--verbose', '-v', action='count')
        parser.add_argument('--debug', '-d', action='count')
        parser.add_argument('--write', '-w', action='store_true')
        parser.add_argument('--find', '-f', action='store_true')
        parser.add_argument('--diff', action='store_true')
        parser.add_argument('--prop', action='store')
        parser.add_argument('--propId', action='store')
        parser.add_argument('--contractId', action='store')
        parser.add_argument('--groupId', action='store')
        parser.add_argument('--from_ver', action='store')
        parser.add_argument('--to_ver', action='store')

        required_options = ['client_token','client_secret','host','access_token']
        optional_options = {'max-body':131072}

        options = Set(required_options) | Set(optional_options.keys())
        arguments = {}
        
        parser.add_argument('--max_body', default=131072, type=int)
        parser.add_argument('--config_file', default='~/.edgerc')

        for argument in required_options:
        	parser.add_argument('--' + argument)
        	if argument in config_values and config_values[argument]:
        		arguments[argument] = config_values[argument]
        		config_values.remove[argument]
        		if argument in required_options:
        			required_options.remove(argument)		

        for argument in config_values:
        	if config_values[argument]:
        		if config_values[argument] == "False" or config_values[argument] == "True":
        			parser.add_argument('--' + argument, action='count')
        		parser.add_argument('--' + argument)
        		arguments[argument] = config_values[argument]
        	
        args = parser.parse_args()
        arguments = vars(args)

        if arguments['debug'] != None:
        	arguments['verbose'] = arguments['debug']

        if arguments['verbose']:
            import httplib as http_client
            http_client.HTTPConnection.debuglevel = 1
            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("requests.packages.urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True


        # Environment variables are next
        # Only use AKA_<VAR> environment options
        akamai_options = Set(['AKA_%s' % option.upper() for option in options])
        for key in Set(os.environ) & akamai_options:
            lower_key = re.sub('AKA_','',key).lower()
            if lower_key not in arguments or arguments[lower_key] == None:
                arguments[lower_key] = os.environ[key]

        arguments["config_file"] = os.path.expanduser(arguments["config_file"])	

        if os.path.isfile(arguments["config_file"]):
        	config = ConfigParser.ConfigParser()
        	config.readfp(open(arguments["config_file"]))
        	for key, value in config.items(configuration):
        		# ConfigParser lowercases magically
        		if key not in arguments or arguments[key] == None:
        			arguments[key] = value
        else:
        	print "Missing configuration file.  Run python gen_creds.py to get your credentials file set up once you've provisioned credentials in LUNA."
        	exit()
        missing_args = []
        for argument in required_options:
        	if argument not in arguments:
        		missing_args.append(argument)

        if len(missing_args) > 0:
        	print "Missing args: %s" % missing_args
        	exit()

        for option in arguments:
            setattr(self,option,arguments[option])

        self.create_base_url()

    def create_base_url(self):
        self.base_url = "https://%s" % self.host
