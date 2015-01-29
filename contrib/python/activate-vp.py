#! /usr/bin/python
import time
import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
import pprint
session = requests.Session()
debug = False

VPNAME = 'icass_vptest2'
VERSION = "1"


# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig({},"default")
#if hasattr(config, 'verbose'):
#	debug = config.verbose

# Enable debugging for the requests module
if debug:
	print "Setting up debugging"
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


session.headers.update({'x-testheader': 'testdata'})

baseurl = '%s://%s/' % ('https', config.host)

def getResult(endpoint, parameters=None):
	if parameters:
		parameter_string = urllib.urlencode(parameters)
		path = ''.join([endpoint + '?',parameter_string])
	else:
		path = endpoint
		endpoint_result = session.get(urljoin(baseurl,path))
	return endpoint_result.json()

def getAllActivations():
	activations = getResult('/config-visitor-prioritization-data/api/v1/common/activation?historyOnly=false');
        return activations

def getVPActivation():
	activations = getAllActivations()
	for activation in activations:
		if activation['name'] == VPNAME:
			return activation
	raise RuntimeException('No VP Activation records found')

def getActivation(v):
	print
	print "Getting Activation record for version " + v
	vpactivation = getVPActivation()
	for policy in vpactivation['policies']:
		for version in policy['versions']:
			if version['version'] == v:
				activation = {'fileId':vpactivation['fileId'], 'assetId':vpactivation['assetId'], 'policyVersionId':version['policyVersionId']}
				if debug:
					pprint.pprint(activation)
				return activation
	raise RuntimeException('No VP Activation records found with the requested version')

def getPolicies():
	print
	print "Requesting VP policies"

        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','Accept':'application/json'}
        path = "/config-visitor-prioritization-data/api/v1/policymanager?command=getAllPolicyInfoMaps"
        parameters = { "query": {"policyManagerRequest": { "command": "getPolicyInfoMapUsingACGIDs", "getPolicyInfoMapUsingACGIDs":{} } } }
        data_string = urllib.urlencode({p: json.dumps(parameters[p]) for p in parameters})
        result = session.post(urljoin(baseurl,path),data=data_string, headers=headers)
        obj = json.loads(result.text)
        return obj

def setPolicy(activation):
	print "Setting policy"
	pprint.pprint(activation)
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','Accept':'application/json'}
        path = "/config-visitor-prioritization-data/api/v1/policymanager"
	parameters = { "query": { "policyManagerRequest": { "command": "activate", "activate": { "tapiocaIDs": [ activation['policyVersionId'] ], "arlId": str(activation['fileId']), "assetId": str(activation['assetId']), "network": "staging" } } } }
        data_string = urllib.urlencode({p: json.dumps(parameters[p]) for p in parameters})
        result = session.post(urljoin(baseurl,path),data=data_string, headers=headers)
        obj = json.loads(result.text)
        return obj

if __name__ == "__main__":
	print "Starting..."
	#print getPolicies()
	activation = getActivation(VERSION)
	result = setPolicy(activation)
	pprint.pprint(result)

		
