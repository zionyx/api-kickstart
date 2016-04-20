#! /usr/bin/env node

/**
Copyright 2015 Akamai Technologies, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.

You may obtain a copy of the License at 

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
**/

/**
 * Example of using the Akamai OPEN Prolexic Analytics API
 * https://developer.akamai.com/api/luna/prolexic-analytics/reference.html
 */

var path = require('path'),
  os = require('os'),
  prettyJSON = require('prettyjson'),
  argv = require('minimist')(process.argv.slice(2)),
  async = require('async'),
  logger = require('./logger'),
  EdgeGrid = require('edgegrid');

var debug = argv.debug ? true : false,
  verbose = argv.verbose ? true : false,
  edgercPath = path.join(os.homedir(), "/.edgerc"),
  headers = argv.headers ? argv.headers : {},
  sectionName = "prolexic-analytics";

var eg = new EdgeGrid({
  path: edgercPath,
  section: sectionName,
  debug: debug
});

// Retrieve random location, then make a Dig request with it
// async.waterfall([getLocations, makeDigRequest]);

/**
 * Retrieves the metric types that area available to this account.
 * 
 * @param  {Function} callback Callback that accepts location.
 */
function getMetricTypes(callback) {
  console.log("getMetricTypes");

  eg.auth({
    path: '/prolexic-analytics/v1/metric-types',
    method: 'GET'
  });

  eg.send(function(data, response) {
    console.log("Requesting list of available metric types...");

    // Pick random location
    // data = JSON.parse(data);
    console.log("Data: ", data);

    // if (verbose) logger.logResponse(response);
    // console.log("\nThere are " + locationCount + " locations that can run dig in the Akamai Network,");
    // console.log("We will make our call from " + location);

    // // Return location to be used in Dig Request
    // if (callback) return callback(null, location);
  });
}
getMetricTypes(null);