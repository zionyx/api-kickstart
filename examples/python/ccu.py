#! /usr/bin/python
""" Sample client for CCU
Note that in order for this to work you need to provision credentials
specifically for CCU - you cannot extend existing credentials to add
CCU as it's managed under "CCU" in the API credential system.

Configure->Organization->Manage APIs
Select "CCU APIs"
Create client collections/clients
Add authorization

Put the credentials in ~/.edgerc as demonstrated by api-kickstart/sample_edgerc
"""

import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
import os
session = requests.Session()
debug = False

config = EdgeGridConfig({"verbose":debug},"ccu")

if config.debug or config.verbose:
	debug = True


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

def postResult(endpoint, body, parameters=None):
	headers = {'content-type': 'application/json'}
        if parameters:
                parameter_string = urllib.urlencode(parameters)
                path = ''.join([endpoint + '?',parameter_string])
        else:
                path = endpoint
        endpoint_result = session.post(urljoin(baseurl,path), data=body, headers=headers)
        if debug: print ">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n"
        return endpoint_result.json()

def getQueue():
	print
	purge_queue_result = getResult('/ccu/v2/queues/default')
	print "The queue currently has %s items in it" % int(purge_queue_result['queueLength'])

def checkProgress(resource):
        print
        purge_queue_result = getResult(resource)
        print purge_queue_result

def postPurgeRequest():
	purge_obj = {
			"objects" : [
				"https://developer.akamai.com/stuff/Akamai_Time_Reference/AkamaiTimeReference.html"
			]
		    }
	print "Adding %s to queue" % json.dumps(purge_obj)
	purge_post_result = postResult('/ccu/v2/queues/default', json.dumps(purge_obj))
	return purge_post_result

if __name__ == "__main__":
	Id = {}
	getQueue()
	purge_post_result = postPurgeRequest()
	purge_post_result = postPurgeRequest()
	
	seconds_to_wait = purge_post_result['pingAfterSeconds']
	resource_to_check = purge_post_result['progressUri']
	checkProgress(resource_to_check)
	print "You should wait %s seconds before checking queue again..." % seconds_to_wait
