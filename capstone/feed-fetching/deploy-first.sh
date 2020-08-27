#!/bin/bash

curl -X PUT "elastic-stack-instance:9200/_ilm/policy/remove-old-vt-feed" -H 'Content-Type: application/json' -d'
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "set_priority": {
            "priority": 100
          }
        }
      },
      "delete": {
        "min_age": "1d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
'

curl -X PUT "elastic-stack-instance:9200/_template/virustotal-feed?include_type_name" -H 'Content-Type: application/json' -d'
{
  "order": 0,
  "index_patterns": [
    "virustotal-feed-*"
  ],
  "settings": {
    "index": {
      "lifecycle": {
        "name": "remove-old-vt-feed"
      }
    }
  },
  "mappings": {
    "_doc": {
      "_source": {
        "excludes": [],
        "includes": [],
        "enabled": true
      },
      "_meta": {},
      "_routing": {
        "required": false
      },
      "dynamic": true,
      "numeric_detection": true,
      "date_detection": true,
      "dynamic_date_formats": [
        "strict_date_optional_time",
        "yyyy/MM/dd HH:mm:ss Z||yyyy/MM/dd Z"
      ],
      "dynamic_templates": [],
      "properties": {}
    }
  }
}
'

CRONTAB=$(crontab -l 2>/dev/null)
JOB='*/15 * * * * ~/cron/feed-fetching/venv/bin/python3 ~/cron/feed-fetching/get_vt_feed.py'

if [[ "$CRONTAB" != *"$JOB"* ]]; then
        (echo -e "$CRONTAB\nVTKEY=$VTKEY\n$JOB") | crontab -
fi
