/**
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

provider "google" {
    version = "3.5.0"

    credentials = file("application_default_credentials.json")

    project = "virustotal-step-2020"
    region = "europe-west1"
    zone = "europe-west1-c"
}

resource "google_compute_network" "vpc_network" {
  name = "wazuh-network"
}


resource "google_compute_instance" "wazuh_agent" {
  name         = "wazuh-agent-instance"
  machine_type = "e2-standard-2"

  tags = ["allow-inbound"]

  metadata = {
    "enable-oslogin" = "TRUE"
  }

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.self_link
    access_config {
    }
  }

  can_ip_forward = true
}

resource "google_compute_instance" "wazuh_manager" {
  name         = "wazuh-manager-instance"
  machine_type = "e2-standard-2"

  tags = ["server"]

  metadata = {
    "enable-oslogin" = "TRUE"
  }

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.self_link
  }
}

resource "google_compute_instance" "elastic_stack" {
  name         = "elastic-stack-instance"
  machine_type = "e2-standard-2"

  tags = ["server"]

  metadata = {
    "enable-oslogin" = "TRUE"
  }

  boot_disk {
    initialize_params {
      image = "debian-cloud/debian-9"
    }
  }

  network_interface {
    network = google_compute_network.vpc_network.self_link
  }
}

resource "google_compute_route" "internet_access" {
  name = "internet-access"
  description = "Route to internet for private instances"
  dest_range = "0.0.0.0/0"
  network = google_compute_network.vpc_network.self_link
  next_hop_instance = google_compute_instance.wazuh_agent.self_link
  next_hop_instance_zone = google_compute_instance.wazuh_agent.zone
  tags = ["server"]
  priority = 100
}
