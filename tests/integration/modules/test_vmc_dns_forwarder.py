"""
    Integration Tests for vmc_dns_forwarder execution module
"""

import pytest
import requests
from saltext.vmware.utils import vmc_request


@pytest.fixture
def common_data(vmc_nsx_connect):
    hostname, refresh_key, authorization_host, org_id, sddc_id, verify_ssl, cert = vmc_nsx_connect
    data = {
        "hostname": hostname,
        "refresh_key": refresh_key,
        "authorization_host": authorization_host,
        "org_id": org_id,
        "sddc_id": sddc_id,
        "verify_ssl": verify_ssl,
        "cert": cert,
    }
    yield data


@pytest.fixture
def request_headers(common_data):
    return vmc_request.get_headers(common_data["refresh_key"], common_data["authorization_host"])


@pytest.fixture
def dns_zones_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/infra/dns-forwarder-zones"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
    )
    return api_url


@pytest.fixture
def dns_services_url(common_data):
    url = (
        "https://{hostname}/vmc/reverse-proxy/api/orgs/{org_id}/sddcs/{sddc_id}/"
        "policy/api/v1/search?query=resource_type:PolicyDnsForwarder"
    )
    api_url = url.format(
        hostname=common_data["hostname"],
        org_id=common_data["org_id"],
        sddc_id=common_data["sddc_id"],
    )
    return api_url


@pytest.fixture
def get_dns_zones(dns_zones_url, common_data, request_headers):
    return api_call(dns_zones_url, common_data, request_headers)


@pytest.fixture
def get_dns_services(dns_services_url, common_data, request_headers):
    return api_call(dns_services_url, common_data, request_headers)


def api_call(api_url, common_data, request_headers):
    session = requests.Session()
    response = session.get(
        url=api_url,
        verify=common_data["cert"] if common_data["verify_ssl"] else False,
        headers=request_headers,
    )
    response.raise_for_status()
    return response.json()


def test_get_dns_zones_smoke_test(salt_call_cli, get_dns_zones, common_data):
    ret = salt_call_cli.run("vmc_dns_forwarder.get_dns_zones", **common_data)
    result_as_json = ret.json
    assert result_as_json == get_dns_zones


def test_get_dns_services_smoke_test(salt_call_cli, get_dns_services, common_data):
    ret = salt_call_cli.run("vmc_dns_forwarder.get_dns_services", **common_data)
    result_as_json = ret.json
    assert result_as_json == get_dns_services
