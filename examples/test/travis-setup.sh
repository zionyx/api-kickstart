#!/usr/bin/env bash
sudo apt-get update
START=$PWD
cd examples/$LANGUAGE
test/travis-setup.sh
cd $START
