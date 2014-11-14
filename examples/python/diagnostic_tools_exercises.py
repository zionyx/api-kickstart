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

    Optionally:
      export AKA_VERBOSE=True
      export AKA_MAX_BODY=2048

	In a configuration file - default is ~/.edgerc - can be changed using CONFIG_FILE
	in environment variables or on the command line
	[default]
	host = xxxx.luna.akamaiapis.net
	client_token = xxxx
	client_secret = xxxx
	access_token = xxxx
	max-body = 2048
"""

import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()
debug = False

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
config = EdgeGridConfig(config_values,"default")
if hasattr(config, 'verbose'):
	debug = config.verbose

# Enable debugging for the requests module
if debug:
  import httplib as http_client
  http_client.HTTPConnection.debuglevel = 1
  logging.basicConfig()
  logging.getLogger().setLevel(logging.DEBUG)
  requests_log = logging.getLogger("requests.packages.urllib3")
  requests_log.setLevel(logging.DEBUG)
  requests_log.propagate = True


# Set the config options
session.auth = EdgeGridAuth(
            client_token=config.client_token,
            client_secret=config.client_secret,
            access_token=config.access_token
)

# Set the baseurl for all calls
baseurl = '%s://%s/' % ('https', config.host)

# Request locations that support the diagnostic-tools
print
print "Requesting locations that support the diagnostic-tools API.\n"

location_result = session.get(urljoin(baseurl, '/diagnostic-tools/v1/locations'))
if debug: print ">>>\n" + json.dumps(location_result.json(), indent=2) + "\n<<<\n"

# Select a random locaiton to host our request
print "There are %s locations that can run dig in the Akamai Network" % len(location_result.json()['locations'])
rand_location = randint(0, len(location_result.json()['locations']))
location = location_result.json()['locations'][rand_location]
print "We will make our call from " + location + "\n"

# Request the dig request the {OPEN} Developer Site IP informantion
print "Running dig from " + location
dig_parameters = { "hostname":"developer.akamai.com.", "location":location, "queryType":"A" }
parameter_string = urllib.urlencode(dig_parameters)
path = ''.join(['/diagnostic-tools/v1/dig?',parameter_string])
dig_result = session.get(urljoin(baseurl,path))

# Display the results from dig
if debug: print ">>>\n" + json.dumps(dig_result.json(), indent=2) + "\n<<<\n"
print dig_result.json()['dig']['result']
