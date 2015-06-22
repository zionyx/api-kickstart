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


Sample client for CCU v3 API
Note that in order for this to work you need to provision credentials
specifically for CCU - you cannot extend existing credentials to add
CCU as it's managed under "CCU" in the API credential system.

Configure->Organization->Manage APIs
Select "CCU APIs"
Create client collections/clients
Add authorization

Put the credentials in ~/.edgerc as demonstrated by api-kickstart/sample_edgerc
"""

import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
import os
import sys
session = requests.Session()
debug = False
section_name = "ccu"

logging.getLogger("requests").setLevel(logging.DEBUG) 

# If all parameters are set already, use them.  Otherwise
# use the config
try:
        config_values = {"verbose":False,
                         "ccu_host":True,
                         "ccu_paths":True}
        config = EdgeGridConfig(config_values, section_name)
except:
        error_msg = "ERROR: No section named %s was found in your ~/.edgerc file\n" % section_name
        error_msg += "ERROR: Please generate credentials for the script functionality\n"
        error_msg += "ERROR: and run 'gen_edgerc %s' to generate the credential file\n" % section_name
        sys.exit(error_msg)

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
        httpErrors(endpoint_result.status_code, path, endpoint_result.json())
        if debug: print ">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n"
        return endpoint_result.json()

def httpErrors(status_code, endpoint, result):
        if status_code == 403:
                error_msg =   "ERROR: Call to %s failed with a 403 result\n" % endpoint
                error_msg +=  "ERROR: This indicates a problem with authorization.\n"
                error_msg +=  "ERROR: Please ensure that the credentials you created for this script\n"
                error_msg +=  "ERROR: have the necessary permissions in the Luna portal.\n"
                error_msg +=  "ERROR: Also check the hostname you are attempting to purge.\n"
                error_msg +=  "ERROR: Problem details: %s\n" % result["detail"]
                exit(error_msg)

        if status_code in [400, 401]:
                error_msg =   "ERROR: Call to %s failed with a %s result\n" % (endpoint, status_code)
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

        if status_code == 507:
                error_msg = "ERROR: Too many pending requests\n"
                error_msg += "ERROR: Please try again later\n"
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
  	httpErrors(endpoint_result.status_code, path, endpoint_result.json())
        return endpoint_result.json()

def postPurgeRequest(host, paths):
	purge_obj = { "hostname": host,
                      "objects" : [ p for p in paths ]
		    }
	print "Invadating  %s" % json.dumps(purge_obj)
	purge_post_result = postResult('/ccu/v3/invalidate/url', json.dumps(purge_obj))
	return purge_post_result

if __name__ == "__main__":
        if not config.ccu_host or not config.ccu_paths:
                print "The arguments --ccu_host and --ccu_paths must be specified"
                print "where "
                print "   --ccu_host is the hostname to invalidate and"
                print "   --ccu_path is the space separated list of paths to invalidate"
                print "For example:"
                print '   --ccu_host="example.com" --ccu_paths="/index.html /image.jpg"'
                exit(1)

        host = config.ccu_host
        paths = config.ccu_paths.split()
        print "invalidating paths %s on host %s"%(paths, host)
	purge_post_result = postPurgeRequest(host, paths)
        print "result:", purge_post_result
