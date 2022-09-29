"""
VMC Security group state module

Add new security group, update existing security group and delete existing security group from an SDDC.

Example usage :

.. code-block:: yaml

    Security_group_1:
      vmc_security_groups.present:
        - hostname: sample-nsx.vmwarevmc.com
        - refresh_key: 7jPSGSZpCa8e5Ouks4UY5cZyOtynAhF
        - authorization_host: console-stg.cloud.vmware.com
        - org_id: 10e1092f-51d0-473a-80f8-137652c39fd0
        - sddc_id: b43da080-2626-f64c-88e8-7f31d9d2c306
        - domain_id: mgw
        - verify_ssl: False
        - cert: /path/to/client/certificate

.. warning::

    It is recommended to pass the VMC authentication details using Pillars rather than specifying as plain text in SLS
    files.


"""
import logging

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_state

log = logging.getLogger(__name__)


def present(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    domain_id,
    verify_ssl=True,
    cert=None,
    expression=None,
    description=None,
    tags=vmc_constants.VMC_NONE,
    display_name=None,
):
    """
    Ensure a given security group exists for given SDDC

    name
        Indicates the security group id, any unique string identifying the security group.
        Also same as the display_name by default.

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC for which the security groups should be added

    domain_id
        The domain_id for which the security group should belong to. Possible values: mgw, cgw

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.
    expression
        Expression for security group members
            The expression list must follow below criteria:
            1. A non-empty expression list, must be of odd size. In a list, with
            indices starting from 0, all non-conjunction expressions must be at
            even indices, separated by a conjunction expression at odd
            indices.
            2. The total of ConditionExpression and NestedExpression in a list
            should not exceed 5.
            3. The total of IPAddressExpression, MACAddressExpression, external
            IDs in an ExternalIDExpression and paths in a PathExpression must not exceed
            500.
            4. Each expression must be a valid Expression. See the definition of
            the Expression type for more information.

        Its list of dicts
            Example values

            1. [{"member_type":"VirtualMachine","resource_type":"ExternalIDExpression",
            "external_ids":["52bf8bd0-95b1-2e58-5180-ccfa743da576"]}]

            2. [{"value":"Linux","member_type":"VirtualMachine","key":"OSName",
               "operator":"EQUALS","resource_type":"Condition"},
               {"resource_type":"ConjunctionOperator","conjunction_operator":"OR"},
               {"member_type":"VirtualMachine","resource_type":"ExternalIDExpression",
               "external_ids":["52bf8bd0-95b1-2e58-5180-ccfa743da576"]}]

            3. [{"ip_addresses" : ["203.0.113.1", "203.0.113.2"],
                "resource_type" : "IPAddressExpression"} ]

    description
        (Optional) Description of Security Groups

    tags
        (Optional) Opaque identifiers meaningful to the user.

        .. code-block::

            tags='[
                {
                    "tag": "<tag-key-1>"
                    "scope": "<tag-value-1>"
                },
                {
                    "tag": "<tag-key-2>"
                    "scope": "<tag-value-2>"
                }
            ]'

    display_name
        Identifier to use when displaying entity in logs or GUI. This is applicable for only update scenario.
        For create scenario, display_name would be same as security_group_id.

    Example values:

        .. code-block::

            {
                "expression": [
                  {
                    "member_type": "VirtualMachine",
                    "value": "webvm",
                    "key": "Tag",
                    "operator": "EQUALS",
                    "resource_type": "Condition"
                  }
                ],
                "description": "web group"
            }

    """
    security_group_id = name
    input_dict = {
        "expression": expression,
        "description": description,
        "tags": tags,
        "display_name": display_name,
    }

    input_dict = {k: v for k, v in input_dict.items() if v != vmc_constants.VMC_NONE}

    security_group = __salt__["vmc_security_groups.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_group_id=security_group_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in security_group:
        if "could not be found" in security_group["error"]:
            security_group = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=security_group["error"], result=False
            )

    if __opts__.get("test"):
        log.info("present is called with test option")
        return vmc_state._create_state_response(
            name=name,
            comment="Security group {} will be {}".format(
                security_group_id, "updated" if security_group else "created"
            ),
        )

    if security_group:
        updatable_keys = input_dict.keys()
        is_update_required = vmc_state._check_for_updates(
            security_group, input_dict, updatable_keys, ["tags"]
        )

        if is_update_required:
            updated_security_group = __salt__["vmc_security_groups.update"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                domain_id=domain_id,
                security_group_id=security_group_id,
                verify_ssl=verify_ssl,
                cert=cert,
                expression=expression,
                description=description,
                tags=tags,
                display_name=display_name,
            )

            if "error" in updated_security_group:
                return vmc_state._create_state_response(
                    name=name, comment=updated_security_group["error"], result=False
                )

            updated_security_group = __salt__["vmc_security_groups.get_by_id"](
                hostname=hostname,
                refresh_key=refresh_key,
                authorization_host=authorization_host,
                org_id=org_id,
                sddc_id=sddc_id,
                domain_id=domain_id,
                security_group_id=security_group_id,
                verify_ssl=verify_ssl,
                cert=cert,
            )

            if "error" in updated_security_group:
                return vmc_state._create_state_response(
                    name=name, comment=updated_security_group["error"], result=False
                )

            return vmc_state._create_state_response(
                name=name,
                comment="Updated security group {}".format(security_group_id),
                old_state=security_group,
                new_state=updated_security_group,
                result=True,
            )
        else:
            log.info("All fields are same as existing Security group %s", security_group_id)
            return vmc_state._create_state_response(
                name=name,
                comment="Security group exists already, no action to perform",
                result=True,
            )
    else:
        log.info("No security group found with ID %s", security_group_id)
        created_security_group = __salt__["vmc_security_groups.create"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            domain_id=domain_id,
            security_group_id=security_group_id,
            verify_ssl=verify_ssl,
            cert=cert,
            expression=expression,
            description=description,
            tags=tags,
        )

        if "error" in created_security_group:
            return vmc_state._create_state_response(
                name=name, comment=created_security_group["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Created security group {}".format(security_group_id),
            new_state=created_security_group,
            result=True,
        )


def absent(
    name,
    hostname,
    refresh_key,
    authorization_host,
    org_id,
    sddc_id,
    domain_id,
    verify_ssl=True,
    cert=None,
):
    """
    Ensure a given security group does not exist on given SDDC

    name
        Indicates the security group id, any unique string identifying the security group.

    hostname
        The host name of NSX-T manager

    refresh_key
        API Token of the user which is used to get the Access Token required for VMC operations

    authorization_host
        Hostname of the VMC cloud console

    org_id
        The Id of organization to which the SDDC belongs to

    sddc_id
        The Id of SDDC from which the security group should be deleted

    domain_id
        The domain_id for which the security group should belong to. Possible values: mgw, cgw

    verify_ssl
        (Optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (Optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    security_group_id = name
    log.info("Checking if security group with ID %s is present", security_group_id)
    security_group = __salt__["vmc_security_groups.get_by_id"](
        hostname=hostname,
        refresh_key=refresh_key,
        authorization_host=authorization_host,
        org_id=org_id,
        sddc_id=sddc_id,
        domain_id=domain_id,
        security_group_id=security_group_id,
        verify_ssl=verify_ssl,
        cert=cert,
    )

    if "error" in security_group:
        if "could not be found" in security_group["error"]:
            security_group = None
        else:
            return vmc_state._create_state_response(
                name=name, comment=security_group["error"], result=False
            )

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if security_group:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will delete security group with ID {}".format(
                    security_group_id
                ),
            )
        else:
            return vmc_state._create_state_response(
                name=name,
                comment="State absent will do nothing as no security group found with ID {}".format(
                    security_group_id
                ),
            )

    if security_group:
        log.info("Security group found with ID %s", security_group_id)
        deleted_security_group = __salt__["vmc_security_groups.delete"](
            hostname=hostname,
            refresh_key=refresh_key,
            authorization_host=authorization_host,
            org_id=org_id,
            sddc_id=sddc_id,
            domain_id=domain_id,
            security_group_id=security_group_id,
            verify_ssl=verify_ssl,
            cert=cert,
        )

        if "error" in deleted_security_group:
            return vmc_state._create_state_response(
                name=name, comment=deleted_security_group["error"], result=False
            )

        return vmc_state._create_state_response(
            name=name,
            comment="Deleted security group {}".format(security_group_id),
            old_state=security_group,
            result=True,
        )
    else:
        log.info("No security group found with ID %s", security_group_id)
        return vmc_state._create_state_response(
            name=name,
            comment="No security group found with ID {}".format(security_group_id),
            result=True,
        )
