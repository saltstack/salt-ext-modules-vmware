.. _managing vmc sddc:

Managing VMC Sddc with Salt
================================

Things to know about running VMC modules & states
-------------------------------------------------
To create CSP API token which is referred to as `refresh_key` across all the VMC modules and states:
    Please refer `Generate API Token <https://docs.vmware.com/en/vRealize-Operations-Manager/8.4/com.vmware.vcom.core.doc/GUID-3B8C8821-FB07-412F-A2E4-C5CA34D8A473.html>`_.

To get the org_id:
    1. Login to VMware Cloud Services, select your user profile in the top-right corner, and click View Organization.
    2. In the Organization page, pick the Long Organization ID.

To create an SDDC in the Organization:
    Execute the `create` function from vmc_sddc module. This function will return the ID of the created SDDC.

Alternatively, to get the ``sddc_id`` from the UI:
    Navigate to the support tab of an SDDC on UI.

To find the nsx-reverse-proxy-host which is referred to as `hostname` in some of the VMC modules and states:
    Execute `vmc_sddc.get_by_id` and get the `nsx_reverse_proxy_url` from the output.

    For example,

    .. code::

        {
            "nsx_reverse_proxy_url": "https://nsx-10-182-160-142.rp.stg.vmwarevmc.com/vmc/reverse-proxy/api/"
        }

    here `nsx-10-182-160-142.rp.stg.vmwarevmc.com` represents the nsx-reverse-proxy-host


To find the hostname, username and password for vCenter associated with the SDDC:
    Execute `vmc_sddc.get_vcenter_detail` function. Sample output for `vmc_sddc.get_vcenter_detail`:

    .. code::

        "vcenter_detail": {
            "vcenter_url": "https://vcenter.sddc-10-182-160-142.vmwarevmc.com/",
            "username": "user@example.local",
            "password": "Password123"
        }

To find the VirtualMachine Identifier which is referred to as `vm_id` in some of the VMC modules:
    Login to vCenter Console using the above credentials, and click on any of the virtual machines available in VC.
    We can see the url like,

    .. code::

        "https://vcenter.sddc-10-182-160-142.vmwarevmc.com/ui/app/vm;nav=h/urn:vmomi:VirtualMachine:vm-1003:f0876254-4ce2-4dc6-8bc3-792432406c31/summary"

    Here `vm-1003` represents the `vm_id`.


Using script to create vmc_config.json
--------------------------------------
Below command will return the required information to create vmc_config.json which is required to run Integration tests for VMC

.. code-block:: bash

    python tools/test_value_scraper_vmc.py --help


Modules and States for controlling VMC SDDC:

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
