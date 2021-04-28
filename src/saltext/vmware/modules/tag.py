# SPDX-License-Identifier: Apache-2.0
import logging
import sys

import saltext.vmware.utils.vmware
from salt.utils.decorators import depends
from salt.utils.decorators import ignores_kwargs

log = logging.getLogger(__name__)

try:
    # pylint: disable=no-name-in-module
    from pyVmomi import (
        vim,
        vmodl,
        pbm,
        VmomiSupport,
    )

    # pylint: enable=no-name-in-module

    # We check the supported vim versions to infer the pyVmomi version
    if (
        "vim25/6.0" in VmomiSupport.versionMap
        and sys.version_info > (2, 7)
        and sys.version_info < (2, 7, 9)
    ):

        log.debug("pyVmomi not loaded: Incompatible versions " "of Python. See Issue #29537.")
        raise ImportError()
    HAS_PYVMOMI = True
except ImportError:
    HAS_PYVMOMI = False


__virtualname__ = "vmware_tag"


def __virtual__():
    return __virtualname__


def _get_client(server, username, password, verify_ssl=None, ca_bundle=None):
    """
    Establish client through proxy or with user provided credentials.

    :param basestring server:
        Target DNS or IP of vCenter center.
    :param basestring username:
        Username associated with the vCenter center.
    :param basestring password:
        Password associated with the vCenter center.
    :param boolean verify_ssl:
        Verify the SSL certificate. Default: True
    :param basestring ca_bundle:
        Path to the ca bundle to use when verifying SSL certificates.
    :returns:
        vSphere Client instance.
    :rtype:
        vSphere.Client
    """
    # Get salted vSphere Client
    details = None
    if not (server and username and password):
        # User didn't provide CLI args so use proxy information
        details = __salt__["vcenter.get_details"]()
        server = details["vcenter"]
        username = details["username"]
        password = details["password"]

    if verify_ssl is None:
        if details is None:
            details = __salt__["vcenter.get_details"]()
        verify_ssl = details.get("verify_ssl", True)
        if verify_ssl is None:
            verify_ssl = True

    if ca_bundle is None:
        if details is None:
            details = __salt__["vcenter.get_details"]()
        ca_bundle = details.get("ca_bundle", None)

    if verify_ssl is False and ca_bundle is not None:
        log.error("Cannot set verify_ssl to False and ca_bundle together")
        return False

    if ca_bundle:
        ca_bundle = salt.utils.http.get_ca_bundle({"ca_bundle": ca_bundle})

    # Establish connection with client
    client = salt.utils.vmware.get_vsphere_client(
        server=server,
        username=username,
        password=password,
        verify_ssl=verify_ssl,
        ca_bundle=ca_bundle,
    )
    # Will return None if utility function causes Unauthenticated error
    return client


def list_tag_categories(
    server=None,
    username=None,
    password=None,
    service_instance=None,
    verify_ssl=None,
    ca_bundle=None,
):
    """
    List existing categories a user has access to.

    CLI Example:

    .. code-block:: bash

            salt vm_minion vsphere.list_tag_categories

    :param basestring server:
        Target DNS or IP of vCenter center.
    :param basestring username:
        Username associated with the vCenter center.
    :param basestring password:
        Password associated with the vCenter center.
    :param boolean verify_ssl:
        Verify the SSL certificate. Default: True
    :param basestring ca_bundle:
        Path to the ca bundle to use when verifying SSL certificates.
    :returns:
        Value(s) of category_id.
    :rtype:
        list of str
    """
    categories = None
    client = _get_client(server, username, password, verify_ssl=verify_ssl, ca_bundle=ca_bundle)

    if client:
        categories = client.tagging.Category.list()
    return {"Categories": categories}


