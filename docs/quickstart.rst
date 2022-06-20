.. _quickstart:

Quickstart
==========

This guide is to get you started playing around with the Salt Extension Modules
for VMware as quick as possible.

.. note::

    This extension module is currently undergoing rapid changes. If you're
    using it for any production purposes, make sure that you're specifying
    which version of the extension module that you want, and you're testing the
    newest versions before you upgrade! If you find any errors, please create
    an issue on the `GitHub Repository`_.

.. note::

    In the future this module may support the `deltaproxy`_ approach to
    managing SDDCs.


Dev Environment
---------------

Since this extension module is currently under active development, it's a good
idea to have a dev system. This guide also assumes that you have installed
Salt, by following directions on `<https://repo.saltproject.io/>`_. If you
don't have an install of Salt, a quick way would be:

.. code::

    python3 -m venv .dev-saltenv --prompt dev-salt
    source .dev-saltenv/bin/activate
    python -m pip install salt

You'll probably want to grab a snack as it will take a few minutes to install
all of your dependencies. If this doesn't work (Mac and Windows may have some
missing dependencies, for example), using Salt's install guide should work
better.

.. note::

    The rest of this guide assumes you have Salt installed and you have your
    ``venv`` activated, or that you have Salt installed in your system-wide
    Python 3. If salt is installed system-wide, then user should be root and
    the Saltfile instructions may be ignored. Additionally, the paths should be
    relative to ``/`` instead of the users' homedir.


Config
------

This isn't required for installation, but it is necessary for communicating
with your vSphere. You'll need to set the config values in one of the following locations:

* minion config (default: ``/etc/salt/minion``)
* pillar file (default: ``/srv/pillar``)
* environment variables - this is more for one-off ``salt-call --local``
  statements, and not recommended for general use. But if you really want to,
  ``SALTEXT_VMWARE_HOST``, ``SALTEXT_VMWARE_PASSWORD``, and
  ``SALTEXT_VMWARE_USER`` are the names.

.. note::

    For more info on pillars, see the Salt `Pillar Walkthru
    <https://docs.saltproject.io/en/latest/topics/tutorials/pillar.html>`_. For more
    info on minion config, see `Configuring the Salt Minion
    <https://docs.saltproject.io/en/latest/ref/configuration/minion.html>`_.

This guide will use the pillar approach, along with Saltfile for convenience.

.. note::

    When using Saltfile, either the Saltfile must be passed as a command line
    argument, or the salt commands must be run in the directory containing the
    Saltfile.

First, let's create the directories that we need:


.. code::

    cd
    mkdir -p salt/etc/salt/pki/
    mkdir -p salt/var/cache/ salt/var/log/
    mkdir -p salt/srv/pillar/ salt/srv/salt
    cd salt

Now, the Salt config files:

.. code::

    $ cat <<EOF> Saltfile
    salt-call:
      local: True
      config_dir: etc/salt

    $ cat <<EOF> etc/salt/master
    user: $(whoami)
    root_dir: $HOME/salt/
    file_roots:
      base:
        - $HOME/salt/
    publish_port: 55505
    ret_port: 55506
    EOF

    $ cat <<EOF> etc/salt/minion
    id: master_minion
    user: $(whoami)
    root_dir: $HOME/salt/
    file_root: $HOME/salt/
    pillar_root: $HOME/salt/srv/pillar
    master: localhost
    master_port: 55506
    EOF

Setting the minion ID will allow for easier targeting in the pillar top file.

.. code:: yaml

    # srv/pillar/top.sls
    base:
      master_minion:
        - my_vsphere_conf


.. code:: yaml

    # srv/pillar/my_vsphere_conf.sls
    saltext.vmware:
      host: 203.0.113.42
      password: VMware1!
      user: adminstrator@vsphere.local

Verify that your config is correct by running

.. code::

    $ salt-call pillar.items
    local:
        ----------
        saltext.vmware:
            ----------
            host:
                203.0.113.42
            password:
                VMware1!
            user:
                administrator@vsphere.local

If you get no output, verify that your minion name in ``srv/pillar/top.sls``
matches the ID configured in ``etc/salt/minion``. Try again with ``salt-call
-ldebug pillar.items`` to see debug logging. Now that you've got your salt
environment configured, let's install the extension module!


Installation
------------

Unlike custom execution modules and state modules for Salt where files are
dropped directly into a directory (typically ``/srv/salt/_modules/`` and
``/srv/salt/_states/``), extension modules will be installed via pip. This
makes managing the versions much easier!

.. note::

    Until we are using the deltaproxy approach for VMware SDDC, the extension
    module should be installed on the Salt master (unless you have a specific
    minion that you want to communicate with vSphere). If you have a minion
    that should communicate with your SDDC, replace ``salt-call`` with
    ``salt yourminion ...``. One reason you might need to have a particular
    minion is if your salt master IP is on a blocklist or not on an allowlist
    for your SDDC, but your minion is allowed.

