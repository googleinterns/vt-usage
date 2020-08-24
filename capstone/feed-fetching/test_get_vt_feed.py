import bz2
import io
import os
import pytest
import requests
import unittest
from datetime import datetime
from unittest.mock import patch, Mock


class MockResponse:
    def __init__(self, status_code=200, text='', content=b''):
        self.status_code = status_code
        self.text = text
        self.content = content



class TestFeedFetching(unittest.TestCase):
    @unittest.mock.patch('os.environ.get', return_value='test-key')
    @unittest.mock.patch('requests.get', return_value=MockResponse(status_code=200, content=b'vt-feed'))
    @unittest.mock.patch('bz2.open', return_value=io.BytesIO(b'{ "attributes": { "attr1": "val1", "attr2": "val2" } }'))
    def test_get_feed(self, bz2_open, requests_get, os_environ):
        import get_vt_feed
        result = list(get_vt_feed.get_feed(0))

        os.environ.get.assert_called_with('VTKEY')
        filename = datetime.utcnow().strftime('%Y%m%d%H%M')
        requests.get.assert_called_once_with('https://www.virustotal.com/api/v3/feeds/files/{}'.format(filename),
                                            headers={'X-Apikey': 'test-key'})
        bz2.open.assert_called_once()
        assert result == [{'attr1': 'val1', 'attr2': 'val2'}]


    def test_prepare_doc(self):
        import get_vt_feed

        assert get_vt_feed.prepare_doc({'md5': '', 'md6': '', 'sha1': '', 'sha256': '', 'field': ''}) == \
            {'md5': '', 'sha1': '', 'sha256': ''}
        
        assert get_vt_feed.prepare_doc({'field1': 1, 'field2': 2, 'first_submission_date': 1598269912}) == \
            {'first_submission_date': datetime(2020, 8, 24, 14, 51, 52)}
        
        assert get_vt_feed.prepare_doc({'field1': 1, 'field2': 2, 'last_submission_date': 1598269912}) == \
            {'last_submission_date': datetime(2020, 8, 24, 14, 51, 52)}

        feed = {field: field for field in get_vt_feed.ALLOWED_FIELDS}
        feed.update({'first_submission_date': 0, 'last_submission_date': 0})
        result = get_vt_feed.prepare_doc(feed)
        feed.update({'first_submission_date': datetime(1970, 1, 1, 3, 0), 'last_submission_date': datetime(1970, 1, 1, 3, 0)})
        assert result == feed

if __name__ == "__main__":
    unittest.main()
