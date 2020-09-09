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
import os
import requests
import unittest
from datetime import datetime
from unittest.mock import patch, Mock

import get_vt_feed


class MockResponse:
    def __init__(self, status_code=200, text='', content=b''):
        self.status_code = status_code
        self.text = text
        self.content = content



class TestFeedFetching(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vtkey = get_vt_feed.API_KEY
        get_vt_feed.API_KEY = 'test-key'

    @classmethod
    def tearDownClass(cls):
        get_vt_feed.API_KEY = cls.vtkey

    @unittest.mock.patch('requests.get', return_value=MockResponse(status_code=200, content=b'vt-feed'))
    @unittest.mock.patch('bz2.open', return_value=io.BytesIO(b'{ "attributes": { "attr1": "val1", "attr2": "val2" } }'))
    def test_get_feed(self, bz2_open, requests_get):
        result = list(get_vt_feed.get_feed(0))

        filename = datetime.utcnow().strftime('%Y%m%d%H%M')
        requests.get.assert_called_once_with('https://www.virustotal.com/api/v3/feeds/files/{}'.format(filename),
                                            headers={'X-Apikey': 'test-key'})
        bz2.open.assert_called_once()
        assert result == [{'attr1': 'val1', 'attr2': 'val2'}]
    

    @unittest.mock.patch('requests.get', return_value=MockResponse(status_code=400, text='bad test request'))
    @unittest.mock.patch('bz2.open', return_value=io.BytesIO(b'{ "attributes": { "attr1": "val1", "attr2": "val2" } }'))
    def test_get_feed_fail(self, bz2_open, requests_get):
        filename = datetime.utcnow().strftime('%Y%m%d%H%M')
        with self.assertRaisesRegex(Exception, 'Feed fetching for {} failed with 400: bad test request'.format(filename)):
            list(get_vt_feed.get_feed(0))


    def test_prepare_doc(self):
        assert get_vt_feed.prepare_doc({'md5': '', 'md6': '', 'sha1': '', 'sha256': '', 'field': ''}) == \
            {'md5': '', 'sha1': '', 'sha256': ''}
        
        assert get_vt_feed.prepare_doc({'field1': 1, 'field2': 2, 'first_submission_date': 1598269912}) == \
            {'first_submission_date': datetime.fromtimestamp(1598269912)}
        
        assert get_vt_feed.prepare_doc({'field1': 1, 'field2': 2, 'last_submission_date': 1598269912}) == \
            {'last_submission_date': datetime.fromtimestamp(1598269912)}

        feed = {field: field for field in get_vt_feed.ALLOWED_FIELDS}
        feed.update({'first_submission_date': 0, 'last_submission_date': 0})
        result = get_vt_feed.prepare_doc(feed)
        feed.update({'first_submission_date': datetime.fromtimestamp(0), 'last_submission_date': datetime.fromtimestamp(0)})
        assert result == feed

if __name__ == "__main__":
    unittest.main()
