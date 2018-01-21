DIMS Build Out on Digital Ocean
===============================

This directory contains helper scripts for generating terraform plans to
create droplets in Digital Ocean. These droplets can then be provisioned
using ansible-dims-playbooks playbooks and inventory files.

For information on how to use the DigitalOcean provider with terraform,
see:

  https://www.digitalocean.com/community/tutorials/how-to-use-terraform-with-digitalocean
  https://gist.github.com/thisismitch/91815a582c27bd8aa44d


Ansible Inventory Management
----------------------------

There is a static YAML style inventory in $PBR/environments/do/inventory, which
includes a symbolic link to a generated static inventory file in the
subdirectory "inventory/" located in this directory.  The Terraform
state file is used to generate this secondary inventory file for
connectivity purposes to active droplets. It uses variables in
the user's environment for things like DNS domain, etc., that may
vary from deployment to deployment.

To use `ansible` or `ansible-playbook` directly, you may wish to place
an `ansible.cfg` file in this directory and set the `inventory` variable
like this:

```
inventory      = ${PBR}/environments/${TF_VAR_environment}/inventory
```

```
$ ansible -m ping do
blue | SUCCESS => {
    "changed": false,
    "failed": false,
    "ping": "pong"
}
green | SUCCESS => {
    "changed": false,
    "failed": false,
    "ping": "pong"
}
```

Related Information
-------------------

To get a list of available DigitalOcean images, do:


```
$ curl -X GET --silent "https://api.digitalocean.com/v2/images?per_page=999" -H "Authorization: Bearer $DO_API_TOKEN" | python -m json.tool | less
```

A modified version of the `digital\_ocean.py` dynamic inventory file is
being used for augmenting the YAML inventory files in the `$PBR/inventory/`
directory.

```
$ make hosts
[droplets]
red
orange
purple
blue
```

TODO
----

When droplets are created using `make create`, the SSH public keys and fingerprints are
extracted from the `terraform` log output. The files are placed in the
`fingerprints` and `known\_hosts` directories.

```
$ tree fingerprints known_hosts
fingerprints
├── blue.devops.local
│   └── ssh-rsa.fingerprint
├── orange.devops.local
│   ├── ssh-ed25519.fingerprint
│   └── ssh-rsa.fingerprint
├── purple.devops.local
│   ├── ssh-ed25519.fingerprint
│   └── ssh-rsa.fingerprint
└── red.devops.local
    ├── ssh-ed25519.fingerprint
    └── ssh-rsa.fingerprint
known_hosts
├── blue.devops.local
│   └── ssh-rsa.known_hosts
├── orange.devops.local
│   ├── ssh-ed25519.known_hosts
│   └── ssh-rsa.known_hosts
├── purple.devops.local
│   ├── ssh-ed25519.known_hosts
│   └── ssh-rsa.known_hosts
└── red.devops.local
    ├── ssh-ed25519.known_hosts
    └── ssh-rsa.known_hosts

8 directories, 14 files
```

See also:

https://github.com/landro/terraform-digitalocean/blob/master/terraform.tf

How to create a VPN using Terraform in Digital Ocean - Infrastructure tutorial part one
https://techpunch.co.uk/development/how-to-create-a-vpn-using-terraform-in-digital-ocean-infrastructure-tutorial-part-one
