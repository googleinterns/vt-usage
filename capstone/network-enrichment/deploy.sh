#! /bin/bash

scp custom_vt_network.py wazuh-manager:custom-vt-network
ssh wazuh-manager << EOF
    sudo su
    mv custom-vt-network /var/ossec/integrations/custom-vt-network
    chmod 750 /var/ossec/integrations/custom-vt-network
    chown root:ossec /var/ossec/integrations/custom-vt-network

    OSSECCONF=$(cat /var/ossec/etc/ossec.conf)
    if [[ '$OSSECCONF' != *'custom-vt-network'* ]]; then
        echo "
<ossec_config>
    <integration>
        <name>custom-vt-network</name>
        <group>sshd</group>
        <api_key>bd23bf03d9975b3b5c22b5963c0b63293fa38170daaf2d8a5ab3c84747819799</api_key>
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
