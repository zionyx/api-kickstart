#! /usr/bin/python
""" Sample client for CCU
"""

import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()
debug = True

config = EdgeGridConfig({},"ccu")

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

def postPurgeRequest():
	purge_obj = {
			"objects" : [
				"https://developer.akamai.com/stuff/openProgramGA.html"
			]
		    }
	purge_post_result = postResult('/ccu/v2/queues/default', json.dumps(purge_obj))

if __name__ == "__main__":
	Id = {}
	getQueue()
	postPurgeRequest()	

