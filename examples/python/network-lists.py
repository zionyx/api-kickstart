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
section_name = "networklists"

# If all parameters are set already, use them.  Otherwise
# use the config
try:
	config = EdgeGridConfig({"verbose":False},section_name)
except:
	print "ERROR: No section named %s was found in your ~/.edgerc file" % section_name
	print "ERROR: Please generate credentials for the script functionality"
	print "ERROR: and run 'gen_edgerc %s' to generate the credential file" % section_name
	exit(1)

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

def postResult(endpoint, body, parameters=None):
	headers = {'content-type': 'application/json'}
        if parameters:
                parameter_string = urllib.urlencode(parameters)
                path = ''.join([endpoint + '?',parameter_string])
        else:
                path = endpoint
        endpoint_result = session.post(urljoin(baseurl,path), data=body, headers=headers)
  	httpErrors(endpoint_result.status_code, path, endpoint_result.json())
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
	
	postResult(urljoin(baseurl,path), json.dumps(data_obj))

if __name__ == "__main__":
	Id = {}
	lists = getNetworkLists()["network_lists"]
	def mapper(x):
		print str(x["numEntries"]) + ", " + x["name"]
	map(mapper, lists)
	createNetworkList("test",["1.2.3.4"])

