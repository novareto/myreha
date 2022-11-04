from knappe.response import Response
from reha.app.validation import JSONModelValidator, JSONError
from . import router


@router.register('/api/users/schema')
def user_schema(request):
    return Response.from_json(
        200, body=request.app.models['user'].schema)


@router.register('/api/users')
def list_users(request):
    user = request.app.models['user']
    collection = request.app.dbconn.database[user.table]
    items = ','.join((user.model(**d).json() for d in collection.find()))
    return Response.from_json(200, body=f'[{items}]')


@router.register('/api/users/{loginname}', methods=('PUT',))
def create_user(request):
    factory = request.app.models['user']
    validator = JSONModelValidator(factory.model)
    try:
        user = validator.from_request(request)
    except JSONError as err:
        return err.to_response()
    collection = request.app.dbconn.database[user.table]
    return Response.from_json(200, body=user.json())
