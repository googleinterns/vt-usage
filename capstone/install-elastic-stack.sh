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

# Kropka jest znakiem specjalnym.
# Bind Elastic to IP.
sed "s/#network.host:.*/network.host: \"elastic-stack-instance\"/" /etc/elasticsearch/elasticsearch.yml

# Create or uncomment node.
if [ grep -xq "#node.name:" /etc/elasticsearch/elasticsearch.yml -eq 0 ]; then
    sed -e "s/#node.name:.*/node.name: \"Capstone\"/" /etc/elasticsearch/elasticsearch.yml
else
    echo "node.name: \"Capstone\"" >> /etc/elasticsearch/elasticsearch.yml
fi

if [ grep -xq "#cluster.initial_master_nodes" /etc/elasticsearch/elasticsearch.yml -eq 0 ]; then
    sed "s/#cluster.initial_master_nodes:*/cluster.initial_master_nodes: [\"Capstone\"]/" /etc/elasticsearch/elasticsearch.yml
else
    echo "cluster.initial_master_nodes: [\"Capstone\"]" >> /etc/elasticsearch/elasticsearch.yml
fi

# Start Elasticsearch service
systemctl daemon-reload
systemctl enable elasticsearch.service
systemctl start elasticsearch.service
