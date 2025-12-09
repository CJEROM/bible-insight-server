locals {
    proxmox_dns = "https://proxmox.cerom.duckdns.org:8006/api2/json"
    proxmox_endpoint = "http://192.168.0.200:8006/api2/json"
}

variable "proxmox_token_secret" {
  type      = string
  sensitive = true
}

terraform {
  required_version = ">= 1.1.0"
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = ">= 2.9.5"
    }
  }
}

provider "proxmox" {
    pm_api_url   = "https://proxmox.cerom.duckdns.org/api2/json"
    pm_api_token_id = "bible-insight-test@pve!terraform"
    pm_api_token_secret  = var.proxmox_token_secret
    pm_tls_insecure = true
}

resource "proxmox_vm_qemu" "bible-insight-dev" {
  name        = "bible-insight-dev"
  target_node = "proxmox"

  ### or for a Clone VM operation
  clone = "Docker-Template"

  ### or for a PXE boot VM operation
  # pxe = true
  # boot = "scsi0;net0"
  # agent = 0
}

resource "proxmox_vm_qemu" "testvm" {
  name        = "terraform-test"
  target_node = "proxmox"
  clone       = "Docker-Template"

  memory      = 2048
  cores       = 2
  sockets     = 1

  network {
    model = "virtio"
    bridge = "vmbr0"
  }

  disk {
    size  = "20G"
    type  = "scsi"
    storage = "local-lvm"
  }
}