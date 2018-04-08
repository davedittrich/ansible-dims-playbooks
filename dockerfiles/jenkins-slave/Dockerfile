FROM base:latest
MAINTAINER Dave Dittrich <dave.dittrich@gmail.com>

# Make sure the package repository is up to date.
RUN apt-get update \
 && apt-get -y upgrade \
 && locale-gen en_US.UTF-8 \
 && apt-get install -y \
      build-essential \
      git \
      locales \
      maven \
      openjdk-7-jdk \
      openssh-server \
      python-dev \
      python-pip \
      python-setuptools \
 && apt-get clean \
 && rm -rf /var/cache/apt/archives/* /var/lib/apt/lists/*

RUN sed -i 's|session    required     pam_loginuid.so|session    optional     pam_loginuid.so|g' /etc/pam.d/sshd
RUN mkdir -p /var/run/sshd

RUN adduser --quiet jenkins
# Set password for the jenkins user
RUN echo "jenkins:jenkins" | chpasswd

RUN mkdir /home/jenkins/.m2
ADD settings.xml /home/jenkins/.m2/
RUN chown -R jenkins:jenkins /home/jenkins/.m2/ 

# Create entry point script and plugin directory.
COPY docker.entrypoint /
COPY docker.entrypoint.d/* /docker.entrypoint.d/
ONBUILD COPY docker.entrypoint.d/* /docker.entrypoint.d/

# Standard SSH port
EXPOSE 22

ENTRYPOINT ["/docker.entrypoint"]
