#!/usr/bin/env bash
sudo apt-get install --yes php5-cli php5-curl curl
curl -sS https://getcomposer.org/installer | php
php composer.phar install --prefer-source