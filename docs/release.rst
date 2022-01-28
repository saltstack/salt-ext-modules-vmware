.. _release:

Release
=======

The purpose of this document is to specify and outline the release process for
the Salt Extension Modules for VMware. Previously many of the steps were
manual, but the process is now mostly automatic.

Overview
--------

.. note::

    You may have issues building wheels on MacOS. It may be easier to build in
    a docker container or other VM.

The goal for this module is to have nightly dev builds released frequently.
It's possible that days go by without changes happening, but these builds will
still be called nightly builds.

The release cadence target for this module is every two weeks a release may be
published. A release candidate (rcN) package should be published a week ahead
of the release, allowing users time to test the upcoming packages against their
own environment.

Automated testing will happen against release artifacts, using at least the
current version of Salt, along with the current main development branch of
Salt. This will ensure that any breaking changes within Salt are detected ahead
of time, and can either be accounted for within this module, or upstream bugs
can be filed.

.. _dependencies:

Dependencies
------------

In order to run the release script, you'll need to have gpg installed with
gpg-agent. If you can run the following gpg command without having to type
anything in you should be good to go:

.. code::

     echo 'hello' | gpg --armor --clear-sign | gpg --verify

Obviously you'll need Python installed as well, and be able to run ``git push``
in your clone directory without `entering a
password<https://docs.github.com/en/authentication/connecting-to-github-with-ssh>`_.
``tar`` is also required.

In order to cut a release, you must be a project maintainer on TestPyPI as well
as PyPI. You'll need to have a token configured for the project. Your
``~/.pypirc`` should contain your key like the following:

.. code::

    [distutils]
      index-servers =
        test_saltext_vmware

    [test_saltext_vmware]
      repository = https://test.pypi.org/legacy/
      username = __token__
      password = pypi-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...

You *must* have ``test_saltext_vmware`` and ``saltext_vmware`` sections in your
distutils segment as well as have tokens configured.

.. _prebuild:

Pre-Build
---------

Before running the script you'll want to ensure that all the tests are passing.
With your activated venv, run the following command:

.. code::

    python -m nox -e tests-3

The result should be completely passing tests. If there are any failures,
ensure that they are fixed before continuing. Because the only difference
between this version and the actual deployed version will be the package
version, we're banking on the fact that the tests should still pass if they
already were here. But we *will* be testing the release artifact!

Ensure Version
--------------

The first thing to do is ensure that ``src/saltext/vmware/version.py`` has the
correct version for this release. In regards to version numbers, this project
uses Calver_, with the ``YY.M.D.PATCH`` style. Breaking (and any other) changes
should be communicated through the changelog_. Release candidate versions
should be created with the **expected** release date with ``rcN`` modifier. For
instance, if we planned to release 2010, August 14, we would set the version
like so:

.. code::

    __version__ = "10.8.14rc1"

Typically there will only be one RC build - though if bugs are found,
especially severe bugs, new RC versions will be built, tagged, and released.

.. _CalVer: https://calver.org/
.. _changelog: https://github.com/saltstack/salt-ext-modules-vmware/blob/main/CHANGELOG.md

The changelog will be automatically updated as part of this release process,
but if corrections need to be made it's totally fine to make updates out of
band.

Run the Release
---------------

Assuming that your environment is properly configured, all you should need to
do now is run:

.. code::

    python tools/release.py

The script will do several checks, ensuring that you have no outstanding
changes in the repo, it can correctly run gpg, and that you're not running
within a virtual environment (as it takes care of that for you).

After running the checks, which shouldn't really make any serious changes to
your system, you will be asked:

.. code::

    Continue to build and test saltext.vmware version 21.12.15.0rc1? [y/N]: y

The default is no. If you answer ``yes`` or ``y``, then a virtual environment
will be created for testing the release, the package will be built, installed
to the virtual environment, and then tested.

If anything fails up to this point then the release will bail out and you'll
need to make changes.

If everything succeeds, and all looks OK then you will be given one last chance
to bail out before pushing changes to PyPI and GitHub.

.. code::

    WARNING: This will really upload saltext.vmware version 21.12.15.0rc1 to
    pypi. There is no going back from this point.
    Enter "deploy" without quotes to really deploy: deploy

If you enter anything besides ``deploy`` then the release will abort. Basically
we want to be *very* sure that we're ready to release! If you are, cool - just
type ``deploy`` and hit enter.

The release will then be pushed to
https://test.pypi.org/project/saltext.vmware/ and
https://pypi.org/project/saltext.vmware/ after the successful completion of
which, the tag will be created and pushed to GitHub, suitable for `drafting a
new
release<https://github.com/saltstack/salt-ext-modules-vmware/releases/new>`_.

The finally part of the release script will create
``/tmp/saltext.vmware-build-{version}.tar.gz`` that you can use to get the
changelog, ``.whl``, and ``.whl.asc`` signature file to use for creating the
GitHub release, as well as publishing notifications to social media/websites.

Congrats! You've just cut a new release!
