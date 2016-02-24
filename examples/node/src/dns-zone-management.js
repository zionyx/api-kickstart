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
 * Example of calculating Origin Offload using the Akamai Events Center API
 *
 * Instructions:
 *
 * Property Manager: https://developer.akamai.com/api/luna/papi/overview.html
 * Event Center: https://developer.akamai.com/api/luna/events/overview.html
 *
 * TODO:
 * - Add instructions on provisioning credentials to include PAPI and EventCenter
 * - Find an account with Data that we can pull to test out bandwidth calcs. 
 * currently, data is not being returned in getBandwidthUsage so can't test.
 */

var path = require('path');
var os = require('os');
var prettyJSON = require('prettyjson');
var async = require('async');
var argv = require('minimist')(process.argv.slice(2));
var EdgeGrid = require('edgegrid');

// Parse command-line arguments
var debug = argv.debug ? true : false;
var verbose = argv.verbose ? true : false;
var edgercPath = path.join(os.homedir(), "/.edgerc");
var headers = argv.headers ? argv.headers : {};

// The name of the section in the .edgerc with Read and Write access to the 
// DNS Zone Management APIs.
var sectionName = "dns";

// Instantiate the EdgeGrid object with the local .edgerc file path and 
// appropriate section name.
var eg = new EdgeGrid({
  path: edgercPath,
  section: sectionName,
  debug: debug
});

/**
 * Retrieves the zone configuration for the specified zone.
 * 
 * @param  {String}   zone     The zone who configuration should be retrieved.
 * @param  {Function} callback Function to be called after retrieval.
 */
function getZoneConfiguration(zone, callback) {
  console.log("Retrieving zone configuration for " + zone + " ...");

  eg.auth({
    path: '/config-dns/v1/zones/' + zone,
    method: 'GET',
    headers: {},
    body: {}
  });

  eg.send(function(data, response) {
    console.log("Status: " + response.statusCode);

    // If a 404 is returned, this means that the configuration does not yet 
    // exist and a record must be added to the zone.
    if (response.statusCode == "404") {
      return callback("Zone configuration does not yet exist. You must add " +
        "records to zone before configuration will be created.");
    }

    data = JSON.parse(data);
    console.log(prettyJSON.render(data));
  });
}

/**
 * Modifies an existing zone configuration to add a new A-record.
 *
 * @param  {String}   zone     The zone who configuration should be retrieved.
 * @param  {String}   config   The configuration file to update.
 * @param  {Function} callback Function to be called after retrieval.
 */
function modifyZoneConfiguration(zone, config, callback) {
  console.log("Adding A-Record to configuration...");

  // Sample A-Record
  var record = {
    "active": true,
    "name": "test-record",
    "target": "0.0.0.0",
    "ttl": 7200
  };

  // If the config has an existing A-record array, add the record to it. 
  // Otherwise, create and add a new array with containing the record.
  if (config.zone.hasOwnProperty('a')) {
    config.zone.a.push(record);
  } else {
    config.zone.a = [record];
  }

  // Increment the serial on the configuration
  console.log("Updating serial: " + config.zone.soa.serial);
  config.zone.soa.serial++;
  console.log("Serial updated: " + config.zone.soa.serial);

  // PUSH the updated configuration
  eg.auth({
    path: '/config-dns/v1/zones/' + zone,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: config
  });

  eg.send(function(data, response) {
    console.log("Request returned:");
    data = JSON.parse(data);
    console.log(prettyJSON.render(data));
  });
}

/**
 * Creates and adds a new zone configuration file. This will be used when 
 * creating a zone configuration file for the first time.
 *
 * @param  {String}   zone     The zone who configuration should be retrieved.
 * @param  {Function} callback Function to be called after retrieval.
 */
function addZoneConfiguration(zone, callback) {
  console.log("Adding new configuration to zone: " + zone + " ...");

  // Sample configuration containing a single a-record. Note that the "token"
  // property must be set to "new" when creating a new zone configuration.
  var config = {
    "token": "new",
    "zone": {
      "name": "example.com",
      "soa": {
        "contact": "hostmaster.test.com.",
        "expire": 604800,
        "minimum": 180,
        "originserver": "server.test.com.",
        "refresh": 900,
        "retry": 300,
        "serial": 123456,
        "ttl": 900
      },
      "a": [{
        "active": true,
        "name": "www",
        "target": "1.2.3.4",
        "ttl": 3600
      }],
    }
  };

  // PUSH the updated configuration
  eg.auth({
    path: '/config-dns/v1/zones/' + zone,
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: config
  });

  eg.send(function(data, response) {
    console.log("Request returned:");
    data = JSON.parse(data);
    console.log(prettyJSON.render(data));
  });
}
