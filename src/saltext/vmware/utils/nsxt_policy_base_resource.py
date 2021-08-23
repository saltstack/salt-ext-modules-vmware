import inspect
from abc import ABC
from abc import abstractmethod

import salt.utils.dictdiffer
from salt.exceptions import SaltInvocationError
from saltext.vmware.utils import nsxt_request


class NSXTPolicyBaseResource(ABC):
    def get(self, url, username, password, **kwargs):

        params = self._create_query_params(**kwargs)

        return nsxt_request.call_api(
            method="get",
            url=url,
            username=username,
            password=password,
            cert_common_name=kwargs.get("cert_common_name"),
            verify_ssl=kwargs.get("verify_ssl", True),
            cert=kwargs.get("cert"),
            params=params,
        )

    def _create_query_params(self, **kwargs):
        query_params = dict()
        for param in self.get_resource_base_query_params():
            if kwargs.get(param):
                query_params[param] = kwargs[param]

        return query_params

    def get_by_display_name(self, url, username, password, display_name, **kwargs):

        results = list()
        page_cursor = None

        while True:
            response_page = self.get(url, username, password, **kwargs, cursor=page_cursor)

            # check if error dictionary is returned
            if "error" in response_page:
                return response_page

            # add all the result from paginated response with given display name to list
            for result in response_page["results"]:
                if result.get("display_name") and result["display_name"] == display_name:
                    results.append(result)

            # if cursor is not present then we are on the last page, end loop
            if "cursor" not in response_page:
                break
            # updated query parameter with cursor
            page_cursor = response_page["cursor"]

        return {"results": results}

    def get_by_display_name_or_id(self, url):

        results = list()
        page_cursor = None

        while True:
            response_page = self.get(
                url,
                username=self.nsx_resource_params.get("username"),
                password=self.nsx_resource_params.get("password"),
                cert=self.nsx_resource_params.get("cert"),
                cert_common_name=self.nsx_resource_params.get("cert_common_name"),
                verify_ssl=self.nsx_resource_params.get("verify_ssl"),
                cursor=page_cursor,
            )

            # check if error dictionary is returned
            if "error" in response_page:
                return response_page

            # filter support based on the display name
            display_name = self.resource_params["display_name"]
            id = self.resource_params["id"]
            if display_name is not None:
                results.extend(
                    result
                    for result in response_page.get("results", [response_page])
                    if result.get("display_name") == display_name
                )

            else:
                results.extend(
                    result
                    for result in response_page.get("results", [response_page])
                    if result.get("id") == id
                )

            # if cursor is not present then we are on the last page, end loop
            if "cursor" not in response_page:
                break
            # updated query parameter with cursor
            page_cursor = response_page["cursor"]

        return {"results": results}

    def get_id_using_display_name(self, url, display_name):
        results = self.get_by_display_name(
            url=url,
            username=self.nsx_resource_params.get("username"),
            password=self.nsx_resource_params.get("password"),
            display_name=display_name,
            cert=self.nsx_resource_params.get("cert"),
            cert_common_name=self.nsx_resource_params.get("cert_common_name"),
            verify_ssl=self.nsx_resource_params.get("verify_ssl"),
        )

        if "error" in results:
            raise SaltInvocationError(
                {"resourceType": self.get_spec_identifier(), "error": results["error"]}
            )

        if not results or len(results.get("results")) == 0:
            raise SaltInvocationError(
                {
                    "resourceType": self.get_spec_identifier(),
                    "error": "No object found with display name {} at path {}".format(
                        display_name, url
                    ),
                }
            )

        if len(results.get("results", [])) > 1:
            raise SaltInvocationError(
                {
                    "resourceType": self.get_spec_identifier(),
                    "error": "Multiple objects found with display name {} at path {}, please provide id".format(
                        display_name, url
                    ),
                }
            )

        return results["results"][0]["id"]

    def create_or_update(
        self,
        hostname,
        username,
        password,
        cert=None,
        cert_common_name=None,
        verify_ssl=True,
        execution_logs=[],
        **kwargs
    ):
        # must call this method for creation of resource and sub-resources

        self.resource_class = self.__class__

        self.nsx_resource_params = self._set_nsx_resource_params(
            hostname=hostname,
            username=username,
            password=password,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
        )

        self._save(execution_logs, **kwargs)

    @staticmethod
    def get_nsxt_base_url():
        return "https://{}/policy/api/v1"

    def _save(self, execution_logs, **kwargs):
        self.update_resource_params(**kwargs)

        if self.multi_resource_params and len(self.multi_resource_params) > 0:
            for param in self.multi_resource_params:
                self.resource_params = param

                if self.create_or_update_subresource_first(**kwargs):
                    self._patch_subresource(execution_logs, **kwargs)

                is_update = False

                if not hasattr(self, "_parent_info"):
                    self._parent_info = {}
                self.update_parent_info(self._parent_info)

                url = (
                    NSXTPolicyBaseResource.get_nsxt_base_url()
                    + self.get_resource_base_url(self.get_parent_info())
                ).format(self.nsx_resource_params["hostname"])

                get_by_display_name_response = self.get_by_display_name_or_id(url)

                if get_by_display_name_response and "error" in get_by_display_name_response:
                    raise SaltInvocationError(
                        {
                            "resourceType": self.get_spec_identifier(),
                            "error": get_by_display_name_response["error"],
                        }
                    )

                existing_resource = get_by_display_name_response["results"]

                if len(existing_resource) > 1:
                    raise SaltInvocationError(
                        {
                            "resourceType": self.get_spec_identifier(),
                            "error": "More then one resource exist with same name",
                        }
                    )
                else:
                    self.existing_resource_param = (
                        existing_resource[0] if len(existing_resource) > 0 else None
                    )

                if self.existing_resource_param is not None:
                    # If user had specified state as delete for a particular resource it will delete the resource
                    # This flow will not be called for the base resource tier0
                    if (
                        self.resource_params.get("state")
                        and self.resource_params["state"] == "absent"
                    ):
                        self.delete(
                            self.nsx_resource_params["hostname"],
                            self.nsx_resource_params["username"],
                            self.nsx_resource_params["password"],
                            self.existing_resource_param["id"],
                            self.nsx_resource_params.get("cert"),
                            self.nsx_resource_params.get("cert_common_name"),
                            self.nsx_resource_params.get("verify_ssl"),
                            execution_logs,
                        )
                        continue
                    self._fill_missing_resource_params(
                        self.existing_resource_param, self.resource_params
                    )
                    is_update = self._check_for_update(
                        self.existing_resource_param, self.resource_params
                    )
                    if not is_update and not self.create_or_update_subresource_first(**kwargs):
                        self._patch_subresource(execution_logs, **kwargs)
                        continue

                response = self._patch_resource(**kwargs)
                if response:
                    spec_identifier = self.get_spec_identifier()
                    execution_logs.append({"resourceType": spec_identifier, "results": response})

                if not self.create_or_update_subresource_first(**kwargs):
                    self._patch_subresource(execution_logs, **kwargs)

    def _patch_resource(self, **kwargs):

        if not hasattr(self, "_parent_info"):
            self._parent_info = {}
        self.update_parent_info(self._parent_info)

        url = (
            NSXTPolicyBaseResource.get_nsxt_base_url()
            + self.get_resource_base_url(self.get_parent_info())
        ).format(self.nsx_resource_params["hostname"])
        response = self._send_request_to_API(
            resource_base_url=url,
            suffix="/" + self.resource_params["id"],
            method="PATCH",
            data=self.resource_params,
        )

        if response and "error" in response:
            raise SaltInvocationError(
                {"resourceType": self.get_spec_identifier(), "error": response["error"]}
            )

        response = self._send_request_to_API(
            resource_base_url=url, suffix="/" + self.resource_params["id"], method="GET", data=None
        )

        if response and "error" in response:
            raise SaltInvocationError(
                {"resourceType": self.get_spec_identifier(), "error": response["error"]}
            )

        return response

    def update_resource_params(self, resource_params):
        # Can be used to updates the params of resource before making
        # the API call.
        # Should be overridden in the subclass if needed
        pass

    def is_object_deletable(self):
        return True

    def _update_parent_info(self):
        # This update is always performed and should not be overriden by the
        # subresource's class
        self._parent_info["_parent"] = self

    def _patch_subresource(self, execution_logs, **kwargs):
        my_parent = self._parent_info.get("_parent", "")
        self._update_parent_info()
        for sub_resource_class in self._get_sub_resources_class_of(self.resource_class):
            sub_resource = sub_resource_class()
            sub_resource.set_parent_info(self._parent_info)

            sub_resource.create_or_update(
                self.nsx_resource_params["hostname"],
                self.nsx_resource_params["username"],
                self.nsx_resource_params["password"],
                self.nsx_resource_params.get("cert"),
                self.nsx_resource_params.get("cert_common_name"),
                self.nsx_resource_params.get("verify_ssl"),
                execution_logs,
                **kwargs
            )

        self._parent_info["_parent"] = my_parent

    def _get_nsx_access_argument_spec(self):
        return {
            "hostname": {"type": "str", "required": True},
            "username": {"type": "str", "required": True},
            "password": {"type": "str", "required": True},
            "verify_ssl": {"type": "bool", "requried": False, "default": True},
            "cert": {"type": "str", "required": False},
            "cert_common_name": {"type": "str", "required": False},
        }

    def _get_sub_resources_class_of(self, resource_class):
        subresources = []
        for attr in resource_class.__dict__.values():
            if inspect.isclass(attr) and issubclass(attr, NSXTPolicyBaseResource):
                subresources.append(attr)

        # TODO: if update then make reverse as false
        subresources.sort(
            key=lambda subresource: subresource().get_resource_update_priority(), reverse=True
        )
        for subresource in subresources:
            yield subresource

    def _set_nsx_resource_params(self, **resource_params):
        filtered_params = {}

        def filter_with_spec(spec):
            for key in spec.keys():
                if key in resource_params and resource_params[key] is not None:
                    filtered_params[key] = resource_params[key]

        filter_with_spec(self._get_nsx_access_argument_spec())
        return filtered_params

    def update_parent_info(self, parent_info):
        # Override this and fill in self._parent_info if that is to be passed
        # to the sub-resource
        # By default, parent's id is passed
        parent_info[self.get_spec_identifier() + "_id"] = self.resource_params.get("id")

    def _send_request_to_API(
        self,
        suffix="",
        ignore_error=False,
        method="GET",
        data=None,
        resource_base_url=None,
        accepted_error_codes=set(),
    ):

        response = nsxt_request.call_api(
            method,
            resource_base_url + suffix,
            self.nsx_resource_params.get("username"),
            self.nsx_resource_params.get("password"),
            self.nsx_resource_params.get("cert_common_name"),
            self.nsx_resource_params.get("verify_ssl"),
            self.nsx_resource_params.get("cert"),
            data,
            None,
        )
        return response

    @classmethod
    def get_spec_identifier(cls):
        # Can be overriden in the subclass to provide different
        # unique_arg_identifier. It is used to infer which args belong to which
        # subresource.
        # By default, class name is used for subresources.
        return cls.get_resource_name()

    def get_parent_info(self):
        return self._parent_info

    def get_resource_base_query_params(self):
        return ()

    @staticmethod
    @abstractmethod
    def get_resource_base_url(parent_info):
        # Must be overridden by the subclass
        raise NotImplementedError

    @classmethod
    def get_resource_name(cls):
        return cls.__name__

    def create_or_update_subresource_first(self, **kwargs):
        # return True if subresource should be created/updated before parent
        # resource
        return kwargs.get("create_or_update_subresource_first", False)

    @staticmethod
    def get_resource_update_priority():
        # this priority can be used to create/delete subresources
        # at the same level in a particular order.
        # by default, it returns 1 so the resources are created/updated/
        # deleted in a fixed but random order.
        # should be overloaded in subclass to specify its priority.
        # for creation or update, we iterate in descending order.
        # for deletion, we iterate in ascending order.
        return 1

    def set_parent_info(self, parent_info):
        self._parent_info = parent_info

    def delete(
        self,
        hostname,
        username,
        password,
        resource_id,
        cert=None,
        cert_common_name=None,
        verify_ssl=True,
        execution_logs=[],
    ):

        self.resource_class = self.__class__

        self.nsx_resource_params = self._set_nsx_resource_params(
            hostname=hostname,
            username=username,
            password=password,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
        )

        self._delete_resource_with_id(execution_logs, resource_id)

    def _delete_resource_with_id(self, execution_logs, resource_id):
        if not hasattr(self, "_parent_info"):
            self._parent_info = {}
        self._parent_info[self.get_spec_identifier() + "_id"] = resource_id

        self._delete_sub_resources(execution_logs)

        if self.is_object_deletable():
            url = (
                NSXTPolicyBaseResource.get_nsxt_base_url()
                + self.get_resource_base_url(self.get_parent_info())
            ).format(self.nsx_resource_params["hostname"])
            response = self._send_request_to_API(
                resource_base_url=url, suffix="/" + resource_id, method="DELETE"
            )
            if response and "error" in response:
                raise SaltInvocationError(
                    {"resourceType": self.get_spec_identifier(), "error": response["error"]}
                )
            execution_logs.append(
                {
                    "resourceType": self.get_spec_identifier(),
                    "results": "{} deleted successfully".format(resource_id),
                }
            )

    def _delete_sub_resources(self, execution_logs):
        for sub_resource_class in self._get_sub_resources_class_of(self.resource_class):
            sub_resource = sub_resource_class()
            sub_resource.set_parent_info(self._parent_info)

            url = (
                NSXTPolicyBaseResource.get_nsxt_base_url()
                + sub_resource.get_resource_base_url(self.get_parent_info())
            ).format(self.nsx_resource_params["hostname"])
            response = self._send_request_to_API(resource_base_url=url, suffix="", method="GET")
            if "error" in response:
                raise SaltInvocationError(
                    {"resourceType": sub_resource.get_spec_identifier(), "error": response["error"]}
                )
            if "results" in response:
                for resource in response["results"]:
                    sub_resource.delete(
                        self.nsx_resource_params["hostname"],
                        self.nsx_resource_params["username"],
                        self.nsx_resource_params["password"],
                        resource["id"],
                        self.nsx_resource_params.get("cert"),
                        self.nsx_resource_params.get("cert_common_name"),
                        self.nsx_resource_params.get("verify_ssl"),
                        execution_logs,
                    )
            else:
                sub_resource.delete(
                    self.nsx_resource_params["hostname"],
                    self.nsx_resource_params["username"],
                    self.nsx_resource_params["password"],
                    "bgp",
                    self.nsx_resource_params.get("cert"),
                    self.nsx_resource_params.get("cert_common_name"),
                    self.nsx_resource_params.get("verify_ssl"),
                    execution_logs,
                )

    def get_hierarchy(
        self,
        hostname,
        username,
        password,
        resource_id,
        cert=None,
        cert_common_name=None,
        verify_ssl=True,
        result={},
    ):
        self.resource_class = self.__class__

        self.nsx_resource_params = self._set_nsx_resource_params(
            hostname=hostname,
            username=username,
            password=password,
            cert=cert,
            cert_common_name=cert_common_name,
            verify_ssl=verify_ssl,
        )
        self._get_hierarchy(resource_id, result)

    def _get_hierarchy(self, resource_id, result):
        if not hasattr(self, "_parent_info"):
            self._parent_info = {}
        self._parent_info[self.get_spec_identifier() + "_id"] = resource_id

        url = (
            NSXTPolicyBaseResource.get_nsxt_base_url()
            + self.get_resource_base_url(self.get_parent_info())
        ).format(self.nsx_resource_params["hostname"])

        response = self._send_request_to_API(
            resource_base_url=url, suffix="/" + resource_id, method="GET", data=None
        )

        if response and "error" in response:
            raise SaltInvocationError(response["error"])

        if self.get_spec_identifier() not in result:
            result[self.get_spec_identifier()] = response
        else:
            children = []
            children.append(result[self.get_spec_identifier()])
            children.append(response)
            result[self.get_spec_identifier()] = children

        self._get_child_hierarchy(response)

    def _get_child_hierarchy(self, result):
        for sub_resource_class in self._get_sub_resources_class_of(self.resource_class):
            sub_resource = sub_resource_class()
            sub_resource.set_parent_info(self._parent_info)

            url = (
                NSXTPolicyBaseResource.get_nsxt_base_url()
                + sub_resource.get_resource_base_url(self.get_parent_info())
            ).format(self.nsx_resource_params["hostname"])
            response = self._send_request_to_API(resource_base_url=url, suffix="", method="GET")
            if response and "error" in response:
                raise SaltInvocationError(
                    "Failure while querying {}: {}".format(
                        sub_resource.get_spec_identifier(), response["error"]
                    )
                )
            if "results" in response:
                for resource in response["results"]:
                    sub_resource.get_hierarchy(
                        self.nsx_resource_params["hostname"],
                        self.nsx_resource_params["username"],
                        self.nsx_resource_params["password"],
                        resource["id"],
                        self.nsx_resource_params.get("cert"),
                        self.nsx_resource_params.get("cert_common_name"),
                        self.nsx_resource_params.get("verify_ssl"),
                        result,
                    )
            else:
                sub_resource.get_hierarchy(
                    self.nsx_resource_params["hostname"],
                    self.nsx_resource_params["username"],
                    self.nsx_resource_params["password"],
                    "bgp",
                    self.nsx_resource_params.get("cert"),
                    self.nsx_resource_params.get("cert_common_name"),
                    self.nsx_resource_params.get("verify_ssl"),
                    result,
                )

    def _check_for_update(self, existing_params, resource_params):
        diff = salt.utils.dictdiffer.deep_diff(existing_params, resource_params)
        return bool(diff)

    def _fill_missing_resource_params(self, existing_params, resource_params):
        """
        resource_params: dict
        existing_params: dict

        Fills resource_params with the key:value from existing_params if
        missing in the former.
        """
        if not existing_params:
            return
        for k, v in existing_params.items():
            if k not in resource_params:
                resource_params[k] = v
            elif isinstance(v, dict):
                self._fill_missing_resource_params(v, resource_params[k])
