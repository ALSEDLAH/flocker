================
Before You Begin
================

Requirements
============

To replicate the steps demonstrated in this tutorial, you will need:

* Linux, FreeBSD, or OS X
* `Vagrant`_ (1.6.2 or newer)
* `VirtualBox`_
* At least 10GB disk space available for the two virtual machines
* The OpenSSH client (the ``ssh``, ``ssh-agent``, and ``ssh-add`` command-line programs)
* bash
* The ``mongo`` MongoDB interactive shell (see below for installation instructions)

You will also need ``flocker-cli`` installed (providing the ``flocker-deploy`` command).
See :ref:`installing-flocker-cli`.

Setup
=====

Installing MongoDB
------------------

The MongoDB client can be installed through the various package managers for Linux, FreeBSD and OS X.
If you do not already have the client on your machine, you can install it by running the appropriate command for your system.

Ubuntu
^^^^^^

.. code-block:: console

   alice@mercury:~$ sudo apt-get install mongodb-clients
   ...
   alice@mercury:~$

Red Hat / Fedora
^^^^^^^^^^^^^^^^

.. code-block:: console

   alice@mercury:~$ sudo yum -y install mongodb
   ...
   alice@mercury:~$

OS X
^^^^

Install `Homebrew`_

.. code-block:: console

   alice@mercury:~$ brew update
   ...
   alice@mercury:~$ brew install mongodb
   ...
   alice@mercury:~$

Other Systems
^^^^^^^^^^^^^

See the official `MongoDB installation guide`_ for your system.

Creating Vagrant VMs Needed for Flocker
---------------------------------------

Before you can deploy anything with Flocker you'll need a node onto which to deploy it.
To make this easier, this tutorial uses `Vagrant`_ to create two VirtualBox VMs.

These VMs serve as hosts on which Flocker can run Docker.
Flocker does not require Vagrant or VirtualBox.
You can run it on other virtualization technology (e.g., VMware), on clouds (e.g., EC2), or directly on physical hardware.

For your convenience, this tutorial includes ``Vagrantfile`` which will boot the necessary VMs.
Flocker and its dependencies will be installed on these VMs the first time you start them.
One important thing to note is that these VMs are statically assigned the IPs ``172.16.255.250`` (node1) and ``172.16.255.251`` (node2).
These two IP addresses will be used throughout the tutorial and configuration files.
If these addresses conflict with your local network configuration you can edit the ``Vagrantfile`` to use different values.
Note that you will need to make the same substitution in commands used throughout the tutorial.

.. note:: The two virtual machines are each assigned a 10GB virtual disk.
          The underlying disk files grow to about 5GB.
          So you will need at least 10GB of free disk space on your workstation.

#. Create a tutorial directory:

   .. sourcecode:: sh

      ~$ mkdir -p tutorial
      ~$ cd tutorial

#. Download the Vagrant configuration file by right clicking on the link below.
   Save it in the *tutorial* directory and preserve its filename.

   :download:`Vagrantfile <Vagrantfile>`

   .. literalinclude:: Vagrantfile
      :language: ruby
      :lines: 1-8
      :append: ...

   .. code-block:: console

      ~/tutorial$ ls
      Vagrantfile
      ~/tutorial$

#. Use ``vagrant up`` to start and provision the VMs:

   .. code-block:: console

      ~$ vagrant up
      ...

   This step may take several minutes or more as it downloads the Vagrant image, boots up two nodes and downloads the Docker image necessary to run the tutorial.
   Your network connectivity and CPU speed will affect how long this takes.
   Fortunately this extra work is only necessary the first time you bring up a node (until you destroy it).

#. After ``vagrant up`` completes you may want to verify that the two VMs are really running and accepting SSH connections:

   .. code-block:: console

      ~$ vagrant status
      Current machine states:

      node1                     running (virtualbox)
      node2                     running (virtualbox)
      ...
      ~$ vagrant ssh -c hostname node1
      node1
      Connection to 127.0.0.1 closed.
      ~$ vagrant ssh -c hostname node2
      node2
      Connection to 127.0.0.1 closed.

#. If all goes well, the next step is to configure your SSH agent.
   This will allow Flocker to authenticate itself to the VM:

   If you're not sure whether you already have an SSH agent running, ``ssh-add`` can tell you.
   If you don't, you'll see an error:

   .. code-block:: console

      alice@mercury:~/flocker-tutorial$ ssh-add
      Could not open a connection to your authentication agent.
      alice@mercury:~/flocker-tutorial$

   If you do, you'll see no output:

   .. code-block:: console

      alice@mercury:~/flocker-tutorial$ ssh-add
      alice@mercury:~/flocker-tutorial$

   If you don't have an SSH agent running, start one:

   .. code-block:: console

      alice@mercury:~/flocker-tutorial$ eval $(ssh-agent)
      Agent pid 27233
      alice@mercury:~/flocker-tutorial$

#. Finally, add the Vagrant key to your agent:

   .. sourcecode:: sh

      ~$ ssh-add ~/.vagrant.d/insecure_private_key

You now have two VMs running and easy SSH access to them.
This completes the Vagrant-related setup.

.. _`Homebrew`: http://brew.sh/
.. _`Vagrant`: https://docs.vagrantup.com/
.. _`VirtualBox`: https://www.virtualbox.org/
.. _`vagrant-cachier`: https://github.com/fgrehm/vagrant-cachier
.. _`MongoDB installation guide`: http://docs.mongodb.org/manual/installation/
