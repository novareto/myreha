from knappe.events import Event
from knappe.types import Request


class RequestEvent(Event):
    request: Request

    def __init__(self, request):
        self.request = request


class RequestCreatedEvent(RequestEvent):
    pass
