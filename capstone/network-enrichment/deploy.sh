#! /bin/bash

scp custom_vt_network.py wazuh-manager:custom-vt-network
ssh wazuh-manager << EOF
    sudo su
    mv custom-vt-network /var/ossec/integrations/custom-vt-network
    chmod 750 /var/ossec/integrations/custom-vt-network
    chown root:ossec /var/ossec/integrations/custom-vt-network

    if ! grep -q "custom-vt-network" /var/ossec/etc/ossec.conf; then
        echo "
<ossec_config>
    <integration>
        <name>custom-vt-network</name>
        <group>sshd</group>
        <api_key>YOUR_API_KEY</api_key>
        <alert_format>json</alert_format>
    </integration>
</ossec_config>" >> /var/ossec/etc/ossec.conf
    fi

    if [ ! -f /var/ossec/ruleset/rules/1000-virustotal-enrichment_rules.xml ]; then
        echo "
<group name="virustotal-enrichment,">
    <rule id="100010" level="5">
        <decoded_as>json</decoded_as>
        <field name="integration">custom-vt-network</field>
        <description>Virustotal data enrichment.</description>
    </rule>
</group>" > /var/ossec/ruleset/rules/1000-virustotal-enrichment_rules.xml
    fi

    systemctl restart wazuh-manager
EOF
