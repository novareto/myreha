from knappe.response import Response
from knappe.meta import HTTPMethodEndpointMeta
from reha.app.validation import JSONModelValidator
from pydantic import BaseModel
from . import router


class User(BaseModel):
    username: str
    password: str


@router.register('/login')
class Login(metaclass=HTTPMethodEndpointMeta):

    def GET(self, request):
        schema = User.schema_json(indent=2)
        return Response.from_json(200, schema)

    @JSONModelValidator(User)
    def POST(self, request, item=None):
        auth = request.context['authentication']
        user = auth.from_credentials(request, item.dict())
        if user is not None:
            payload = {'user': user.id}
            jwt = auth.service.generate(payload)
            return Response.to_json(200, body={'token': jwt})
        return Response(403)
