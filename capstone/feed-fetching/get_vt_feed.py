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

import bz2
import io
import itertools
import json
import os
import requests
from time import time
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

es = Elasticsearch('elastic-stack-instance:9200')
API_KEY = os.environ.get('VTKEY')  # is there a better way to store api key?
ALLOWED_FIELDS = {'capabilities_tags', 'first_submission_date', 'last_submission_date', 'last_analysis_stats',
                  'meaningful_name', 'sigma_analysis_stats', 'type_description', 'type_tag', 'reputation', 'vhash',
                  'sha1', 'sha256', 'imphash', 'md5', 'times_submitted', 'authentihash', 'tags', 'timestamp'}


def get_feed(timedelta_mins: int):
    filename = (datetime.utcnow() - timedelta(minutes=timedelta_mins)).strftime('%Y%m%d%H%M')
    response = requests.get('https://www.virustotal.com/api/v3/feeds/files/{}'.format(filename),
                            headers={'X-Apikey': API_KEY})

    if response.status_code != 200:
        raise Exception('Feed fetching for {} failed with {}: {}'.format(filename, response.status_code, response.text))
    stream = io.BytesIO(response.content)

    for line in bz2.open(stream):
        yield json.loads(line.decode())['attributes']


def prepare_doc(doc: dict):
    """
    Prepare file from VirusTotal feed to adding to Elasticsearch.

    Args:
      - doc: document from VT Feed.
    Returns:
      the doc left with only allowed fields and formatted for elastic timestamps.
    """
    summary_doc = {key: val for key, val in doc.items() if key in ALLOWED_FIELDS}

    if 'first_submission_date' in summary_doc:
        summary_doc['first_submission_date'] = datetime.fromtimestamp(summary_doc['first_submission_date'])
    if 'last_submission_date' in summary_doc:
        summary_doc['last_submission_date'] = datetime.fromtimestamp(summary_doc['last_submission_date'])
    return summary_doc


def main():
    for doc in itertools.chain.from_iterable(get_feed(i) for i in range(60, 75)):
        prepared = prepare_doc(doc)
        date = datetime.now().strftime("%Y.%m.%d")
        es.index(index='virustotal-feed-{}'.format(date), body=prepared)


if __name__ == "__main__":
    main()
