=====
Usage
=====

Commands (and subcommands) generally follow the model set by the
`OpenStackClient`_ for its `Command Structure`_. The general structure
of a command is:

.. code-block:: console

   $ d2 [<global-options>] <object-1> <action> [<object-2>] [<command-arguments>]


  * The primary objects are things like ``query``, ``jobs``, etc.

  * The secondary objects are things like ``vars``, ``tql``, etc.

  * The actions are things like ``list``, ``show``, ``cancel``, etc.


.. _OpenStackClient: https://docs.openstack.org/python-openstackclient/latest/
.. _Command Structure: https://docs.openstack.org/python-openstackclient/latest/cli/commands.html


Getting help
------------

To get help information on global command arguments and options, use
the ``help`` command or ``--help`` option flag. The usage documentation
below will detail help output for each command.

.. Can't just get --help output using autoprogram-cliff. :(
..
.. .. autoprogram-cliff:: d2
..    :application: d2.main
..    :arguments: --help

.. literalinclude:: d2-help.txt
    :language: console

..

About
-----

.. autoprogram-cliff:: d2
   :command: about

.. EOF
