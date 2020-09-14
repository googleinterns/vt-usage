#!/var/ossec/framework/python/bin/python3.8
# Copyright (C) 2015-2020, Wazuh Inc, Google LLC.
# September 8, 2020.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.
# Wazuh Inc <support@wazuh.com>
# Google LLC

import json
import logging
import os
import sys
from socket import socket, AF_UNIX, SOCK_DGRAM

try:
    import vt
except ImportError as e:
    print("No module 'vt' found."
          "Follow guide here https://virustotal.github.io/vt-py/howtoinstall.html")
    print("WARNING! Do not install this library using pip!"
          "Currently released version can break this script.")
    sys.exit(1)

# ossec.conf configuration:
#  <integration>
#      <name>virustotal</name>
#      <api_key>api_key_here</api_key>
#      <group>syscheck</group>
#      <alert_format>json</alert_format>
#  </integration>

DEBUG = False
PWD = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Set paths
LOG_FILE_PATH = f'{PWD}/logs/integrations.log'
SOCKET_ADDR = f'{PWD}/queue/ossec/queue'

# Set logger
logging.basicConfig(filename=f'{PWD}/logs/integrations.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)


def main(args):
    """Main function for enrichment flow.

    @param args: System args [file location, api key].
    """
    logging.info("# Starting")

    # Read args
    alert_file_location = args[1]
    apikey = args[2]

    json_alert = {}

    # Load alert. Parse JSON object.
    with open(alert_file_location) as alert_file:
        json_alert = json.load(alert_file)

    logging.info("# Processing alert")
    logging.info(json_alert)

    # Request VirusTotal info
    msg = request_virustotal_info(json_alert, apikey)

    # If positive match, send event to Wazuh Manager
    if msg:
        send_event(msg, json_alert["agent"])
    else:
        logging.error(f"MD5 hash of file not found {json_alert}")


def get_file_info(hash, apikey):
    """A function that gets file information from VirusTotal.

    @param hash: MD5 hash of the file that is sent to VirusTotal.
    @param apikey: VirusTotal API key.
    @return: Instance of vt.Object that contains information about about requested file.
    """
    vt_client = vt.Client(apikey)

    file_info = vt_client.get_object(f"/files/{hash}")

    return file_info


def request_virustotal_info(alert, apikey):
    """A function that requests a vt.Object and parses it into Wazuh alert.

    @param alert: Wazuh alert that we want to enrich.
    @param apikey: VirusTotal API key.
    @return: Wazuh alert enriched with VirusTotal data or None if the file does not have md5 hash.
    """
    alert_output = {}

    # If there is no a md5 checksum present in the alert. Exit.
    if "md5_after" not in alert["syscheck"]:
        return None

    # Request info using VirusTotal API
    file_info = get_file_info(alert["syscheck"]["md5_after"], apikey)

    alert_output = {}

    if file_info is None:
        alert_output["virustotal"] = {}
        alert_output["integration"] = "virustotal"

        logging.error("# Error when conecting VirusTotal API")
        alert_output["virustotal"]["description"] = "Error: API request fail"
    else:
        alert_output["virustotal"] = {}
        alert_output["integration"] = "virustotal"
        alert_output["virustotal"]["source"] = {}
        alert_output["virustotal"]["source"]["alert_id"] = alert["id"]

        alert_output["virustotal"]["source"]["file"] = alert["syscheck"]["path"]
        alert_output["virustotal"]["source"]["md5"] = alert["syscheck"]["md5_after"]
        alert_output["virustotal"]["source"]["sha1"] = alert["syscheck"]["sha1_after"]

        wanted_info = [
            "meaningful_name",
            "capabilities_tags",
            "first_submission_date",
            "last_analysis_stats",
            "reputation",
            "sigma_analysis_stats",
            "type_tag",
        ]

        # Populate JSON Output object with VirusTotal request
        for info in wanted_info:
            alert_output["virustotal"][info] = file_info.get(info)

    logging.info(alert_output)
    return alert_output


def send_event(msg, agent=None):
    """A function that sends ready alert into Elastic.

    @param msg: Python dict with alert.
    @param agent: Wazuh agent.
    """
    if not agent or agent["id"] == "000":
        string = f'1:virustotal:{json.dumps(msg)}'
    else:
        string = f'1:[{agent["id"]}] ({agent["name"]})' \
                 f'{agent["ip"] if "ip" in agent else "any"}->virustotal:{json.dumps(msg)}'

    logging.info(string)
    sock = socket(AF_UNIX, SOCK_DGRAM)
    sock.connect(SOCKET_ADDR)
    sock.send(string.encode())
    sock.close()


if __name__ == "__main__":
    try:
        if len(sys.argv) >= 4:
            logging.info(f"{sys.argv[1]} {sys.argv[2]} {sys.argv[3]} {sys.argv[4]}")
        else:
            logging.error(f"# Exiting: Bad arguments. {sys.argv}")
            exit(1)

        main(sys.argv)

    except Exception as e:
        logging.error(str(e))
        raise
