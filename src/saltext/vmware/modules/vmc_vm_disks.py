"""
Salt execution module for VMC vm disks
Provides methods to Create, Read, Update and Delete virtual disks from the VM.
"""
import logging
import os

from saltext.vmware.utils import vmc_constants
from saltext.vmware.utils import vmc_request
from saltext.vmware.utils import vmc_templates
from saltext.vmware.utils import vmc_vcenter_request

log = logging.getLogger(__name__)

__virtualname__ = "vmc_vm_disks"


def __virtual__():
    return __virtualname__


def get(hostname, username, password, vm_id, verify_ssl=True, cert=None):
    """
    Retrieves the available virtual disks for given VM.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vm_disks.get hostname=sample-vcenter.vmwarevmc.com ...

    hostname
        Hostname of the vCenter console

    username
        username required to login to vCenter console

    password
        password required to login to vCenter console

    vm_id
        Virtual machine identifier for which the available hard disks should be retrieved.

    verify_ssl
        (optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving the available virtual disks for VM %s", vm_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}api/vcenter/vm/{vm_id}/hardware/disk"
    api_url = api_url.format(base_url=api_url_base, vm_id=vm_id)

    headers = vmc_vcenter_request.get_headers(hostname, username, password)
    return vmc_vcenter_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        headers=headers,
        description="vmc_vm_disks.get",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def get_by_id(hostname, username, password, vm_id, disk_id, verify_ssl=True, cert=None):
    """
    Retrieves details of given virtual disk for given VM.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vm_disks.get_by_id hostname=sample-vcenter.vmwarevmc.com ...

    hostname
        Hostname of the vCenter console

    username
        username required to login to vCenter console

    password
        password required to login to vCenter console

    vm_id
        Virtual machine identifier for which the disk details should be retrieved.

    disk_id
        Virtual disk identifier for which the details should be retrieved from given VM

    verify_ssl
        (optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Retrieving details of virtual disk %s for VM %s", disk_id, vm_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}api/vcenter/vm/{vm_id}/hardware/disk/{disk_id}"
    api_url = api_url.format(base_url=api_url_base, vm_id=vm_id, disk_id=disk_id)

    headers = vmc_vcenter_request.get_headers(hostname, username, password)
    return vmc_vcenter_request.call_api(
        method=vmc_constants.GET_REQUEST_METHOD,
        url=api_url,
        headers=headers,
        description="vmc_vm_disks.get_by_id",
        verify_ssl=verify_ssl,
        cert=cert,
    )


def delete(hostname, username, password, vm_id, disk_id, verify_ssl=True, cert=None):
    """
    Deletes given virtual disk from given VM.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vm_disks.delete hostname=sample-vcenter.vmwarevmc.com ...

    hostname
        Hostname of the vCenter console

    username
        username required to login to vCenter console

    password
        password required to login to vCenter console

    vm_id
        Virtual machine identifier for which the disk should be removed.

    disk_id
        Virtual disk identifier which has to be removed from given VM

    verify_ssl
        (optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    """

    log.info("Deleting virtual disk %s from VM %s", disk_id, vm_id)
    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}api/vcenter/vm/{vm_id}/hardware/disk/{disk_id}"
    api_url = api_url.format(base_url=api_url_base, vm_id=vm_id, disk_id=disk_id)

    headers = vmc_vcenter_request.get_headers(hostname, username, password)
    return vmc_vcenter_request.call_api(
        method=vmc_constants.DELETE_REQUEST_METHOD,
        url=api_url,
        headers=headers,
        description="vmc_vm_disks.delete",
        responsebody_applicable=False,
        verify_ssl=verify_ssl,
        cert=cert,
    )


