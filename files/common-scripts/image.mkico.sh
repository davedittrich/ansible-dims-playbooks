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

# Author: Dave Dittrich <dave.dittrich@gmail.com>

# Source shflags
. $DIMS/lib/shflags
. $DIMS/bin/dims_functions.sh

RESOLUTIONS='16,32,48,64,96,128,256'

# Define command line options
DEFINE_boolean 'debug' false 'enable debug mode' 'd'
DEFINE_boolean 'force' false 'force over-writing image' 'f'
DEFINE_string 'resolutions' "${RESOLUTIONS}" 'list of desired .ico resolutions'
DEFINE_boolean 'usage' false 'print usage information' 'u'
DEFINE_boolean 'verbose' false 'be verbose' 'v'

FLAGS_HELP="usage: $BASE [options] args"

usage() {
    flags_help
    cat << EOD

This script produces a multi-resolution .ico icon file from an input
graphics file (any format supported by Imagemagick).  The resulting
file has the same base name as the source file, with the '.ico'
extension.

Default resolutions: ${FLAGS_resolutions}
EOD
    exit 0
}

function validate()
{
    local _remains=$(sed 's/[0-9,]//g' <<< "$1")
    [[ -z "$_remains" ]] || error_exit 1 "Resolutions must only be list of integers like \"$RESOLUTIONS\""
    return 0
}

main()
{
    dims_main_init

    validate "${FLAGS_resolutions}"

    # Temporary working directory
    TDIR=$(get_temp_dir)
    add_on_exit rm -rf ${TDIR}

    IMG_SRC=$1
    [[ -f "${IMG_SRC}" ]] || error_exit 1 "File does not exist: ${IMG_SRC}"
    IMG_BASE=$(basename ${IMG_SRC%.*})
    IMG_DEST="$(dirname $IMG_SRC)/${IMG_BASE}.ico"

    for RES in $(sed 's/,/ /g' <<< ${FLAGS_resolutions}); do
        verbose "Creating ${IMG_BASE}-${RES}.png"
        convert $IMG_SRC -resize ${RES}x${RES} ${TDIR}/${IMG_BASE}-${RES}.png ||
            error_exit $? "convert $IMG_SRC failed"
    done

    verbose "Creating ico file"
    eval "convert ${TDIR}/${IMG_BASE}-{${FLAGS_resolutions}}.png ${TDIR}/${IMG_BASE}.ico"

    verbose "Creating ${IMG_DEST}"
    if [[ ${FLAGS_force} == ${FLAGS_TRUE} ]]; then
        cp -f ${TDIR}/${IMG_BASE}.ico ${IMG_DEST}
    else
        cp -i ${TDIR}/${IMG_BASE}.ico ${IMG_DEST}
    fi
    RESULT=$?

    debug "Returning from main()"
    return $RESULT
}

# parse the command-line
FLAGS "$@" || exit $?
eval set -- "${FLAGS_ARGV}"
main "$@"
exit $?
