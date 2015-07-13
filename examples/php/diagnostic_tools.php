#!/usr/bin/env php
<?php
require_once __DIR__ . '/cli/init.php';

$client = Akamai\Open\EdgeGrid\Client::createFromEdgeRcFile($configSection, $configFile);

# Request locations that support the diagnostic-tools
echo "Requesting locations that support the diagnostic-tools API.\n";

try {
    $response = $client->get('/diagnostic-tools/v1/locations');
    if ($response) {
        $result = json_decode($response->getBody());
    }

    $locations = sizeof($result->locations);
    
    printf("There are %s locations that can run dig in the Akamai Network\n", $locations);
    
    $location = $result->locations[rand(0, $locations - 1)];
    
    echo "We will make our call from " . $location . "\n";
    
    # Request the dig request the {OPEN} Developer Site IP informantion
    echo "Running dig from " . $location. "\n";
    
    $dig_parameters = [ "hostname" => "developer.akamai.com", "location" => $location, "queryType" => "A" ];
    $response = $client->get("/diagnostic-tools/v1/dig", ['query' => $dig_parameters]);
    if ($response) {
        $dig_result = json_decode($response->getBody());
    }
    
    # Display the results from dig
    echo $dig_result->dig->result;
} catch (GuzzleHttp\Exception\GuzzleException $e) {
    echo "An error occurred: " . $e->getMessage() . "\n";
}
