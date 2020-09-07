import json
import pytest
import requests
import socket
import sys
import unittest

# from custom_vt_network import main
import custom_vt_network

mock_vt_response = {
    'data': {
        'attributes': {
            'last_analysis_stats': {'harmless': 1, 'malicious': 2, 'undetected': 3},
            'last_https_certificate': 'last_https_certificate',
            'reputation': 'reputation',
            'tags': 'tags',
            'whois': 'whois',
        }
    }
}

mock_urls_response = {
    'data': [
        {'url': 'a'},
        {'url': 'b'},
    ],
}


class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text
    
    def json(self):
        return self.text


class TestCustomVTNetwork(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def mock_get(url: str, headers: dict = {}, *args, **kwargs):
            if url == 'http://elastic-stack-instance:9200/wazuh-alerts-3.x-*/_search':
                return MockResponse(200, {'hits': {'total': {'value': 0}}})
            assert 'x-apikey' in headers
            assert headers['x-apikey'] == 'test-apikey'
            
            if url.endswith('/urls'):
                return MockResponse(200, mock_urls_response)
            else:
                return MockResponse(200, mock_vt_response)
        cls.rget = requests.get
        requests.get = mock_get

    @classmethod
    def tearDownClass(cls):
        requests.get = cls.rget

    @unittest.mock.patch('os.path.realpath', return_value='test_path')
    @unittest.mock.patch('custom_vt_network.send_event')
    def test_main(self, sock, ospath):
        custom_vt_network.main('tests/test_alert.json', 'test-apikey', 'test-hook')
        corr = json.loads(open('tests/test_alert_out.json').read())
        sock.assert_called_with(corr, {'name': 'wazuh-manager-instance', 'id': '000'})


if __name__ == "__main__":
    unittest.main()
