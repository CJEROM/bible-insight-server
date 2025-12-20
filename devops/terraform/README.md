Requires setting up Proxmox

1. User with administrator Access
2. API key assigned to user
3. Template created (VM) thats turned off, and has cloud-init installed
4. From Datacenter configure, user, permissions and storage for the VM

Then just have a Template ready, can mess around with and expand terraform later to be more suitable, but works as is currently.

Seek to combine with certain scripts to set it up correctly.

Remember to have a terraform.tfvars file with proxmox_token_secret = "terraform@pam!test=API-KEY"