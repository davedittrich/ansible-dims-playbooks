#FROM base:latest
FROM debian:jessie-backports
MAINTAINER Dave Dittrich <dave.dittrich@gmail.com>

ENV LANG     en_US.UTF-8
ENV LC_ALL   en_US.UTF-8
ENV LANGUAGE en_US:en

# See: https://github.com/fjudith/docker-jenkins/blob/master/Dockerfile

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
      ca-certificates-java \
      curl \
      git \
      golang-go \
      openjdk-8-jdk-headless \
      openjdk-8-jre-headless \
      openssh-server \
      python-dev \
      python-pip \
      python-setuptools \
      sudo \
      tree \
      wget \
 && apt-get install -y dh-golang dh-systemd \
 && apt-get -y upgrade \
 && apt-get clean \
 && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

# Leave apt-get ready to go for Trident builds
RUN apt-get update

RUN mkdir -p /var/run/sshd \
 && sed -i 's|session    required     pam_loginuid.so|session    optional     pam_loginuid.so|g' /etc/pam.d/sshd

RUN groupadd -r jenkins \
 && useradd --create-home \
            --gid jenkins \
            --home-dir /home/jenkins \
            --shell /bin/sh jenkins \
 && usermod -aG sudo jenkins \
 && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers \
 && echo "jenkins:jenkins" | chpasswd

COPY agent.jar /home/jenkins/agent.jar

# Set default options
# http://docs.oracle.com/javase/8/docs/technotes/tools/windows/java.html
#ENV JAVA_OPTS="-Xmx8192m"
ENV JAVA_OPTS="-XX:+UnlockExperimentalVMOptions -XX:+UseCGroupMemoryLimitForHeap"

# http://winstone.sourceforge.net/#commandLine
ENV JENKINS_OPTS="--handlerCountMax=300"
#ENV JENKINS_OPTS="--handlerCountMax=300 --logfile=/var/log/jenkins/jenkins.log"

# Enable access log
ENV JENKINS_ACCESSLOG="--accessLoggerClassName=winstone.accesslog.SimpleAccessLogger --simpleAccessLogger.format=combined --simpleAccessLogger.file=/var/log/jenkins/access.log"

# Standard SSH port
EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
