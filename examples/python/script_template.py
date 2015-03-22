#! /usr/bin/python
# Very basic script template.  Use this to build new
# examples for use in the api-kickstart repository
#
import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()
debug = False


# If all parameters are set already, use them.  Otherwise
# use the config
# In this template, you need to replace "default" with the name of the 
# .edgerc credentials section you wish to use
config = EdgeGridConfig({"verbose":debug},"default")

if config.debug or config.verbose:
	debug = True

# Set the config options
session.auth = EdgeGridAuth(
            client_token=config.client_token,
            client_secret=config.client_secret,
            access_token=config.access_token
)

# Set the baseurl based on config.host
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

def putResult(endpoint, body, parameters=None):
  headers = {'content-type': 'application/json'}
  if parameters:
          parameter_string = urllib.urlencode(parameters)
          path = ''.join([endpoint + '?',parameter_string])
  else:
          path = endpoint
  endpoint_result = session.put(urljoin(baseurl,path), data=body, headers=headers)
  if debug: print ">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n"
  return endpoint_result.json()

if __name__ == "__main__":
	# If you're just doing a simple GET the call is very simple
	# endpoint_result = getResult("ENDPOINT")
	# result_value = endpoint_result["VARIABLE")

	# Add parameters
	# request_parameters = { "name1":value1, "name2":value2 } 
	# endpoint_result = getResult("ENDPOINT",request_parameters)
	# result_value = endpoint_result["VARIABLE")

	# POST example
	#     	sample_obj = { "roleAssignments": [ { "roleId": 14, "groupId": 41241 } ], 
    	#		"firstName": "Kirsten", 
    	#		"phone": "8315887563", 
    	#		"lastName": "Hunter", 
    	#		"email": "kirsten.hunter@akamai.com"
   	#	}
	# sample_post_result = postResult('/user-admin/v1/users', json.dumps(user_obj))

	print "Waiting for some fabulous code here!"
