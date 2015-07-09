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

Sample client for Media Analytics

Put the credentials in ~/.edgerc using gen_edgerc.py
"""

import requests, logging, json, sys
from http_calls import EdgeGridHttpCaller
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
import os
session = requests.Session()
debug = True
section_name = "media"

# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig({"verbose":False},section_name)

if hasattr(config, "debug") or hasattr(config, "verbose"):
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
httpCaller = EdgeGridHttpCaller(session, debug, baseurl)

def getReportPacks():
	print
	report_packs_result = httpCaller.getResult('/media-analytics/v1/audience-analytics/report-packs')

def getReportPackInfo(reportpack):
	print
	report_pack_info = httpCaller.getResult('/media-analytics/v1/audience-analytics/report-packs/%s' % reportpack)

def getDataStores(reportpack):
	print
	report_pack_info = httpCaller.getResult('/media-analytics/v1/audience-analytics/report-packs/%s/data-stores' % reportpack)

def getData(reportpack):
	# Dimensions and metrics are retrieved with getReportPackInfo
	# Dimensions: Hourly viewers = 2002
	# Metrics: Service Provider = 942
	print
	parameters = {	'startDate': '03/22/2015:15:30',
			'endDate'  : '03/23/2015:15:30',
			'dimensions' : 846,
			'metrics'    : 608,
			'filterParams' : '[{"type":"dimension","values":["XXX XXXX"],"id":846,"condition":"in"}]' 
			}
	data_info = httpCaller.getResult('/media-analytics/v1/audience-analytics/report-packs/%s/data' % reportpack, parameters) 	
	
if __name__ == "__main__":
	getReportPacks()
	getReportPackInfo(29049)
	getDataStores(29049)
	#get dimensions and metrics from the Info call
	getData(29049)	

