Release Process
===============

Outcomes
--------

By the end of the release process we will have:

- a tag in version control
- a Python wheel in the `ClusterHQ package index <http://archive.clusterhq.com>`__
- Fedora 20 RPMs for software on the node and client
- documentation on `docs.clusterhq.com <https://docs.clusterhq.com>`__
- download links on https://clusterhq.com


Prerequisites
-------------

Software
~~~~~~~~

- Fedora 20 (``rpmbuild``, ``createrepo``, ``yumdownloader``) - might be possible to install these on Ubuntu though

  You are advised to perform the release from a :doc:`flocker development machine <vagrant>`\ , which will have all the requisite software pre-installed.

- a web browser

- an up-to-date clone of the `Flocker repository <https://github.com/ClusterHQ/flocker.git>`_

- an up-to-date clone of the `homebrew-tap repository <https://github.com/ClusterHQ/homebrew-tap.git>`_

Access
~~~~~~

- A Read the Docs account (`registration <https://readthedocs.org/accounts/signup/>`__),
  with `maintainer access <https://readthedocs.org/dashboard/flocker/users/>`__ to the Flocker project.

- Access to `Google Cloud Storage`_ using `gsutil`_.


Preliminary Step: Pre-populating RPM Repository
-----------------------------------------------

This only needs to be done if the dependency packages for Flocker (i.e. ``geard`` and Python libraries) change; it should *not* be done every release.
If you do run this you need to do it *before* running the release process above as it removes the ``flocker-cli`` etc. packages from the repository!

These steps must be performed from a machine with the ClusterHQ Copr repository installed.
You can either use the :doc:`Flocker development environment <vagrant>`
or install the Copr repository locally by running ``curl https://copr.fedoraproject.org/coprs/tomprince/hybridlogic/repo/fedora-20-x86_64/tomprince-hybridlogic-fedora-20-x86_64.repo >/etc/yum.repos.d/hybridlogic.repo``

::

   mkdir repo
   yumdownloader --destdir=repo geard python-characteristic python-eliot python-idna python-netifaces python-service-identity python-treq python-twisted
   createrepo repo
   gsutil cp -a public-read -R repo gs://archive.clusterhq.com/fedora/20/x86_64


::

   mkdir srpm
   yumdownloader --destdir=srpm --source geard python-characteristic python-eliot python-idna python-netifaces python-service-identity python-treq python-twisted
   createrepo srpm
   gsutil cp -a public-read -R srpm gs://archive.clusterhq.com/fedora/20/SRPMS


Preparing for a release
-----------------------

#. Choose a version number:

   - Release numbers should be of the form x.y.z e.g.:

     .. code-block:: console

        export VERSION=0.0.3

   - Sanity check the proposed version number by checking the last version.
     Check the ClusterHQ website for the last released version.
     You might also double check the current version by running the following commands:

     .. code-block:: console

        $ python setup.py --version
        0.0.1-576-ge15c6be

        $ git tag
        ...
        0.0.6

#. In a clean, local working copy of Flocker with no modifications, checkout the branch for the release:

   .. note:: All releases of the x.y series will be made from the ``releases/flocker-x.y`` branch.

   - If this is a major or minor release then create the branch for the minor version:

     .. code-block:: console

        git checkout -b release/flocker-${VERSION%.*} origin/master
        git push origin --set-upstream release/flocker-${VERSION%.*}

   - If this is a patch release then there will already be a branch:

     .. code-block:: console

        $ git checkout -b release/flocker-${VERSION%.*} origin/release/flocker-"${VERSION%.*}"

#. Update the version number in the download in ``docs/gettingstarted/linux-install.sh``, as well as the two RPMs in ``docs/gettingstarted/tutorial/Vagrantfile``, and the Homebrew recipe in the `homebrew-tap`_ repository (a total of 4 locations).

#. Update the ``sha1`` in the Homebrew recipe in the `homebrew-tap`_.

   With Homebrew on OS X you can get the ``sha1`` using ``brew fetch flocker`` if the latest ``flocker.rb`` is in ``/usr/local/Library/formula``.

   On Linux:

   .. code-block:: console

      wget https://github.com/ClusterHQ/flocker/archive/${VERSION}.tar.gz
      sha1sum ${VERSION}.tar.gz

