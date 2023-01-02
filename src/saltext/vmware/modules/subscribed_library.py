# Copyright 2021 VMware, Inc.
# SPDX-License: Apache-2.0
import logging

import saltext.vmware.utils.connect as connect

log = logging.getLogger(__name__)

__virtualname__ = "vsphere_subscribed_library"


def __virtual__():
    return __virtualname__


def list():
    """
    Lists IDs for all the subscribed libraries on a given vCenter.
    """
    response = connect.request(
        "/api/content/subscribed-library", "GET", opts=__opts__, pillar=__pillar__
    )
    response = response["response"].json()
    return response["value"]


def get(id):
    """
    Returns info on given subscribed library.

    id
        (string) Subscribed Library ID.
    """
    url = f"/api/content/subscribed-library/{id}"
    response = connect.request(url, "GET", opts=__opts__, pillar=__pillar__)
    return response["response"].json()


def create(name, description, published, authentication, datastore):
    """
    Creates a new subscribed library.

    name
        Name of the subscribed library.

    datastore
        Datastore ID where library will store its contents.

    description
        (optional) Description for the subscribed library being created.

    published
        (optional) Whether the subscribed library should be published or not.

    authentication
        (optional) The authentication method for the subscribed library being published.
    """

    publish_info = {"published": published, "authentication_method": authentication}
    storage_backings = {"datastore_id": datastore, "type": "DATASTORE"}

    data = {
        "name": name,
        "publish_info": publish_info,
        "storage_backings": storage_backings,
        "type": "SUBSCRIBED",
    }
    if description is not None:
        data["description"] = description

    response = connect.request(
        "/api/content/subscribed-library", "POST", body=data, opts=__opts__, pillar=__pillar__
    )
    return response["response"].json()


def update(id, name, description, published, authentication, datastore):
    """
    Updates subscribed library with given id.

    id
        (string) Subscribed library ID .

    name
        (optional) Name of the subscribed library.

    description
        (optional) Description for the subscribed library being updated.

    published
        (optional) Whether the subscribed library should be published or not.

    authentication
        (optional) The authentication method for the subscribed library being published.

    datastore
        (optional) Datastore ID where library will store its contents.
    """

    publish_info = {"published": published, "authentication_method": authentication}
    storage_backings = {"datastore_id": datastore, "type": "DATASTORE"}

    data = {}
    if name is not None:
        data["name"] = name
    if description is not None:
        data["name"] = description
    if published is not None:
        data["publish_info"] = publish_info
    if datastore is not None:
        data["storage_backings"] = storage_backings

    url = f"/api/content/subscribed-library/{id}"
    response = connect.request(url, "PATCH", body=data, opts=__opts__, pillar=__pillar__)
    return response["response"].json()


def delete(id):
    """
    Delete subscribed library having corresponding id.

    id
        (string) Subscribed library ID to delete.
    """
    url = f"/api/content/subscribed-library/{id}"
    response = connect.request(url, "DELETE", opts=__opts__, pillar=__pillar__)
    return response["response"].json()
