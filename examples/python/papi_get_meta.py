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

import requests, logging, json, random
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()
debug = False

# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig([],"papi")

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
	# Since this script is all about metadata, just print it out
	print ">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n"
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
	#groupId = group['groupId']
	groupId = "grp_34382"
	#groupName = group['groupName']
	groupName = "PAPI"
	print
	print "Using group %s (%s)" % (groupName, groupId)

	# Use the first contractId for requests, will work fine
	#contractId = group['contractIds'][0]
	contractId = "ctr_C-FKL41U"
	print "Using contract ID %s" % (contractId)
	print

	return (groupId, contractId)

def getProperties(Id):
	"""
	Get the properties for the associated group/contract combination
	"""
	property_parameters = { "contractId":Id['contract'], "groupId":Id['group'] }
	property_result = getResult('/papi/v0/properties', property_parameters)
	property_items = property_result['properties']['items']

	return (property_items)

def getProducts(Id):
	"""
        Get the properties for the associated group/contract combination
        """
        property_parameters = { "contractId":Id['contract'] }
        product_result = getResult('/papi/v0/products', property_parameters)
        product_items = product_result['products']['items']

def getActivations(Id):
	"""
	Get information on a specific property
	"""
	property_parameters = { "contractId":Id['contract'], "groupId":Id['group'] }
	property_result = getResult('/papi/v0/properties/' + Id['property'] + '/activations', property_parameters)
	property_items = property_result['activations']['items']

	return (property_items)

if __name__ == "__main__":
	Id = {}
	(Id['group'], Id['contract']) = getGroup()
	properties = getProperties(Id)
	products = getProducts(Id)
	# Get the ID of the first property, then get activations associated with it
	Id['property'] = properties[0]['propertyId']
	activations = getActivations(Id)

	# Define a filter to run on the list of activations where we only accept
	# activations that are on the 'PRODUCTION' network and have a non-empty note
	def sslOnly(activation):
		return activation['network'] == 'PRODUCTION' and not activation['note'].isspace()
	prodActivations = filter(sslOnly, activations)

	print 'Total activations: ' + str(len(activations))
	print 'Total production activations with notes: ' + str(len(prodActivations))
	print '2 random production activations with notes:'
	print json.dumps(random.sample(prodActivations,2), indent=2)
