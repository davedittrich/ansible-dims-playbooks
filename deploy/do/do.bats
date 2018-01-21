#!/usr/bin/env bats
#
# vim: set ts=4 sw=4 tw=0 et :

@test "[S][EV] Directory for secrets (~/.secrets/) exists" {
    [ -d ~/.secrets ]
}

@test "[S][EV] Directory for secrets (~/.secrets/) is mode 700" {
    [ $(stat -c %a ~/.secrets 2>&1) == "700" ]
}

@test "[S][EV] Directory for DigitalOcean secrets (~/.secrets/digital-ocean/) exists" {
    [ -d ~/.secrets/digital-ocean ]
}

@test "[S][EV] DigitalOcean token is in ~/.secrets/digital-ocean/token" {
    [ -s ~/.secrets/digital-ocean/token ]
}

@test "[S][EV] Variable DO_API_VERSION (dopy) is defined in environment" {
    [ ! -z "$DO_API_VERSION" ]
}

@test "[S][EV] Variable DO_API_TOKEN (dopy) is defined in environment" {
    [ ! -z "$DO_API_TOKEN" ]
}

@test "[S][EV] Variable DO_PAT (terraform) is defined in environment" {
    [ ! -z "$DO_PAT" ]
}

@test "[S][EV] Variable TF_VAR_do_token (terraform) is defined in environment" {
    [ ! -z "$TF_VAR_do_token" ]
}

@test "[S][EV] Variable TF_VAR_region (terraform) is defined in environment" {
    [ ! -z "$TF_VAR_region" ]
}

@test "[S][EV] Variable TF_VAR_environment (terraform) is defined in environment" {
    [ ! -z "$TF_VAR_environment" ]
}

@test "[S][EV] Variable TF_VAR_domain (terraform) is defined in environment" {
    [ ! -z "$TF_VAR_domain" ]
}

@test "[S][EV] Variable TF_VAR_datacenter (terraform) is defined in environment" {
    [ ! -z "$TF_VAR_datacenter" ]
}

@test "[S][EV] Variable TF_VAR_private_key (terraform) is defined in environment" {
    [ ! -z "$TF_VAR_private_key" ]
}

@test "[S][EV] Variable TF_VAR_public_key (terraform) is defined in environment" {
    [ ! -z "$TF_VAR_public_key" ]
}

@test "[S][EV] Variable TF_VAR_ssh_fingerprint (terraform) is defined in environment" {
    [ ! -z "$TF_VAR_ssh_fingerprint" ]
}

@test "[S][EV] DO_API_TOKEN authentication succeeds" {
    ! bash -c "make images | grep 'Unable to authenticate you'"
}

@test "[S][EV] Variable TF_VAR_public_key (terraform .tf) is defined in environment" {
    [ ! -z "$TF_VAR_public_key" ]
}

@test "[S][EV] File pointed to by TF_VAR_public_key exists and is readable" {
    [ -r "$TF_VAR_public_key" ]
}

@test "[S][EV] Variable TF_VAR_private_key (terraform .tf) is defined in environment" {
    [ ! -z "$TF_VAR_private_key" ]
}

@test "[S][EV] File pointed to by TF_VAR_private_key exists and is readable" {
    [ -r "$TF_VAR_private_key" ]
}

@test "[S][EV] Variable TF_VAR_ssh_fingerprint (terraform .tf) is defined in environment" {
    [ ! -z "$TF_VAR_ssh_fingerprint" ]
}

@test "[S][EV] DO_API_TOKEN authentication succeeds" {
    ! bash -c "make images | grep 'Unable to authenticate you'"
}

@test "[S][EV] terraform is found in \$PATH" {
    which terraform
}
