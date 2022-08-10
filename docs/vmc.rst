.. _managing vmc sddc:

Managing VMC SDDC with Salt
================================

Things to know about running VMC modules & states
-------------------------------------------------


VMC- Vmware Cloud on AWS which means an instance of the vCloud foundation being executed on AWS bear metal hardware, `You can learn more about VMware Cloud on AWS <https://docs.vmware.com/en/VMware-Cloud-on-AWS/index.html>`_.

SDDC- Software Defined Data Center

To create CSP API token which is referred to as ``refresh_key`` across all the VMC modules and states:
    Please refer `Generate API Token <https://docs.vmware.com/en/vRealize-Operations-Manager/8.4/com.vmware.vcom.core.doc/GUID-3B8C8821-FB07-412F-A2E4-C5CA34D8A473.html>`_.

To get the ``org_id``:
    1. Login to VMware Cloud Services, select your user profile in the top-right corner, and click View Organization.
    2. In the Organization page, pick the Long Organization ID.

To create an SDDC in the Organization:
    Execute the ``create`` function from vmc_sddc module. This function will return the ID of the created SDDC.

    For example,

    .. code-block:: bash

        salt '*' vmc_sddc.create hostname=stg.example.com refresh_key=7TUPdyffgs authorization_host=console.example.com org_id=10e1092e-51d0-473a-80f8-137652fd0b39 provider=AWS num_hosts=1 sddc_name='test-sddc' region='us-west-2' verify_ssl=False  --output=json | python -m json.tool | grep '"id"'

    returns,

    .. code::

        "id": "332e384f-43b1-4c7d-b125-450d5c25a332"

Alternatively, to get the ``sddc_id`` from the UI:
    Navigate to the support tab of an SDDC on UI.

To find the nsx-reverse-proxy-host which is referred to as ``hostname`` in some of the VMC modules and states:
    Execute ``vmc_sddc.get_by_id`` and get the ``nsx_reverse_proxy_url`` from the output.

    For example,

    .. code-block:: bash

        salt * vmc_sddc.get_by_id hostname=stg.example.com refresh_key=7TUPdyffgs authorization_host=console.example.com org_id=10e1092e-51d0-473a-80f8-137652fd0b39 sddc_id=2f225622-17ba-4bae-b0ec-b995123a5330 verify_ssl=False  --output=json | python -m json.tool | grep '"nsx_reverse_proxy_url"'

    returns,

    .. code::

        "nsx_reverse_proxy_url": "https://nsx-203-0-113-42.rp.stg.example.com/vmc/reverse-proxy/api"


    here ``nsx-203-0-113-42.rp.stg.example.com`` represents the nsx-reverse-proxy-host


To find the hostname, username and password for vCenter associated with the SDDC:
    Execute ``vmc_sddc.get_vcenter_detail`` function. Sample output for ``vmc_sddc.get_vcenter_detail``:

    .. code::

        "vcenter_detail": {
            "vcenter_url": "https://vcenter.sddc-203-0-113-42.example.com/",
            "username": "user@example.local",
            "password": "Password123"
        }

To find the VirtualMachine Identifier which is referred to as ``vm_id`` in some of the VMC modules:
    Login to vCenter Console using the above credentials, and click on any of the virtual machines available in VC.
    We can see the url like,

    .. code::

        "https://vcenter.sddc-203-0-113-42.example.com/ui/app/vm;nav=h/urn:vmomi:VirtualMachine:vm-1003:f0876254-4ce2-4dc6-8bc3-792432406c31/summary"

    Here ``vm-1003`` represents the ``vm_id``.


Alternatively, to get the ``vm_id`` , execute ``vmc_sddc.get_vms`` function which returns a list of virtual machines
associated with the SDDC.
Sample output for ``vmc_sddc.get_vms``:

    .. code::

        [
            {
                "memory_size_MiB": 4096,
                "vm": "vm-1001",
                "name": "New Virtual Machine",
                "power_state": "POWERED_OFF",
                "cpu_count": 2
            },
            {
                "memory_size_MiB": 8192,
                "vm": "vm-20",
                "name": "NSX-Edge-1",
                "power_state": "POWERED_ON",
                "cpu_count": 4
            }
        ]

    Here ``vm-1001`` and ``vm-20`` represents the ``vm_id`` of corresponding virtual machines.



Using script to create vmc_config.json
--------------------------------------
Below command will return the required information to create vmc_config.json which is required to run Integration tests for VMC

.. code-block:: bash

    python tools/test_value_scraper_vmc.py --help



Modules and States for controlling VMC SDDC:
--------------------------------------------

.. toctree::
   :glob:
   :maxdepth: 2
   :caption: VMC Execution Modules

   ref/modules/saltext.vmware.modules.vmc*



.. toctree::
   :glob:
   :maxdepth: 2
   :caption: VMC State Modules

   ref/states/saltext.vmware.states.vmc*
