2021-10-28 ESXi.get vs. Grains
==============================

Status
------

We expect that at some point, there may be a native minion on ESXi hosts.

For now, we are providing grain-like data via :func:`saltext.vmware.modules.esxi.get`
The structure of the data returned as grains and ``esxi.get()`` does not match.

Updating states and modules using ``esxi.get()`` will require more than a simple
rename to ``grains.get()``

There is no technical reason they shouldn't be in sync, but it's not currently a
priority for the core team as we are working to extend basic functionality.

Please let us know if this feature is important to you, either by commenting in
`#138 <https://github.com/saltstack/salt-ext-modules-vmware/issues/138>`_ or by
submitting a PR!