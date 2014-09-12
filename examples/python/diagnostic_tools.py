#! /usr/bin/python
# Sample client for diagnostic tools
# This requires the following to be set (in order of priority to the script):
# CLIENT_TOKEN, CLIENT_SECRET, ACCESS_TOKEN, HOST
# optionally you can set VERBOSE to True or max-body to a different buffer size
#
# These can all be set (case insensitive) in the following ways:
# On the command line:
#   --client_token=xxxxx --client_secret=xxxx access_token=xxxx, host=xxxx
# In environment variables:
#   export CLIENT_TOKEN=xxxx
#   export CLIENT_SECRET=xxxx
#   export ACCESS_TOKEN=xxxx
#   export HOST=xxxx.luna.akamaiapis.net
# In a configuration file - default is ~/.edgerc - can be changed using CONFIG_FILE 
# in environment variables or on the command line
# [default]
# host = xxxx.luna.akamaiapis.net
# client_token = xxxx
# client_secret = xxxx
# access_token = xxxx
# max-body = 2048

import EdgeClient

client = EdgeClient.EdgeGridClient()
location_object = client.make_call('/diagnostic-tools/v1/locations','GET')
location = location_object['locations'][0]

print "Found %d locations, selecting the first one: %s" % (len(location_object['locations']), location)

dig_parameters = { "hostname":"developer.akamai.com", "location":location, "queryType":"A" }

dig_object = client.make_call('/diagnostic-tools/v1/dig','GET',dig_parameters)

print dig_object
