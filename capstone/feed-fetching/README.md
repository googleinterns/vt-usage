# VirusTotal Feed fetching

This script fetches [VT feed](https://developers.virustotal.com/v3.0/reference#feeds-file) once in 15 minutes and adds it to a new elasticsearch index. For erasing old data it enables [ILM Policy](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html) that deletes feed older than a day.

## Dependencies

* Python >=3.5
* virtualenv
* ~/.ssh/config  ([example](##example-of-~/.ssh/config))

## Deployment

Updated script can be uploaded to server using `upload.sh`.

If you are **deploying first time**, also run `deploy-first.sh`.

## Example of ~/.ssh/config

```
Host wazuh-agent
  HostName ip.or.hostname
  User your-user-name
  IdentityFIle ~/.ssh/id_rsa
```
