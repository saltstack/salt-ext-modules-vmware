2022-09-26 Config Layout
========================

Status
------

Accepted and Implemented

Context
-------

We need to have a consistent layout for our config that can support any number
of profiles, and other nested config values in order to support ESXi, NSX, VMC,
and vSphere, along with any future VMware products that will need support.

The top-level config/opts key that we will use is ``saltext.vmware``. We will
be using this key as it matches the Python package name, and any future setting
should be nested under this top-level key.

Consequences
------------

We will have to re-factor to use this new key, but generally speaking the
experience should be much more consistent for users, as well as be more stable
in the long-term.
