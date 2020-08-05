#!/bin/bash

# Fail if any command fails.
set -e

# Add the Elastic repository and its GPG key.
apt-get -y install curl apt-transport-https
curl -s https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list
apt-get -y update

# Install Elasticsearch.
apt-get -y install elasticsearch=7.8.1

# Bind Elastic to IP.
echo "network.host: \"elastic-stack-instance\"" >> /etc/elasticsearch/elasticsearch.yml

echo "node.name: \"Capstone\"" >> /etc/elasticsearch/elasticsearch.yml
echo "cluster.initial_master_nodes: [\"Capstone\"]" >> /etc/elasticsearch/elasticsearch.yml

# Start Elasticsearch service
systemctl daemon-reload
systemctl enable elasticsearch.service
systemctl start elasticsearch.service
