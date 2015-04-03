#! /usr/bin/python
""" Sample client 
In order to use this papi client you will need to have access turned
on for your account.  Send the contract IDs you want activated in a 
request to open-developer@akamai.com.

This script pulls the contract groups, properties for that group, and
products for that contract.

Please send any comments, questions or ideas to open-developer@akamai.com

Thanks!
The Akamai Developer Relations Team

"""

import requests, logging, json, random, sys
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()
debug = False

# If all parameters are set already, use them.  Otherwise
# use the config
config_section = "papi"
config = EdgeGridConfig([],config_section)

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
	Request the list of groups for the account.  Print out
	how many groups there are, then use the first group where
	the test property lives.

	"""
	print
	print "Requesting the list of groups for this account"

	groups_result = getResult('/papi/v0/groups')

	return (groups_result)

def getProperties(groupId, contractId):
	"""
	Get the properties for the associated group/contract combination
	"""
	print "Getting properties for group %s and contract %s" % (groupId, contractId)
	property_parameters = { "contractId":contractId, "groupId":groupId }
	property_result = getResult('/papi/v0/properties', property_parameters)
	
	if "properties" in property_result:
		property_items = property_result['properties']['items']
	else:
		property_items = []

	return (property_items)

def getPropertyInfo(propName, groupId, contractId):
	properties = getProperties(groupId, contractId)
	for property in properties:
		if property["propertyName"] == propName:
			return property

def getSingleProperty(propertyId, groupId, contractId ):
	"""
	Get the properties for the associated group/contract combination
	"""
	property_parameters = { "contractId":contractId, "groupId":groupId }
	property_result = getResult('/papi/v0/properties/%s/' % propertyId, 
								property_parameters)
	return (property_result)

def findProperty(config):
	if not hasattr(config, "propId") and not hasattr(config, "prop"):
		print "You gotta have a property"
		exit(0)
	if not config.groupId or not config.contractId:
		groups = getGroup()["groups"]["items"]
	else:
		groups = [{	
					"groupId":config.groupId,
				  	"contractIds":[config.contractId]
				}]
	for group in groups:
		groupId = group["groupId"]
		if "contractIds" in group:
			for contractId in group["contractIds"]:
				if hasattr(config, "prop") and config.prop:
					property = getPropertyInfo(		config.prop, 
													groupId, 
													contractId)
					return property
				elif hasattr(config, "propId") and config.propId:
					property = getSingleProperty(	config.propId,
													groupId,
													contractId)
					return property
				else:
					print "Need a property to make this go."
					exit(0)

def getRealValue(version, property):
	if version == "STAGING":
		return property["stagingVersion"]
	if version == "PRODUCTION":
		return property["productionVersion"]
	if version == "LATEST":
		return property["latestVersion"]
	return version

def getPropertyVersion(property, version):
	result = {}
	property_parameters = { "contractId":property["contractId"],  "groupId":property["groupId"] }
	# We've got to get metadata, hostnames, and rules

	result["meta"]= getResult('/papi/v0/properties/%s/versions/%s'
								% (property["propertyId"], version),
								property_parameters)["versions"]["items"][0]

	hostname_results = getResult('/papi/v0/properties/%s/versions/%s/hostnames/'
								% (property["propertyId"], version),
								property_parameters)
	if "hostnames" in hostname_results:
		result["hostnames"] = hostname_results["hostnames"]["items"][0]

	rules_results = getResult('/papi/v0/properties/%s/versions/%s/rules/'
								% (property["propertyId"], version),
								property_parameters)
	if "rules" in rules_results:
		result["rules"]= rules_results["rules"]

	#print json.dumps(result, indent=2)
	return (result)	

def getDiff(from_ver, to_ver, property):
	from_ver = getRealValue(from_ver, property)
	to_ver = getRealValue(to_ver, property)

	print "Getting difference between version %s and %s" % (from_ver, to_ver)
	from_content = getPropertyVersion(property, from_ver)
	to_content = getPropertyVersion(property, to_ver)

	version_diff = {"rules":{},"meta":{},"hostnames":{}}
	top_from_ver = "VERSION %s" % from_ver
	top_to_ver = "VERSION %s" % to_ver
	diff = compareDeeply(from_content, to_content, version_diff, top_from_ver, top_to_ver)
	return diff

def compareDeeply(from_version, to_version, version_diff, top_from_ver, top_to_ver):
	if from_version == to_version:
		return

	if type(from_version) in [str,int,unicode]:
		version_diff[top_from_ver] = from_version
		version_diff[top_to_ver] = to_version
		return version_diff

	if type(from_version) == list:
		version_diff[top_from_ver] = []
		version_diff[top_to_ver] = []
		for item in from_version:
			if item in to_version:
				continue
			version_diff[top_from_ver].append(item)
		for item in to_version:
			if item in from_version:
				continue
			version_diff[top_to_ver].append(item)
		return version_diff

	
	for key in from_version:
		if key not in version_diff:
			version_diff[key] = {}
		if key not in to_version:
			version_diff[key][top_from_ver] = from_version[key]
			continue
		else:
			diff_value = compareDeeply(from_version[key], to_version[key], version_diff[key], top_from_ver, top_to_ver)
			if diff_value:
				version_diff[key] = diff_value

	for keys in to_version:
		if key not in from_version:
			version_diff[key][top_to_ver] = to_version[key]
			continue

	return version_diff

if __name__ == "__main__":
	if hasattr(config, "find") and config.find:
		property = findProperty(config)
		print json.dumps(property, indent=2) + "\n"
		exit(0)
		
	if hasattr(config, "diff") and config.diff:
		property = findProperty(config)
		
		if not config.from_ver:
			setattr(config, "from_ver", 1)
		if not config.to_ver:
			setattr(config, "to_ver", "LATEST")

		diff = getDiff(config.from_ver, config.to_ver, property)
		keys = diff.keys()

		for key in keys:
			if diff[key] == {}:
				del diff[key]


		print json.dumps(diff, indent=2) + "\n"
			
		

	# If diff is what we want, get the two configurations
	# If the user hasn't specified a group, get the groups to check them out

				
		# Get all group/contract combinations
		# Grab the contracts
		# Look through the group/contract examples for the property in question
		
		# At the end, tell them what the group and contract ID were to make future
	#	  runs faster.  Comment that this can be stored in a DB.  TODO: Store
		# in a sqlite db locally all groups/contracts/property names
		
	#property_name = config.property # Property has to be required, can't do this without it
	#if config.diff:
	#	version1 = config.from
	#	version2 = config.to
	#	print version1
	#	print version2
