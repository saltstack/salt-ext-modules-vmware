# SPDX-License-Identifier: Apache-2.0
import logging

import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

__virtualname__ = "vsphere"


def __virtual__():
    return __virtualname__


def storage_policy(name, policies):
    """
    Checks state of storage policy of each host
    policies
        Policy list to set state to
    """

    res = connect.request(
        "/api/vcenter/storage/policies", "GET", opts=__opts__, pillar=__pillar__
    )
    response = res["response"].json()
    current_policies = [p["name"] for p in response]
    changes = []
    for policy in policies:
        if policy['policyName'] not in current_policies:
            changes.append(policy['policyName'])

    ret = {"name": name, "result": True, "comment": "",
           "changes": changes}
    return ret