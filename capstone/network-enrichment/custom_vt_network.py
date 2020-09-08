#!/var/ossec/framework/python/bin/python3.8
  
import json
import logging
import os
import requests
import sys
from collections import defaultdict
from socket import socket, AF_UNIX, SOCK_DGRAM


PWD = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def send_event(msg, agent = None):
    if not agent or agent["id"] == "000":
        string = f'1:custom-vt-network:{json.dumps(msg)}'
    else:
        string = f'1:[{agent["id"]}] ({agent["name"]}) {agent["ip"] if "ip" in agent else "any"}->custom-vt-network:{json.dumps(msg)}'

    logging.info(string)

    socket_addr = f'{PWD}/queue/ossec/queue'

    sock = socket(AF_UNIX, SOCK_DGRAM)
    sock.connect(socket_addr)
    sock.send(string.encode())
    sock.close()

def check_existing_ip(ip):
    req = {'query': {'bool': {'must': [{'match': {'data.integration': 'custom-vt-network'}}, {'match': {'data.srcip': ip}}]}}}
    resp = requests.get('http://elastic-stack-instance:9200/wazuh-alerts-3.x-*/_search', json=req)
    if resp.status_code != 200:
        logging.error(f'Request to elasticsearch failed: {resp.text}')
        raise Exception('Request to elasticsearch failed')
    return resp.json()['hits']['total']['value'] != 0


def request_virustotal_info(alert, api_key):
    allowed_fields_ip = {
        'last_analysis_stats',
        'last_https_certificate',
        'reputation',
        'tags',
        'whois',
    }

    errors_desc = defaultdict(lambda: 'Error: API request failed', {
        200: 'Success',
        401: 'Error: Check credentials',
        429: 'Error: Quota Exceeded',
        
    })

    alert_output = alert['data'].copy()
    alert_output['integration'] = 'custom-vt-network'
    alert_output['vt-enrichment'] = dict()

    srcip = alert['data']['srcip']
    vt_data_ip = requests.get(f'https://www.virustotal.com/api/v3/ip_addresses/{srcip}', headers={'x-apikey': api_key})

    alert_output['vt-enrichment']['error'] = vt_data_ip.status_code
    alert_output['vt-enrichment']['description'] = errors_desc[vt_data_ip.status_code]

    if vt_data_ip.status_code == 200:
        vt_data_ip_filtered = {key: val for key, val in vt_data_ip.json()['data']['attributes'].items() if key in allowed_fields_ip}
        alert_output['vt-enrichment'].update(vt_data_ip_filtered)

    vt_data_urls = requests.get(f'https://www.virustotal.com/api/v3/ip_addresses/{srcip}/urls', headers={'x-apikey': api_key})

    if vt_data_urls.status_code == 200:
        related_urls = [url['url'] for url in vt_data_urls.json()['data']]
        alert_output['vt-enrichment']['urls'] = related_urls
    else:
        alert_output['vt-enrichment']['urls-error'] = vt_data_ip.status_code
        alert_output['vt-enrichment']['urls-description'] = errors_desc[vt_data_ip.status_code]

    return alert_output


def main(alert_filename, api_key, hook_url):
    with open(alert_filename) as alert_file:
        alert_json = json.loads(alert_file.read())

    if not check_existing_ip(alert_json['data']['srcip']):
        alert_output = request_virustotal_info(alert_json, api_key)
        send_event(alert_output, alert_json['agent'])
    else:
        logging.info(f'IP found again: {alert_json["data"]["srcip"]}')


if __name__ == "__main__":
    logging.basicConfig(filename=f'{PWD}/logs/integrations.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    if len(sys.argv) >= 4:
        main(sys.argv[1], sys.argv[2], sys.argv[3])
    else:
        logging.error('Exiting: Bad arguments.')
