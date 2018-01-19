#!/bin/bash
#
# vim: set ts=4 sw=4 tw=0 et :
#
# Copyright (C) 2014-2017, University of Washington. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

. $DIMS/lib/shflags
. $DIMS/bin/dims_functions.sh

# This script creates a set of host SSH keys, key fingerprints,
# and text to add to known_hosts and authorized_keys files for
# supporting remote SSH access.
#
# Use this script to generate a new set of public and private keys
# that will be used by a DIMS system for SSH access. The public
# keys (and fingerprints) will be distributed using Ansible for
# use on clients.

PURPOSE=${PURPOSE:-DIMS}
FINGERPRINTS=${FINGERPRINTS:-key_fingerprints.txt}
HOSTSADD=${HOSTSADD:-known_hosts.add}
DEST=${DEST:-$PWD}
KEYSET=${KEYSET:-client server}
FLAGS_HELP="usage: $BASE [options] args"

# Define command line options
DEFINE_boolean 'debug' false 'enable debug mode' 'd'
DEFINE_string 'deployment' "${DEPLOYMENT}" 'deployment identifier' 'D'
DEFINE_string 'category' "${CATEGORY}" 'category identifier' 'C'
DEFINE_string 'host' "${HOSTNAME}" 'host identifier' 'H'
DEFINE_string 'group' "${GROUP}" 'inventory group' 'G'
DEFINE_string 'inventory' "${INVENTORY}" 'inventory file' 'i'
DEFINE_boolean 'upgrade' false 'upgrade patches to OS' 'U'
DEFINE_boolean 'usage' false 'print usage information' 'u'
DEFINE_boolean 'verbose' false 'be verbose' 'v'
DEFINE_boolean 'version' false 'print version number and exit' 'V'

# Define functions

usage() {
    flags_help
    cat << EOD

This script does some amazing things.

Using --verbose enables verbose output in this script and runs ansible-playbook with '-vv'.
Using --debug enables debugging output in this script and runs ansible-playbook with '-vv'.
Using both --verbose and --debug gives max output and runs ansible-playbook with '-vvvv'.

EOD
    exit 0
}

function gen_ssh_host_key()
{
    local _keytype=${1:-ed25119}
    local _keytype_upper=$(echo ${_keytype} | tr a-z A-Z)
    local _keylength=""
    case ${_keytype} in
        rsa|ed25119) true ;;
        *) error_exit 1 "Key type \"${_keytype}\" is not valid or not recommended" ;;
    esac
    local _keyfile=$(get_temp_file)
    add_on_exit rm -f $_keyfile

    [[ ${_keytype} == "rsa" ]] && _keylength="-b 2048"
    echo "y" | ssh-keygen -t ${_keytype} ${_keylength} -N "" -C "${_keytype_upper} host key" -f ${_keyfile} -a 100 2>&1 > /dev/null
    cat ${_keyfile}
}

function output_user_data()
{
    cat << EOD
---

secrets:
  category: "${FLAGS_category}"
  deployment: "${FLAGS_deployment}"
  group: "${FLAGS_group}"
ssh_keys:
  rsa_private: |
  ${RSA_PRIVATE}
  rsa_public: |
  ${RSA_PUBLIC}
  ed25519_public: |
  ${ED25519_PRIVATE}
  ed25519_public: |
  ${ED25519_PUBLIC}

EOD
    return 0
}

main()
{
    dims_main_init

    if [[ ${FLAGS_verbose} -eq ${FLAGS_true} ]]; then
        #show the values as read in by the flags
        cat <<EOF
    PURPOSE=$PURPOSE
    FINGERPRINTS=$FINGERPRINTS
    HOSTSADD=$HOSTSADD
    DEST=$DEST
    KEYSET=$KEYSET
EOF
    fi

    # Add command option to select creation of directory if
    # it does not exist.
    if [ ! -d $DEST ]; then
    	${ERROR_EXIT} 1 "Directory $DEST does not exist"
    fi

    # Change directory, if necessary, to where files will be created.
    if [ -d $DEST -a $DEST != $PWD ]; then
    	cd ${DEST}
    fi

    cp /dev/null $FINGERPRINTS
    for type in $KEYSET; do
    	# Generate each of the standard keys with specific bit sizes
        RSA_PRIVATE=$(gen_ssh_host_key rsa)
        RSA_PUBLIC=$(echo $RSA_PRIVATE|ssh-keygen -y)
        ED25519_PRIVATE=$(gen_ssh_host_key ed25519)
    	#for proto in dsa rsa ecdsa ed25519; do
    	#	# Add fingerprints to a file that can be used for key validation.
    	#	ssh-keygen -l -f ${type}_host_${proto}_key >> $FINGERPRINTS
    	#	# Add public keys to a file that can be added to known_hosts
    	#	ssh-keygen -y -f ${type}_host_${proto}_key >> $HOSTSADD
    	#done
    done

    output_user_data

    debug "Returning from main()"
    on_exit
    return $?
}


# parse the command-line
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"
main "$@"
exit $?

