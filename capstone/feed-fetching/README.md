# VirusTotal Feed fetching

This script fetches VT feed once in 15 minutes and adds it to a new elasticsearch index. 

## Deployment

Updated script can be uploaded to server using `upload.sh`. You have to **set up ssh config** file prior to running the script. The example of config file is below.

Since the cron job is created once and don't need to be updated, its configuration is not stated in the script. If you are **deploying first time**, you have to create it manually. Run `crontab -e` and add following lines:

```
VTKEY=<api key>
*/15 * * * * ~/cron/feed-fetching/venv/bin/python3 ~/cron/feed-fetching/get_vt_feed.py
```

## Erasing old data

Since VT Feed has lots of files, it can take up a lot of space. To avoid disk space overflow, you should enable [ILM Policies](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html).

## Example of ~/.ssh/config

```
Host wazuh-agent
  HostName ip.or.hostname
  User your-user-name
  IdentityFIle ~/.ssh/id_rsa
```
