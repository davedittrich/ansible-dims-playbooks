DIMS Build Out on Digital Ocean
===============================

This directory contains helper scripts for generating terraform plans to
create droplets in Digital Ocean. These droplets can then be provisioned
using ansible-dims-playbooks playbooks and inventory files.

For information on how to use the DigitalOcean provider with terraform,
see:

  https://www.digitalocean.com/community/tutorials/how-to-use-terraform-with-digitalocean
  https://gist.github.com/thisismitch/91815a582c27bd8aa44d

To get a list of available DigitalOcean images, do:


```
$ curl -X GET --silent "https://api.digitalocean.com/v2/images?per_page=999" -H "Authorization: Bearer $DO_API_TOKEN" | python -m json.tool | less
```

A modified version of the `digital_ocean.py` dynamic inventory file is
being used for augmenting the YAML inventory files in the `$PBR/inventory/`
directory.

```
$ make hosts
red.devops.local
orange.devops.local
purple.devops.local
blue.devops.local
```
