.. _release:

Release
=======

The purpose of this document is to specify and outline the release process for
the Salt Extension Modules for VMware. Initially for the beta releases, many of
these steps will be manual. Over time the process will become more automated.

Overview
--------

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


Build
-----

To build a release artifact, ``python setup.py bdist_wheel`` will generate a
``.whl`` file. Non-dev tests will be executed against this wheel.

Test the Build
--------------

A new virtualenv will be created, and will install this wheel. Tests will then
be executed:

.. code::

    python -m venv env --prompt vmw-ext
    source env/bin/activate
    python -m pip install dist/saltext.vmware-VERSION-py2.py3-none-any.whl  # use actual version
    python -m nox -e test-build  # TODO - list multiple pythons?

This will run tests against the build artifact. If all tests pass the build
may be released.

Versions, Tagging, and Changelog
--------------------------------

This project uses CalVer_ for versions. In order to
communicate breaking changes, this project keeps a
changelog_.

.. _CalVer: https://calver.org/
.. _changelog: https://keepachangelog.com/en/1.0.0/

For dev/nightly builds, no tags will be used, and packages will not be uploaded
to PyPI.

Release candidate builds will be tagged with the **expected** release date with
``rcN`` modifier. Typically there will only be one RC build - though if bugs
are found, especially severe bugs, new RC versions will be built, tagged, and
released.

Final releases will be tagged, signed, and annotated with the changelog for
that particular version. While the source code should not change between RC
versions and final releases, the final release *will* be a new artifact, and
will go through the same build/test/upload process as non-final versions. Once
the release artifact it successfully tested and uploaded to PyPI, the annotated
tag will be pushed to the repo.
