This directory contains a cookiecutter template for creating
a complete skeleton repository suitable for hosting on GitHub
that includes a Sphinx docs/ directory at the top level.


--------------------------------------------------------------------------
$ cookiecutter -h
Usage: cookiecutter [OPTIONS] TEMPLATE

  Create a project from a Cookiecutter project template (TEMPLATE).

Options:
  -V, --version              Show the version and exit.
  --no-input                 Do not prompt for parameters and only use
                             cookiecutter.json file content
  -c, --checkout TEXT        branch, tag or commit to checkout after git clone
  -v, --verbose              Print debug information
  --replay                   Do not prompt for parameters and only use
                             information entered previously
  -f, --overwrite-if-exists  Overwrite the contents of the output directory if
                             it already exists
  -o, --output-dir PATH      Where to output the generated project dir into
  --config-file PATH         User configuration file
  --default-config           Do not load a config file. Use the defaults
                             instead
  -h, --help                 Show this message and exit.
--------------------------------------------------------------------------

The defaults for cookiecutter prompts are kept in the file
"dims-new-repo/cookiecutter.json". A subset of these settings
is found in the YAML configuration file "dims-new-repo.yml".

Copy the file "dims-new-repo.yml" to customize it, using a
unique name to differentiate it from other configuration files
if you are going to make more than one repo at a time. For this
example, we will use "testrepo.yml" for the configuration file.

$ cp dims-new-repo.yml testrepo.yml

Edit the template to customize is at necessary. It should end
up looking something like this:


$ cat testrepo.yml
---

default_context:
  full_name: "Dave Dittrich"
  email: "dave.dittrich@gmail.com"
  project_name: "D2 Ansible Playbooks"
  project_slug: "ansible-dims-playbooks"
  project_short_description: "Ansible Playbooks for D2 System Configuration"
  project_copyright_name: "David Dittrich"


Now run "cookiecutter":

$ cookiecutter --no-input -f -o /tmp --config-file testrepo.yml dims-new-repo
[+] Fix underlining in these files:
/tmp/ansible-dims-playbooks/docs/source/index.rst
/tmp/ansible-dims-playbooks/README.rst

The templated RST file above cannot handle creating the section
underlining with the correct width for a given templated title,
since this is not a feature supported by Jinja2 and "cookiecutter"
(however "cookiecutter" does support hooks, which is how the
message above was generated.)

-------------------------------------------------------------------
.. ansible-dims-playbooks documentation master file, created by
   cookiecutter on 2018-01-01.

DIMS Ansible Playbooks v |release|
.. FIX_UNDERLINE

* GitHub repo: https://github.com/davedittrich/ansible-dims-playbooks/
* Documentation: https://davedittrich/projects/ansible-dims-playbooks/en/latest/
* License: Apache 2.0 License

Contact:
--------

Dave Dittrich dave.dittrich@gmail.com

.. |copy|   unicode:: U+000A9 .. COPYRIGHT SIGN

Copyright |copy| 2018 David Dittrich. All rights reserved.
----------------------------------------------------------

Edit the "FIX_UNDERLINE" line to look like this:


D2 Ansible Playbooks v |release|
================================


The repo directory is now ready to be populated
and committed to Git.

$ tree /tmp/ansible-dims-playbooks/
/tmp/ansible-dims-playbooks/
├── docs
│   ├── build
│   ├── Makefile
│   └── source
│       ├── conf.py
│       ├── license.rst
│       ├── license.txt
│       ├── _static
│       ├── _templates
│       ├── d2-logo.ico
│       └── d2-logo.png
├── README.rst
└── VERSION

5 directories, 8 files

