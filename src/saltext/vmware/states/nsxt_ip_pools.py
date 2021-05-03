# -*- coding: utf-8 -*-
"""
Salt State file to create/update/delete an IP Address Pool

Example:

.. code-block:: yaml

    create_ip_pool:
      nsxt_ip_pools.present:
        - name: Create IP Pool
          hostname: <hostname>
          username: <username>
          password: <password>
          cert: <certificate path>
          verify_ssl: <False/True>
          display_name: <ip pool name>
          description: <ip pool description>
          tags:
            - tag: <tag-key-1>
              scope: <tag-value-1>
            - tag: <tag-key-2>
              scope: <tag-value-2>
          subnets:
            - cidr: <cidr_value>
              gateway_ip: <gateway_ip_value>
              dns_nameservers:
                - <dns_nameserver1>
                - <dns_nameserver2>
              allocation_ranges:
                - "start": <IP-Address-Range-start-1>
                  "end": <IP-Address-Range-end-1>
          ip_release_delay: <delay in milliseconds>
"""
from __future__ import absolute_import, print_function, unicode_literals

import logging

log = logging.getLogger(__name__)

__virtual_name__ = "nsxt_ip_pools"


def __virtual__():
    """
        Only load if the nsxt_ip_pools module is available in __salt__
    """
    return (
        __virtual_name__ if "nsxt_ip_pools.get" in __salt__ else False,
        "'nsxt_ip_pools' binary not found on system",
    )


def present(
        name,
        display_name,
        hostname,
        username,
        password,
        **kwargs
):
    """
    Creates/Updates(if present with the same name) an IP Address Pool

    .. code-block:: yaml

    create_ip_pool:
      nsxt_ip_pools.present:
        - name: Create IP Pool
          hostname: <hostname>
          username: <username>
          password: <password>
          certificate: <certificate>
          verify_ssl: <False/True>
          display_name: <ip pool name>
          description: <ip pool description>
          tags:
            - tag: <tag-key-1>
              scope: <tag-value-1>
            - tag: <tag-key-2>
              scope: <tag-value-2>
          subnets:
            - cidr: <cidr_value>
              gateway_ip: <gateway_ip_value>
              dns_nameservers:
                - <dns_nameserver1>
                - <dns_nameserver2>
              allocation_ranges:
                - start: <IP-Address-Range-start-1>
                  end: <IP-Address-Range-end-1>
          ip_release_delay: <delay in milliseconds>

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
        The name using which IP Address Pool will be created. In case of update the provided display_name should be
        unique else the method will raise an error

    description
        (Optional) description for the IP Address Pool

    tags
        (Optional) Opaque identifiers meaningful to the API user. Maximum 30 tags can be associated:
        tags:
            - tag: <tag-key-1>
              scope: <tag-value-1>
            - tag: <tag-key-2>
              scope: <tag-value-2>

    subnets
        (Optional) The collection of one or more subnet objects in a pool.
        Subnets can be IPv4 or IPv6 and they should not overlap. The maximum number will not exceed 5 subnets.
        subnets:
            - cidr: <cidr_value>
              gateway_ip: <gateway_ip_value>
              dns_nameservers:
                - <dns_nameserver1>
                  <dns_nameserver2>
              allocation_ranges:
                - start: <IP-Address-Range-start-1>
                  end: <IP-Address-Range-end-1>

    ip_release_delay
        (Optional) Delay in milliseconds, while releasing allocated IP address from IP pool (Default is 2 mins).
    """

    log.info("Checking if IP Pool with name %s is present", display_name)
    get_ip_pools_response = __salt__["nsxt_ip_pools.get_by_display_name"](hostname, username, password, display_name,
                                                                          **kwargs)

    if get_ip_pools_response and "error" in get_ip_pools_response:
        return _create_state_response(name, None, None, False, get_ip_pools_response["error"])

    ip_pools = get_ip_pools_response["results"]

    if ip_pools.__len__() > 1:
        log.info("Multiple instances found for the provided display name %s", display_name)
        return _create_state_response(name, None, None, False,
                                      "Multiple IP Pools found for the provided display name {}".format(display_name))

    existing_ip_pool = ip_pools[0] if ip_pools.__len__() > 0 else None

    if __opts__.get("test"):
        log.info("present is called with test option")
        if existing_ip_pool:
            return _create_state_response(name, None, None, None,
                                          "State present will update IP Pool with name {}".format(display_name))
        else:
            return _create_state_response(name, None, None, None,
                                          "State present will create IP Pool with name {}".format(display_name))
    if existing_ip_pool:
        is_update_required = _check_for_updates(existing_ip_pool, **kwargs)

        if is_update_required:
            _fill_kwargs_with_existing_info(existing_ip_pool, kwargs)

            log.info("IP Pool found with name %s", display_name)
            updated_ip_pool = __salt__["nsxt_ip_pools.update"](ip_pool_id=existing_ip_pool["id"],
                                                               revision=existing_ip_pool["_revision"],
                                                               hostname=hostname,
                                                               username=username,
                                                               password=password,
                                                               **kwargs)

            if updated_ip_pool and "error" in updated_ip_pool:
                return _create_state_response(name, None, None, False, updated_ip_pool["error"])

            return _create_state_response(name, existing_ip_pool, updated_ip_pool, True,
                                          "Updated IP Pool {}".format(display_name))
        else:
            log.info("All fields are same as existing IP Address Pool %s", display_name)
            return _create_state_response(name, None, None, True,
                                          "IP Address Pool exists already, no action to perform")
    else:
        log.info("No IP Pool found with name %s", display_name)
        created_ip_pool = __salt__["nsxt_ip_pools.create"](hostname, username, password, display_name=display_name,
                                                           **kwargs)

        if created_ip_pool and "error" in created_ip_pool:
            return _create_state_response(name, None, None, False, created_ip_pool["error"])

        return _create_state_response(name, None, created_ip_pool, True, "Created IP Pool {}".format(display_name))