def list_tags(
    server=None,
    username=None,
    password=None,
    service_instance=None,
    verify_ssl=None,
    ca_bundle=None,
):
    """
    List existing tags a user has access to.

    CLI Example:

    .. code-block:: bash

            salt vm_minion vsphere.list_tags

    :param basestring server:
        Target DNS or IP of vCenter center.
    :param basestring username:
        Username associated with the vCenter center.
    :param basestring password:
        Password associated with the vCenter center.
    :param boolean verify_ssl:
        Verify the SSL certificate. Default: True
    :param basestring ca_bundle:
        Path to the ca bundle to use when verifying SSL certificates.
    :return:
        Value(s) of tag_id.
    :rtype:
        list of str
    """
    tags = None
    client = _get_client(server, username, password, verify_ssl=verify_ssl, ca_bundle=ca_bundle)

    if client:
        tags = client.tagging.Tag.list()
    return {"Tags": tags}


def attach_tag(
    object_id,
    tag_id,
    managed_obj="ClusterComputeResource",
    server=None,
    username=None,
    password=None,
    service_instance=None,
    verify_ssl=None,
    ca_bundle=None,
):
    """
    Attach an existing tag to an input object.

    The tag needs to meet the cardinality (`CategoryModel.cardinality`) and
    associability (`CategoryModel.associable_types`) criteria in order to be
    eligible for attachment. If the tag is already attached to the object,
    then this method is a no-op and an error will not be thrown. To invoke
    this method, you need the attach tag privilege on the tag and the read
    privilege on the object.

    CLI Example:

    .. code-block:: bash

            salt vm_minion vsphere.attach_tag domain-c2283 \
                urn:vmomi:InventoryServiceTag:b55ecc77-f4a5-49f8-ab52-38865467cfbe:GLOBAL

    :param str object_id:
        The identifier of the input object.
    :param str tag_id:
        The identifier of the tag object.
    :param str managed_obj:
        Classes that contain methods for creating and deleting resources
        typically contain a class attribute specifying the resource type
        for the resources being created and deleted.
    :param basestring server:
        Target DNS or IP of vCenter center.
    :param basestring username:
        Username associated with the vCenter center.
    :param basestring password:
        Password associated with the vCenter center.
    :param boolean verify_ssl:
        Verify the SSL certificate. Default: True
    :param basestring ca_bundle:
        Path to the ca bundle to use when verifying SSL certificates.
    :return:
        The list of all tag identifiers that correspond to the
        tags attached to the given object.
    :rtype:
        list of tags
    :raise: Unauthorized
        if you do not have the privilege to read the object.
    :raise: Unauthenticated
        if the user can not be authenticated.
    """
    tag_attached = None
    client = _get_client(server, username, password, verify_ssl=verify_ssl, ca_bundle=ca_bundle)

    if client:
        # Create dynamic id object associated with a type and an id.
        # Note, here the default is ClusterComputeResource, which
        # infers a lazy loaded vim.ClusterComputerResource.

        # The ClusterComputeResource data object aggregates the compute
        # resources of associated HostSystem objects into a single compute
        # resource for use by virtual machines.
        dynamic_id = DynamicID(type=managed_obj, id=object_id)
        try:
            tag_attached = client.tagging.TagAssociation.attach(tag_id=tag_id, object_id=dynamic_id)
        except vsphere_errors:
            log.warning(
                "Unable to attach tag. Check user privileges and" " object_id (must be a string)."
            )
    return {"Tag attached": tag_attached}


