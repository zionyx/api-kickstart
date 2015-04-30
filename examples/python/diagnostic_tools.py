#! /usr/bin/python
# Very basic script demonstrating diagnostic tools functionality
#
import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()
debug = False
section_name = "default"

# If all parameters are set already, use them.  Otherwise
# use the config
try:
	config = EdgeGridConfig({"verbose":debug},section_name)
except:
	print "ERROR: No section named %s was found in your ~/.edgerc file" % section_name
	print "ERROR: Please generate credentials for the script functionality"
	print "ERROR: and run 'gen_edgerc %s' to generate the credential file" % section_name
	exit(1)

if config.verbose or config.debug:
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
  if endpoint_result.status_code == 403:
	print
	print "ERROR: Call to %s failed with a 403 result" % endpoint
	print "ERROR: This indicates a problem with authorization."
	print "ERROR: Please ensure that the credentials you created for this script"
	print "ERROR: have the necessary permissions in the Luna portal."
	print "ERROR: Problem details: %s" % endpoint_result.json()["detail"]
	exit(1)

  if endpoint_result.status_code in [400, 401]:
	print
	print "ERROR: Call to %s failed with a %s result" % (endpoint, endpoint_result.status_code)
	print "ERROR: This indicates a problem with authentication or headers."
	print "ERROR: Please ensure that the .edgerc file is formatted correctly."
	print "ERROR: If you still have issues, please use gen_edgerc.py to generate the credentials"
	print "ERROR: Problem details: %s" % endpoint_result.json()["detail"]
	exit(1)

  if endpoint_result.status_code in [404]:
	print
	print "ERROR: Call to %s failed with a %s result" % (endpoint, endpoint_result.status_code)
	print "ERROR: This means that the page does not exist as requested."
	print "ERROR: Please ensure that the URL you're calling is correctly formatted"
	print "ERROR: or look at other examples to make sure yours matches."
	print "ERROR: Problem details: %s" % endpoint_result.json()["detail"]
	exit(1)

  return_value = endpoint_result.json()
  error_string = None
  if "errorString" in return_value:
	if return_value["errorString"]:
		error_string = return_value["errorString"]	
  else:
	for key in return_value:
		if "errorString" in return_value[key] and return_value[key]["errorString"]:
			error_string = return_value[key]["errorString"]
  if error_string:
	print
	print "ERROR: Call caused a server fault."
	print "ERROR: Please check the problem details for more information:"
	print "ERROR: Problem details: %s" % error_string
	exit(1)

  if debug: print ">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n"
  return endpoint_result.json()

# Request locations that support the diagnostic-tools
print
print "Requesting locations that support the diagnostic-tools API.\n"

location_result = getResult('/diagnostic-tools/v1/locations')

# Select a random location to host our request
location_count = len(location_result['locations'])

print "There are %s locations that can run dig in the Akamai Network" % location_count
rand_location = randint(0, location_count-1)
location = location_result['locations'][rand_location]
print "We will make our call from " + location + "\n"

# Request the dig request the {OPEN} Developer Site IP informantion
print "Running dig from " + location
dig_parameters = { "hostname":"developer.akamai.com", "location":location, "queryType":"A" }
dig_result = getResult("/diagnostic-tools/v1/dig",dig_parameters)

# Display the results from dig
print dig_result['dig']['result']
