#!/bin/bash
sudo apt-get update
sudo apt-get -y install python3 python3-dev python3-pip git libssl-dev pssh pscp
pip3 install --upgrade git+https://github.com/arthaud/python3-pwntools.git
