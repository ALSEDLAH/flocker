Release Process
===============

Outcomes
--------

By the end of the release process we will have:

- a tag in version control
- a Python wheel in the `ClusterHQ package index <http://archive.clusterhq.com>`__
- TODO: Will the pre-release wheel files be uploaded to the same archive or do we want to keep them separate (in the same way that we want to keep pre-release RPMs separate - https://github.com/ClusterHQ/flocker/issues/506)
- TODO: We also probably need a python source package on the same server, for use in Homebrew recipes.
- Fedora 20 RPMs for software on the node and client

If this is not a pre-release, we will also have:

- documentation on `docs.clusterhq.com <https://docs.clusterhq.com>`__
- download links on https://clusterhq.com


Prerequisites
-------------

Software
~~~~~~~~

- Fedora 20 (``rpmbuild``, ``createrepo``, ``yumdownloader``) - might be possible to install these on Ubuntu though

  You are advised to perform the release from a :doc:`Flocker development machine <vagrant>`\ , which will have all the requisite software pre-installed.

- a web browser

- an up-to-date clone of the `Flocker repository <https://github.com/ClusterHQ/flocker.git>`_

- an up-to-date clone of the `homebrew-tap repository <https://github.com/ClusterHQ/homebrew-tap.git>`_

Access
~~~~~~

- A Read the Docs account (`registration <https://readthedocs.org/accounts/signup/>`__),
  with `maintainer access <https://readthedocs.org/dashboard/flocker/users/>`__ to the Flocker project.

- Access to `Google Cloud Storage`_ using `gsutil`_.


Overview
~~~~~~~~

Every Flocker release shall follow these steps:

#. Prepare for a release
#. Release N pre-releases
#. Release the final release


Preliminary Step: Pre-populating RPM Repository
-----------------------------------------------

# TODO : Do this for the testing repo specifically?

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

   - Release numbers should be of the form x.y.z, or use the 'preN' suffix if this is a pre-release e.g.:

     .. code-block:: console

        export VERSION=0.0.3

#. File a ticket

   #. Assign it to yourself
   #. Call it "Release $RELEASE"

#. In a clean, local working copy of Flocker with no modifications, checkout the branch for the release:

   - If this is the first pre-release or a weekly release, make a branch and push it to Github:

     .. code-block:: console

        git checkout -b release/flocker-${VERSION%pre*} origin/master
        git push origin --set-upstream release/flocker-${VERSION%pre*}

   - If this is a follow up pre-release or a final release then there will already be a branch:

     .. code-block:: console

        $ git checkout -b release/flocker-${VERSION%pre*} origin/release/flocker-"${VERSION%pre*}"

        # TODO: Changes since the last pre-release need to be merged into the release branch? eg

        # TODO: For patch releases, document how the bug fixes in that release are chosen and merged to the release branch.

#. Update the version number in the download in ``docs/gettingstarted/linux-install.sh``, as well as the two RPMs in ``docs/gettingstarted/tutorial/Vagrantfile``, and the Homebrew recipe in the `homebrew-tap`_ repository (a total of 4 locations).
   # We could copy https://github.com/Homebrew/homebrew-versions and have a different `.rb` file for each release and pre-release e.g. flocker010.rb (eurgh)

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

   XXX Pre-releases should not be uploaded to the canonical RPM repository.
   See https://github.com/ClusterHQ/flocker/issues/506

   .. code-block:: console

      python setup.py bdist_wheel
      gsutil cp -a public-read dist/Flocker-"${VERSION}"-py2-none-any.whl gs://archive.clusterhq.com/downloads/flocker/
      admin/upload-rpms "${VERSION}"

#. Build tagged docs at Read the Docs:

   #. Go to the Read the Docs `dashboard <https://readthedocs.org/dashboard/flocker/versions/>`_.
   #. Enable the version being released.
   #. Wait for the documentation to build.
      The documentation will be visible at http://docs.clusterhq.com/en/${VERSION} when it has been built.
   #. Set the default version to that version (not for pre-releases).
   #. Force Read the Docs to reload the repository, in case the GitHub webhook fails, by running:

      .. code-block:: console

         curl -X POST http://readthedocs.org/build/flocker

#. Make a Pull Request on GitHub for the release branch against ``master``, with a ``Fixes #123`` line in the description referring to the release issue that it resolves.

Announcing Releases
~~~~~~~~~~~~~~~~~~~

Pre-releases do not need to be announced.

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

# TODO - what is acceptance testing? The whole tutorial / all examples? With pre-releases or just released software?