#. Commit the changes:

   .. code-block:: console

      git commit -am"Bumped version number in installers and Vagrantfiles"
      git push

#. Ensure the release notes in :file:`NEWS` are up-to-date.

   XXX: Process to be decided. See https://github.com/ClusterHQ/flocker/issues/523

#. Ensure copyright dates in :file:`LICENSE` are up-to-date.

   XXX: Process to be decided.
   If we modify the copyright in the release branch, then we'll need to merge that back to master.
   It should probably just be updated routinely each year.
   See https://github.com/ClusterHQ/flocker/issues/525

#. Ensure all the tests pass on BuildBot.
   Go to the `BuildBot web status <http://build.clusterhq.com/boxes-flocker>`_ and force a build on the just-created branch.
#. Do the acceptance tests. (https://github.com/ClusterHQ/flocker/issues/315)

- Start a new Ubuntu VM
- Clone flocker
- Build the documentation
- Create a new directory to run the acceptance tests from
- Copy all the things from docs/_build/html/_downloads into this new directory
- Install wordish
- Run the tests
# TODO Can we have alice@mercury? If not, make Fedora / OS X instructions consistent
# TODO integrate with trial so we can have this as part of our suite
# TODO not just copy, but also put some things in different directories, e.g. Vagrantfile in the flocker-tutorial directory
# TODO change the name of the flocker-tutorial directory because it is confusing with the automatically created directory
# TODO specify the order of "articles" - add this feature to wordish?

Release
-------

#. Change your working directory to be the Flocker release branch checkout.

#. Create (if necessary) and activate the Flocker release virtual environment:

   .. code-block:: console

      virtualenv ~/Environments/flocker-release
      . ~/Environments/flocker-release/bin/activate
      pip install --editable .[release]

#. Tag the version being released:

   .. code-block:: console

      git tag --annotate "${VERSION}" release/flocker-"${VERSION%.*}" -m "Tag version ${VERSION}"
      git push origin "${VERSION}"

#. Go to the `BuildBot web status <http://build.clusterhq.com/boxes-flocker>`_ and force a build on the tag.

   .. note:: We force a build on the tag as well as the branch because the RPMs built before pushing the tag won't have the right version.
             Also, the RPM upload script currently expects the RPMs to be built from the tag, rather than the branch.

   You force a build on a tag by putting the tag name into the branch box (without any prefix).

#. Set up ``gsutil`` authentication by following the instructions from the following command:

   .. code-block:: console

      $ gsutil config

#. Build python packages for upload, and upload them to ``archive.clusterhq.com``, as well as uploading the RPMs:

   .. code-block:: console

      python setup.py bdist_wheel
      gsutil cp -a public-read dist/Flocker-"${VERSION}"-py2-none-any.whl gs://archive.clusterhq.com/downloads/flocker/
      admin/upload-rpms "${VERSION}"

#. Build tagged docs at Read the Docs:

   #. Go to the Read the Docs `dashboard <https://readthedocs.org/dashboard/flocker/versions/>`_.
   #. Enable the version being released.
   #. Set the default version to that version.
   #. Force Read the Docs to reload the repository, in case the GitHub webhook fails, by running:

      .. code-block:: console

         curl -X POST http://readthedocs.org/build/flocker

#. Make a Pull Request on GitHub for the release branch against ``master``, with a ``Fixes #123`` line in the description referring to the release issue that it resolves.

Update Download Links
~~~~~~~~~~~~~~~~~~~~~

XXX Update download links on https://clusterhq.com:

XXX Arrange to have download links on a page on https://clusterhq.com.
See:

- https://github.com/ClusterHQ/flocker/issues/359 and
- https://www.pivotaltracker.com/n/projects/946740/stories/75538272


.. _gsutil: https://developers.google.com/storage/docs/gsutil
.. _wheel: https://pypi.python.org/pypi/wheel
.. _Google cloud storage: https://console.developers.google.com/project/apps~hybridcluster-docker/storage/archive.clusterhq.com/
.. _homebrew-tap: https://github.com/ClusterHQ/homebrew-tap
