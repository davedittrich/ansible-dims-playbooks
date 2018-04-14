#!/usr/bin/env bats
#
# vim: set ts=4 sw=4 tw=0 et :

@test "[S][EV] terraform is found in \$PATH" {
    echo "    ==> Install terraform (see https://www.terraform.io/intro/getting-started/install.html)" >&2
    which terraform
}

@test "[S][EV] Directory for secrets (~/.secrets/) exists" {
    echo "    ==> Run \"make init\"" >&2
    [ -d ~/.secrets ]
}

@test "[S][EV] Directory for secrets (~/.secrets/) is mode 700" {
    echo "    ==> Run \"make init\"" >&2
    [ ! -z $(find ~/.secrets -type d -maxdepth 0 -perm 0700) ]
}

@test "[S][EV] Directory for DigitalOcean secrets (~/.secrets/digital-ocean/) exists" {
    echo "    ==> Run \"make init\"" >&2
    [ -d ~/.secrets/digital-ocean ]
}

@test "[S][EV] DigitalOcean token file (~/.secrets/digital-ocean/token) is not empty" {
    echo "    ==> Generate API token via DigitalOcean panel and place in \"~/.secrets/digital-ocean/token\"" >&2
    [ -s ~/.secrets/digital-ocean/token ]
}

@test "[S][EV] Secrets for DigitalOcean (~/.secrets/digital-ocean/secrets.yml) exist" {
    echo "    ==> Create and edit \"~/.secrets/digital-ocean/secrets.yml\"" >&2
    [ -s ~/.secrets/digital-ocean/secrets.yml ]
}

@test "[S][EV] Variable DIMS_DOMAIN is defined in environment" {
    echo "    ==> Define \"DIMS_DOMAIN\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$DIMS_DOMAIN" ]
}

@test "[S][EV] Variable DIMS_SITE_ID is defined in environment" {
    echo "    ==> Define \"DIMS_SITE_ID\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$DIMS_SITE_ID" ]
}

@test "[S][EV] Variable DO_API_VERSION (dopy) is defined in environment" {
    echo "    ==> Define \"DO_API_VERSION\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$DO_API_VERSION" ]
}

@test "[S][EV] Variable DO_API_TOKEN (dopy) is defined in environment" {
    echo "    ==> Define \"DO_API_TOKEN\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$DO_API_TOKEN" ]
}

@test "[S][EV] Variable DO_PAT (terraform) is defined in environment" {
    echo "    ==> Define \"DO_PAT\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$DO_PAT" ]
}

@test "[S][EV] Variable TF_VAR_do_token (terraform) is defined in environment" {
    echo "    ==> Define \"TF_VAR_do_token\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$TF_VAR_do_token" ]
}

@test "[S][EV] Variable TF_VAR_region (terraform) is defined in environment" {
    echo "    ==> Define \"TF_VAR_region\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$TF_VAR_region" ]
}

@test "[S][EV] Variable TF_VAR_environment (terraform) is defined in environment" {
    echo "    ==> Define \"TF_VAR_environment\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$TF_VAR_environment" ]
}

@test "[S][EV] Variable TF_VAR_domain (terraform) is defined in environment" {
    echo "    ==> Define \"TF_VAR_domain\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$TF_VAR_domain" ]
}

@test "[S][EV] Variable TF_VAR_datacenter (terraform) is defined in environment" {
    echo "    ==> Define \"TF_VAR_datacenter\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$TF_VAR_datacenter" ]
}

@test "[S][EV] Variable TF_VAR_private_key (terraform) is defined in environment" {
    echo "    ==> Define \"TF_VAR_private_key\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$TF_VAR_private_key" ]
}

@test "[S][EV] Variable TF_VAR_public_key (terraform) is defined in environment" {
    echo "    ==> Define \"TF_VAR_public_key\" in ~/.bash_alias or ~/.bashrc" >&2
    [ ! -z "$TF_VAR_public_key" ]
}

@test "[S][EV] DO_API_TOKEN authentication succeeds" {
    echo "    ==> Check DO_API_TOKEN" >&2
    ! bash -c "make images | grep 'Unable to authenticate you'"
}

@test "[S][EV] File pointed to by TF_VAR_public_key exists and is readable" {
    echo "    ==> Run \"make newkeypair\"" >&2
    [ -r "$TF_VAR_public_key" ]
}

@test "[S][EV] File pointed to by TF_VAR_private_key exists and is readable" {
    echo "    ==> Run \"make newkeypair\"" >&2
    [ -r "$TF_VAR_private_key" ]
}

@test "[S][EV] Git user.name is set" {
    echo "    ==> Run \"git config user.name 'Firstname Lastname'\"" >&2
    [ ! -z "$(git config user.name)" ]
}

@test "[S][EV] Git user.email is set" {
    echo "    ==> Run \"git config user.email 'address@example.com'\"" >&2
    [ ! -z "$(git config user.email)" ]
}

@test "[S][EV] Can run opendkim-genkey" {
    echo "    ==> Install opendkim (\"apt-get install opendkim\" or \"brew install opendkim\")" >&2
    opendkim-genkey --version
}
