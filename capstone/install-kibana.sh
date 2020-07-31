#!/bin/bash

# Fail if any command fails.
set -e

# Install Kibana.
apt-get install kibana=7.8.1
(cd /usr/share/kibana/ && sudo -u kibana bin/kibana-plugin install https://packages.wazuh.com/wazuhapp/wazuhapp-3.13.1_7.8.1.zip)

# Bind Kibana to IP.
sed "s/#server.host:*/server.host: \"elastic-stack-instance\"" /etc/kibana/kibana.yml

# Configure the URL of the Elasticsearch.
sed "s/#elasticsearch.hosts:*/elasticsearch.hosts: [\"http://elastic-stack-instance:9200\"]" /etc/kibana/kibana.yml

# Increase heap size for Kibana.
echo "NODE_OPTIONS=\"--max_old_space_size=2048\"" >> /etc/default/kibana

# Start Kibana.
systemctl daemon-reload
systemctl enable kibana.service
systemctl start kibana.service

# Disable Elasticsearch updates.
sed -i "s/^deb/#deb/" /etc/apt/sources.list.d/elastic-7.x.list
apt-get update
