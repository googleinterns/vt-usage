#! /bin/bash

scp custom_vt_network.py wazuh-manager:custom-vt-network
ssh wazuh-manager << EOF
    sudo su
    mv custom-vt-network /var/ossec/integrations/custom-vt-network
    chmod 750 /var/ossec/integrations/custom-vt-network
    chown root:ossec /var/ossec/integrations/custom-vt-network

    # TODO : ADD INTEGRATION TO OSSEC.CONF

    if [ ! -f /var/ossec/ruleset/rules/1000-virustotal-enrichment_rules.xml ]; then
        echo "<group name="virustotal-enrichment,">
                <rule id="100010" level="5">
                    <decoded_as>json</decoded_as>
                    <field name="integration">custom-vt-network</field>
                    <description>Virustotal data enrichment.</description>
                </rule>
            </group>" > /var/ossec/ruleset/rules/1000-virustotal-enrichment_rules.xml
    fi

    systemctl restart wazuh-manager
EOF
