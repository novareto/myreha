import json
import typing as t
from pathlib import Path
from cromlech.jwt.components import TokenException, JWTHandler, JWTService
from knappe.response import Response
from jwcrypto import jwk
from knappe.types import Handler, RqT
from knappe.auth import Authenticator, Source, Credentials, User
from knappe.request import WSGIRequest


def options_method_filter(
        caller: Handler[WSGIRequest, Response], request: WSGIRequest):
    if request.method == 'OPTIONS':
        return caller(request)


def get_key(path: Path):
    if not path.is_file():
        with open(path, 'w+', encoding="utf-8") as keyfile:
            key = JWTHandler.generate_key()
            export = key.export()
            keyfile.write(export)
    else:
        with open(path, 'r', encoding="utf-8") as keyfile:
            data = json.loads(keyfile.read())
            key = jwk.JWK(**data)

    return key


def make_jwt_service(key, TTL=600):
    key = get_key(Path(key))
    return JWTService(key, JWTHandler, lifetime=TTL)


class JWTAuthenticator(
        Authenticator[WSGIRequest, t.Union[t.Mapping, str, bytes]]):

    sources: t.Iterable[
        Source[WSGIRequest, t.Union[t.Mapping, str, bytes]]
    ]

    def __init__(self,
                 service: JWTService,
                 sources: t.Iterable[Source[RqT, Credentials]],
                 context_key: str = 'user'):
        self.sources = sources
        self.service = service
        self.context_key = context_key

    def identify(self, request: WSGIRequest) -> t.Optional[User]:
        auth = request.get('HTTP_AUTHORIZATION')
        if auth:
            authtype, token = auth.split(' ', 1)
            if authtype.lower() == 'bearer':
                try:
                    payload = self.service.check_token(token)
                except (TokenException, ValueError) as err:
                    payload = None
                return payload

    def forget(self, request: WSGIRequest):
        pass

    def remember(self, request: WSGIRequest, user: User):
        request.context[self.context_key] = user
