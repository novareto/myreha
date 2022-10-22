import colander
import deform
from knappe.response import Response
from knappe.decorators import html
from knappe_deform import FormPage, trigger
from jsonschema_colander import schema_fields
from reha.models.user import User
from . import router, actions


def validate_unique_loginname(node, value, **kwargs):
    request = node.bindings["request"]
    db = request.app.dbconn
    User = request.app.models['user']
    import pdb
    pdb.set_trace()


@router.register('/user/{objectid}', name="user.view")
def user_view(request):
    return Response(200, body='I am a user')


@actions.register(
    User, "view_user",
    title="View",
    classifiers=('listing',)
)
def view_user(request, item):
    return request.script_name + request.app.route_url(
        "user.view", objectid=item.id
    )


@router.register('/user.add', name="user.add")
class AddUserForm(FormPage):

    def get_form(self, request, modelinfo=None) -> deform.form.Form:
        if modelinfo is None:
            modelinfo = request.app.models['user']
        schema = schema_fields(
            modelinfo.schema.json,
            exclude=(
                'annotation',
                'state',
                'creation_date',
                'salt',
                '_id',
                'preferences',
            )
        )().bind(request=request)
        return deform.form.Form(schema, buttons=self.buttons)

    @trigger('cancel', title="Cancel", order=2)
    def cancel(self, request):
        return Response.redirect('/')

    @trigger('add', title="Add", order=1)
    def add(self, request):
        try:
            user = request.app.models['user']
            form = self.get_form(request, modelinfo=user)
            appstruct = form.validate(request.data.form)
            collection = request.app.dbconn.database[user.table]
            result_id = collection.insert_one(appstruct).inserted_id
            return Response.redirect('/')
        except deform.exception.ValidationFailure as e:
            return {
                "error": None,
                "rendered_form": e.render()
            }
