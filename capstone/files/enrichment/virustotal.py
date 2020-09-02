#!/usr/bin/env python
# Copyright (C) 2015-2020, Wazuh Inc.
# October 19, 2017.
#
# This program is free software; you can redistribute it
# and/or modify it under the terms of the GNU General Public
# License (version 2) as published by the FSF - Free Software
# Foundation.
# Wazuh, Inc <support@wazuh.com>

import json
import sys
import time
import os
from socket import socket, AF_UNIX, SOCK_DGRAM

try:
    import requests
    from requests.auth import HTTPBasicAuth
except Exception as e:
    print("No module 'requests' found. Install: pip install requests")
    sys.exit(1)

try:
    import vt
except Exception as e:
    print("No module 'vt' found. Install pip install vt-py")
    sys.exit(1)

# ossec.conf configuration:
#  <integration>
#      <name>virustotal</name>
#      <api_key>api_key_here</api_key>
#      <group>syscheck</group>
#      <alert_format>json</alert_format>
#  </integration>

# Global vars

DEBUG = False
PWD = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
json_alert = {}
now = time.strftime("%a %b %d %H:%M:%S %Z %Y")

# Set paths
LOG_FILE_PATH = '{0}/logs/integrations.log'.format(PWD)
SOCKET_ADDR = '{0}/queue/ossec/queue'.format(PWD)


def main(args):
    debug("# Starting")

    # Read args
    alert_file_location = args[1]
    apikey = args[2]

    debug("# API Key")
    debug(apikey)

    debug("# File location")
    debug(alert_file_location)

    # Load alert. Parse JSON object.
    with open(alert_file_location) as alert_file:
        json_alert = json.load(alert_file)
    debug("# Processing alert")
    debug(json_alert)

    # Request VirusTotal info
    msg = request_virustotal_info(json_alert, apikey)

    # If positive match, send event to Wazuh Manager
    if msg:
        send_event(msg, json_alert["agent"])


def debug(msg):
    if DEBUG:
        msg = "{0}: {1}\n".format(now, msg)

        print(msg)

        with open(LOG_FILE_PATH, "a") as log_file:
            log_file.write(msg)


def in_database(data, hash):
    result = data['response_code']
    if result == 0:
        return False
    return True


def get_file_info(hash, apikey):
    """

    @param hash: MD5 hash of the file that is sent to VirusTotal.
    @param apikey: VirusTotal API key.
    @return: Instance of vt.Object that contains information about about requested file.
    """
    vt_client = vt.Client(apikey)

    file_info = vt_client.get_object("/files/{}".format(hash))

    if file_info is not None:
        return file_info
    else:
        alert_output = {}
        alert_output["virustotal"] = {}
        alert_output["integration"] = "virustotal"

        debug("# Error when conecting VirusTotal API")
        alert_output["virustotal"]["description"] = "Error: API request fail"
        send_event(alert_output)
        exit(0)



def request_virustotal_info(alert, apikey):
    alert_output = {}

    # If there is no a md5 checksum present in the alert. Exit.
    if "md5_after" not in alert["_source"]["syscheck"]:
        return None

    # Request info using VirusTotal API
    file_info = get_file_info(alert["_source"]["syscheck"]["md5_after"], apikey)

    # Create alert
    alert_output["virustotal"] = {}
    alert_output["integration"] = "virustotal"
    alert_output["virustotal"]["found"] = 0
    alert_output["virustotal"]["malicious"] = 0
    alert_output["virustotal"]["source"] = {}
    alert_output["virustotal"]["source"]["alert_id"] = alert["_id"]
    alert_output["virustotal"]["source"]["file"] = alert["_source"]["syscheck"]["path"]
    alert_output["virustotal"]["source"]["md5"] = alert["_source"]["syscheck"]["md5_after"]
    alert_output["virustotal"]["source"]["sha1"] = alert["_source"]["syscheck"]["sha1_after"]

    alert_output["virustotal"]["malicious"] = 1

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

    debug(alert_output)

    return alert_output


def send_event(msg, agent=None):
    if not agent or agent["id"] == "000":
        string = '1:virustotal:{0}'.format(json.dumps(msg))
    else:
        string = '1:[{0}] ({1}) {2}->virustotal:{3}'.format(agent["id"], agent["name"],
                                                            agent["ip"] if "ip" in agent else "any", json.dumps(msg))

    debug(string)
    sock = socket(AF_UNIX, SOCK_DGRAM)
    sock.connect(SOCKET_ADDR)
    sock.send(string.encode())
    sock.close()


if __name__ == "__main__":
    try:
        # Read arguments
        bad_arguments = False
        if len(sys.argv) >= 4:
            msg = '{0} {1} {2} {3} {4}'.format(now, sys.argv[1], sys.argv[2], sys.argv[3],
                                               sys.argv[4] if len(sys.argv) > 4 else '')
            DEBUG = (len(sys.argv) > 4 and sys.argv[4] == 'debug')
        else:
            msg = '{0} Wrong arguments'.format(now)
            bad_arguments = True

        # Logging the call
        with open(LOG_FILE_PATH, 'a') as log_file:
            log_file.write(msg + '\n')

        if bad_arguments:
            debug("# Exiting: Bad arguments.")
            sys.exit(1)

        # Main function
        main(sys.argv)

    except Exception as e:
        debug(str(e))
        raise
