# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import json
import logging

import salt.exceptions
import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

try:
    from pyVmomi import pbm, VmomiSupport, SoapStubAdapter, vim

    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "storage_policy"


def __virtual__():
    if not HAS_PYVMOMI:
        return False, "Unable to import pyVmomi module."
    return __virtualname__


def _connect_spbm_(stub, context):
    hostname = stub.host.split(":")[0]
    sessionCookie = stub.cookie.split('"')[1]
    VmomiSupport.GetRequestContext()["vcSessionCookie"] = sessionCookie

    pbmStub = SoapStubAdapter(
        host=hostname,
        path="/pbm/sdk",
        version="pbm.version.version2",
        sslContext=context,
    )
    pbmStub.cookie = stub.cookie
    pbmSi = pbm.ServiceInstance("ServiceInstance", pbmStub)
    return pbmSi


def _get_vsan_storage_policies_(pbmSi):
    """
    Example of VMOMI Object:

    (pbm.profile.CapabilityBasedProfile) {
        dynamicType = <unset>,
        dynamicProperty = (vmodl.DynamicProperty) [],
        profileId = (pbm.profile.ProfileId) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            uniqueId = '9983b8d1-d959-4bca-aa1d-364bb3c709fa'
        },
        name = 'Performance',
        description = '',
        creationTime = 2022-09-16T17:44:20.409Z,
        createdBy = 'Temporary user handle',
        lastUpdatedTime = 2022-09-16T17:44:20.409Z,
        lastUpdatedBy = 'Temporary user handle',
        profileCategory = 'REQUIREMENT',
        resourceType = (pbm.profile.ResourceType) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            resourceType = 'STORAGE'
        },
        constraints = (pbm.profile.SubProfileCapabilityConstraints) {
            dynamicType = <unset>,
            dynamicProperty = (vmodl.DynamicProperty) [],
            subProfiles = (pbm.profile.SubProfileCapabilityConstraints.SubProfile) [
                (pbm.profile.SubProfileCapabilityConstraints.SubProfile) {
                    dynamicType = <unset>,
                    dynamicProperty = (vmodl.DynamicProperty) [],
                    name = 'VSAN',
                    capability = (pbm.capability.CapabilityInstance) [
                    (pbm.capability.CapabilityInstance) {
                        dynamicType = <unset>,
                        dynamicProperty = (vmodl.DynamicProperty) [],
                        id = (pbm.capability.CapabilityMetadata.UniqueId) {
                            dynamicType = <unset>,
                            dynamicProperty = (vmodl.DynamicProperty) [],
                            namespace = 'VSAN',
                            id = 'hostFailuresToTolerate'
                        },
                        constraint = (pbm.capability.ConstraintInstance) [
                            (pbm.capability.ConstraintInstance) {
                                dynamicType = <unset>,
                                dynamicProperty = (vmodl.DynamicProperty) [],
                                propertyInstance = (pbm.capability.PropertyInstance) [
                                (pbm.capability.PropertyInstance) {
                                    dynamicType = <unset>,
                                    dynamicProperty = (vmodl.DynamicProperty) [],
                                    id = 'hostFailuresToTolerate',
                                    operator = <unset>,
                                    value = 1
                                }
                                ]
                            }
                        ]
                    },
                    (pbm.capability.CapabilityInstance) {
                        dynamicType = <unset>,
                        dynamicProperty = (vmodl.DynamicProperty) [],
                        id = (pbm.capability.CapabilityMetadata.UniqueId) {
                            dynamicType = <unset>,
                            dynamicProperty = (vmodl.DynamicProperty) [],
                            namespace = 'VSAN',
                            id = 'replicaPreference'
                        },
                        constraint = (pbm.capability.ConstraintInstance) [
                            (pbm.capability.ConstraintInstance) {
                                dynamicType = <unset>,
                                dynamicProperty = (vmodl.DynamicProperty) [],
                                propertyInstance = (pbm.capability.PropertyInstance) [
                                (pbm.capability.PropertyInstance) {
                                    dynamicType = <unset>,
                                    dynamicProperty = (vmodl.DynamicProperty) [],
                                    id = 'replicaPreference',
                                    operator = <unset>,
                                    value = 'RAID-1 (Mirroring) - Performance'
                                }
                                ]
                            }
                        ]
                    },
                    (pbm.capability.CapabilityInstance) {
                        dynamicType = <unset>,
                        dynamicProperty = (vmodl.DynamicProperty) [],
                        id = (pbm.capability.CapabilityMetadata.UniqueId) {
                            dynamicType = <unset>,
                            dynamicProperty = (vmodl.DynamicProperty) [],
                            namespace = 'VSAN',
                            id = 'checksumDisabled'
                        },
                        constraint = (pbm.capability.ConstraintInstance) [
                            (pbm.capability.ConstraintInstance) {
                                dynamicType = <unset>,
                                dynamicProperty = (vmodl.DynamicProperty) [],
                                propertyInstance = (pbm.capability.PropertyInstance) [
                                (pbm.capability.PropertyInstance) {
                                    dynamicType = <unset>,
                                    dynamicProperty = (vmodl.DynamicProperty) [],
                                    id = 'checksumDisabled',
                                    operator = <unset>,
                                    value = false
                                }
                                ]
                            }
                        ]
                    },
                    (pbm.capability.CapabilityInstance) {
                        dynamicType = <unset>,
                        dynamicProperty = (vmodl.DynamicProperty) [],
                        id = (pbm.capability.CapabilityMetadata.UniqueId) {
                            dynamicType = <unset>,
                            dynamicProperty = (vmodl.DynamicProperty) [],
                            namespace = 'VSAN',
                            id = 'stripeWidth'
                        },
                        constraint = (pbm.capability.ConstraintInstance) [
                            (pbm.capability.ConstraintInstance) {
                                dynamicType = <unset>,
                                dynamicProperty = (vmodl.DynamicProperty) [],
                                propertyInstance = (pbm.capability.PropertyInstance) [
                                (pbm.capability.PropertyInstance) {
                                    dynamicType = <unset>,
                                    dynamicProperty = (vmodl.DynamicProperty) [],
                                    id = 'stripeWidth',
                                    operator = <unset>,
                                    value = 1
                                }
                                ]
                            }
                        ]
                    },
                    (pbm.capability.CapabilityInstance) {
                        dynamicType = <unset>,
                        dynamicProperty = (vmodl.DynamicProperty) [],
                        id = (pbm.capability.CapabilityMetadata.UniqueId) {
                            dynamicType = <unset>,
                            dynamicProperty = (vmodl.DynamicProperty) [],
                            namespace = 'VSAN',
                            id = 'forceProvisioning'
                        },
                        constraint = (pbm.capability.ConstraintInstance) [
                            (pbm.capability.ConstraintInstance) {
                                dynamicType = <unset>,
                                dynamicProperty = (vmodl.DynamicProperty) [],
                                propertyInstance = (pbm.capability.PropertyInstance) [
                                (pbm.capability.PropertyInstance) {
                                    dynamicType = <unset>,
                                    dynamicProperty = (vmodl.DynamicProperty) [],
                                    id = 'forceProvisioning',
                                    operator = <unset>,
                                    value = false
                                }
                                ]
                            }
                        ]
                    },
                    (pbm.capability.CapabilityInstance) {
                        dynamicType = <unset>,
                        dynamicProperty = (vmodl.DynamicProperty) [],
                        id = (pbm.capability.CapabilityMetadata.UniqueId) {
                            dynamicType = <unset>,
                            dynamicProperty = (vmodl.DynamicProperty) [],
                            namespace = 'VSAN',
                            id = 'iopsLimit'
                        },
                        constraint = (pbm.capability.ConstraintInstance) [
                            (pbm.capability.ConstraintInstance) {
                                dynamicType = <unset>,
                                dynamicProperty = (vmodl.DynamicProperty) [],
                                propertyInstance = (pbm.capability.PropertyInstance) [
                                (pbm.capability.PropertyInstance) {
                                    dynamicType = <unset>,
                                    dynamicProperty = (vmodl.DynamicProperty) [],
                                    id = 'iopsLimit',
                                    operator = <unset>,
                                    value = 0
                                }
                                ]
                            }
                        ]
                    },
                    (pbm.capability.CapabilityInstance) {
                        dynamicType = <unset>,
                        dynamicProperty = (vmodl.DynamicProperty) [],
                        id = (pbm.capability.CapabilityMetadata.UniqueId) {
                            dynamicType = <unset>,
                            dynamicProperty = (vmodl.DynamicProperty) [],
                            namespace = 'VSAN',
                            id = 'cacheReservation'
                        },
                        constraint = (pbm.capability.ConstraintInstance) [
                            (pbm.capability.ConstraintInstance) {
                                dynamicType = <unset>,
                                dynamicProperty = (vmodl.DynamicProperty) [],
                                propertyInstance = (pbm.capability.PropertyInstance) [
                                (pbm.capability.PropertyInstance) {
                                    dynamicType = <unset>,
                                    dynamicProperty = (vmodl.DynamicProperty) [],
                                    id = 'cacheReservation',
                                    operator = <unset>,
                                    value = 0
                                }
                                ]
                            }
                        ]
                    },
                    (pbm.capability.CapabilityInstance) {
                        dynamicType = <unset>,
                        dynamicProperty = (vmodl.DynamicProperty) [],
                        id = (pbm.capability.CapabilityMetadata.UniqueId) {
                            dynamicType = <unset>,
                            dynamicProperty = (vmodl.DynamicProperty) [],
                            namespace = 'VSAN',
                            id = 'proportionalCapacity'
                        },
                        constraint = (pbm.capability.ConstraintInstance) [
                            (pbm.capability.ConstraintInstance) {
                                dynamicType = <unset>,
                                dynamicProperty = (vmodl.DynamicProperty) [],
                                propertyInstance = (pbm.capability.PropertyInstance) [
                                (pbm.capability.PropertyInstance) {
                                    dynamicType = <unset>,
                                    dynamicProperty = (vmodl.DynamicProperty) [],
                                    id = 'proportionalCapacity',
                                    operator = <unset>,
                                    value = 0
                                }
                                ]
                            }
                        ]
                    }
                    ],
                    forceProvision = <unset>
                }
            ]
        },
        generationId = 0,
        isDefault = false,
        systemCreatedProfileType = <unset>,
        lineOfService = <unset>
        }

    Args:
        pbmSi: PBM Service Instance

    Returns:
        list: of profile VMOMI objects
    """
    resourceType = pbm.profile.ResourceType(resourceType=pbm.profile.ResourceTypeEnum.STORAGE)

    profileManager = pbmSi.RetrieveContent().profileManager
    profileIds = profileManager.PbmQueryProfile(resourceType)
    profiles = profileManager.PbmRetrieveContent(profileIds)
    return profiles


