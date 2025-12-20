terraform {
  required_providers {
    proxmox = {
        source = "bpg/proxmox"
        version = ">= 0.50.0"
    }
  }
  required_version = ">= 0.13"
}

variable "proxmox_token_secret" {
  type      = string
  sensitive = true
}

provider "proxmox" {
  endpoint  = "https://proxmox.cerom.duckdns.org/"
  api_token = var.proxmox_token_secret
}

variable "vms" {
  default = {
    dev01 = 4096
    dev02 = 4096
  }
}

resource "proxmox_virtual_environment_vm" "vm" {
  for_each = var.vms

  name      = each.key
  node_name = "proxmox"

  clone {
    vm_id = 502
  }

  memory {
    dedicated = each.value
  }
}