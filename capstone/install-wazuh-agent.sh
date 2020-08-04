#!/bin/bash

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
echo "#USER_INSTALL_TYPE=\"agent\"" >> wazuh/etc/preloaded-vars.conf

# Install Wazuh.
printf "\n" | (cd wazuh && ./install.sh)

# Install agent.
WAZUH_MANAGER="wazuh-manager-instance" apt-get install wazuh-agent

# Disable updates.
sed -i "s/^deb/#deb/" /etc/apt/sources.list.d/wazuh.list
apt-get update
