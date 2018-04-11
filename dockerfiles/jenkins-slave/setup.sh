#!/bin/bash
#
#  Copyright [2018] Dave Dittrich <dave.dittrich@gmail.com>. All rights reserved.
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

AGENT_VERSION=${AGENT_VERSION:-3.9}

# Ensure that a version of the Jenkins agent.jar file is available for
# installation in the container via Dockerfile COPY command. The
# Ansible 'jenkins2' role should extract the agent.jar file into the
# JENKINS_HOME directory. If not, pull from Jenkins web site.

if [[ ! -z $JENKINS_HOME && -f $JENKINS_HOME/agent.jar ]]; then
        cp $JENKINS_HOME/agent.jar .
else
    curl -sSLo \
        agent.jar \
        https://repo.jenkins-ci.org/public/org/jenkins-ci/main/remoting/${AGENT_VERSION}/remoting-${AGENT_VERSION}.jar
fi
exit $?

# vim: set ts=4 sw=4 tw=0 et :  
