import logging
from horseman.response import Response, Headers


Logger = logging.getLogger(__name__)


def cors_headers(policy, environ) -> Headers:
    origin = environ.get('HTTP_ORIGIN')
    acr_method = environ.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD')
    acr_headers = environ.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
    return policy.preflight(
        origin=origin,
        acr_method=acr_method,
        acr_headers=acr_headers
    )