def update(
    hostname,
    username,
    password,
    vm_id,
    disk_id,
    verify_ssl=True,
    cert=None,
    backing_type=None,
    vmdk_file=None,
):
    """
    Updates the configuration of a given virtual disk of given VM. An update operation can be used to detach
    the existing VMDK file and attach another VMDK file to the virtual machine.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vm_disks.update hostname=sample-vcenter.vmwarevmc.com ...

    hostname
        Hostname of the vCenter console

    username
        username required to login to vCenter console

    password
        password required to login to vCenter console

    vm_id
        Virtual machine identifier for which the disk should be added.

    disk_id
        Virtual disk identifier which has to be updated for given VM

    verify_ssl
        (optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    backing_type
        (mandatory) Backing type for the virtual disk. Possible values are: VMDK_FILE

    vmdk_file
        (mandatory) Path of the VMDK file backing the virtual disk.

    """

    log.info("Updating configuration for virtual disk %s of VM %s", disk_id, vm_id)

    validation_result = []
    if backing_type is None:
        validation_result.append("backing_type")
    if vmdk_file is None:
        validation_result.append("vmdk_file")

    if validation_result:
        error_msg = "Mandatory params {} are missing from user input".format(validation_result)
        log.error(error_msg)
        return {vmc_constants.ERROR: error_msg}

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}api/vcenter/vm/{vm_id}/hardware/disk/{disk_id}"
    api_url = api_url.format(base_url=api_url_base, vm_id=vm_id, disk_id=disk_id)

    headers = vmc_vcenter_request.get_headers(hostname, username, password)

    payload = {"backing": {"type": backing_type, "vmdk_file": vmdk_file}}

    return vmc_vcenter_request.call_api(
        method=vmc_constants.PATCH_REQUEST_METHOD,
        url=api_url,
        headers=headers,
        description="vmc_vm_disks.update",
        responsebody_applicable=False,
        verify_ssl=verify_ssl,
        cert=cert,
        data=payload,
    )


