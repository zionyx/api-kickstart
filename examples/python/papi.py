#! /usr/bin/python
""" Sample client 
  	This requires the following to be set (in order of priority to the script):
	CLIENT_TOKEN, CLIENT_SECRET, ACCESS_TOKEN, HOST
	optionally you can set VERBOSE to True or max-body to a different buffer size

	These can all be set (case insensitive) in the following ways:
	On the command line:
	  --client_token xxxxx --client_secret xxxx access_token xxxx, host xxxx
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

if config.debug or config.verbose:
	debug = True

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

def getGroup():
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

	return (groupId, contractId)

def getProperties(Id,propertyName):
	"""
	Get the properties for the associated group/contract combination
	"""
	property_parameters = { "contractId":Id['contract'], "groupId":Id['group'] }
	property_result = getResult('/papi/v0/properties', property_parameters)
	property_items = property_result['properties']['items']
	print "Grabbing specific information about the %s property" % propertyName

	"""
	Just go ahead and iterate over the dictionary, we're just
	finding a particular property
	"""

	testproperty_item = {}

	for item in property_items:
		if item['propertyName'] != propertyName:
			continue

		testproperty_item = item

	if not testproperty_item:
		print "  No %s found" % propertyName
		exit()

	print "  Found the property %s" % propertyName
	print "    Name: %s" % testproperty_item['propertyName']
	print "    Latest Version: %s"  % testproperty_item['latestVersion']
	print "    Property ID: %s"  % testproperty_item['propertyId']
	print "    Group ID: %s"  % Id['group']
	print "    Contract ID: %s"  % Id['contract']
	return (testproperty_item['propertyId'],testproperty_item['latestVersion'])

def getPropertyRules(Id,propertyVersion,behaviorName):
	"""
	Now we're going to grab the property rules for this guy
	"""
	print
	print "Retrieving property rules"
	path = "/papi/v0/properties/%s/versions/%s/rules" % (Id['property'],propertyVersion)
	rule_parameters = { "contractId":Id['contract'], "groupId":Id['group'] }
	rule_result = getResult(path, rule_parameters)
	
	for item in rule_result['rules']['behaviors']:
		if item['name'] != behaviorName:
			continue
		print "Current status is %s" % item['options']['enabled']
		return (rule_result)

def toggleOffOn(value):
	switch_dict = {"on":"off","off":"on"}
	if value in switch_dict:
		return switch_dict[value]
	return None

def switchPropertyStatus(Id,propertyVersion,behaviorName,rules):
	"""
	Now we're going to switch the prefetch rule for this guy
	"""
	print "Switching status, please be patient..."
	headers = {'Content-Type': 'application/vnd.akamai.papirules.latest+json'}
	headers["Accept"] = "application/vnd.akamai.papirules.latest+json,application/problem+json,application/json"
	path = "/papi/v0/properties/%s/versions/%s/rules" % (Id['property'],propertyVersion)
	
	newBehaviors = []
	for item in rules['rules']['behaviors']:
		if item['name'] != behaviorName:
			newBehaviors.append(item)
		else:
			item['options']['enabled'] = toggleOffOn(item['options']['enabled'])
			newBehaviors.append(item)

	rules['rules']['behaviors'] = newBehaviors

	status_parameters = { "contractId":Id['contract'], "groupId":Id['group'] }
	parameter_string = urllib.urlencode(status_parameters)
	path = ''.join([path + '?',parameter_string])

	create_result = session.put(urljoin(baseurl,path),data=json.dumps(rules), headers=headers)


if __name__ == "__main__":
	Id = {}
	testProperty = "papiTest1"
	testRule = "prefetching"
	(Id['group'], Id['contract']) = getGroup()
	(Id['property'], propertyVersion) = getProperties(Id,testProperty)
	(rules) = getPropertyRules(Id,propertyVersion,testRule)
	print
	if config.write:
		switchPropertyStatus(Id,propertyVersion,testRule,rules)
		getPropertyRules(Id,propertyVersion,testRule)


