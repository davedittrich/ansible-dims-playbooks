#FROM base:latest
FROM debian:jessie-backports
MAINTAINER Dave Dittrich <dave.dittrich@gmail.com>

ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8

RUN ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime \
 && dpkg-reconfigure tzdata \
 && localedef -i en_US -f UTF-8 en_US.UTF-8

# Make sure the package repository is up to date.
ENV DEBIAN_FRONTEND=noninteractive
RUN dpkg --add-architecture i386 \
 && apt-get update > /dev/null \
 && apt-get -y upgrade \
 && apt-get install -y \
      apt-utils \
      build-essential \
      curl \
      git \
      locales \
      openjdk-8-jre-headless \
      openssh-server \
      python-dev \
      python-pip \
      python-setuptools \
      sudo > /dev/null \
 && apt-get clean \
 && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

RUN mkdir -p /var/run/sshd \
 && sed -i 's|session    required     pam_loginuid.so|session    optional     pam_loginuid.so|g' /etc/pam.d/sshd

RUN useradd -m -d /home/jenkins -s /bin/sh jenkins \
 && echo "jenkins:jenkins" | chpasswd

COPY agent.jar /usr/share/jenkins/agent.jar

# Standard SSH port
EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
