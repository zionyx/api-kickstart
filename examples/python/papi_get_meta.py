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

import requests, logging, json, random, sys, re
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
from subprocess import call
import os
session = requests.Session()
debug = False
section_name = "papi"

# If all parameters are set already, use them.  Otherwise
# use the config
try:
	config = EdgeGridConfig({"verbose":False},section_name)
except:
	print "ERROR: No section named %s was found in your ~/.edgerc file" % section_name
	print "ERROR: Please generate credentials for the script functionality"
	print "ERROR: and run 'gen_edgerc %s' to generate the credential file" % section_name
	exit(1)

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
  httpErrors(endpoint_result.status_code, path, endpoint_result.json())
  if debug: print ">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n"
  return endpoint_result.json()

def httpErrors(status_code, endpoint, result):
        if status_code == 403:
                print "ERROR: Call to %s failed with a 403 result" % endpoint
                print "ERROR: This indicates a problem with authorization."
                print "ERROR: Please ensure that the credentials you created for this script"
                print "ERROR: have the necessary permissions in the Luna portal."
                print "ERROR: Problem details: %s" % result["detail"]
                exit(1)

        if status_code in [400, 401]:
                print "ERROR: Call to %s failed with a %s result" % (endpoint, status_code)
                print "ERROR: This indicates a problem with authentication or headers."
                print "ERROR: Please ensure that the .edgerc file is formatted correctly."
                print "ERROR: If you still have issues, please use gen_edgerc.py to generate the credentials"
                print "ERROR: Problem details: %s" % result["detail"]
                exit(1)

        if status_code in [404]:
                print "ERROR: Call to %s failed with a %s result" % (endpoint, status_code)
                print "ERROR: This means that the page does not exist as requested."
                print "ERROR: Please ensure that the URL you're calling is correctly formatted"
                print "ERROR: or look at other examples to make sure yours matches."
                print "ERROR: Problem details: %s" % result["detail"]
                exit(1)

	error_string = None
	if "errorString" in result:
               if result["errorString"]:
                       error_string = result["errorString"]
	else:
               for key in result:
			if type(result[key]) is int:
				continue
			if result[key] is None:
				continue
			if result[key] and "errorString" not in result[key]:
				continue
                       	if type(result[key]["errorString"]) is str:
                               	error_string = result[key]["errorString"]
	if error_string:
                print
                print "ERROR: Call caused a server fault."
                print "ERROR: Please check the problem details for more information:"
                print "ERROR: Problem details: %s" % error_string
                exit(1)

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

def getPropertyActivations(propertyId, groupId, contractId ):
	"""
	Get the properties for the associated group/contract combination
	"""
	property_parameters = { "contractId":contractId, "groupId":groupId }
	property_activations = getResult('/papi/v0/properties/%s/activations' % propertyId, 
								property_parameters)
	return (property_activations)


def findProperty(propertyName, config):
	print "Propname is %s" % propertyName
	groups = getGroup()
	if config.prop and not config.groupId or not config.contractId and "groups" in groups:
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
				if propertyName:
					property = getPropertyInfo(
									propertyName, 
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

	result_properties = getResult('/papi/v0/properties/%s/versions/%s'
								% (property["propertyId"], version),
								property_parameters)
	if "versions" not in result_properties:
		return
	result["meta"] = result_properties["versions"]["items"][0]

	hostname_results = getResult('/papi/v0/properties/%s/versions/%s/hostnames/'
								% (property["propertyId"], version),
								property_parameters)
	if "hostnames" in hostname_results and "items" in hostname_results["hostnames"] :
		if len(hostname_results["hostnames"]["items"])> 0:
			result["hostnames"] = hostname_results["hostnames"]["items"][0]

	rules_results = getResult('/papi/v0/properties/%s/versions/%s/rules/'
								% (property["propertyId"], version),
								property_parameters)
	if "rules" in rules_results:
		result["rules"]= rules_results["rules"]

	#print json.dumps(result, indent=2)
	return (result)	

if __name__ == "__main__":

	groupInfo = getGroup()
	first_account = groupInfo["accountId"]
	first_account_string = re.search('act_(.+?)$', first_account) 
	first_account = first_account_string.group(1)

	groups = groupInfo["groups"]["items"]

	for group in groups:
		groupId = group["groupId"]
		print "GroupId = %s:%s" % (group["groupId"], group["groupName"])
		if "contractIds" in group:
			for contractId in group["contractIds"]:
				properties = getProperties(groupId, contractId)
				for property in properties:
					if property["productionVersion"] != None or property["stagingVersion"] != None:
						property["activations"] = getPropertyActivations(property["propertyId"],
																		group["groupId"],
																		contractId)
					print json.dumps(property, indent=2)

					print "Latest Version is %s for %s" % (property["latestVersion"], property["propertyName"])
					for version in range(1, property["latestVersion"]+1):
						property_version = getPropertyVersion(property, version)
						print "\n" + json.dumps(property_version, indent=2) + "\n"
