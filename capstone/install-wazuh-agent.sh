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

# Install needed packages.
apt-get -y update
apt-get -y install python gcc make libc6-dev curl policycoreutils automake autoconf libtool git

# Clone Wazuh repository.
git clone https://github.com/wazuh/wazuh.git

# Copy wazuh.conf.
cp wazuh.conf wazuh/etc/preloaded-vars.conf

# Set install agent.
printf "\nUSER_INSTALL_TYPE=\"agent\"" >> wazuh/etc/preloaded-vars.conf

# Install Wazuh.
printf "\n" | (cd wazuh && ./install.sh)

# Install agent.
WAZUH_MANAGER="wazuh-manager-instance" apt-get install wazuh-agent

# Disable updates.
sed -i "s/^deb/#deb/" /etc/apt/sources.list.d/wazuh.list
apt-get update
