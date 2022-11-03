from knappe.response import Response
from knappe.meta import HTTPMethodEndpointMeta
from reha.app.validation import json_validate
from pydantic import BaseModel
from . import router


@router.register('/users/schema')
def user_schema(request):
    import json
    print(json.dumps(request.app.models['user'].schema.json, indent=4))
    return Response.from_json(
        200, body=request.app.models['user'].schema)


@router.register('/users')
def list_users(request):
    user = request.app.models['user']
    collection = request.app.dbconn.database[user.table]
    items = ','.join((user.model(**d).json() for d in collection.find()))
    return Response.from_json(200, body=f'[{items}]')
