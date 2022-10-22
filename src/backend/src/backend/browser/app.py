from knappe.response import Response
from knappe.decorators import html
from knappe_deform import FormPage, trigger
from prejudice.errors import ConstraintError
from reha.app import Application
from . import router, actions


def authenticated(action, request, context):
    if request.context.get('user') is None:
        raise ConstraintError('Anonymous user forbidden.')


@actions.register(
    Application, "new_user",
    title="Add a new user",
    classifiers=('content',),
    conditions=(authenticated,),
    attributes=(("css", "bi-file-earmark-plus"),))
def add_user(request, item):
    return request.script_name + item.route_url("user.add")


@router.register("/")
@html('listing')
def index(request):
    user = request.app.models['user']
    collection = request.app.dbconn.database[user.table]
    return {
        'request': request,
        'actions': request.context['actions'],
        'items': (user.model(**d) for d in collection.find()),
        'listing_title': 'Users'
    }


@router.register("/", methods=('POST',))
def search(request):
    pass
