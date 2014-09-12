#! /usr/bin/python

import EdgeClient

client = EdgeClient.EdgeGridClient()
return_object = client.make_call('/diagnostic-tools/v1/locations','GET')
location = return_object['locations'][0]
print location
print return_object

# Get locations
# Pick first location
# Do a dig on the server at that location
# Run mtr on that server
