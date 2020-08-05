#!/bin/bash

# Setup Filebeat.
# WARNING: Run AFTER install-wazuh.sh and install-elastic-stack.sh
filebeat setup --index-management -E setup.template.json.enabled=false
