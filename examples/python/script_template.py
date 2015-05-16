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
config_section = "default"

try:
        config = EdgeGridConfig({"verbose":debug},section_name)
except:
        error_msg = "ERROR: No section named %s was found in your ~/.edgerc file\n" % section_name
        error_msg += "ERROR: Please generate credentials for the script functionality\n"
        error_msg += "ERROR: and run 'gen_edgerc %s' to generate the credential file\n" % section_name
        exit(error_msg)

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
  httpErrors(endpoint_result.status_code, path, endpoint_result.json())
  if debug: print ">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n"
  return endpoint_result.json()

def httpErrors(status_code, endpoint, result):
  if status_code == 403:
                error_msg =  "ERROR: Call to %s failed with a 403 result\n" % endpoint
                error_msg +=  "ERROR: This indicates a problem with authorization.\n"
                error_msg +=  "ERROR: Please ensure that the credentials you created for this script\n"
                error_msg +=  "ERROR: have the necessary permissions in the Luna portal.\n"
                error_msg +=  "ERROR: Problem details: %s\n" % result["detail"]
                exit(error_msg)

  if status_code in [400, 401]:
                error_msg =  "ERROR: Call to %s failed with a %s result\n" % (endpoint, status_code)
                error_msg +=  "ERROR: This indicates a problem with authentication or headers.\n"
                error_msg +=  "ERROR: Please ensure that the .edgerc file is formatted correctly.\n"
                error_msg +=  "ERROR: If you still have issues, please use gen_edgerc.py to generate the credentials\n"
                error_msg +=  "ERROR: Problem details: %s\n" % result["detail"]
                exit(error_msg)

  if status_code in [404]:
                error_msg =  "ERROR: Call to %s failed with a %s result\n" % (endpoint, status_code)
                error_msg +=  "ERROR: This means that the page does not exist as requested.\n"
                error_msg +=  "ERROR: Please ensure that the URL you're calling is correctly formatted\n"
                error_msg +=  "ERROR: or look at other examples to make sure yours matches.\n"
                error_msg +=  "ERROR: Problem details: %s\n" % result["detail"]
                exit(error_msg)

  error_string = None
  if "errorString" in result:
               if result["errorString"]:
                       error_string = result["errorString"]
  else:
    for key in result:
      if type(key) is not str:
        continue
      if type(result[key]["errorString"]) is str:
        error_string = result[key]["errorString"]
  if error_string:
                error_msg =  "ERROR: Call caused a server fault.\n"
                error_msg +=  "ERROR: Please check the problem details for more information:\n"
                error_msg +=  "ERROR: Problem details: %s\n" % error_string
                exit(error_msg) 

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
