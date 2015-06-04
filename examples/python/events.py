#! /usr/bin/python
""" Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.
 
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.

 You may obtain a copy of the License at 

    http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

Sample client for events

You can set up an event in the LUNA event center, a long running or short
running event.  With a long running event firing every 3 minutes, you can
create dashboards with near real-time information about your traffic.

"""



import requests, logging, json
from http_calls import EdgeGridHttpCaller
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
session = requests.Session()
section_name = "events"

# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig({"verbose":False},section_name)

if hasattr(config, "debug") or hasattr(config, "verbose"):
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
httpCaller = EdgeGridHttpCaller(session, debug, baseurl)

def getEvents(account_id):
	print
	print "Requesting the list of events for %s" % (account_id)

	events_result = httpCaller.getResult('/events/v2/%s/events' % (account_id))

	# Once you pull a particular event (with an ID from the above call) you can make the following
	# calls to the event API to get information about a particular time segment, or as listed below
	# to get all information about the event itself.

	# Bandwidth can be retrieved for a particular event.  Available choices are origin, edge, or both.
	#event_result = httpCaller.getResult('/events/v2/%s/events/1099191/trafficdata/cpcode/bandwidth' % (account_id))
	#event_result = httpCaller.getResult('/events/v2/%s/events/1099191/trafficdata/cpcode/origin/bandwidth' % (account_id))
	#event_result = httpCaller.getResult('/events/v2/%s/events/1099191/trafficdata/cpcode/edge/bandwidth' % (account_id))

	# Requests can be retrieved for a particular event.  Available choices are origin, edge, or both.
	#event_result = httpCaller.getResult('/events/v2/%s/events/1041567/trafficdata/cpcode/edge/requests' % (account_id))
	#event_result = httpCaller.getResult('/events/v2/%s/events/1041567/trafficdata/cpcode/origin/requests' % (account_id))
	#event_result = httpCaller.getResult('/events/v2/%s/events/1099191/trafficdata/cpcode/requests' % (account_id))

	# Status can be retrieved for a particular event.  Available choices are origin or edge
	event_result = httpCaller.getResult('/events/v2/%s/events/1099191/trafficdata/cpcode/edge/status' % (account_id))
	event_result = httpCaller.getResult('/events/v2/%s/events/1099191/trafficdata/cpcode/origin/status' % (account_id))


if __name__ == "__main__":
	Id = {}
	account_id = "B-3-112OHLC"
	getEvents(account_id)


