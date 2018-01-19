#!/usr/bin/env sh

# sleep timer for packer
sleep 30

# add additional repos
add-apt-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc) main universe"
add-apt-repository "deb http://archive.ubuntu.com/ubuntu $(lsb_release -sc)-updates main universe"

# update, install curl and linux kernel 3.16
apt-get update --fix-missing
apt-get upgrade -y
apt-get install -y curl linux-headers linux-headers-generic \
                   linux-image-generic linux-image-extra-generic

rm -f /etc/ssh/ssh_host_*
dpkg-reconfigure openssh-server

for KEY in /etc/ssh/ssh_host*key; do
  ssh-keygen -l -f $KEY;
done
