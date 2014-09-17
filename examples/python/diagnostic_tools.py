#! /usr/bin/python
""" Sample client for diagnostic tools
  	This requires the following to be set (in order of priority to the script):
	CLIENT_TOKEN, CLIENT_SECRET, ACCESS_TOKEN, HOST
	optionally you can set VERBOSE to True or max-body to a different buffer size

	These can all be set (case insensitive) in the following ways:
	On the command line:
	  --client_token=xxxxx --client_secret=xxxx access_token=xxxx, host=xxxx
	In environment variables:
	  export CLIENT_TOKEN=xxxx
	  export CLIENT_SECRET=xxxx
	  export ACCESS_TOKEN=xxxx
	  export HOST=xxxx.luna.akamaiapis.net
	In a configuration file - default is ~/.edgerc - can be changed using CONFIG_FILE 
	in environment variables or on the command line
	[default]
	host = xxxx.luna.akamaiapis.net
	client_token = xxxx
	client_secret = xxxx
	access_token = xxxx
	max-body = 2048
"""

import requests
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()

# Set these in the script if desired, or
# use the config options listed above
config_values = {
	"client_token"  : '',
	"client_secret" : '',
	"access_token"  : '',
	"host"          : ''
}

# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig(config_values)

# Set the config options
session.auth = EdgeGridAuth(
            client_token=config.client_token,
            client_secret=config.client_secret,
            access_token=config.access_token
)

baseurl = 'https://%s/' % config.host
location_result = session.get(urljoin(baseurl, '/diagnostic-tools/v1/locations'))
location = location_result.json()['locations'][0]
print location

dig_parameters = { "hostname":"developer.akamai.com", "location":location, "queryType":"A" }
parameter_string = urllib.urlencode(dig_parameters)

path = ''.join(['/diagnostic-tools/v1/dig?',parameter_string])

dig_result = session.get(urljoin(baseurl,path))

print dig_result.json()