def list_attached_tags(
    object_id,
    managed_obj="ClusterComputeResource",
    server=None,
    username=None,
    password=None,
    service_instance=None,
    verify_ssl=None,
    ca_bundle=None,
):
    """
    List existing tags a user has access to.

    CLI Example:

    .. code-block:: bash

            salt vm_minion vsphere.list_attached_tags domain-c2283

    :param str object_id:
        The identifier of the input object.
    :param str managed_obj:
        Classes that contain methods for creating and deleting resources
        typically contain a class attribute specifying the resource type
        for the resources being created and deleted.
    :param basestring server:
        Target DNS or IP of vCenter center.
    :param basestring username:
        Username associated with the vCenter center.
    :param basestring password:
        Password associated with the vCenter center.
    :param boolean verify_ssl:
        Verify the SSL certificate. Default: True
    :param basestring ca_bundle:
        Path to the ca bundle to use when verifying SSL certificates.
    :return:
        The list of all tag identifiers that correspond to the
        tags attached to the given object.
    :rtype:
        list of tags
    :raise: Unauthorized
        if you do not have the privilege to read the object.
    :raise: Unauthenticated
        if the user can not be authenticated.
    """
    attached_tags = None
    client = _get_client(server, username, password, verify_ssl=verify_ssl, ca_bundle=ca_bundle)

    if client:
        # Create dynamic id object associated with a type and an id.
        # Note, here the default is ClusterComputeResource, which
        # infers a lazy loaded vim.ClusterComputerResource.

        # The ClusterComputeResource data object aggregates the compute
        # resources of associated HostSystem objects into a single compute
        # resource for use by virtual machines.
        dynamic_id = DynamicID(type=managed_obj, id=object_id)
        try:
            attached_tags = client.tagging.TagAssociation.list_attached_tags(dynamic_id)
        except vsphere_errors:
            log.warning(
                "Unable to list attached tags. Check user privileges"
                " and object_id (must be a string)."
            )
    return {"Attached tags": attached_tags}


def create_tag_category(
    name,
    description,
    cardinality,
    server=None,
    username=None,
    password=None,
    service_instance=None,
    verify_ssl=None,
    ca_bundle=None,
):
    """
    Create a category with given cardinality.

    CLI Example:

    .. code-block:: bash

            salt vm_minion vsphere.create_tag_category

    :param str name:
        Name of tag category to create (ex. Machine, OS, Availability, etc.)
    :param str description:
        Given description of tag category.
    :param str cardinality:
        The associated cardinality (SINGLE, MULTIPLE) of the category.
    :param basestring server:
        Target DNS or IP of vCenter center.
    :param basestring username:
        Username associated with the vCenter center.
    :param basestring password:
        Password associated with the vCenter center.
    :param boolean verify_ssl:
        Verify the SSL certificate. Default: True
    :param basestring ca_bundle:
        Path to the ca bundle to use when verifying SSL certificates.
    :return:
        Identifier of the created category.
    :rtype:
        str
    :raise: AlreadyExists
        if the name` provided in the create_spec is the name of an already
        existing category.
    :raise: InvalidArgument
        if any of the information in the create_spec is invalid.
    :raise: Unauthorized
        if you do not have the privilege to create a category.
    """
    category_created = None
    client = _get_client(server, username, password, verify_ssl=verify_ssl, ca_bundle=ca_bundle)

    if client:
        if cardinality == "SINGLE":
            cardinality = CategoryModel.Cardinality.SINGLE
        elif cardinality == "MULTIPLE":
            cardinality = CategoryModel.Cardinality.MULTIPLE
        else:
            # Cardinality must be supplied correctly
            cardinality = None

        create_spec = client.tagging.Category.CreateSpec()
        create_spec.name = name
        create_spec.description = description
        create_spec.cardinality = cardinality
        associable_types = set()
        create_spec.associable_types = associable_types
        try:
            category_created = client.tagging.Category.create(create_spec)
        except vsphere_errors:
            log.warning(
                "Unable to create tag category. Check user privilege" " and see if category exists."
            )
    return {"Category created": category_created}


