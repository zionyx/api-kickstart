#! /usr/bin/python
"""
A simple script demonstrating how to add new users and delete them.
Note that this isn't a great script to run on your production system,
but it will create a user unlikely to conflict with the ones you have.
This is more of sample code than anything else.


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

section_name = "user"

# If all parameters are set already, use them.  Otherwise
# use the config
try:
	config = EdgeGridConfig({"verbose":debug},section_name)
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

def getUsers():
  print
  user_result = getResult('/user-admin/v1/users')
  print "Users: %s" % user_result

def createUserRequest():
    	user_obj = {
    		"roleAssignments": [
      			{
        		"rolesId": 14, 
        		"groupId": 41241
      			}
    		], 
    		"firstName": "Kirsten", 
    		"phone": "8315887563", 
    		"lastName": "Hunter", 
    		"email": "kirsten.hunter@akamai.com"
   	}

	print "creating user"
	purge_post_result = postResult('/user-admin/v1/users', json.dumps(user_obj))
	print
	print purge_post_result
	return purge_post_result["contactId"]

def deleteUserRequest(contactid):
	print "Deleting user %s" % contactid
	delete_result = endpoint_result = session.delete(urljoin(baseurl,'/user-admin/v1/users/%s' % contactid))

if __name__ == "__main__":
  getUsers()
  contactid = createUserRequest()
  deleteUserRequest(contactid)
  getUsers()
