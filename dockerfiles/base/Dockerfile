FROM ubuntu:14.04

MAINTAINER Dave Dittrich <dittrich@u.washington.edu>

# LAST_UPDATED, VERSION, AUTHOR, and IMAGE are set
# by building script.

ARG LAST_UPDATED
ENV LAST_UPDATED "$LAST_UPDATED"

ARG VERSION
ENV VERSION $VERSION

ARG AUTHOR
ENV AUTHOR $AUTHOR

ARG IMAGE
ENV IMAGE $IMAGE

#ENV LANG en_US.UTF-8
#ENV LANGUAGE en_US.UTF-8
#ENV LC_ALL en_US.UTF-8

# This Dockerfile requires that the Google 'shflags' repo
# be checked out into this directory on build.
# $ git clone https://github.com/kward/shflags
#
# TODO(dittrich): Make this more robust and user-friendly.
COPY shflags/shflags /shflags

# It also requires that the "bats" repo be checked out into
# this directory on build.
# git clone https://github.com/sstephenson/bats
# (cd bats && git checkout v0.4.0)
COPY bats/libexec/* /bin/

# Copy files in to save build state for later use.
COPY VERSION /
COPY IMAGE /
COPY LAST_UPDATED /
COPY AUTHOR /
COPY usage.txt /

# Create entry point script and plugin directory.
COPY docker.entrypoint /
COPY docker.entrypoint.d/* /docker.entrypoint.d/
ONBUILD COPY docker.entrypoint.d/* /docker.entrypoint.d/

# Add some stuff via apt-get
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        bc \
        ca-certificates \
        curl \
        unzip \
    && rm -rf /var/lib/apt/lists/*

# Add Consul template
# Releases at https://releases.hashicorp.com/consul-template/
#ENV CONSUL_TEMPLATE_VERSION 0.14.0
#ENV CONSUL_TEMPLATE_SHA1 7c70ea5f230a70c809333e75fdcff2f6f1e838f29cfb872e1420a63cdf7f3a78
ENV CONSUL_TEMPLATE_VERSION 0.15.0
ENV CONSUL_TEMPLATE_SHA1 b7561158d2074c3c68ff62ae6fc1eafe8db250894043382fb31f0c78150c513a

RUN curl --retry 7 -Lso /tmp/consul-template.zip "https://releases.hashicorp.com/consul-template/${CONSUL_TEMPLATE_VERSION}/consul-template_${CONSUL_TEMPLATE_VERSION}_linux_amd64.zip" \
    && echo "${CONSUL_TEMPLATE_SHA1}  /tmp/consul-template.zip" | sha256sum -c \
    && unzip /tmp/consul-template.zip -d /usr/local/bin \
    && rm /tmp/consul-template.zip

# get ContainerPilot release
# https://github.com/joyent/containerpilot/releases
ENV CONTAINERPILOT_VERSION 2.3.0
RUN export CP_SHA1=ec9dbedaca9f4a7a50762f50768cbc42879c7208 \
    && curl -Lso /tmp/containerpilot.tar.gz \
         "https://github.com/joyent/containerpilot/releases/download/${CONTAINERPILOT_VERSION}/containerpilot-${CONTAINERPILOT_VERSION}.tar.gz" \
    && echo "${CP_SHA1}  /tmp/containerpilot.tar.gz" | sha1sum -c \
    && tar zxf /tmp/containerpilot.tar.gz -C /bin \
    && rm /tmp/containerpilot.tar.gz

# Set up for tests
COPY tests.d/* /tests.d/

ENTRYPOINT ["/docker.entrypoint"]

CMD []
