#! /usr/bin/python
""" Sample client for network-lists
In order to "create" a new list, you'll want to 
remove the # at the beginning of the "createNetworkList" call
and update the IP addresses to be appropriate for your needs.
"""



import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()
debug = False

config = EdgeGridConfig({},"networklists")

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

def getNetworkLists():
	print
	print "Requesting the list of network lists"

	events_result = getResult('/network-list/v1/network_lists')
	return events_result

def createNetworkList(name,ips):
	print "Creating a network list %s for ip addresses %s" % (name, json.dumps(ips))
	headers = {'Content-Type': 'application/json'}
	path = "/network-list/v1/network_lists"
	data_obj = {
		"name" : name,
		"type" : "IP",
		"list" : ips
	}
	print json.dumps(data_obj)	
	create_result = session.post(urljoin(baseurl,path),data=json.dumps(data_obj), headers=headers)

if __name__ == "__main__":
	Id = {}
	lists = getNetworkLists()["network_lists"]
	def mapper(x):
		print str(x["numEntries"]) + ", " + x["name"]
	map(mapper, lists)
	#createNetworkList("test",["1.2.3.4"])

