#!/bin/bash

# Install needed packages.
apt-get update
apt-get install curl apt-transport-https lsb-release gnupg2

# Install GPG key.
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add -

# Add the repository.
echo "deb https://packages.wazuh.com/3.x/apt/ stable main" | tee -a /etc/apt/sources.list.d/wazuh.list

# Update package information.
apt-get update

# Install the Wazuh manager.
apt-get install wazuh-manager


# Install NodeJS.
curl -sL https://deb.nodesource.com/setup_10.x | bash -
apt-get install nodejs

# Install Wazuh API.
apt-get install wazuh-api

# Disable auto-updates.
sed -i "s/^deb/#deb/" /etc/apt/sources.list.d/wazuh.list
apt-get update


# Add the Elastic repository and its GPG key.
apt-get install curl apt-transport-https
curl -s https://artifacts.elastic.co/GPG-KEY-elasticsearch | apt-key add -
echo "deb https://artifacts.elastic.co/packages/7.x/apt stable main" | tee /etc/apt/sources.list.d/elastic-7.x.list
apt-get update

# Install Filebeat.
apt-get install filebeat=7.8.1

# Download the Filebeat config file from the Wazuh repository.
curl -so /etc/filebeat/filebeat.yml https://raw.githubusercontent.com/wazuh/wazuh/v3.13.1/extensions/filebeat/7.x/filebeat.yml

# Download the alerts template for Elasticsearch.
curl -so /etc/filebeat/wazuh-template.json https://raw.githubusercontent.com/wazuh/wazuh/v3.13.1/extensions/elasticsearch/7.x/wazuh-template.json

# Download the Wazuh module for Filebeat.
curl -s https://packages.wazuh.com/3.x/filebeat/wazuh-filebeat-0.1.tar.gz | sudo tar -xvz -C /usr/share/filebeat/module

# Set elastic server ip.
sed "s/YOUR_ELASTIC_SERVER_IP/elastic-stack-instance" /etc/filebeat/filebeat.yml

# Enable Filebit service.
systemctl daemon-reload
systemctl enable filebeat.service
systemctl start filebeat.service
