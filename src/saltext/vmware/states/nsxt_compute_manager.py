"""
State module for NSX-T compute manager registration and de-registration
"""
import logging

log = logging.getLogger(__name__)

try:
    from saltext.vmware.modules import nsxt_compute_manager

    HAS_NSXT_COMPUTE_MANAGER = True
except ImportError:
    HAS_NSXT_COMPUTE_MANAGER = False


def __virtual__():
    if not HAS_NSXT_COMPUTE_MANAGER:
        return False, "'nsxt_compute_manager' binary not found on system"
    return "nsxt_compute_manager"


def _needs_update(
    existing_compute_manager, thumbprint, server_origin_type, **compute_manager_params
):
    if thumbprint and thumbprint != existing_compute_manager["credential"]["thumbprint"]:
        return True
    if server_origin_type and server_origin_type != existing_compute_manager["origin_type"]:
        return True

    optional_params = ("display_name", "description", "set_as_oidc_provider")
    for param in optional_params:
        param_val = compute_manager_params.get(param)
        if param_val and existing_compute_manager[param] != param_val:
            return True
    return False


def present(
    name,
    hostname,
    username,
    password,
    compute_manager_server,
    credential,
    server_origin_type="vCenter",
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
    display_name=None,
    description=None,
    set_as_oidc_provider=None,
):
    """

    Registers compute manager in NSX-T Manager or updates the registration

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_compute_manager.present hostname=nsxt-manager.local username=admin ...

    .. code-block:: yaml

        register_compute_manager:
          nsxt_compute_manager.present:
            - name: Registration
              hostname: {{ pillar['nsxt_manager_hostname'] }}
              username: {{ pillar['nsxt_manager_username'] }}
              password: {{ pillar['nsxt_manager_password'] }}
              cert: {{ pillar['nsxt_manager_certificate'] }}
              verify_ssl: <False/True>
              compute_manager_server: <compute manager IP address or FQDN>
              server_origin_type: <compute manager origin type>
              credential:
                credential_type:  UsernamePasswordLoginCredential
                username: {{ pillar['compute manager username'] }}
                password: {{ pillar['compute manager password'] }}
                thumbprint: {{ pillar['compute manager thumbprint'] }}
              display_name: <compute manager name>
              description: <compute manager description>
              set_as_oidc_provider: <False/True>

    name
        name of the operation to perform

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    compute_manager_server
        Compute manager server IP address or FQDN

    credential
        An object which contains credential details to validate compute manager
        Sample usage in sls file:

        .. code::

            credential:
               credential_type: "UsernamePasswordLoginCredential"
               username: "user"
               password: "pass"
               thumbprint: "36:XX:XX:XX:XX:XX:XX66"

        credential_type
            Type of credential provided. For now only UsernamePasswordLoginCredential is supported.

        username
            Username of the compute manager

        password
            Password of the compute manager

        thumbprint
            Thumbprint of the compute manager

    server_origin_type
        (Optional) Server origin type of the compute manager. Default is vCenter

    display_name
        (Optional) Display name of the compute manager

    description
        (Optional) description for the compute manager

    set_as_oidc_provider
        (Optional) Specifies whether compute manager has been set as OIDC provider. Default is false. If the
         compute manager is VC and need to set set as OIDC provider for NSX then this flag should be set as true.

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    For more information, see `VMware API docs for NSX-T <https://code.vmware.com/apis/1163/nsx-t>`_

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}
    compute_managers_result = __salt__["nsxt_compute_manager.get"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        server=compute_manager_server,
    )
    if "error" in compute_managers_result:
        ret["result"] = False
        ret["comment"] = "Failed to get compute managers from NSX-T Manager : {}".format(
            compute_managers_result["error"]
        )
        return ret

    if compute_managers_result["result_count"] > 1:
        ret["result"] = False
        ret["comment"] = "Found multiple results for the provided compute manager in NSX-T"
        return ret
    else:
        existing_compute_manager = (
            compute_managers_result["results"][0]
            if compute_managers_result["result_count"] == 1
            else None
        )

    if __opts__["test"]:
        if existing_compute_manager is None:
            ret["result"] = None
            ret["comment"] = "Compute manager would be registered to NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "Compute manager registration would be updated"
        return ret

    if isinstance(credential, dict):
        thumbprint = credential.get("thumbprint", None)
    else:
        ret["result"] = False
        ret[
            "comment"
        ] = "Parameter credential must be of type dictionary. Please refer documentation"
        return ret

    if existing_compute_manager is None:
        log.info("Going to register new compute manager, as no existing compute manager found")
        result = __salt__["nsxt_compute_manager.register"](
            hostname=hostname,
            username=username,
            password=password,
            verify_ssl=verify_ssl,
            cert=cert,
            cert_common_name=cert_common_name,
            compute_manager_server=compute_manager_server,
            credential=credential,
            server_origin_type=server_origin_type,
            display_name=display_name,
            description=description,
            set_as_oidc_provider=set_as_oidc_provider,
        )
        if "error" in result:
            ret["result"] = False
            ret["comment"] = "Failed to register compute manager with NSX-T Manager : {}".format(
                result["error"]
            )
            return ret
        else:
            ret[
                "comment"
            ] = "Compute manager {compute_manager_server} successfully registered with NSX-T".format(
                compute_manager_server=compute_manager_server
            )
            ret["changes"]["new"] = result
            return ret
    else:
        log.info("Compute manager already exists. Going to check for updates")
        is_update_required = _needs_update(
            existing_compute_manager=existing_compute_manager,
            thumbprint=thumbprint,
            server_origin_type=server_origin_type,
            display_name=display_name,
            description=description,
            set_as_oidc_provider=set_as_oidc_provider,
        )
        if is_update_required:
            result = __salt__["nsxt_compute_manager.update"](
                hostname=hostname,
                username=username,
                password=password,
                verify_ssl=verify_ssl,
                cert=cert,
                cert_common_name=cert_common_name,
                compute_manager_server=compute_manager_server,
                credential=credential,
                server_origin_type=server_origin_type,
                display_name=display_name,
                description=description,
                set_as_oidc_provider=set_as_oidc_provider,
                compute_manager_id=existing_compute_manager["id"],
                compute_manager_revision=existing_compute_manager["_revision"],
            )
            if "error" in result:
                ret["result"] = False
                ret[
                    "comment"
                ] = "Failed to update existing registration of compute manager with NSX-T Manager : {}".format(
                    result["error"]
                )
                return ret
            else:
                ret[
                    "comment"
                ] = "Compute manager {compute_manager_server} registration successfully updated with NSX-T".format(
                    compute_manager_server=compute_manager_server
                )
                ret["changes"]["old"] = existing_compute_manager
                ret["changes"]["new"] = result
                return ret
        else:
            ret["comment"] = (
                "Compute manager registration for {compute_manager_server} already exists. "
                "Nothing to update. Modifiable fields:[display_name, description, set_as_oidc_provider, "
                "thumbprint, origin_type]".format(compute_manager_server=compute_manager_server)
            )
            return ret


def absent(
    name,
    hostname,
    username,
    password,
    compute_manager_server=None,
    verify_ssl=True,
    cert=None,
    cert_common_name=None,
):
    """

    De-Registers compute manager in NSX-T Manager if present. Requires either compute_manager_server or
    compute_manager_id to be provided

    CLI Example:

    .. code-block:: bash

        salt vm_minion nsxt_compute_manager.absent hostname=nsxt-manager.local username=admin ...

    .. code-block:: yaml

        register_compute_manager:
          nsxt_compute_manager.absent:
            - name: Registration
              hostname: {{ pillar['nsxt_manager_hostname'] }}
              username: {{ pillar['nsxt_manager_username'] }}
              password: {{ pillar['nsxt_manager_password'] }}
              cert: {{ pillar['nsxt_manager_certificate'] }}
              verify_ssl: <False/True>
              compute_manager_server: <compute manager IP address or FQDN>

    name
        Name of the operation to perform

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

    compute_manager_server
        (Optional) Compute manager server IP address or FQDN

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL certificate file to connect to NSX-T manager.
        The certificate can be retrieved from browser.

    cert_common_name
        (Optional) By default, the hostname parameter and the common name in certificate is compared for host name verification.
        If the client certificate common name and hostname do not match (in case of self-signed certificates),
        specify the certificate common name as part of this parameter. This value is then used to compare against
        certificate common name.

    """
    ret = {"name": name, "result": True, "comment": "", "changes": {}}

    compute_managers_result = __salt__["nsxt_compute_manager.get"](
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        cert=cert,
        cert_common_name=cert_common_name,
        server=compute_manager_server,
    )
    compute_manager_to_delete = None
    if "error" in compute_managers_result:
        ret["result"] = False
        ret["comment"] = "Failed to get compute managers from NSX-T Manager : {}".format(
            compute_managers_result["error"]
        )
        return ret

    if compute_managers_result["result_count"] == 1:
        compute_manager_to_delete = compute_managers_result["results"][0]
    elif compute_managers_result["result_count"] > 1:
        ret["result"] = False
        ret["comment"] = "Found multiple results for the provided compute manager in NSX-T"
        return ret

    if __opts__["test"]:
        if compute_manager_to_delete is not None:
            ret["result"] = None
            ret["comment"] = "Compute manager would be removed/de-registered from NSX-T Manager"
        else:
            ret["result"] = None
            ret["comment"] = "Compute manager registration does not exists"
        return ret

    if compute_manager_to_delete is None:
        ret["comment"] = "Compute manager server not present in NSX-T manager"
        return ret
    else:
        result = __salt__["nsxt_compute_manager.remove"](
            hostname=hostname,
            username=username,
            password=password,
            compute_manager_id=compute_manager_to_delete["id"],
            verify_ssl=verify_ssl,
            cert=cert,
        )
        if "error" in result:
            ret["result"] = False
            ret[
                "comment"
            ] = "Failed to remove registration of compute manager with NSX-T Manager : {}".format(
                result["error"]
            )
            return ret
        else:
            ret["comment"] = "Compute manager registration removed successfully from NSX-T manager"
            ret["changes"]["old"] = compute_manager_to_delete
            ret["changes"]["new"] = {}
            return ret
