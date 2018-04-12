#!/bin/bash
#
# Copyright (c) 2018, Dave Dittrich <dave.dittrich@gmail.com>. All rights reserved.


# IMAGE, VERSION and AUTHOR are set in Dockerfile at build time.
IMAGE="$(cat /IMAGE)"
VERSION="$(cat /VERSION)"
AUTHOR="$(cat /AUTHOR)"
LAST_UPDATED="$(cat /LAST_UPDATED)"

# This script is here to serve as an example and demonstration of how an
# entrypoint modular script works and testing the "dims/base" image.
# It can't be deleted from the image, but the script will only run
# if the image name matches the name of the base image.

[ ! -d /var/run/sshd ] && mkdir -p /var/run/sshd
/usr/sbin/sshd -D &
exec "$@"
