import typing as t
from dataclasses import dataclass, field
from horseman.mapping import RootNode
from roughrider.cors.policy import CORSPolicy
from knappe.pipeline import Pipeline, Middleware
from knappe.routing import Router
from knappe.events import Subscribers
from knappe.actions import Actions, ContextualActions
from knappe.request import RoutingRequest as Request
from knappe.response import Response
from roughrider.cors.policy import CORSPolicy
from .models import Models
from .cors import cors_headers
from .database import DatabaseConnection
from .lifecycle import RequestCreatedEvent


@dataclass
class Application(RootNode):
    dbconn: DatabaseConnection
    models: Models = field(default_factory=Models)
    router: Router = field(default_factory=Router)
    middlewares: t.Iterable[Middleware] = field(default_factory=tuple)
    subscribers: Subscribers = field(default_factory=Subscribers)
    actions: Actions = field(default_factory=Actions)

    def __post_init__(self, middlewares=()):
        self.pipeline: Pipeline[Request, Response] = Pipeline(
            self.middlewares
        )
        self.cors_policy = CORSPolicy(
            credentials=True,
            allow_headers=["Authorization", "Content-Type"]
        )

    def route_url(self, name, **params) -> t.Optional[str]:
        if self.router.has_route(name):
            return self.router.url_for(name, **params)

    def resolve(self, path, environ):
        if environ['REQUEST_METHOD'] == 'OPTIONS':
            found, params = self.router.match(path)
            if found is None:
                return Response(404)
            policy = self.cors_policy._replace(methods=set(found.keys()))
            return Response(200, headers=cors_headers(policy, environ))

        endpoint = self.router.match_method(path, environ['REQUEST_METHOD'])
        request = Request(
            environ,
            app=self,
            endpoint=endpoint,
        )
        response = self.pipeline(endpoint.handler)(request)
        if isinstance(response, Response) and \
           not 'Access-Control-Allow-Origin' in response.headers:
            response.headers[
                'Access-Control-Allow-Origin'] = self.cors_policy.origin

        return response
