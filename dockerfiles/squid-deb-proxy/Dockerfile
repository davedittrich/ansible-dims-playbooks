FROM hub.vlan1.dims:5000/base:latest

# Derived from Dockerfile created by Panagiotis Moustafellos <pmoust@gmail.com>

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

# update and install squid-deb-proxy
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      squid-deb-proxy \
      squid-deb-proxy-client \
      avahi-daemon \
      avahi-utils && \
     apt-get clean

# Extra locations to cache from
ADD extra-sources.acl /etc/squid-deb-proxy/mirror-dstdomain.acl.d/20-extra-sources.acl
ADD squid-deb-proxy.conf /etc/squid-deb-proxy/squid-deb-proxy.conf

# Point cache directory to /cachedir
RUN ln -sf /cachedir /var/cache/squid-deb-proxy

# Redirect logs to stdout for the container
RUN ln -sf /dev/stdout /var/log/squid-deb-proxy/access.log
RUN ln -sf /dev/stdout /var/log/squid-deb-proxy/store.log
RUN ln -sf /dev/stdout /var/log/squid-deb-proxy/cache.log

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

VOLUME ["/cachedir"]

EXPOSE 8000
EXPOSE 5353/udp

ENTRYPOINT ["/docker.entrypoint"]

CMD []
