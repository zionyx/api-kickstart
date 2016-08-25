#! /usr/bin/env python
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


Sample client for billing-usage v2

NOTE: This code requires credentials set up for both the Legacy Billing Usage
API and the current Billing Center API

This client pulls the reportSources you have access to from the v1 API.
For the first result, it pulls all products from the v2 API.  Then it
creates monthly reports for the range you specify for each product, and finally 
generates a report based on this information from the v2 API.

The combination of calls should be sufficient to let
you do what you need with the billing-usage API.

Contact open-developer@akamai.com with questions, ideas
or comments.

Thanks!
"""

import requests, logging, json, sys
from http_calls import EdgeGridHttpCaller
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
import urllib
session = requests.Session()
debug = False
verbose = False
section_name = "billingusage"

if sys.version_info[0] >= 3:
     # python3
     from urllib import parse
else:
     # python2.7
     import urlparse as parse


# If all parameters are set already, use them.  Otherwise
# use the config
config = EdgeGridConfig({},"billingusage")

if hasattr(config, "debug") and config.debug:
  debug = True

if hasattr(config, "verbose") and config.verbose:
  verbose = True

# Set the config options
session.auth = EdgeGridAuth(
            client_token=config.client_token,
            client_secret=config.client_secret,
            access_token=config.access_token
)

baseurl = '%s://%s/' % ('https', config.host)

httpCaller = EdgeGridHttpCaller(session, debug, verbose, baseurl)

def getReportSources():
	print
	print ("Requesting the list of report sources")

	events_result = httpCaller.getResult('/billing-usage/v1/reseller/reportSources')
	return events_result['contents']

def getProducts(parameters):
        print
        print ("Requesting a list of products for the given time period")
        headers = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8','Accept':'application/json'}
        path = "/billing-usage/v1/products"

        data_string = parse.urlencode({p: json.dumps(parameters[p]) for p in parameters})
        products_result = session.post(parse.urljoin(baseurl,path),data=data_string, headers=headers)
        products_obj = json.loads(products_result.text)
        return products_obj['contents']

def getStatisticTypes(contractId, productId, parameters):
	print
	print ("Requesting the list of statistic types valid for product %s" % productId)
	path = "/billing-center-api/v2/contracts/%s/products/%s/statistics" % (contractId, productId)
	statistics_result = httpCaller.getResult(path, parameters)
	return statistics_result

def getMonthlyUsage(contractId, productId, parameters):
	print
	path = "/billing-center-api/v2/contracts/%s/products/%s/measures" % (contractId, productId)
	report_result = httpCaller.getResult(path, parameters)

if __name__ == "__main__":
	# getReportSources will return a list of reporting groups and/or contract ids
	# include the group or contract as contractId and the reportType as returned
	# by getReportSources
	# You could loop through them here, or just get one big kahuna report and chunk it up yourself
	reportSource = getReportSources()
	contractId = reportSource[0]['id']

	# Year and Month
	v2parameters = { 
		"year"   : 2016,
		"month"  : 8
	}

	# From year and from month
	v2parameters = {
		"fromYear" : 2016,
		"toYear" : 2016,
		"fromMonth" : 8,
		"toMonth" : 8
	}

	v1parameters = {
		"startDate" : {"month":8, "year": 2016},
		"endDate"   : {"month":9, "year": 2016},
		"reportSources" : reportSource[0]
	}

	products = getProducts(v1parameters)
	# Just grab the first product
	productId = products[0]['id']

	# Grab the statistics
	statisticTypes = getStatisticTypes(contractId, productId, v2parameters)
	for statisticType in statisticTypes:
		v2parameters["statisticName"] = statisticType["name"]
		getMonthlyUsage(contractId, productId, v2parameters)
