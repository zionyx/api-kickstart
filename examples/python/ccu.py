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
section_name = "ccu"

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
  if endpoint_result.status_code == 403:
	print "ERROR: Call to %s failed with a 403 result" % endpoint
	print "ERROR: This indicates a problem with authorization."
	print "ERROR: Please ensure that the credentials you created for this script"
	print "ERROR: have the necessary permissions in the Luna portal."
	print "ERROR: Problem details: %s" % endpoint_result.json()["detail"]
	exit(1)

  if endpoint_result.status_code in [400, 401]:
	print "ERROR: Call to %s failed with a %s result" % (endpoint, endpoint_result.status_code)
	print "ERROR: This indicates a problem with authentication or headers."
	print "ERROR: Please ensure that the .edgerc file is formatted correctly."
	print "ERROR: If you still have issues, please use gen_edgerc.py to generate the credentials"
	print "ERROR: Problem details: %s" % endpoint_result.json()["detail"]
	exit(1)

  if endpoint_result.status_code in [404]:
	print "ERROR: Call to %s failed with a %s result" % (endpoint, endpoint_result.status_code)
	print "ERROR: This means that the page does not exist as requested."
	print "ERROR: Please ensure that the URL you're calling is correctly formatted"
	print "ERROR: or look at other examples to make sure yours matches."
	print "ERROR: Problem details: %s" % endpoint_result.json()["detail"]
	exit(1)

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
	return purge_queue_result

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
	
	check_result = checkProgress(purge_post_result["progressUri"])
	seconds_to_wait = check_result['pingAfterSeconds']
	print "You should wait %s seconds before checking queue again..." % seconds_to_wait
