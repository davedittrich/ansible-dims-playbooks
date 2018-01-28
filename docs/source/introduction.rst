.. _introduction:

Introduction 
============

This chapter documents the D2 DIMS Ansible playbooks [*]_
(``ansible-dims-playbooks`` for short) repository.

This repository contains the Ansible playbooks and inventory
for a development/test environment. It can be extended, enhanced,
and customized for a production deployment using the features
described in this document.

At a high level, these playbooks assist in composing a *small-scale
distributed system* (i.e., a larger system composed of multiple
hosts and/or containers that are configured to operate in concert.)

The resulting system supports any/all of the following features:

* Semi-automated provisioning and deployment of Digital Ocean droplets and DNS
  records using ``terraform``.

* Support for SSH host key management allowing ``StrictHostKeyChecking``
  to be left enabled, while avoiding manual host key validation or
  insertion/deletion.

* A Trident trust group management and communication portal behind an NGINX
  reverse proxy secured by TLS.

* A Jenkins build server behind an Nginx reverse proxy secured by TLS, with
  Jenkins CLI secured with SSH.

* Support for Letsencrypt SSL/TLS certificate generation, backup/restoration,
  renewal-hooks for deploying certificates to non-privileged services, and
  scheduled certificate renewal maintenance.

* Support for SPF, DKIM, and DMARC in Postfix SMTP email.

* Centralized ``rsyslog`` logging secured by TLS.

* AMQP (RabbitMQ) message bus for remote procedure call, log distribution, and
  simple text chat, all secured by TLS.


Installation Steps
------------------

Before diving into the details, it is helpful to understand the
high level tasks that must be performed to bootstrap a functional
deployment.

* Install the base operating system for the initial Ansible
  control host that will be used for configuring the deployment
  (e.g., on a development laptop or server).

* Set up host playbook and vars files for the Ansible control host.

* Pre-populate artifacts on the Ansible control host for use
  by virtual machines under Ansible control.

* Instantiate the virtual machines that will be used to
  provide the selected services and install the base operating
  system on them, including an ``ansible`` account with initial
  password and/or SSH ``authorized_keys`` files allowing access
  from the Ansible control host.

* Set up host playbooks, host vars files, and inventory definitions
  for the selected virtual machines.

* Validate that the Ansible control host is capable of connecting
  to all of the appropriate hosts defined in the inventory using
  Ansible *ad-hoc* mode.

* Finish customizing any templates, installed scripts, and secrets
  (e.g., passwords, certificates) unique to the deployment.

.. [*] D2 is a fork of the original DIMS Ansible Playbooks.
