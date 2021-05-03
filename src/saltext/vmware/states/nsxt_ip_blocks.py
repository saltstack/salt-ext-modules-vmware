# -*- coding: utf-8 -*-
"""
Salt State file to create/update/delete an IP Address Block

Example:

.. code-block:: yaml

    create_ip_block:
      nsxt_ip_blocks.present:
        - name: Create IP Block
          hostname: <hostname>
          username: <username>
          password: <password>
          cert: <certificate path>
          verify_ssl: <False/True>
          display_name: <ip block name>
          description: <ip block description>
          tags:
            - tag: <tag-key-1>
              scope: <tag-value-1>
            - tag: <tag-key-2>
              scope: <tag-value-2>
          cidr: <cidr>
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_ip_blocks"


def __virtual__():
    """
        Only load if the nsxt_ip_blocks module is available in __salt__
    """
    return (
        __virtual_name__ if "nsxt_ip_blocks.get" in __salt__ else False,
        "'nsxt_ip_blocks' binary not found on system",
    )


def present(
        name,
        display_name,
        cidr,
        hostname,
        username,
        password,
        **kwargs
):
    """
    Creates/Updates(if present with the same name) an IP Address Block

    .. code-block:: yaml

    create_ip_block:
      nsxt_ip_blocks.present:
        - name: Create IP Block
          hostname: <hostname>
          username: <username>
          password: <password>
          certificate: <certificate>
          verify_ssl: <False/True>
          display_name: <ip block name>
          description: <ip block description>
          tags:
            - tag: <tag-key-1>
              scope: <tag-value-1>
            - tag: <tag-key-2>
              scope: <tag-value-2>
          cidr: <cidr>

    name
        The Operation to perform

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

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

    display_name
        The name using which IP Address Block will be created. In case of update the provided display_name should be
        unique else the method will raise an error

    description
        (Optional) description for the IP Address Block

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:
        tags:
            - tag: <tag-key-1>
              scope: <tag-value-1>
            - tag: <tag-key-2>
              scope: <tag-value-2>

    cidr
        Represents network address and the prefix length which will be associated with a layer-2 broadcast domain
    """

    log.info("Checking if IP Block with name %s is present", display_name)
    get_ip_blocks_response = __salt__["nsxt_ip_blocks.get_by_display_name"](hostname, username, password, display_name,
                                                                            **kwargs)

    if get_ip_blocks_response and "error" in get_ip_blocks_response:
        return _create_state_response(name, None, None, False, get_ip_blocks_response["error"])

    ip_blocks = get_ip_blocks_response["results"]

    if ip_blocks.__len__() > 1:
        log.info("Multiple instances found for the provided display name %s", display_name)
        return _create_state_response(name, None, None, False,
                                      "Multiple IP Blocks found for the provided display name {}".format(display_name))

    existing_ip_block = ip_blocks[0] if ip_blocks.__len__() > 0 else None

    if __opts__.get("test"):
        log.info("present is called with test option")
        if existing_ip_block:
            return _create_state_response(name, None, None, None,
                                          "State present will update IP Block with name {}".format(display_name))
        else:
            return _create_state_response(name, None, None, None,
                                          "State present will create IP Block with name {}".format(display_name))
    if existing_ip_block:
        is_update_required = _check_for_updates(existing_ip_block, cidr=cidr, **kwargs)

        if is_update_required:
            _fill_kwargs_with_existing_info(existing_ip_block, kwargs, cidr)

            log.info("IP Block found with name %s", display_name)
            updated_ip_block = __salt__["nsxt_ip_blocks.update"](ip_block_id=existing_ip_block["id"],
                                                                 revision=existing_ip_block["_revision"],
                                                                 hostname=hostname,
                                                                 username=username,
                                                                 password=password,
                                                                 **kwargs)

            if updated_ip_block and "error" in updated_ip_block:
                return _create_state_response(name, None, None, False, updated_ip_block["error"])

            return _create_state_response(name, existing_ip_block, updated_ip_block, True,
                                          "Updated IP Block {}".format(display_name))
        else:
            log.info("All fields are same as existing IP Address Block %s", display_name)
            return _create_state_response(name, None, None, True,
                                          "IP Address Block exists already, no action to perform")
    else:
        log.info("No IP Block found with name %s", display_name)
        created_ip_block = __salt__["nsxt_ip_blocks.create"](cidr, hostname, username, password,
                                                             display_name=display_name, **kwargs)

        if created_ip_block and "error" in created_ip_block:
            return _create_state_response(name, None, None, False, created_ip_block["error"])

        return _create_state_response(name, None, created_ip_block, True, "Created IP Block {}".format(display_name))


def absent(
        name,
        display_name,
        hostname,
        username,
        password,
        **kwargs
):
    """
    Deletes an IP Address Block of provided name (if present)

    .. code-block:: yaml

    delete_ip_block:
      nsxt_ip_blocks.absent:
        - name: Delete IP Block
          hostname: <hostname>
          username: <username>
          password: <password>
          certificate: <certificate>
          verify_ssl: <False/True>
          display_name: <ip block name>

    name
        The Operation to perform

    hostname
        The host name of NSX-T manager

    username
        Username to connect to NSX-T manager

    password
        Password to connect to NSX-T manager

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

    display_name
        Display name of IP Address Block to delete
    """

    log.info("Checking if IP Address Block with name %s is present", display_name)

    get_ip_blocks_response = __salt__["nsxt_ip_blocks.get_by_display_name"](hostname, username, password, display_name,
                                                                            **kwargs)

    if get_ip_blocks_response and "error" in get_ip_blocks_response:
        return _create_state_response(name, None, None, False, get_ip_blocks_response["error"])

    ip_blocks = get_ip_blocks_response["results"]

    if ip_blocks.__len__() > 1:
        log.info("Multiple instances found for the provided display name %s", display_name)
        return _create_state_response(name, None, None, False,
                                      "Multiple IP Blocks found for the provided display name {}".format(display_name))

    existing_ip_block = ip_blocks[0] if ip_blocks.__len__() > 0 else None

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if existing_ip_block:
            return _create_state_response(name, None, None, None,
                                          "State absent will delete IP Block with name {}".format(display_name))
        else:
            return _create_state_response(name, None, None, None,
                                          "State absent will do nothing as no IP Block found with name {}".format(
                                              display_name))

    if existing_ip_block:
        log.info("IP Address Block found with name %s", display_name)
        deleted_response = __salt__["nsxt_ip_blocks.delete"](existing_ip_block["id"], hostname, username, password,
                                                             **kwargs)

        if deleted_response and "error" in deleted_response:
            return _create_state_response(name, None, None, False, deleted_response["error"])

        return _create_state_response(name, existing_ip_block, None, True, "Deleted IP Block {}".format(display_name))
    else:
        log.info("No IP Address Block found with name %s", display_name)
        return _create_state_response(name, None, None, True,
                                      "No IP Address Block found with name {}".format(display_name))


def _create_state_response(name, old_state, new_state, result, comment):
    state_response = dict()
    state_response["name"] = name
    state_response["result"] = result
    state_response["comment"] = comment
    state_response["changes"] = dict()
    if new_state or old_state:
        state_response["changes"]["old"] = old_state
        state_response["changes"]["new"] = new_state

    return state_response


def _check_for_updates(existing_ip_block, **kwargs):
    updatable_keys = ["cidr", "description", "tags"]

    is_updatable = False

    # check if any updatable field has different value from the existing one
    for key in updatable_keys:
        if not existing_ip_block.__contains__(key) and kwargs.__contains__(key):
            is_updatable = True
        if existing_ip_block.__contains__(key) and kwargs.__contains__(key) and existing_ip_block[key] != kwargs[key]:
            is_updatable = True

    return is_updatable


def _fill_kwargs_with_existing_info(existing_ip_block, kwargs, cidr):
    for key in dict(existing_ip_block).keys():
        if key not in kwargs:
            kwargs[key] = existing_ip_block[key]

    kwargs["cidr"] = cidr
