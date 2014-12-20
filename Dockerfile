FROM ubuntu:12.04
MAINTAINER Kirsten Hunter (khunter@akamai.com)
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y -q curl python-all python-pip wget vim
ADD ./examples /opt/examples/
WORKDIR /opt/examples
RUN pip install -r requirements.txt
