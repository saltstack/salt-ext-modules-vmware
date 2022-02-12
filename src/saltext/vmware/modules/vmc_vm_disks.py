"""
Salt execution module for VMC vm disks
Provides methods to Create, Read, Update and Delete virtual disks from the VM.
"""
import logging
import os

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates
from saltext.vmware.utils import vmc_vcenter_request

log = logging.getLogger(__name__)

__virtualname__ = "vmc_vm_disks"


def __virtual__():
    return __virtualname__


def get(hostname, username, password, vm_id, verify_ssl=True, cert=None):
    """
    Retrieves the available virtual disks for given VM.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vm_disks.get hostname=sample-vcenter.vmwarevmc.com ...

    hostname
        Hostname of the vCenter console

    username
        username required to login to vCenter console

    password
        password required to login to vCenter console

    vm_id
        Virtual machine identifier for which the available hard disks should be retrieved.

    verify_ssl
        (optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving the available virtual disks for VM %s", vm_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}api/vcenter/vm/{vm_id}/hardware/disk"
    api_url = api_url.format(base_url=api_url_base, vm_id=vm_id)

    headers = vmc_vcenter_request.get_headers(hostname, username, password)
    return vmc_vcenter_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        headers=headers,
        description="vmc_vm_disks.get",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_by_id(hostname, username, password, vm_id, disk_id, verify_ssl=True, cert=None):
    """
    Retrieves details of given virtual disk for given VM.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vm_disks.get_by_id hostname=sample-vcenter.vmwarevmc.com ...

    hostname
        Hostname of the vCenter console

    username
        username required to login to vCenter console

    password
        password required to login to vCenter console

    vm_id
        Virtual machine identifier for which the disk details should be retrieved.

    disk_id
        Virtual disk identifier for which the details should be retrieved from given VM

    verify_ssl
        (optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving details of virtual disk %s for VM %s", disk_id, vm_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}api/vcenter/vm/{vm_id}/hardware/disk/{disk_id}"
    api_url = api_url.format(base_url=api_url_base, vm_id=vm_id, disk_id=disk_id)

    headers = vmc_vcenter_request.get_headers(hostname, username, password)
    return vmc_vcenter_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        headers=headers,
        description="vmc_vm_disks.get_by_id",
        verify_ssl=verify_ssl,
        cert=cert,
    )
