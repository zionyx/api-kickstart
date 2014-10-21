#! /usr/bin/python
""" Sample client 
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
config = EdgeGridConfig(config_values,"papi")

# Enable debugging for the requests module
if debug or config.verbose:
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

if hasattr(config, 'headers'):
	session.headers.update(config.headers)

baseurl = '%s://%s/' % ('https', config.host)

def getResult(endpoint, parameters=None):
	if parameters:
		parameter_string = urllib.urlencode(parameters)
		path = ''.join([endpoint + '?',parameter_string])
	else:
		path = endpoint
	endpoint_result = session.get(urljoin(baseurl,path))
	if debug: print ">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n"
	return endpoint_result.json()


"""
Request the list of groups for the property.  Print out
how many groups there are, then use the first group where
the test property lives.

"""
print
print "Requesting the list of groups for this property"

groups_result = getResult('/papi/v0/groups')

print "There are %s groups associated with the account:" % len(groups_result['groups']['items'])
print "    %s (%s)" % (groups_result['accountName'], groups_result['accountId'])

group = groups_result['groups']['items'][0]
groupId = group['groupId']
groupName = group['groupName']
print
print "Using group %s (%s)" % (groupName, groupId)

# Use the first contractId for requests, will work fine
contractId = group['contractIds'][0]
print "Using contract ID %s" % (contractId)
print

"""
Get the properties for the associated group/contract combination
"""
testproperty = "papiTest1"
property_parameters = { "contractId":contractId, "groupId":groupId }
property_result = getResult('/papi/v0/properties', property_parameters)
property_items = property_result['properties']['items']
print "Grabbing specific information about the %s property" % testproperty

"""
Just go ahead and iterate over the dictionary, we're just
finding a particular property
"""

testproperty_item = {}

for item in property_items:
	if item['propertyName'] == testproperty:
		testproperty_item = item

if testproperty_item:
	print "  Found the property %s" % testproperty
	print "    Name: %s" % testproperty_item['propertyName']
	print "    Production Version: %s"  % testproperty_item['productionVersion']
	print "    Group ID: %s"  % groupId
	print "    Group Name: %s"  % groupName
	print "    Contract ID: %s"  % contractId
else:
	print "  No %s found" % testproperty


