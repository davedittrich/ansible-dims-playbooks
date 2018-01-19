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

# Tracks with bumpversion
DIMS_VERSION=2.3.1

DEPLOYMENT=${DIMS_DEPLOYMENT:-$(get_deployment)}
CATEGORY=${DIMS_CATEGORY:-devops}
GROUP=${DEPLOYMENT}
HOSTNAME=$(hostname)
INVENTORY=${INVENTORY:-$PBR/inventory}

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

ANSIBLE_OPTIONS="${ANSIBLE_OPTIONS}"
FLAGS_HELP="usage: $BASE [options] args"

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

main()
{
    dims_main_init

    cat << EOD
---

secrets:
  category: "${FLAGS_category}"
  deployment: "${FLAGS_deployment}"
  group: "${FLAGS_group}"

EOD

    debug "Returning from main()"
    on_exit
    return $?
}


# parse the command-line
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"
main "$@"
exit $?
