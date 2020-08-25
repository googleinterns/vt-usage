# User friendly file hosting

## Overview
This FastAPI app that is capable of providing
really simple file-hosting service.

## Run  
To run it in development mode you should run `main.py`.
The best way to do it is use virtual environment.
```shell script
python3 -m venv venv
. venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Deploy
This app can be deployed to server using Docker.
To run this script smoothly you need to:
* be able to run docker commands without `sudo`
both locally and on production
* have the `~/.ssh/config` set, you can see the example below

If you have met this requirements you should be able to
deploy the app by running `./deploy.sh`.

### Example of ~/.ssh/config
```
Host wazuh-agent
  HostName ip.or.hostname
  User your-user-name
  IdentityFIle ~/.ssh/id_rsa
```
