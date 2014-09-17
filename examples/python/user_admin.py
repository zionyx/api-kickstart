#! /usr/bin/python
""" Sample client for diagnostic tools
  	This requires the following to be set (in order of priority to the script):
	CLIENT_TOKEN, CLIENT_SECRET, ACCESS_TOKEN, HOST
	optionally you can set VERBOSE to True or max-body to a different buffer size

	These can all be set (case insensitive) in the following ways:
	On the command line:
	  --client_token=xxxxx --client_secret=xxxx access_token=xxxx, host=xxxx
	In environment variables:
	  export CLIENT_TOKEN=xxxx
	  export CLIENT_SECRET=xxxx
	  export ACCESS_TOKEN=xxxx
	  export HOST=xxxx.luna.akamaiapis.net
	In a configuration file - default is ~/.edgerc - can be changed using CONFIG_FILE 
	in environment variables or on the command line
	[default]
	host = xxxx.luna.akamaiapis.net
	client_token = xxxx
	client_secret = xxxx
	access_token = xxxx
	max-body = 2048
"""

import requests
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
import string
import random
import json

session = requests.Session()

# Set these in the script if desired, or
# use the config options listed above
config_values = {
	"client_token"  : '',
	"client_secret" : '',
	"access_token"  : '',
	"host"          : ''
}

# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig(config_values)

# Set the config options
session.auth = EdgeGridAuth(
            client_token=config.client_token,
            client_secret=config.client_secret,
            access_token=config.access_token
)

baseurl = 'https://%s/' % config.host

# Create new user
# Search for new user (to get the user's info)
# Create new group
# Add user to group
# Remove user from group
# Delete group
# Delete user 

# Set the headers for post requests
headers = {'content-type': 'application/json'}

# Make a random name
def id_generator(size=6, chars=string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))

# Generate username for the test
print "Generating new username for test"
username = id_generator() + '_user'
print "Generated username %s" % username

# Search to make sure it doesn't already exist
path = '/user-admin/v1/search?keyword=%s' % 'akamai'
search_result = session.get(urljoin(baseurl,path))
users = search_result.json()['users']
print users
if len(users) != 0:
	print "Unable to create new user %s, already exists" % username
else:
	print "No %s in search results" % username

# We have to have a group in order to add the user to it.
# Get our contract ID
path = '/billing-usage/v1/reportSources'
id_result = session.get(urljoin(baseurl,path))
cid = id_result.json()['contents'][0]['id']
print "Found %s for contract id" % cid
path = "/user-admin/v1/accounts/%s/groups/%s" % (cid,cid)
create_result = session.get(urljoin(baseurl,path))
print create_result.text
print path


# Create a random group name
group = id_generator() + '_group'
path = '/user-admin/v1/accounts/%s/groups/1' % cid

values = {
	"groupName":group
}

datastring = json.dumps(values)
print "Datastring for group create is %s" % datastring
create_result = session.post(urljoin(baseurl,path),data=datastring, headers=headers)
print create_result.text


# Great, no user, we can create a new one
# First, let's build the user object

values = {
    "firstName": "a",
    "lastName": "b",
    "username": username,
    "email": username + '@example.com',
    "phone":1234567890
}


# Build the URL
path = '/user-admin/v1/users'
datastring = json.dumps(values)
print "Datastring is %s" % datastring
create_result = session.post(urljoin(baseurl,path),data=datastring, headers=headers)
print create_result.text