.. code::

    $ salt-call pip.install saltext.vmware
    local:
        ----------
        pid:
            9319
        retcode:
            0
        stderr:
        stdout:
            Collecting saltext.vmware
              Using cached saltext.vmware-21.10.4.1.dev38-py2.py3-none-any.whl (275 kB)
            Requirement already satisfied: salt>=3002 in /usr/lib/python3.9/site-packages (from saltext.vmware) (3003.3)
            Requirement already satisfied: pyvmomi==7.0.2 in /usr/lib/python3.9/site-packages (from saltext.vmware) (7.0.2)
            Requirement already satisfied: requests>=2.3.0 in /usr/lib/python3.9/site-packages (from pyvmomi==7.0.2->saltext.vmware) (2.26.0)
            Requirement already satisfied: six>=1.7.3 in /usr/lib/python3.9/site-packages (from pyvmomi==7.0.2->saltext.vmware) (1.16.0)
            Requirement already satisfied: chardet>=3.0.2 in /usr/lib/python3.9/site-packages (from requests>=2.3.0->pyvmomi==7.0.2->saltext.vmware) (4.0.0)
            Requirement already satisfied: idna>=2.5 in /usr/lib/python3.9/site-packages (from requests>=2.3.0->pyvmomi==7.0.2->saltext.vmware) (3.2)
            Requirement already satisfied: urllib3>=1.21.1 in /usr/lib/python3.9/site-packages (from requests>=2.3.0->pyvmomi==7.0.2->saltext.vmware) (1.26.6)
            Requirement already satisfied: distro>=1.0.1 in /usr/lib/python3.9/site-packages (from salt>=3002->saltext.vmware) (1.5.0)
            Requirement already satisfied: Jinja2 in /usr/lib/python3.9/site-packages (from salt>=3002->saltext.vmware) (3.0.1)
            Requirement already satisfied: MarkupSafe in /usr/lib/python3.9/site-packages (from salt>=3002->saltext.vmware) (2.0.1)
            Requirement already satisfied: pyzmq>=19.0.2 in /usr/lib/python3.9/site-packages (from salt>=3002->saltext.vmware) (22.2.1)
            Requirement already satisfied: contextvars in /usr/lib/python3.9/site-packages (from salt>=3002->saltext.vmware) (2.4)
            Requirement already satisfied: PyYAML in /usr/lib/python3.9/site-packages (from salt>=3002->saltext.vmware) (5.4.1)
            Requirement already satisfied: pycryptodomex>=3.9.8 in /usr/lib/python3.9/site-packages (from salt>=3002->saltext.vmware) (3.10.1)
            Requirement already satisfied: msgpack!=0.5.5,>=0.5 in /usr/lib/python3.9/site-packages (from salt>=3002->saltext.vmware) (1.0.2)
            Requirement already satisfied: immutables>=0.9 in /usr/lib/python3.9/site-packages (from contextvars->salt>=3002->saltext.vmware) (0.16)
            Installing collected packages: saltext.vmware
            Successfully installed saltext.vmware-21.10.4.1.dev38

Your output might be a bit different, but as long as ``Successfully installed
saltext.vmware`` shows up, you should be able to communicate with your vSphere.
Try it out!

.. code::

    $ salt-call vmware_datacenter.list

If this fails, but ``pillar.items`` worked, ensure that your config values
match that of your vSphere. If it's still failing, search the `issues on
GitHub <https://github.com/saltstack/salt-ext-modules-vmware/issues>`_ for your
error. If no existing issues fit, go ahead and create a new one!

Your First State
----------------

New states and modules are being created weekly. The most up-to-date list can
be found in the complete list of :ref:`all the states/modules`. Each state or
module will list the required arguments. For this example, find the vmc_sddc
module in that list to get more information about what pillar values are
required, but you could write this state:

.. code:: yaml

    # srv/salt/my_sddc.sls
    create_sddc:
      module.run:
        - name: vmc_sddc.create
        - hostname: {{ pillar['vmware']['vmc_host'] }}
        - refresh_key: {{ pillar['vmware']['refresh_key'] }}
        - authorization_host: console.cloud.vmware.com
        - org_id: {{ pillar['vmware']['org_id'] }}
        - sddc_name: {{ pillar['sddc_name'] }}
        - num_host: 2
        - provider: ZEROCLOUD
        - region: US_WEST_1
        - verify_ssl: True


You can either reference this file in a top file, and use ``salt-call state.apply``
to run a highstate and apply all of your state files:

.. code:: yaml

    # srvs/salt/top.sls
    base:
      master_minion:
        - my_sddc

Or just simply run it with ``salt-call state.apply my_sddc``. The end result of
this is that you should have a VMC SDDC created, with name provided in your
pillar, 2 hosts, in the ``US_WEST_1`` region.

Check out the rest of the :ref:`extension documentation <welcome>` for more information, and happy Salting!


.. _GitHub Repository: https://github.com/saltstack/salt-ext-modules-vmware
.. _deltaproxy: https://docs.saltproject.io/en/master/ref/proxy/all/salt.proxy.deltaproxy.html
