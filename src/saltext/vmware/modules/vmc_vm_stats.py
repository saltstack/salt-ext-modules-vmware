"""
Salt execution module for VMC vm stats
Provides methods to get cpu or memory related settings of a virtual machine
"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_vcenter_request

log = logging.getLogger(__name__)

__virtualname__ = "vmc_vm_stats"


def __virtual__():
    return __virtualname__


def get(hostname, username, password, vm_id, stats_type, verify_ssl=True, cert=None):
    """
    Retrieves the cpu or memory related settings for given VM.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vm_stats.get hostname=sample-vcenter.vmwarevmc.com ...

    hostname
        Hostname of the vCenter console

    username
        username required to login to vCenter console

    password
        password required to login to vCenter console

    vm_id
        Virtual machine identifier for which the stats should be retrieved.

    stats_type
        Type of the stats to be retrieved for given VM. Possible values: cpu, memory

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving the %s related settings for VM %s", stats_type, vm_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}api/vcenter/vm/{vm_id}/hardware/{stats_type}"
    api_url = api_url.format(base_url=api_url_base, vm_id=vm_id, stats_type=stats_type)

    headers = vmc_vcenter_request.get_headers(hostname, username, password)
    return vmc_vcenter_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        headers=headers,
        description="vmc_vm_stats.get",
        verify_ssl=verify_ssl,
        cert=cert,
    )
