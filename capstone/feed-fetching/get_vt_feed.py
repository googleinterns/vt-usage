import bz2
import io
import itertools
import json
import os
import requests
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch

es = Elasticsearch('elastic-stack-instance:9200')
apikey = os.environ('VTKEY')  # is there a better way to store api key?

fields_allowed = {'capabilities_tags', 'first_submission_date', 'last_submission_date', 'last_analysis_stats',
                  'meaningful_name', 'sigma_analysis_stats', 'type_description', 'type_tag', 'reputation', 'vhash',
                  'sha1', 'sha256', 'imphash', 'md5', 'times_submitted', 'authentihash', 'tags', 'timestamp'}


def get_feed(timedelta_mins: int):
    filename = (datetime.utcnow() - timedelta(minutes=timedelta_mins)).strftime('%Y%m%d%H%M')
    response = requests.get('https://www.virustotal.com/api/v3/feeds/files/{}'.format(filename),
                            headers={'X-Apikey': apikey})

    if response.status_code != 200:
        raise 'Feed fetching for {} failed with {}: {}'.format(filename, response.status_code, response.text)  # f-strings work only in python >= 3.6  :c
    stream = io.BytesIO(response.content)

    for line in bz2.open(stream):
        yield json.loads(line.decode())['attributes']


def prepare_doc(feed: dict):
    for field in list(feed.keys()):
        if field not in fields_allowed:
            del feed[field]

    if 'first_submission_date' in feed:
        feed['first_submission_date'] = datetime.fromtimestamp(feed['first_submission_date'])
    if 'last_submission_date' in feed:
        feed['last_submission_date'] = datetime.fromtimestamp(feed['last_submission_date'])
    return feed


def main():
    for doc in itertools.chain.from_iterable(get_feed(i) for i in range(60, 75)):
        prepared = prepare_doc(doc)
        date = datetime.now().strftime("%Y.%m.%d")
        es.index(index='virustotal-feed-{}'.format(date), body=prepared)


if __name__ == "__main__":
    main()