def create(
    hostname,
    username,
    password,
    vm_id,
    bus_adapter_type,
    verify_ssl=True,
    cert=None,
    backing=None,
    new_vmdk=None,
    scsi=None,
    sata=None,
    ide=None,
):
    """
    Creates virtual disk for given VM.

    CLI Example:

    .. code-block:: bash

        salt vm_minion vmc_vm_disks.create hostname=sample-vcenter.vmwarevmc.com ...

    hostname
       Hostname of the vCenter console

    username
        username required to login to vCenter console

    password
        password required to login to vCenter console

    vm_id
        Virtual machine identifier for which the disk should be added.

    bus_adapter_type
        Type of host bus adapter to which the disk should be attached. Possible values are: IDE, SATA, SCSI

    verify_ssl
        (optional) Option to enable/disable SSL verification. Enabled by default.
        If set to False, the certificate validation is skipped.

    cert
        (optional) Path to the SSL client certificate file to connect to VMC Cloud Console.
        The certificate can be retrieved from browser.

    backing
        (optional) Existing physical resource backing for the virtual disk.
        Exactly one of backing or new_vmdk must be specified.
        If unset, the virtual disk will not be connected to an existing backing.

        It is a json object which can contain 'type' and 'vmdk_file' keys.

        'type': (String) (mandatory)
            Backing type for the virtual disk. Possible values are: VMDK_FILE

        'vmdk_file': (String) (optional)
            Path of the VMDK file backing the virtual disk.
            This field is optional and it is only relevant when the value of backing type is VMDK_FILE

        For ex:

            .. code::

                "backing": {
                    "type": "VMDK_FILE",
                    "vmdk_file": "[WorkloadDatastore] 8dff8760-b6da-24d2-475b-0200a629f7fc/test-vm-1.vmdk"
                }

    new_vmdk
        (optional) Specification for creating a new VMDK backing for the virtual disk.
        Exactly one of backing or new_vmdk must be specified.
        If unset, a new VMDK backing will not be created.

        It is a json object which can contain 'capacity', 'name' and 'storage_policy' keys.

        'capacity': (Integer As Int64) (optional)
            Capacity of the virtual disk backing in bytes. If unset, defaults to a guest-specific capacity.

        'name': (String) (optional)
            Base name of the VMDK file. The name should not include the '.vmdk' file extension.
            If unset, a name (derived from the name of the virtual machine) will be chosen by the server.

        'storage_policy': (optional)
            The storage_policy structure contains information about the storage policy that is to be associated
            with the VMDK file. If unset the default storage policy of the target datastore (if applicable)
            is applied. Currently a default storage policy is only supported by
            object based datastores : VVol & vSAN.
            For non-object datastores, if unset then no storage policy would be associated with the VMDK file.

            It is a json object which contains a key 'policy'.

            'policy': (String) (mandatory)
                Identifier of the storage policy which should be associated with the VMDK file.
                When clients pass a value of this structure as a parameter, the field must be
                an identifier for the resource type: com.vmware.vcenter.StoragePolicy.

        For ex:

            .. code::

                "new_vmdk": {
                    "capacity": 17179869184,
                    "name": "test-1",
                    "storage_policy": {
                        "policy":"aa6d5a82-1c88-45da-85d3-3d74b91a5bad"
                    }
                }

    scsi
        (optional) Address for attaching the device to a virtual SCSI adapter. If unset, the server will choose
        an available address; if none is available, the request will fail.

        It is a json object which can contain 'bus' and 'unit' keys.

        'bus': (Integer As Int64) (mandatory)
            Bus number of the adapter to which the device should be attached.

        'unit': (Integer As Int64) (optional)
            Unit number of the device. If unset, the server will choose an available unit number on the
            specified adapter. If there are no available connections on the adapter, the request will be rejected.

        For ex:

            .. code::

                "scsi": {
                    "bus": 0,
                    "unit": 1
                }

    sata
        (optional) Address for attaching the device to a virtual SATA adapter. If unset, the server will choose
        an available address; if none is available, the request will fail.

        It is a json object which can contain 'bus' and 'unit' keys.

        'bus': (Integer As Int64) (mandatory)
            Bus number of the adapter to which the device should be attached.

        'unit': (Integer As Int64) (optional)
            Unit number of the device. If unset, the server will choose an available unit number on the
            specified adapter. If there are no available connections on the adapter, the request will be rejected.

        For ex:

            .. code::

                "sata": {
                    "bus": 0,
                    "unit": 1
                }

    ide
        (optional) Address for attaching the device to a virtual IDE adapter. If unset, the server will choose
        an available address; if none is available, the request will fail.

        It is a json object which can contain 'master' and 'primary' keys.

        'master': (Boolean) (Optional)
            Flag specifying whether the device should be the master or slave device on the IDE adapter.
            If unset, the server will choose an available connection type. If no IDE connections are available,
            the request will be rejected.

        'primary': (Boolean) (Optional)
            Flag specifying whether the device should be attached to the primary or secondary IDE adapter
            of the virtual machine. If unset, the server will choose a adapter with an available connection.
            If no IDE connections are available, the request will be rejected.

        For ex:

            .. code::

                "ide": {
                    "master": false,
                    "primary": false
                }

    NOTE:  Exactly one of backing or new_vmdk must be specified. Else the request will be rejected.

    """

    log.info("Creating virtual disk on virtual %s adapter for VM %s", bus_adapter_type, vm_id)

    if backing is None and new_vmdk is None:
        error_msg = "Exactly one of backing or new_vmdk must be specified to create virtual disk"
        log.error(error_msg)
        return {vmc_constants.ERROR: error_msg}

    if backing is not None and new_vmdk is not None:
        error_msg = "Either an existing disk backing or a new VMDK may be specified but not both"
        log.error(error_msg)
        return {vmc_constants.ERROR: error_msg}

    api_url_base = vmc_request.set_base_url(hostname)
    api_url = "{base_url}api/vcenter/vm/{vm_id}/hardware/disk"
    api_url = api_url.format(base_url=api_url_base, vm_id=vm_id)

    headers = vmc_vcenter_request.get_headers(hostname, username, password)

    allowed_dict = {
        "backing": backing,
        "ide": ide,
        "new_vmdk": new_vmdk,
        "sata": sata,
        "scsi": scsi,
    }

    req_data = vmc_request._filter_kwargs(allowed_kwargs=allowed_dict.keys(), **allowed_dict)

    payload = vmc_request.create_payload_for_request(vmc_templates.create_vm_disks, req_data)
    payload["type"] = bus_adapter_type

    return vmc_vcenter_request.call_api(
        method=vmc_constants.POST_REQUEST_METHOD,
        url=api_url,
        headers=headers,
        description="vmc_vm_disks.create",
        verify_ssl=verify_ssl,
        cert=cert,
        data=payload,
    )
