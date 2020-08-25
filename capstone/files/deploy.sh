#!/bin/bash

NC='\033[0m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'

set -e

echo -e "${YELLOW}Build docker image...${NC}"
docker build -t files-app .
echo -e "${GREEN}Image built!${NC}"

echo -e "${YELLOW}Save image...${NC}"
docker save -o ./files-app-image files-app
echo -e "${GREEN}Image saved!${NC}"

echo -e "${YELLOW}Upload to server...${NC}"
scp files-app-image wazuh-agent:~
echo -e "${GREEN}Upload finished!${NC}"

echo -e "${YELLOW}Deploy the app...${NC}"
ssh wazuh-agent << EOF
  set -e
  docker stop files-app
  docker rm files-app
  docker load -i files-app-image
  docker run --restart=always --name=files-app -d -v /usr/media:/app/media -p 80:80 files-app
EOF

echo -e "${GREEN}The app has ben deployed successfully!${NC}"
