import wrapt
import typing as t
from http import HTTPStatus
from horseman.types import MIMEType, HTTPCode
from knappe.response import Response
from horseman.exceptions import HTTPError
from pydantic import BaseModel, ValidationError
from .models import JSONType


class JSONError(Exception):

    def __init__(self,
                 status: HTTPCode,
                 body: JSONType):
        self.status = HTTPStatus(status)
        self.body = body

    def to_response(self):
        return Response.from_json(self.status, body=self.body)


class JSONModelValidator:

    def __init__(self,
                 model: t.Type[BaseModel],
                 accepted: t.Sequence[MIMEType] = ('application/json',)):
        self.model = model
        self.accepted = accepted

    def validate(self, data: JSONType) -> BaseModel:
        try:
            return self.model.parse_obj(data)
        except ValidationError as e:
            raise JSONError(400, e.json())

    def from_request(self, request) -> BaseModel:
        if not request.content_type or \
           request.content_type.mimetype not in self.accepted:
            raise HTTPError(
                status=406,
                message=f'Expected content-type(s): {self.accepted}.'
            )
        return self.validate(request.data.json)

    @wrapt.decorator
    def __call__(self, wrapped, instance, args, kwargs):
        request = args[0]
        try:
            item = self.from_request(request)
        except JSONError as e:
            return e.to_response()
        return wrapped(*args, item=item, **kwargs)
