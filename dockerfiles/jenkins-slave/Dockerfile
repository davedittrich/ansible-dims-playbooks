#FROM base:latest
FROM debian:jessie-backports
MAINTAINER Dave Dittrich <dave.dittrich@gmail.com>

ENV LANG     en_US.UTF-8
ENV LC_ALL   en_US.UTF-8
ENV LANGUAGE en_US:en

# Make sure the package repository is up to date.
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y apt-utils locales \
 && sed -i 's/^# *\(en_US.UTF-8\)/\1/' /etc/locale.gen \
 && locale-gen \
 && dpkg-reconfigure locales \
 && ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime \
 && dpkg-reconfigure tzdata \
 && apt-get clean \
 && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

RUN apt-get update \
 && apt-get install -t jessie-backports -y \
      build-essential \
      curl \
      git \
      ca-certificates-java \
      openjdk-8-jre-headless \
      openssh-server \
      python-dev \
      python-pip \
      python-setuptools \
      sudo \
 && apt-get -y upgrade \
 && apt-get clean \
 && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*


RUN mkdir -p /var/run/sshd \
 && sed -i 's|session    required     pam_loginuid.so|session    optional     pam_loginuid.so|g' /etc/pam.d/sshd

RUN groupadd -r jenkins \
 && useradd -m -g sudo -d /home/jenkins -s /bin/sh jenkins \
 && echo "jenkins:jenkins" | chpasswd

COPY agent.jar /home/jenkins/agent.jar

# Standard SSH port
EXPOSE 22

USER jenkins:jenkins

CMD ["/usr/sbin/sshd", "-D"]