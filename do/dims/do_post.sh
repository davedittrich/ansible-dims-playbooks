#!/bin/bash
#
# vim: set ts=4 sw=4 tw=0 et :
#
# Copyright (C) 2018, David Dittrich. All rights reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# This script is based on https://gist.github.com/leucos/6f8d93de3493431acd29
#
# Change defaults below
# ---------------------

cat <<EOD
---
# This is a generated inventory file produced by $0.
# DO NOT EDIT THIS FILE.

do:
  hosts:
EOD

# Create inventory for running droplets from terraform state file
terraform output --json | jq -r 'to_entries[] | [ .key, (.value.value|to_entries[]| .key, .value) ]|@sh' |
awk '{
    printf "    %s:\n", $1
    printf "      ansible_fqdn: %s\n", $2
    printf "      ansible_host: %s\n", $3
     }'

exit 0
