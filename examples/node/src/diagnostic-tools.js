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
 * Example of using the Akamai OPEN diagnostic-tools API
 * https://developer.akamai.com/api/luna/diagnostic-tools/reference.html
 */

var path = require('path');
var os = require('os');
var prettyJSON = require('prettyjson');
var argv = require('minimist')(process.argv.slice(2));
var EdgeGrid = require('edgegrid');

var debug = argv.debug ? true : false;
var verbose = argv.verbose ? true : false;
var sectionName = "default";
var edgercPath = path.join(os.homedir(), "/.edgerc");
var headers = argv.headers ? argv.headers : {};

var eg = new EdgeGrid({
  path: edgercPath,
  section: sectionName,
  debug: debug
});

eg.auth({
  path: '/diagnostic-tools/v1/locations',
  method: 'GET',
  headers: {},
  body: {}
});

eg.send(function(data, response) {
  console.log("\nRequesting locations that support the diagnostic-tools API.");
  console.log("Data: ", data);

  // Convert data to JSON format
  data = JSON.parse(data);

  // Pick random location
  var locationCount = data.locations.length;
  var location = data.locations[Math.floor(Math.random() * locationCount)];

  console.log("There are " + locationCount + " locations that can run dig in the Akamai Network.");
  console.log("We will make our call from " + location);

  // Prettify the output and list locations
  // console.log("\nData received from diagnostic-tools request:");
  // console.log(prettyJSON.render(data));

  // Start dig request
  makeDigRequest(location);
});

function makeDigRequest(location) {
  console.log("Starting dig request, this may take a moment...");
  // Perform dig request for developer.akamai.com using the Akamai server 
  // location specified and query type 'A' which performs a mapping to an IPv4
  // address
  var digParameters = {
    "hostname": "developer.akamai.com",
    "queryType": "A",
    "location": location
  };

  // Call auth, passing the query string parameters in via the 'qs' property
  eg.auth({
    path: '/diagnostic-tools/v1/dig',
    method: 'GET',
    headers: {},
    body: {},
    qs: digParameters
  });

  eg.send(function(data, response) {
    // Convert data to JSON format
    data = JSON.parse(data);

    // Display the results from dig
    console.log("\nData received from dig request:");
    console.log(prettyJSON.render(data));
  });
}
