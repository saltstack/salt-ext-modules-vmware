"""
Salt execution Module to interact with NSX-T REST APIs

"""
import logging

from saltext.vmware.utils import nsxt_request

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_rest"


def call_api(
    url,
    username,
    password,
    method="get",
    cert_common_name=None,
    verify_ssl=True,
    cert=None,
    data=None,
    params=None,
):
    """
    Used to execute NSX-T REST API calls. In case of error, function returns a dictionary with respective error.
    Sample error returned : {'error': 'Error message'}

    CLI Example:

        .. code-block:: bash

            salt vm_minion nsxt_rest.call_api method=get url=https://nsxt-instance/ ...

        url
            Url or api endpoint to access

        username
            Username to connect to NSX-T manager

        password
            Password to connect to NSX-T manager


        method
            Http request method. Default is 'get'. Accepted values: get, post, put, patch, delete..

        verify_ssl
            Option to enable/disable SSL verification. Enabled by default.
            If set to False, the certificate validation is skipped.

        cert
            Path to the SSL client certificate file to connect to NSX-T manager.
            The certificate can be retrieved from browser.

        cert_common_name
            (Optional) By default, the hostname parameter and the common name in certificate is compared for host name
            verification. If the client certificate common name and hostname do not match (in case of self-signed
            certificates), specify the certificate common name as part of this parameter. This value is then used to
            compare against

        data
            (Optional) Data to be sent to the specified url. Request body

        params
            (Optional) Query parameters for the request. Usually a dictionary with key-value pairs

    """
    log.info("{} call for url: {}".format(method.upper(), url))
    log.info("data: {}\n params: {}".format(data, params))
    response = nsxt_request.call_api(
        url=url,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        method=method,
        data=data,
        params=params,
    )
    if response:
        return response
    else:
        return "{} call is success".format(method.upper())
