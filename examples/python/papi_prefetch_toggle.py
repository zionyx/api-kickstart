#! /usr/bin/python
""" Sample client 
In order to use this papi client you will need to have access turned
on for your account.  Send the contract IDs you want activated in a 
request to open-developer@akamai.com.

This script pulls the contract groups, products for that group, and
then looks for a property named "Papitest1".  You can change the 
particular items it's looking for easily enough - right now all it
does is pull the first group, first contract, first product, which
is where the test property lives.

When you run the script with the --write flag, it will toggle the
prefetch bit on the test property.

Please send any comments, questions or ideas to open-developer@akamai.com

Thanks!
The Akamai Developer Relations Team

"""



import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()
debug = False

# Use the credentials from the 'papi' section in ~/.edgerc
config = EdgeGridConfig({},"papi")
if hasattr(config, 'verbose'):
	debug = config.verbose

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
	if create_result.status_code != requests.codes.ok:
		if debug: print ">>>\n" + json.dumps(create_result.json(), indent=2) + "\n<<<\n"
		create_result.raise_for_status()

if __name__ == "__main__":
	Id = {}
	testProperty = "developer.akamai.com"
	testRule = "prefetching"
	(Id['group'], Id['contract']) = getGroup()
	(Id['property'], propertyVersion) = getProperties(Id,testProperty)
	(rules) = getPropertyRules(Id,propertyVersion,testRule)
	print
	if config.write:
		switchPropertyStatus(Id,propertyVersion,testRule,rules)
		getPropertyRules(Id,propertyVersion,testRule)


