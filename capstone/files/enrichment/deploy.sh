#!/bin/bash

scp virustotal.py wazuh-manager:virustotal
scp 0490-virustotal_rules.xml wazuh-manager:0490-virustotal_rules.xml

ssh wazuh-manager << EOF
    sudo su

    chmod 750 virustotal
    chown root:ossec virustotal

    mv virustotal /var/ossec/integrations/virustotal
    mv 0490-virustotal_rules.xml /var/ossec/ruleset/rules

    if ! grep -q "<name>virustotal</name>" /var/ossec/etc/ossec.conf; then
        echo "Updating configuration"
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
