#!/bin/bash

# Fail if any command fails.
set -e

# Install needed packages.
apt-get install curl apt-transport-https lsb-release gnupg2

# Install the Wazuh repository GPG key.
curl -s https://packages.wazuh.com/key/GPG-KEY-WAZUH | apt-key add -

# Add the repository.
echo "deb  https://packages-dev.wazuh.com/staging/apt/ stable main" | tee /etc/apt/sources.list.d/wazuh.list

# Update the package information.
apt-get update

# Install agent.
WAZUH_MANAGER="wazuh-manager-instance" apt-get install wazuh-agent

# Disable updates.
sed -i "s/^deb/#deb/" /etc/apt/sources.list.d/wazuh.list
apt-get update
