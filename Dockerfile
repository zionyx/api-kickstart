FROM ubuntu:15.04
MAINTAINER Kirsten Hunter (khunter@akamai.com)
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y -q curl python-all wget vim
ADD ./examples /opt/examples
ADD ./contrib/python /opt/examples/python/contrib
WORKDIR /opt/examples/python
RUN python /opt/examples/python/tools/setup.py install
ADD ./MOTD /opt/MOTD
RUN echo "cat /opt/MOTD" >> /root/.bashrc
