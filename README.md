# VirusTotal SIEM enrichment

![Monorepo CI](https://github.com/googleinterns/step242-2020/workflows/Monorepo%20CI/badge.svg)

## Capstone Project

### Overview

This project shows the example usage of [Wazuh](https://wazuh.com/) SIEM combined with [VirusTotal](https://virustotal.com) API.

### Infrastructure

We use 3 VMs, for Elastic Stack, Wazuh Manager and Wazuh Agent. They all are connected into one VPC. Only the wazuh agent instance is connected to the internet, others shall be accessed through port-forwarding. You can easily set up this configuration in google cloud using the terraform script.

**Wazuh Agent:**
* Collects information about its server and processes that are running on it

**Wazuh Manager:**
* Monitors agent and collects info from it
* Enriches some alerts

**Elastics Stack:**
* Hosts elasticsearch database
* Provides Kibana UI, visualizations, dashboards
* Fetches VT feed

### Data enrichment

There're two types of data alerts enrichment: network and feed. Both of them run a script on alert creation, fetch additional data from virustotal and create a new alert based on it. These alerts will be added to the same wazuh index, with the labels `data.integration: virustotal` and `data.integration: custom-vt-network`.

### Feed

Feed is a paid VirusTotal service that gives users the list of all files that has been discovered recently. We created a script that fetches this feed and adds it to a separate Elasticsearch index. You can analyze it, create dashboards and combine it with wazuh files data.

### Deployment

You can deploy all the mentioned modules using `deploy.sh` scripts in corresponding directories.

## Learning Project

As our pet learning project we developed web application that periodically runs VT query and sends results to a specified webhook. It consists of two parts: 
* [Default](https://github.com/googleinterns/step242-2020/tree/master/default) - web service that сonsists of the form collecting users' credentials and a cron job that runs query and sends results to a webhook.
* [Webhook](https://github.com/googleinterns/step242-2020/tree/master/webhook) - webhook that accepts virustotal response and sends it to email.

Both apps are created on Python3.8 using FastAPI for Google App Engine. They are using Google Cloud Datastore for data storage and Secret Manager for storage of access keys.

## Source Code Headers

Every file containing source code must include copyright and license
information. This includes any JS/CSS files that you might be serving out to
browsers. (This is to help well-intentioned people avoid accidental copying that
doesn't comply with the license.)

Apache header:

    Copyright 2020 Google LLC

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        https://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
