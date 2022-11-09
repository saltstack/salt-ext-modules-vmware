CSP_AUTHORIZATION_URL = "csp/gateway/am/api/auth/api-tokens/authorize"
HTTPS_URL_PREFIX = "https://"
URL_SUFFIX = "/"
REFRESH_TOKEN = "refresh_token"
CONTENT_TYPE = "Content-Type"
ACCESS_TOKEN = "access_token"
APPLICATION_JSON = "application/json"
APPLICATION_URLENCODED = "application/x-www-form-urlencoded"
CSP_AUTH_TOKEN = "csp-auth-token"
ERROR = "error"
ERROR_MSG = "error_message"
ERROR_MSGS = "error_messages"
NO_CERTIFICATE_ERROR_MSG = (
    "No certificate path specified. Please specify certificate path in cert parameter"
)
HTTP_ERROR_MSG = (
    "HTTP Error occurred while calling VMC API {} for {}. Please check logs for more details."
)
SSL_ERROR_MSG = (
    "SSL Error occurred while calling VMC API {} for {}. Please check if the certificate is valid "
    "and hostname matches certificate common name."
)
REQUEST_EXCEPTION_MSG = (
    "RequestException occurred while calling VMC API {} for {}. Please check logs for more details."
)
PARSE_ERROR_MSG = "Couldn't parse the response as json. Returning response text as error message"
PATCH_REQUEST_METHOD = "patch"
GET_REQUEST_METHOD = "get"
DELETE_REQUEST_METHOD = "delete"
POST_REQUEST_METHOD = "post"
PUT_REQUEST_METHOD = "put"
VERIFY_SSL = "verify_ssl"
CERT = "cert"
SERVER = "server"
RELAY = "relay"
DHCP_SERVER_CONFIGS = "dhcp-server-configs"
DHCP_RELAY_CONFIGS = "dhcp-relay-configs"
VCENTER_API_SESSION_URL = "api/session"
VMWARE_API_SESSION_ID = "vmware-api-session-id"
VPN_ERROR_SPECIFY_ONE = "Specify either tier0_id or tier1_id, specify only one at a time"
VPN_ERROR_SPECIFY_ATLEAST_ONE = "Specify either tier0_id or tier1_id, specify atleast one value"
VMC_NONE = "USER_DEFINED_NONE"
DHCP_CONFIGS = "dhcp-{}-configs"
