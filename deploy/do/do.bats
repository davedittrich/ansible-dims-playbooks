#!/usr/bin/env bats
#
# vim: set ts=4 sw=4 tw=0 et :

@test "terraform is found in \$PATH" {
    echo "    ==> Install terraform (see https://www.terraform.io/intro/getting-started/install.html)" >&2
    which terraform
}

@test "playbooks_root is defined" {
    echo "    ==> Run 'psec secrets set --undefined'" >&2
    [ "$(psec -q secrets get playbooks_root)" != '' ] && [ "$(psec -q secrets get playbooks_root)" != 'None' ]
}

@test "do_domain is defined" {
    echo "    ==> Run 'psec secrets set --undefined'" >&2
    [ "$(psec -q secrets get do_domain)" != '' ] && [ "$(psec -q secrets get do_domain)" != 'None' ]
}

@test "do_datacenter is defined" {
    echo "    ==> Run 'psec secrets set --undefined'" >&2
    [ "$(psec -q secrets get do_datacenter)" != '' ] && [ "$(psec -q secrets get do_datacenter)" != 'None' ]
}

@test "do_environment is defined" {
    echo "    ==> Run 'psec secrets set --undefined'" >&2
    [ "$(psec -q secrets get do_environment)" != '' ] && [ "$(psec -q secrets get do_environment)" != 'None' ]
}

@test "do_private_key_file is defined" {
    echo "    ==> Run 'psec secrets set --undefined'" >&2
    [ "$(psec -q secrets get do_private_key_file)" != '' ] && [ "$(psec -q secrets get do_private_key_file)" != 'None' ]
}

@test "do_region is defined" {
    echo "    ==> Run 'psec secrets set --undefined'" >&2
    [ "$(psec -q secrets get do_region)" != '' ] && [ "$(psec -q secrets get do_region)" != 'None' ]
}

@test "do_token is defined" {
    echo "    ==> Run 'psec secrets set --undefined'" >&2
    [ "$(psec -q secrets get do_token)" != '' ] && [ "$(psec -q secrets get do_token)" != 'None' ]
}

@test "opendkim_selector is defined" {
    echo "    ==> Run 'psec secrets set --undefined'" >&2
    [ "$(psec -q secrets get opendkim_selector)" != '' ] && [ "$(psec -q secrets get opendkim_selector)" != 'None' ]
}

@test "Variable PBR (ansible-dims-playbooks) is defined in environment" {
    echo "    ==> Export variables with 'psec -R run' " >&2
    [ ! -z "$PBR" ]
}

@test "Variable TF_VAR_do_token (terraform) is defined in environment" {
    echo "    ==> Export variables with 'psec -R run' " >&2
    [ ! -z "$TF_VAR_do_token" ]
}

@test "Variable TF_VAR_region (terraform) is defined in environment" {
    echo "    ==> Export variables with 'psec -R run' " >&2
    [ ! -z "$TF_VAR_region" ]
}

@test "Variable TF_VAR_environment (terraform) is defined in environment" {
    echo "    ==> Export variables with 'psec -R run' " >&2
    [ ! -z "$TF_VAR_environment" ]
}

@test "Variable TF_VAR_domain (terraform) is defined in environment" {
    echo "    ==> Export variables with 'psec -R run' " >&2
    [ ! -z "$TF_VAR_domain" ]
}

@test "Variable TF_VAR_datacenter (terraform) is defined in environment" {
    echo "    ==> Export variables with 'psec -R run' " >&2
    [ ! -z "$TF_VAR_datacenter" ]
}

@test "Variable TF_VAR_private_key_file (terraform) is defined in environment" {
    echo "    ==> Export variables with 'psec -R run' " >&2
    [ ! -z "$TF_VAR_private_key_file" ]
}

@test "DO_API_TOKEN authentication succeeds" {
    echo "    ==> Check DO_API_TOKEN" >&2
    ! bash -c "make images | grep 'Unable to authenticate you'"
}

@test "File pointed to by TF_VAR_private_key_file exists and is readable" {
    echo "    ==> Run \"make newkeypair\"" >&2
    [ -r "$TF_VAR_private_key_file" ]
}

@test "Git user.name is set" {
    echo "    ==> Run \"git config user.name 'Firstname Lastname'\"" >&2
    [ ! -z "$(git config user.name)" ]
}

@test "Git user.email is set" {
    echo "    ==> Run \"git config user.email 'address@example.com'\"" >&2
    [ ! -z "$(git config user.email)" ]
}

@test "Can run opendkim-genkey" {
    echo "    ==> Install opendkim (\"apt-get install opendkim\" or \"brew install opendkim\")" >&2
    opendkim-genkey --version
}