def absent(
        name,
        display_name,
        hostname,
        username,
        password,
        **kwargs
):
    """
    Deletes an IP Address Pool of provided name (if present)

    .. code-block:: yaml

    delete_ip_pool:
      nsxt_ip_pools.absent:
        - name: Delete IP Pool
          hostname: <hostname>
          username: <username>
          password: <password>
          certificate: <certificate>
          verify_ssl: <False/True>
          display_name: <ip pool name>

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
        Display name of IP Address Pool to delete
    """

    log.info("Checking if IP Address Pool with name %s is present", display_name)

    get_ip_pools_response = __salt__["nsxt_ip_pools.get_by_display_name"](hostname, username, password, display_name,
                                                                          **kwargs)

    if get_ip_pools_response and "error" in get_ip_pools_response:
        return _create_state_response(name, None, None, False, get_ip_pools_response["error"])

    ip_pools = get_ip_pools_response["results"]

    if ip_pools.__len__() > 1:
        log.info("Multiple instances found for the provided display name %s", display_name)
        return _create_state_response(name, None, None, False,
                                      "Multiple IP Pools found for the provided display name {}".format(display_name))

    existing_ip_pool = ip_pools[0] if ip_pools.__len__() > 0 else None

    if __opts__.get("test"):
        log.info("absent is called with test option")
        if existing_ip_pool:
            return _create_state_response(name, None, None, None,
                                          "State absent will delete IP Pool with name {}".format(display_name))
        else:
            return _create_state_response(name, None, None, None,
                                          "State absent will do nothing as no IP Pool found with name {}".format(
                                              display_name))

    if existing_ip_pool:
        log.info("IP Address Pool found with name %s", display_name)
        deleted_response = __salt__["nsxt_ip_pools.delete"](existing_ip_pool["id"], hostname, username, password,
                                                            **kwargs)

        if deleted_response and "error" in deleted_response:
            return _create_state_response(name, None, None, False, deleted_response["error"])

        return _create_state_response(name, existing_ip_pool, None, True, "Deleted IP Pool {}".format(display_name))
    else:
        log.info("No IP Address Pool found with name %s", display_name)
        return _create_state_response(name, None, None, True,
                                      "No IP Address Pool found with name {}".format(display_name))


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


def _check_for_updates(existing_ip_pool, **kwargs):
    updatable_keys = ["subnets", "description", "tags", "ip_release_delay"]

    is_updatable = False

    # check if any updatable field has different value from the existing one
    for key in updatable_keys:
        if not existing_ip_pool.__contains__(key) and kwargs.__contains__(key):
            is_updatable = True
        if existing_ip_pool.__contains__(key) and kwargs.__contains__(key) and existing_ip_pool[key] != kwargs[key]:
            is_updatable = True

    return is_updatable


def _fill_kwargs_with_existing_info(existing_ip_pool, kwargs):
    for key in dict(existing_ip_pool).keys():
        if key not in kwargs:
            kwargs[key] = existing_ip_pool[key]
