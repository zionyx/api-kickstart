<?php
# This file is _only_ used to setup and run these command line examples.
include __DIR__ . '/composer.php';
$cli = new League\CLImate\CLImate();
$cli->arguments->add(
    [
        'debug' => [
            'prefix' => 'd',
            'longPrefix' => 'debug',
            'description' => 'Enable Debug Mode: Output HTTP traffic to STDOUT',
            'defaultValue' => false,
            'noValue' => true
        ],
        'verbose' => [
            'prefix' => 'v',
            'longPrefix' => 'verbose',
            'description' => 'Enable Verbose Mode: Output response bodies (JSON) to STDOUT',
            'defaultValue' => false,
            'noValue' => true
        ],
        'file' => [
            'prefix' => 'e',
            'longPrefix' => 'edgerc',
            'description' => 'Path to .edgerc file',
            'defaultValue' => null,
        ],
        'section' => [
            'prefix' => 's',
            'longPrefix' => 'section',
            'description' => '.edgerc section to use',
            'defaultValue' => 'default',
        ],
        'help' => [
            'prefix' => 'h',
            'longPrefix' => 'help',
            'description' => 'Show this help',
            'defaultValue' => false,
            'noValue' => true
        ]
    ]
);
$cli->arguments->parse($_SERVER['argv']);
if ($cli->arguments->get('help')) {
    $cli->usage();
    exit;
}
if ($cli->arguments->get('debug')) {
    \Akamai\Open\EdgeGrid\Client::setDebug(true);
}
if ($cli->arguments->get('verbose')) {
    \Akamai\Open\EdgeGrid\Client::setVerbose(true);
}
$configFile = $cli->arguments->get('config');
$configSection = $cli->arguments->get('section');

if (!extension_loaded('curl')) {
    $cli->whisper("PHP curl extension not enabled. Output from --debug may be less useful.");
}