def delete_tag_category(
    category_id,
    server=None,
    username=None,
    password=None,
    service_instance=None,
    verify_ssl=None,
    ca_bundle=None,
):
    """
    Delete a category.

    CLI Example:

    .. code-block:: bash

            salt vm_minion vsphere.delete_tag_category

    :param str category_id:
        The identifier of category to be deleted.
        The parameter must be an identifier for the resource type:
        ``com.vmware.cis.tagging.Category``.
    :param basestring server:
        Target DNS or IP of vCenter center.
    :param basestring username:
        Username associated with the vCenter center.
    :param basestring password:
        Password associated with the vCenter center.
    :param boolean verify_ssl:
        Verify the SSL certificate. Default: True
    :param basestring ca_bundle:
        Path to the ca bundle to use when verifying SSL certificates.
    :raise: NotFound
        if the tag for the given tag_id does not exist in the system.
    :raise: Unauthorized
        if you do not have the privilege to delete the tag.
    :raise: Unauthenticated
        if the user can not be authenticated.
    """
    category_deleted = None
    client = _get_client(server, username, password, verify_ssl=verify_ssl, ca_bundle=ca_bundle)

    if client:
        try:
            category_deleted = client.tagging.Category.delete(category_id)
        except vsphere_errors:
            log.warning(
                "Unable to delete tag category. Check user privilege" " and see if category exists."
            )
    return {"Category deleted": category_deleted}


def create_tag(
    name,
    description,
    category_id,
    server=None,
    username=None,
    password=None,
    service_instance=None,
    verify_ssl=None,
    ca_bundle=None,
):
    """
    Create a tag under a category with given description.

    CLI Example:

    .. code-block:: bash

            salt vm_minion vsphere.create_tag

    :param basestring server:
        Target DNS or IP of vCenter client.
    :param basestring username:
         Username associated with the vCenter client.
    :param basestring password:
        Password associated with the vCenter client.
    :param str name:
        Name of tag category to create (ex. Machine, OS, Availability, etc.)
    :param str description:
        Given description of tag category.
    :param str category_id:
        Value of category_id representative of the category created previously.
    :param boolean verify_ssl:
        Verify the SSL certificate. Default: True
    :param basestring ca_bundle:
        Path to the ca bundle to use when verifying SSL certificates.
    :return:
        The identifier of the created tag.
    :rtype:
        str
    :raise: AlreadyExists
        if the name provided in the create_spec is the name of an already
        existing tag in the input category.
    :raise: InvalidArgument
        if any of the input information in the create_spec is invalid.
    :raise: NotFound
        if the category for in the given create_spec does not exist in
        the system.
    :raise: Unauthorized
        if you do not have the privilege to create tag.
    """
    tag_created = None
    client = _get_client(server, username, password, verify_ssl=verify_ssl, ca_bundle=ca_bundle)

    if client:
        create_spec = client.tagging.Tag.CreateSpec()
        create_spec.name = name
        create_spec.description = description
        create_spec.category_id = category_id
        try:
            tag_created = client.tagging.Tag.create(create_spec)
        except vsphere_errors:
            log.warning("Unable to create tag. Check user privilege and see" " if category exists.")
    return {"Tag created": tag_created}


def delete_tag(
    tag_id,
    server=None,
    username=None,
    password=None,
    service_instance=None,
    verify_ssl=None,
    ca_bundle=None,
):
    """
    Delete a tag.

    CLI Example:

    .. code-block:: bash

            salt vm_minion vsphere.delete_tag

    :param str tag_id:
        The identifier of tag to be deleted.
        The parameter must be an identifier for the resource type:
        ``com.vmware.cis.tagging.Tag``.
    :param basestring server:
        Target DNS or IP of vCenter center.
    :param basestring username:
        Username associated with the vCenter center.
    :param basestring password:
        Password associated with the vCenter center.
    :param boolean verify_ssl:
        Verify the SSL certificate. Default: True
    :param basestring ca_bundle:
        Path to the ca bundle to use when verifying SSL certificates.
    :raise: AlreadyExists
        if the name provided in the create_spec is the name of an already
        existing category.
    :raise: InvalidArgument
        if any of the information in the create_spec is invalid.
    :raise: Unauthorized
        if you do not have the privilege to create a category.
    """
    tag_deleted = None
    client = _get_client(server, username, password, verify_ssl=verify_ssl, ca_bundle=ca_bundle)

    if client:
        try:
            tag_deleted = client.tagging.Tag.delete(tag_id)
        except vsphere_errors:
            log.warning(
                "Unable to delete category. Check user privileges" " and that category exists."
            )
    return {"Tag deleted": tag_deleted}
