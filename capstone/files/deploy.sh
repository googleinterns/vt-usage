#!/bin/bash
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


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
