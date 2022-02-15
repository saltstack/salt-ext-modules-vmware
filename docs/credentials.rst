.. _credentials:

Credentials
===========

Providing credentials on the command line or as environment variables is dangerous and can easily allow leaking secrets. A much better approach is to use Salt's config mechanisms - adding credentials to either Salt master or minion config, or providing them as pillar data which can be encrypted on disk is both more secure as well as more consistent with Salt.

Passing Credentials in a Salty way
----------------------------------

The best way to pass Credentials is through salt pillars.
pillar walkthrough:  https://docs.saltproject.io/en/latest/topics/tutorials/pillar.html

Examples of how we are currently doing this in vCenter modules:

``/srv/pillar/top.sls``

.. code::

    base:
        '*':
            - vmware

``/srv/pillar/vmware.sls``

.. code::

    vmware_config:
        host: 10.225.1.101
        password: VMware!
        user: administrator

In code we can grab these values like this:

* Example in ``salt-ext-modules-vmware/src/salt/ext/vmware/utils/connect.py``

.. code::

    pillar.get("vmware_config", {}).get("host")

We also create a hierarchy for grabbing credential so they can be over written when needed.

* Example in ``salt-ext-modules-vmware/src/salt/ext/vmware/utils/connect.py``

.. code::

    host = (
        esxi_host
        or os.environ.get("VMWARE_CONFIG_HOST")
        or opts.get("vmware_config", {}).get("host")
        or pillar.get("vmware_config", {}).get("host")
    )

The priority is as follows:

* Environment vars
* Opts
* Pillar
