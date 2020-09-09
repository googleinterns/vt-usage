#!/bin/bash

scp virustotal.py wazuh-manager:virustotal

ssh wazuh-manager << EOF
    sudo su

    chmod 750 virustotal
    chown root:ossec virustotal

    mv virustotal /var/ossec/integrations/virustotal

    if ! grep -q "<name>virustotal</name>" /var/ossec/etc/ossec.conf; then
        echo "
<ossec_config>
    <integration>
        <name>virustotal</name>
        <api_key>YOUR_API_KEY</api_key>
        <group>syscheck</group>
        <alert_format>json</alert_format>
    </integration>
</ossec_config>" >> /var/ossec/etc/ossec.conf
    fi

    systemctl restart wazuh-manager
EOF
