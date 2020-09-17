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

# Install Kibana.
apt-get install kibana=7.8.1
(cd /usr/share/kibana/ && sudo -u kibana bin/kibana-plugin install https://packages-dev.wazuh.com/trash/ui/kibana/wazuhapp-4.0.0_7.8.1.zip)
sed -i 's/v4\///g' /usr/share/kibana/plugins/wazuh/server/controllers/wazuh-api.js
sed -i 's/v4\///g' /usr/share/kibana/plugins/wazuh/server/lib/api-interceptor.js
sed -i 's/v4\///g' /usr/share/kibana/plugins/wazuh/server/lib/cron-scheduler/apiRequest.js
sed -i "s/path \= path \+ \'\/v4\'//g" /usr/share/kibana/plugins/wazuh/util/get-path.js

# Bind Kibana to IP.
sed -i "s/#server.host:.*/server.host: \"elastic-stack-instance\"/" /etc/kibana/kibana.yml

# Configure the URL of the Elasticsearch.
sed -i "s/#elasticsearch.hosts:.*/elasticsearch.hosts: [\"http:\/\/elastic-stack-instance:9200\"]/" /etc/kibana/kibana.yml

# Increase heap size for Kibana.
echo "NODE_OPTIONS=\"--max_old_space_size=2048\"" >> /etc/default/kibana

# Start Kibana.
systemctl daemon-reload
systemctl enable kibana.service
systemctl start kibana.service

# Disable Elasticsearch updates.
sed -i "s/^deb/#deb/" /etc/apt/sources.list.d/elastic-7.x.list
apt-get update
