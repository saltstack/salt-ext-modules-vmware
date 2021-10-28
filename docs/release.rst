.. _release:

Release
=======

The purpose of this document is to specify and outline the release process for
the Salt Extension Modules for VMware. Initially for the beta releases, many of
these steps will be manual. Over time the process will become more automated.

Overview
--------

.. note::

    You may have issues building wheels on MacOS. It may be easier to build in
    a docker container or other VM.

The goal for this module is to have nightly dev builds released frequently.
It's possible that days go by without changes happening, but these builds will
still be called nightly builds.

The release cadence target for this module is every two weeks a release may be
published. A release candidate (rcN) package will be published a week ahead of
the release, allowing users time to test the upcoming packages against their
own environment.

Automated testing will happen against release artifacts, using at least the
current version of Salt, along with the current main development branch of
Salt. This will ensure that any breaking changes within Salt are detected
ahead of time, and can either be accounted for within this module, or upstream
bugs can be filed.

.. _build:

Build
-----

To prepare for a release, the first step is to ensure you're on the latest
commit on the main branch and build the release artifact, along with
dependencies:

.. code::

    git fetch salt
    git stash  # if needed
    git checkout salt/main
    # If pip and wheel are not already installed/up-to-date
    python -m pip install --upgrade pip wheel
    python -m pip wheel .\[dev,tests,release\] -w dist/

This will create a ``.whl`` file for the extension module, as well as all of
the dependencies, in the ``dist/`` directory.


Ensure Version
--------------

When it comes time to build a release, ensure that
``src/saltext/vmware/version.py`` contains the correct version. For an release
candidate (RC) release the format should be ``YY.M.D.PATCHrcN``. Any subsequent RC
releases should increment ``N``. The release manager should start cutting RCs
far enough ahead of time to be able to cut a complete release on the target
date. For a production release, the format should be ``YY.M.D.PATCH``. For
instance, if we were going to release on 2010-08-14, we would start with

.. code::

    __version__ = '10.8.14.0rc1'

When the release is deemed ready, the version would be ``10.8.14.0``.

If the incorrect version is present in the ``main`` branch, it should be
updated, committed, and pushed before continuing this process.

Commit ``src/saltext/vmware/version.py``, rebuild and continue testing. Do **not** merge into https://github.com/saltstack/salt-ext-modules-vmware/.

Install and Test the Build
--------------------------

To ensure that the virtual environment is pristine, create a new one. Then the
package and necessary dependencies can be installed into the environment. By
building the extension and dependencies locally, and using a pristine
environment, this will help ensure that any missing dependencies are detected
before release. Tests will be executed against the installed package, and not
the local source, which helps to ensure the complete install process is tested.

.. code::

    deactivate  # if a venv is already activated
    python3 -m venv /tmp/test_saltext --prompt test-vmw-ext
    source /tmp/test_saltext/bin/activate
    python -m pip install --upgrade pip wheel
    python -m pip install --no-index --find-links dist/ saltext.vmware\[dev,tests,release\]
    pytest --cov=saltext.vmware tests/

This will run tests against the build artifact. If all tests pass this nightly
build may be released.

The release process be tested by using Twine with the TestPyPI_

.. _TestPyPI: https://test.pypi.org/project/saltext.vmware/

In order to cut a release, you must be a project maintainer on TestPyPI and
have a token configured for the project. Your ``~/.pypirc`` should contain your
key like the following:

.. code::

    [distutils]
      index-servers =
        test_saltext_vmware

    [test_saltext_vmware]
      repository = https://test.pypi.org/legacy/
      username = __token__
      password = pypi-AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA...

Then you would run:

.. code::

    twine upload --repository test_saltext_vmware dist/saltext.vmware-VERSION-py2.py3-none-any.whl

Merge the Version Update into the Main Repo
-------------------------------------------

Now that the build has been tested and verified, create a merge request with the new ``__version__`` to https://github.com/saltstack/salt-ext-modules-vmware/.

With the new version committed, go back and :ref:`build a new artifact<build>`.

Versions, Tagging, and Changelog
--------------------------------

In order to cut a release, you must be a maintainer of this project on PyPI.
You should have a ``[saltext_vmware]`` section in your pypirc file, similar to
the test setting.

In regards to version numbers, this project uses Calver_, with the
``YY.M.D.PATCH`` style. Breaking (and any other) changes should be
communicated through the changelog_.

.. _CalVer: https://calver.org/
.. _changelog: https://github.com/saltstack/salt-ext-modules-vmware/blob/main/CHANGELOG.md

For dev/nightly builds, tags will ONLY be used if the package gets uploaded to
the production PyPI. At that point an annotated tag should be created with the
current changelog for that particular version.

Release candidate builds will be tagged with the **expected** release date with
``rcN`` modifier. For instance, if we planned to release 2010, August 14, we would tag like so:

.. code::

   git tag 10.8.14rc1 -a

Typically there will only be one RC build - though if bugs
are found, especially severe bugs, new RC versions will be built, tagged, and
released.

To cut a final release, the repository will be tagged as above, the changelog
added to the tag, and then a new package will be built, installed, and tested.
This order is required because we use setuptools_scm to generate the version
number from the latest tag. Tagging does not produce any code changes (other
than the version number), so the tests should continue to pass. If they fail
for any reason other than your Internet going out, this should be considered a
critical issue! Flaky tests are undesirable, since they are often just
misleading. If a test scenario is that flaky, it should be performed manually,
or not at all.

..
    That flaky bit could be a in a different document, and linked to from here.

Once the full test suite has passed, sign the production package with gpg and
upload the package with twine:

.. code::

    # SIGNING_KEY should be replaced with the signing key, and FINAL-VERSION
    # with the actual version number
    gpg --detach-sign -u SIGNING_KEY dist/saltext.vmware-FINAL-VERSION-py2.py3.none-any.whl
    twine upload --repository = saltext_vmware dist/saltext.vmware-FINAL-VERSION-py2.py3.none-any.whl

Once the package has been uploaded to PyPI the tag should be pushed:

.. code::

    git push salt 10.8.14   # to use the previous example

A release should also be created on GitHub, uploading both the package as well
as the `.sig` file.

Congrats! You've just cut a new release!
