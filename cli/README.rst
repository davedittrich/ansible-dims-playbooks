==
d2
==

.. .. image:: https://img.shields.io/pypi/v/d2.svg
..         :target: https://pypi.python.org/pypi/d2
..
.. .. image:: https://img.shields.io/travis/davedittrich/d2.svg
..         :target: https://travis-ci.org/davedittrich/d2
..
.. .. image:: https://readthedocs.org/projects/d2/badge/?version=latest
..         :target: https://d2.readthedocs.io/en/latest/?badge=latest
..         :alt: Documentation Status


Python CLI for LiminalAI.

* License: Apache 2.0 License
* Documentation: https://d2.readthedocs.io/en/latest/


Features
--------

* Uses the `openstack/cliff`_ command line framework.

.. _openstack/cliff: https://github.com/openstack/cliff

Usage information for subcommands is available in the **Usage** section.
This section covers high-level concepts related to the ``d2`` app.

Output formatting
-----------------

One of the benefits of the Cliff framework is the ability to switch from the
table output seen earlier to another output format, such as JSON, CSV, or in
certain cases even shell variable definitions.  This helps generalize and
abstract out into data structures a mechanism to handle the coupling of
internal program variable names between multiple programs. Rather than
hard-coding, the template can be used to define the variables and values for a
given program run.

.. EOF
