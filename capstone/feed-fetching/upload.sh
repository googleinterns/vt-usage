scp -r ../feed-fetching wazuh-agent:~/cron/feed-fetching
ssh wazuh-agent << EOF
    cd ~/cron/feed-fetching
    python3 -m virtualenv venv
    source venv/bin/activate
    pip3 install -r requirements.txt
EOF
