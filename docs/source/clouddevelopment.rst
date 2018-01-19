.. _clouddevelopment:

Developing in the Cloud
=======================

This section covers deployment and development using a cloud
service provider.

Developing on DigitalOcean
--------------------------

This chapter covers development or prototype deployment on the
`DigitalOcean`_ platform using Hashicorp `Terraform`_.

Control of Digital Ocean droplets using these playbooks is done in the
subdirectory ``do/dims/`` beneath the root directory of the cloned repository.
(This document assumes an environment variable ``$PBR`` points to the
repository root.)

A helper ``Makefile`` and related scripts facilitate most of the steps used for
creating and controlling DigitalOcean droplets using DigitalOcean's remote
API.  This remote API is accessible directly using programs like ``dopy``
or ``curl``, or indirectly using ``terraform``.

.. note::

    The ``Makefile`` has built-in help text that serves as a reminder of
    capabilities it supports.

    .. code-block:: none

        Usage: make [something]

        Where 'something' is one of these:

         help - print this help text
         init - initialize terraform state (this is automatic)
         droplets - show list of active droplets using digital_ocean.py dynamic inventory
         hosts - show list of hosts in group 'do'
         images - lists available DigitalOcean images
         regions - lists available DigitalOcean regions
         provider - generate terraform provider.tf file for creating nodes in group 'do'

         plan - show the terraform plan for the current state
         graph - generate terraform graph (output is 'graph.png')
         newkeypair - generate a new SSH user keypair
         insertpubkey - insert SSH public key on DigitalOcean
         removepubkey - remove SSH public key on DigitalOcean
         create - applies terraform plan to create droplets for hosts in group 'do'
         bootstrap - create, then run bootstrap.yml and ca-certs.yml playbooks
         installcerts - run 'certbot-installcert.yml' playbook to install SSL certs
         deploy - run 'master.yml' playbook to deploy roles on droplets

         update - update packages
         reboot - reboot the system in +1 minute
         cancel - cancel rebooting (if you REALLY DIDN'T MEAN IT)

         addhostkeys - adds SSH host public keys to selected known_hosts files
         removehostkeys - removes SSH host public keys from selected known_hosts files

         dumpvars - produces Ansible debug output of vars for hosts in group 'do'
         ping - does Ansible ad-hoc ping of hosts in group 'do'
         pre.test - run pre-requisite tests for using terraform with DigitalOcean
         post.test - run 'test.runner --terse' on all droplets

         destroy - destroys droplets for hosts in group 'do'
         spotless - remove terraform log and state files

         * The default if you just type 'make' is the same as 'make help'
         * To control Ansible, set DIMS_ANSIBLE_ARGS to the arguments you want
           to pass along on the command line, for example:
             $ make DIMS_ANSIBLE_ARGS="--tags tests --limit purple" deploy
             $ make DIMS_ANSIBLE_ARGS="--limit purple" post.test

    ..

..

.. _gettingstarted:

Getting Started
~~~~~~~~~~~~~~~

To use this remote API, you must first create a **personal access token**
and store it locally in your account.  Start by initializing the directory for
use by running ``make init``. This will both initialize ``terraform`` and
ensure that a directory for storing secrets (and empty ``token`` file)
is created with the proper permissions.

.. code-block:: none

    $ make init
    $ tree -aifp ~ | grep ~/.secrets
    [drwx------]  /Users/dittrich/.secrets
    [drwx------]  /Users/dittrich/.secrets/digital-ocean
    [-rw-------]  /Users/dittrich/.secrets/digital-ocean/token

..

The file that will hold the token is the last one listed. To get the token, go
to your DigitalOcean control panel, select **API**, then select **Generate New
Token**. Copy the token and place it in the file
``~/.secrets/digital-ocean/token``.

Next, add to your Bash shell initialization file (``~/.bashrc`` or
``~/.bash_aliases``) the following lines:

.. code-block:: none

    # For dopy
    export DO_API_VERSION="2"
    export DO_API_TOKEN="$(cat ~/.secrets/digital-ocean/token)"

    # For terraform
    export DO_PAT=${DO_API_TOKEN}
    export TF_VAR_do_token="${DO_PAT}"
    export TF_VAR_region="sfo1"  # See output of "make regions" for available regions
    export TF_VAR_name="do"
    export TF_VAR_private_key="/Users/dittrich/.ssh/do"
    export TF_VAR_public_key="${TF_VAR_private_key}.pub"
    export TF_VAR_ssh_fingerprint="$(ssh-keygen -E md5 -lf ${TF_VAR_public_key} | awk '{print $2}' | sed 's/^[Mm][Dd]5://')"

..

After loading the token, you should be able to get a list of available
regions with ``make regions``:


.. code-block:: json

   ["nyc1","sfo1","nyc2","ams2","sgp1","lon1","nyc3","ams3","fra1","tor1","sfo2","blr1"]

..

You can get a list of available images (just the first 10 shown here)
using ``make images``:

.. code-block:: json

    {"slug":"cassandra","distribution":"Ubuntu","name":"Cassandra on 14.04"}
    {"slug":"centos-6-5-x32","distribution":"CentOS","name":"6.7 x32"}
    {"slug":"centos-6-5-x64","distribution":"CentOS","name":"6.7 x64"}
    {"slug":"centos-6-x32","distribution":"CentOS","name":"6.9 x32"}
    {"slug":"centos-6-x64","distribution":"CentOS","name":"6.9 x64"}
    {"slug":"centos-7-x64","distribution":"CentOS","name":"7.4 x64"}
    {"slug":"coreos-alpha","distribution":"CoreOS","name":"1618.0.0 (alpha)"}
    {"slug":"coreos-beta","distribution":"CoreOS","name":"1590.2.0 (beta)"}
    {"slug":"coreos-stable","distribution":"CoreOS","name":"1576.4.0 (stable)"}
    {"slug":"debian-7-x32","distribution":"Debian","name":"7.11 x32"}

..

A ``bats`` test file exists to validate *all* of the required elements necessary
to create and control DigitalOcean droplets. When all pre-requisites are
satisfied, all tests will succeed.

.. code-block:: none

    $ make test
    bats do.bats
     ✓ [S][EV] Directory for secrets (~/.secrets/) exists
     ✓ [S][EV] Directory for secrets (~/.secrets/) is mode 700
     ✓ [S][EV] Directory for DigitalOcean secrets (~/.secrets/digital-ocean/) exists
     ✓ [S][EV] DigitalOcean token is in ~/.secrets/digital-ocean/token
     ✓ [S][EV] Variable DO_API_VERSION (dopy) is defined in environment
     ✓ [S][EV] Variable DO_API_TOKEN (dopy) is defined in environment
     ✓ [S][EV] Variable DO_PAT (terraform) is defined in environment
     ✓ [S][EV] Variable TF_VAR_do_token (terraform) is defined in environment
     ✓ [S][EV] Variable TF_VAR_region (terraform) is defined in environment
     ✓ [S][EV] Variable TF_VAR_name (terraform) is defined in environment
     ✓ [S][EV] Variable TF_VAR_domain (terraform) is defined in environment
     ✓ [S][EV] Variable TF_VAR_datacenter (terraform) is defined in environment
     ✓ [S][EV] Variable TF_VAR_private_key (terraform) is defined in environment
     ✓ [S][EV] Variable TF_VAR_public_key (terraform) is defined in environment
     ✓ [S][EV] Variable TF_VAR_ssh_fingerprint (terraform) is defined in environment
     ✓ [S][EV] DO_API_TOKEN authentication succeeds
     ✓ [S][EV] Variable TF_VAR_public_key (terraform .tf) is defined in environment
     ✓ [S][EV] File pointed to by TF_VAR_public_key exists and is readable
     ✓ [S][EV] Variable TF_VAR_private_key (terraform .tf) is defined in environment
     ✓ [S][EV] File pointed to by TF_VAR_private_key exists and is readable
     ✓ [S][EV] Variable TF_VAR_ssh_fingerprint (terraform .tf) is defined in environment
     ✓ [S][EV] DO_API_TOKEN authentication succeeds
     ✓ [S][EV] terraform is found in $PATH

    23 tests, 0 failures

..

.. _bootstrapping:

Bootstrapping DigitalOcean Droplets
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once remote access to DigitalOcean via the remote API is set up,
the next tasks are to generate an SSH user key to use for remote
access to droplets.  Use the helper ``Makefile`` target ``sshkey``
to create a new SSH user key in the location specified by the
environment variable


.. _terraformstate:

Leveraging the Terraform State File
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Terraform maintains state in a file named ``terraform.tfstate`` (and
a backup file ``terraform.tfstate.backup``) in the home directory
where Terraform was initialized. While the ``terraform.tfstate`` file
is a JSON object that can be manipulated using programs like `jq`_,
the proper way to exploit this state is to use ``terraform output --json``.

Introduction to ``jq``
^^^^^^^^^^^^^^^^^^^^^^

To better understand how to manipulate the contents of the
``terraform.tfstate`` file with ``jq``, we will start out by directly
manipulating the file so we don't have to *also* struggle with defining
Terraform ``output`` variables.

.. note::

    See `Reshaping JSON with jq`_ for examples of how to use ``jq``.

..

Using the filter ``.`` with ``jq`` will show the entire structure. Here are the
first 10 lines in a ``terraform.tfstate`` file

.. code-block:: none

    $ jq -r '.' terraform.tfstate | head
    {
      "version": 3,
      "terraform_version": "0.11.1",
      "serial": 7,
      "lineage": "755c781e-407c-41e2-9f10-edd0b80bcc9f",
      "modules": [
        {
          "path": [
            "root"
          ],

..

.. note::

   To more easily read the JSON, you can pipe the output through
   ``pygmentize`` to colorize it, then ``less -R`` to preserve
   the ANSI colorization codes. The command line to use is:

   .. code-block:: bash

       $ jq -r '.' terraform.tfstate | pygmentize | less -R

   ..

..

By choosing a specific field for the filter, ``jq`` will print just that field.

.. code-block:: none

    $ jq -r '.lineage' terraform.tfstate
    755c781e-407c-41e2-9f10-edd0b80bcc9f

..

Adding ``[]`` to a field that is an array produces a list, and piping filters with
a ``|`` allows additional filtering to be applied to narrow the results. Functions
like ``select()`` can be used to extract a specific field from a list element that
is a dictionary, allowing selection of just specific members. In the next example,
the nested structures named ``resources`` within the structure ``modules`` are
evaluated, selecting only those where the ``type`` field is ``digitalocean_record``
(i.e., DNS records).

.. code-block:: bash

    $ jq -r '.modules[] | .resources[] | select(.type | test("digitalocean_record"))' terraform.tfstate

..

The first record is highlighted in the output here.  Within the record are
two fields (``.primary.attributes.fqdn`` and ``.primary.attributes.value``)
that are needed to help build ``/etc/hosts`` style DNS mappings, or to
generate a YAML inventory file.

.. code-block:: json
   :emphasize-lines: 1-26
   :linenos:

    {
      "type": "digitalocean_record",
      "depends_on": [
        "digitalocean_domain.default",
        "digitalocean_droplet.blue"
      ],
      "primary": {
        "id": "XXXXXXXX",
        "attributes": {
          "domain": "secretsmgmt.tk",
          "fqdn": "blue.secretsmgmt.tk",
          "id": "XXXXXXXX",
          "name": "blue",
          "port": "0",
          "priority": "0",
          "ttl": "360",
          "type": "A",
          "value": "XXX.XXX.XXX.XX",
          "weight": "0"
        },
        "meta": {},
        "tainted": false
      },
      "deposed": [],
      "provider": "provider.digitalocean"
    }
    {
      "type": "digitalocean_record",
      "depends_on": [
        "digitalocean_domain.default",
        "digitalocean_droplet.orange"
      ],
      "primary": {
        "id": "XXXXXXXX",
        "attributes": {
          "domain": "secretsmgmt.tk",
          "fqdn": "orange.secretsmgmt.tk",
          "id": "XXXXXXXX",
          "name": "orange",
          "port": "0",
          "priority": "0",
          "ttl": "360",
          "type": "A",
          "value": "XXX.XXX.XXX.XXX",
          "weight": "0"
        },
        "meta": {},
        "tainted": false
      },
      "deposed": [],
      "provider": "provider.digitalocean"
    }

..

By adding another pipe step to create an list item with just these two
fields, and adding the ``-c`` option to create a single-line JSON object.

.. code-block:: none

    $ jq -c '.modules[] | .resources[] | select(.type | test("digitalocean_record")) | [ .primary.attributes.fqdn, .primary.attributes.value ]' terraform.tfstate

..

.. code-block:: json

    ["blue.secretsmgmt.tk","XXX.XXX.XXX.XX"]
    ["orange.secretsmgmt.tk","XXX.XXX.XXX.XXX"]

..

These can be further converted into formats parseable by Unix shell programs
like ``awk``, etc., using the filters ``@csv`` or ``@sh``:

.. code-block:: none

    $ jq -r '.modules[] | .resources[] | select(.type | test("digitalocean_record")) | [ .primary.attributes.name, .primary.attributes.fqdn, .primary.attributes.value ]| @csv' terraform.tfstate
    "blue","blue.secretsmgmt.tk","XXX.XXX.XXX.XX"
    "orange","orange.secretsmgmt.tk","XXX.XXX.XXX.XXX"
    $ jq -r '.modules[] | .resources[] | select(.type | test("digitalocean_record")) | [ .primary.attributes.name, .primary.attributes.fqdn, .primary.attributes.value ]| @sh' terraform.tfstate
    'blue' 'blue.secretsmgmt.tk' 'XXX.XXX.XXX.XX'"
    'blue' 'orange.secretsmgmt.tk' 'XXX.XXX.XXX.XXX'"

..

Processing ``terraform output --json``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The droplets created by ``terraform apply`` are exposed by output
variables to facilitate constructing an Ansible inventory. To see
these variables, use ``terraform output``:

.. code-block:: bash

    $ terraform output
    blue = {
      blue.secretsmgmt.tk = XXX.XX.XXX.XXX
    }
    orange = {
      orange.secretsmgmt.tk = XXX.XX.XXX.XXX
    }

..

This output could be processed with ``awk``, but we want to
use ``jq`` instead to be more direct.  To get JSON output,
add the ``--json`` flag:


.. code-block:: bash

    $ terraform output --json
    {
        "blue": {
            "sensitive": false,
            "type": "map",
            "value": {
                "blue.secretsmgmt.tk": "XXX.XX.XXX.XXX"
            }
        },
        "orange": {
            "sensitive": false,
            "type": "map",
            "value": {
                "orange.secretsmgmt.tk": "XXX.XX.XXX.XXX"
            }
        }
    }

..

To get to clean single-line, multi-colum output, we need to use
``to_entries[]`` to turn the dictionaries into key/value pairs,
nested two levels deep in this case.

.. code-block:: none

    $ terraform output --json | jq -r 'to_entries[] | [ .key, (.value.value|to_entries[]| .key, .value) ]|@sh'
    'blue' 'blue.secretsmgmt.tk' 'XXX.XX.XXX.XXX'
    'orange' 'orange.secretsmgmt.tk' 'XXX.XX.XXX.XXX'

..

Putting all of this together with a much simpler ``awk`` script, a YAML
inventory file can be produced as shown in the script ``do_post.sh``.

.. literalinclude:: ../../do/dims/do_post.sh
   :language: bash

.. code-block:: yaml

    ---
    # This is a generated inventory file produced by ./do_post.sh.
    # DO NOT EDIT THIS FILE.

    do:
      hosts:
        'blue':
          ansible_host: 'XXX.XXX.XXX.XX'
          ansible_fqdn: 'blue.secretsmgmt.tk'
        'orange':
          ansible_host: 'XXX.XXX.XXX.XXX'
          ansible_fqdn: 'orange.secretsmgmt.tk'

..

This inventory file can then be used by Ansible to perform ad-hoc tasks or run
playbooks.

.. code-block:: none

    $ make ping
    ansible -i ../../environments/do/inventory \
                     \
                    -m ping do
    orange | SUCCESS => {
        "changed": false,
        "failed": false,
        "ping": "pong"
    }
    blue | SUCCESS => {
        "changed": false,
        "failed": false,
        "ping": "pong"
    }

..

.. _DigitalOcean: https://www.digitalocean.com/
.. _Terraform: https://www.terraform.io/
.. _jq: https://stedolan.github.io/jq/manual/
.. _Reshaping JSON with jq: https://programminghistorian.org/lessons/json-and-jq

.. EOF
