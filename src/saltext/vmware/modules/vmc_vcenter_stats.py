"""
Salt execution module for VMC vCenter stats
Provides methods to get monitored items list and to query monitored item data for given vCenter.
To get the data from this module, admin credentials for vCenter are required.
"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_vcenter_request

log = logging.getLogger(__name__)

__virtualname__ = "vmc_vcenter_stats"


def __virtual__():
    return __virtualname__


def list_monitored_items(hostname, username, password, verify_ssl=True, cert=None):
    """
    Retrieves monitored items list for given vCenter.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vcenter_stats.list_monitored_items hostname=sample-vcenter.vmwarevmc.com ...

    hostname
        Hostname of the vCenter console

    username
        admin username required to login to vCenter console

    password
       admin password required to login to vCenter console

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving the monitored items list for vCenter")
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}api/appliance/monitoring"
    api_url = api_url.format(base_url=api_url_base)

    headers = vmc_vcenter_request.get_headers(hostname, username, password)
    return vmc_vcenter_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        headers=headers,
        description="vmc_vcenter_stats.list_monitored_items",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def query_monitored_items(
    hostname,
    username,
    password,
    start_time,
    end_time,
    interval,
    aggregate_function,
    monitored_items,
    verify_ssl=True,
    cert=None,
):
    """
    Retrieves aggregate monitoring data for the given ``monitored_items`` across the time range.
    Data will be grouped using the ``aggregate_function`` for each ``interval`` in the time range.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vcenter_stats.query_monitored_items hostname=sample-vcenter.vmwarevmc.com ...

    hostname
        Hostname of the vCenter console

    username
        admin username required to login to vCenter console

    password
       admin password required to login to vCenter console

    start_time
        Start time in UTC (inclusive). Ex: 2021-05-06T22:13:05.651Z

    end_time
        End time in UTC (inclusive). Ex: 2021-05-10T22:13:05.651Z

    interval
         interval between the values in hours and mins, for which aggregation will apply.
         Possible values: MINUTES30, HOURS2, MINUTES5, DAY1, HOURS6

    aggregate_function
        aggregation function. Possible values: COUNT, MAX, AVG, MIN

    monitored_items
        List of monitored item IDs. Ex: [cpu.util, mem.util]

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """
    msg = "Retrieving the vCenter monitoring data for {}".format(monitored_items)
    log.info(msg)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}api/appliance/monitoring/query"
    api_url = api_url.format(base_url=api_url_base)

    headers = vmc_vcenter_request.get_headers(hostname, username, password)
    params = {
        "start_time": start_time,
        "end_time": end_time,
        "function": aggregate_function,
        "interval": interval,
        "names": monitored_items,
    }

    return vmc_vcenter_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        headers=headers,
        description="vmc_vcenter_stats.query_monitored_items",
        verify_ssl=verify_ssl,
        cert=cert,
        params=params,
    )
