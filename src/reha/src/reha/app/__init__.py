import typing as t
from dataclasses import dataclass, field
from horseman.mapping import RootNode
from knappe.pipeline import Pipeline, Middleware
from knappe.routing import Router
from knappe.events import Subscribers
from knappe.actions import Actions, ContextualActions
from knappe.request import RoutingRequest as Request
from knappe.response import Response
from .models import Models
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

    def route_url(self, name, **params) -> t.Optional[str]:
        if self.router.has_route(name):
            return self.router.url_for(name, **params)

    def resolve(self, path, environ):
        endpoint = self.router.match_method(path, environ['REQUEST_METHOD'])
        request = Request(
            environ,
            app=self,
            endpoint=endpoint,
        )
        request.context['actions'] = ContextualActions(
            request, self.actions
        )
        self.subscribers.notify(RequestCreatedEvent(request))
        return self.pipeline(endpoint.handler)(request)
