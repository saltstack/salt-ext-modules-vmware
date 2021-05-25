"""
NSX-T Datacenter Configuration Management state module
======================================================

:maintainer: <VMware>
:maturity: new

Enable/Disable the NSX-T manager's publish_fqdns status.

Example usage:

.. code-block:: yaml

    configure_nsx_manager:
      nsx_manager.publish_fqdns_enabled:
        - name: Enable publish fqdns
          hostname: <hostname>
          username: <username>
          password: <password>
          cert: <certificate pem file path>
          verify_ssl: <False/True>

.. warning::

    It is recommended to pass the NSX authentication details using Pillars rather than specifying as plain text in SLS
    files.

"""
import logging

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_manager"


def __virtual__():
    """
    Only load if the nsxt_manager module is available in __salt__
    """
    return (
        __virtual_name__ if "nsxt_manager.get_manager_config" in __salt__ else False,
        "'nsxt_manager' binary not found on system",
    )


def _set_publish_fqdns_in_nsxt(
    publish_fqdns, revision, hostname, username, password, verify_ssl, cert, cert_common_name
):
    out = __salt__["nsxt_manager.set_manager_config"](
        hostname=hostname,
        username=username,
        password=password,
        revision=revision,
        publish_fqdns=publish_fqdns,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )
    return out


def _get_publish_fqdns_revision_from_nsxt(
    hostname, username, password, verify_ssl, cert, cert_common_name
):
    out = __salt__["nsxt_manager.get_manager_config"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )
    return out


def _get_publish_fqdns_revision_from_response(current_config_response):
    current_publish_fqdns = current_config_response.get("publish_fqdns")
    current_revision = current_config_response.get("_revision")

    return current_publish_fqdns, current_revision


def _create_state_response(name, old_state, new_state, result, comment):
    state_response = dict()
    state_response["name"] = name
    state_response["result"] = result
    state_response["comment"] = comment
    state_response["changes"] = dict()
    if new_state:
        state_response["changes"]["old"] = old_state
        state_response["changes"]["new"] = new_state

    return state_response


def publish_fqdns_enabled(
    name, hostname, username, password, verify_ssl=True, cert=None, cert_common_name=None
):
    """
    Check the value for publish_fqdns, if it is true then do nothing else set it to true

    .. code-block:: yaml

        configure_nsxt_manager:
          nsx_manager.publish_fqdns_enabled:
            - name: Enable publish fqdns
            - hostname: <hostname>
            - username: <username>
            - password: <password>
            - cert: <certificate path>
            - verify_ssl: <False/True>

    name
        The Operation to perform

    hostname
        NSX-T manager's hostname

    username
        NSX-T manager's username

    password
        NSX-T manager's password

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """

    log.info("Getting the manager's config")

    cert_common_name = cert_common_name
    cert = cert

    get_current_config = _get_publish_fqdns_revision_from_nsxt(
        hostname,
        username,
        password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )
    if "error" in get_current_config:
        return _create_state_response(name, None, None, False, get_current_config["error"])

    current_publish_fqdns, current_revision = _get_publish_fqdns_revision_from_response(
        get_current_config
    )

    if __opts__.get("test"):
        log.info("publish_fqdns_enabled is called with test option")
        return _create_state_response(
            name,
            None,
            None,
            None,
            "State publish_fqdns_enabled will execute with params {}, {}, {}, {}, {}".format(
                name, hostname, username, password, verify_ssl
            ),
        )

    if current_publish_fqdns:
        return _create_state_response(
            name, None, None, True, "publish_fqdns is already set to True"
        )

    publish_fqdns = True

    log.info("Updating the NSX-T manager's config")
    updated_config_response = _set_publish_fqdns_in_nsxt(
        publish_fqdns,
        current_revision,
        hostname,
        username,
        password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )

    if "error" in updated_config_response:
        return _create_state_response(name, None, None, False, updated_config_response["error"])

    return _create_state_response(
        name,
        get_current_config,
        updated_config_response,
        True,
        "publish_fqdns has been set to True",
    )


def publish_fqdns_disabled(
    name, hostname, username, password, verify_ssl=True, cert=None, cert_common_name=None
):
    """
    Check the value for publish_fqdns, if it is false then do nothing else set it to false

    .. code-block:: yaml

        configure_nsxt_manager:
          nsx_manager.publish_fqdns_disabled:
            - name: Disable publish fqdns
            - hostname: <hostname>
            - username: <username>
            - password: <password>
            - cert: <certificate>
            - verify_ssl: <False/True>

    name
        The Operation to perform

    hostname
        NSX-T manager's hostname

    username
        NSX-T manager's username

    password
        NSX-T manager's password

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.
    """

    cert_common_name = cert_common_name
    cert = cert

    log.info("Getting the manager's config")
    get_current_config = _get_publish_fqdns_revision_from_nsxt(
        hostname,
        username,
        password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )
    if "error" in get_current_config:
        return _create_state_response(name, None, None, False, get_current_config["error"])

    current_publish_fqdns, current_revision = _get_publish_fqdns_revision_from_response(
        get_current_config
    )

    if __opts__.get("test"):
        log.info("publish_fqdns_disabled is called with test option")
        return _create_state_response(
            name,
            None,
            None,
            None,
            "State publish_fqdns_disabled will execute with params {}, {}, {}, {}, {}".format(
                name, hostname, username, password, verify_ssl
            ),
        )

    if not current_publish_fqdns:
        return _create_state_response(
            name, None, None, True, "publish_fqdns is already set to False"
        )

    publish_fqdns = False

    log.info("Updating the manager's config")
    updated_config_response = _set_publish_fqdns_in_nsxt(
        publish_fqdns,
        current_revision,
        hostname,
        username,
        password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
    )

    if "error" in updated_config_response:
        return _create_state_response(name, None, None, False, updated_config_response["error"])

    return _create_state_response(
        name,
        get_current_config,
        updated_config_response,
        True,
        "publish_fqdns has been set to False",
    )
