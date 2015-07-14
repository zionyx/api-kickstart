#!/usr/bin/env php
<?php
/**
* Sample client for CCU
* Note that in order for this to work you need to provision credentials
* specifically for CCU - you cannot extend existing credentials to add
* CCU as it's managed under "CCU" in the API credential system.
* 
* Configure->Organization->Manage APIs
* Select "CCU APIs"
* Create client collections/clients
* Add authorization
*
* Put the credentials in ~/.edgerc as demonstrated by api-kickstart/sample_edgerc
*/
namespace Akamai\Open\Example;

require_once __DIR__ . '/cli/init.php';

class CcuClient
{
	/**
	 * @var \Akamai\Open\EdgeGrid\Client
	 */
	protected $client;

	public function __construct()
	{
		$this->client = \Akamai\Open\EdgeGrid\Client::createFromEdgeRcFile('ccu');
	}

	public function getQueue()
	{
		$response = $this->client->get('/ccu/v2/queues/default');
		printf("The queue currently has %s items in it\n", json_decode($response->getBody())->queueLength);
	}

	public function checkProgress($resource)
	{
		$response = $this->client->get($resource);
		return json_decode($response->getBody());
	}

	public function postPurgeRequest()
	{
		$purge_body = [
			"objects" => [
				"https://developer.akamai.com/stuff/Akamai_Time_Reference/AkamaiTimeReference.html"
			]
		];

		printf("Adding %s to queue\n", json_encode($purge_body, JSON_UNESCAPED_SLASHES));
		$response = $this->client->post('/ccu/v2/queues/default', [
			'body' => json_encode($purge_body), 
			'headers' => ['Content-Type' => 'application/json']
		]);
		return $response;
	}
}

$ccu = new CcuClient();
$ccu->getQueue();
$purge= $ccu->postPurgeRequest();
$progress = $ccu->checkProgress(json_decode($purge->getBody())->progressUri);
$seconds_to_wait = $progress->pingAfterSeconds;
printf("You should wait %s seconds before checking queue again...\n", $seconds_to_wait);
