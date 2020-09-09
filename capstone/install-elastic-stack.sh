#!/bin/bash
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
