import pytest
from saltext.vmware.utils import nsxt_request

hostname = ""
username = ""
password = ""
license_key = ""
_verify_ssl = False

BASE_URL = "https://{management_host}/api/v1/licenses"


@pytest.fixture(autouse=True)
def setup(nsxt_config):
    """
    This is called once for module
    It loads global values from config section
    """
    globals().update(nsxt_config)


@pytest.fixture
def delete_license():
    """
    Sets up test requirements:
    Queries nsx api for licenses
    Deletes license if exists
    """
    url = BASE_URL.format(management_host=hostname)
    licenses_dict = nsxt_request.call_api(
        method="GET", url=url, username=username, password=password, verify_ssl=_verify_ssl
    )

    if licenses_dict["result_count"] != 0:
        results = licenses_dict["results"]
        for result in results:
            if result["license_key"] == license_key:
                url = (BASE_URL + "?action=delete").format(management_host=hostname)
                data = {"license_key": license_key}

                response = nsxt_request.call_api(
                    method="POST",
                    url=url,
                    username=username,
                    password=password,
                    verify_ssl=_verify_ssl,
                    data=data,
                )

                assert "error" not in response


@pytest.fixture
def get_licenses():
    url = BASE_URL.format(management_host=hostname)
    response = nsxt_request.call_api(
        method="GET", url=url, username=username, password=password, verify_ssl=_verify_ssl
    )

    assert "error" not in response
    return response


@pytest.fixture
def create_license():
    url = BASE_URL.format(management_host=hostname)
    licenses_dict = nsxt_request.call_api(
        method="GET", url=url, username=username, password=password, verify_ssl=_verify_ssl
    )

    assert "error" not in licenses_dict

    if licenses_dict["result_count"] != 0:
        results = licenses_dict["results"]
        for result in results:
            if result["license_key"] == license_key:
                return
    url = BASE_URL.format(management_host=hostname)
    data = {"license_key": license_key}

    response = nsxt_request.call_api(
        method="POST",
        url=url,
        username=username,
        password=password,
        verify_ssl=_verify_ssl,
        data=data,
    )

    assert "error" not in response


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_apply_license(salt_call_cli, delete_license):
    ret = salt_call_cli.run(
        "nsxt_license.apply_license",
        hostname=hostname,
        username=username,
        password=password,
        license_key=license_key,
        verify_ssl=_verify_ssl,
    )
    assert ret
    result_as_json = ret.json
    assert result_as_json["license_key"] == license_key


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_get_licenses(salt_call_cli, get_licenses):
    ret = salt_call_cli.run(
        "nsxt_license.get_licenses",
        hostname=hostname,
        username=username,
        password=password,
        verify_ssl=_verify_ssl,
    )
    assert ret
    result_as_json = ret.json
    assert result_as_json == get_licenses


@pytest.mark.xfail(reason="nsxt tests not working yet")
def test_delete_license(salt_call_cli, create_license):
    ret = salt_call_cli.run(
        "nsxt_license.delete_license",
        hostname=hostname,
        username=username,
        password=password,
        license_key=license_key,
        verify_ssl=_verify_ssl,
    )
    assert ret
    result_as_json = ret.json
    assert result_as_json["message"] == "License deleted successfully"
