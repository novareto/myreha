import logging
from functools import wraps
from horseman.response import Response
from roughrider.cors.policy import CORSPolicy


Logger = logging.getLogger(__name__)


DEFAULT_CORS_POLICY = CORSPolicy(
    credentials=True,
    allow_headers=["Authorization", "Content-Type"]
)


class CORS:

    def __init__(self, policy: CORSPolicy = DEFAULT_CORS_POLICY):
        self.policy = policy

    def __call__(self, handler):
        @wraps(handler)
        def cors_filter(app, path, environ):
            if environ['REQUEST_METHOD'] != 'OPTIONS':
                response = handler(app, path, environ)
                if isinstance(response, Response) and \
                   not 'Access-Control-Allow-Origin' in response.headers:
                    response.headers[
                        'Access-Control-Allow-Origin'
                    ] = self.policy.origin
                return response

            Logger.debug(
                f'Request intercepted. Applying policy {self.policy}.')
            found, params = app.router.match(path)
            if found is None:
                return Response(404)
            policy = self.policy._replace(methods=set(found.keys()))
            headers = policy.preflight(
                origin=environ.get('HTTP_ORIGIN'),
                acr_method=environ.get(
                    'HTTP_ACCESS_CONTROL_REQUEST_METHOD'),
                acr_headers=environ.get(
                    'HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
            )
            return Response(200, headers=headers)
        return cors_filter
