provider "google" {
    version = "3.5.0"

    credentials = file("application_default_credentials.json")

    project = "virustotal-step-2020"
    region = "europe-west1"
    zone = "europe-west1-c"
}

resource "google_compute_network" "vpc_network" {
  name = "terraform-network"
}


resource "google_compute_instance" "vm_instance_1" {
  name         = "terraform-instance-1"
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

resource "google_compute_instance" "vm_instance_2" {
  name         = "terraform-instance-2"
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

resource "google_compute_instance" "vm_instance_3" {
  name         = "terraform-instance-3"
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
  next_hop_instance = google_compute_instance.vm_instance_1.self_link
  next_hop_instance_zone = google_compute_instance.vm_instance_1.zone
  tags = ["server"]
  priority = 100
}