def find(policy_name=None, service_instance=None, profile=None):
    """
    Gets storage policies. Returns list.

    policy_name
        Filter by policy name, if None returns all policies

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    pbmSi = _connect_spbm_(service_instance._stub, service_instance._stub.schemeArgs["context"])
    policies = _get_vsan_storage_policies_(pbmSi)

    result_policies = []
    for policy in policies:
        if isinstance(policy, pbm.profile.CapabilityBasedProfile):
            if policy_name is None or policy.name == policy_name:
                result_policies.append(policy)

    # make JSON representation of current policies
    # old_configs holds only the rules that are in the scope of interest (provided in argument config_input)
    result = []
    for policy in result_policies:
        policy_json = {"policyName": policy.name}
        policy_json["constraints"] = []
        try:
            for sub_profile in policy.constraints.subProfiles:
                policy_constraint = {"name": sub_profile.name}
                policy_json["constraints"].append(policy_constraint)

                for capability in sub_profile.capability:
                    for constraint in capability.constraint:
                        for prop in constraint.propertyInstance:
                            policy_constraint[prop.id] = prop.value
        except AttributeError as err:
            pass  # skip if there is no subProfiles in policy.constraints

        result.append(policy_json)

    return result


def save(policy_config, service_instance=None, profile=None):
    """
    Update policy with given configuration.

    policy_config
        Policy name and configuration values.

    service_instance
        Use this vCenter service connection instance instead of creating a new one. (optional).

    profile
        Profile to use (optional)
    """
    service_instance = service_instance or connect.get_service_instance(
        config=__opts__, profile=profile
    )

    pbmSi = _connect_spbm_(service_instance._stub, service_instance._stub.schemeArgs["context"])
    policies = _get_vsan_storage_policies_(pbmSi)

    policy_name = policy_config["policyName"]

    policy = None
    for profile in policies:
        if isinstance(profile, pbm.profile.CapabilityBasedProfile):
            if profile.name == policy_name:
                policy = profile
                break

    profileManager = pbmSi.RetrieveContent().profileManager

    if policy is None:
        if not policy_name:
            raise salt.exceptions.CommandExecutionError(f"Policy name is required!")

        spec = pbm.profile.CapabilityBasedProfileCreateSpec()
        resourceType = pbm.profile.ResourceType()
        resourceType.resourceType = "STORAGE"
        spec.resourceType = resourceType
        subProfiles = []
        for subProfileProps in policy_config["constraints"]:
            subProfileName = subProfileProps["name"]
            subProfile = pbm.profile.SubProfileCapabilityConstraints.SubProfile()
            subProfile.name = subProfileName
            capabilities = []
            for propName in subProfileProps.keys():
                propValue = subProfileProps[propName]

                capability = pbm.capability.CapabilityInstance()

                id = pbm.capability.CapabilityMetadata.UniqueId()
                id.id = propName
                id.namespace = subProfileName
                capability.id = id

                constraint = pbm.capability.ConstraintInstance()
                propertyInstance = pbm.capability.PropertyInstance()
                propertyInstance.id = propName
                propertyInstance.value = propValue
                constraint.propertyInstance = [propertyInstance]
                capability.constraint = [constraint]

                capabilities.append(capability)
            subProfile.capability = capabilities
            subProfiles.append(subProfile)
        constraints = pbm.profile.SubProfileCapabilityConstraints()
        constraints.subProfiles = subProfiles
        spec.name = policy_name
        spec.constraints = constraints

        policy = profileManager.PbmCreate(spec)
        return {"status": "created"}
    else:
        spec = pbm.profile.CapabilityBasedProfileUpdateSpec()
        subProfiles = list(policy.constraints.subProfiles)
        for subProfileProps in policy_config["constraints"]:
            subProfileName = subProfileProps["name"]

            # find existing
            subProfile = None
            for p in subProfiles:
                if p.name == subProfileName:
                    subProfile = p
                    break
            # otherwise create subProfile
            if subProfile is None:
                subProfile = pbm.profile.SubProfileCapabilityConstraints.SubProfile()
                subProfile.name = subProfileName
                subProfiles.append(subProfile)

            capabilities = list(subProfile.capability)
            for propName in subProfileProps.keys():
                propValue = subProfileProps[propName]

                # find existing
                capability = None
                for c in capabilities:
                    if c.id.id == propName:
                        capability = c
                        break
                # otherwise create capability
                if capability is None:
                    capability = pbm.capability.CapabilityInstance()
                    id = pbm.capability.CapabilityMetadata.UniqueId()
                    id.id = propName
                    id.namespace = subProfileName
                    capability.id = id
                    capabilities.append(capability)

                constraint = pbm.capability.ConstraintInstance()
                propertyInstance = pbm.capability.PropertyInstance()
                propertyInstance.id = propName
                propertyInstance.value = propValue
                constraint.propertyInstance = [propertyInstance]
                capability.constraint = [constraint]
            subProfile.capability = capabilities

        constraints = (
            policy.constraints
        )  # use from policy instance not pbm.profile.SubProfileCapabilityConstraints()
        constraints.subProfiles = subProfiles
        spec.constraints = constraints

        profileManager.PbmUpdate(policy.profileId, spec)
        return {"status": "updated"}
