import colander
import deform
from knappe.response import Response
from knappe_deform import FormPage, trigger, form_template
from jsonschema_colander.types import Object
from reha.models.user import User
from knappe.decorators import html
from reha.app.security import PasswordManager
from bson.objectid import ObjectId
from . import router, actions


def validate_unique(name):
    def validator(node, value, **kwargs):
        request = node.bindings["request"]
        user = request.app.models['user']
        collection = request.app.dbconn.database[user.table]
        found = collection.count_documents({name: value})
        if found:
            raise colander.Invalid(
                node, f'{name} {value!r} already in use.')
    return validator


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


@actions.register(
    User, "edit_user",
    title="Edit",
    classifiers=('listing',)
)
def edit_user(request, item):
    return request.script_name + request.app.route_url(
        "user.edit", objectid=item.id
    )


@router.register('/user.add', name="user.add")
class AddUserForm(FormPage):

    def get_schema(self, request):
        modelinfo = request.app.models['user']
        schema = Object.from_json(
            modelinfo.schema.json,
            config={
                '': {
                    'exclude': {
                        'annotation',
                        'state',
                        'creation_date',
                        'salt',
                        '_id',
                        'preferences',
                    }
                },
                'email': {
                    'validators': [validate_unique('email')],
                },
                'loginname': {
                    'validators': [validate_unique('loginname')],
                }
            }
        )
        return schema()

    @trigger('cancel', title="Cancel", order=2)
    def cancel(self, request):
        return Response.redirect('/')

    @trigger('add', title="Add", order=1)
    def add(self, request):
        try:
            data = self.get_initial_data(request)
            form = self.get_form(request, data)
            appstruct = form.validate(request.data.form)
            password_manager = PasswordManager()
            user = request.app.models['user']
            collection = request.app.dbconn.database[user.table]
            result_id = collection.insert_one({
                **appstruct,
                'password': password_manager.create(appstruct["password"])
            }).inserted_id
            return Response.redirect('/')
        except deform.exception.ValidationFailure as e:
            return {
                "error": None,
                "rendered_form": e.render()
            }


@router.register('/user/{objectid}/edit', name="user.edit")
class EditUserForm(FormPage):

    def get_initial_data(self, request, modelinfo):
        collection = request.app.dbconn.database[modelinfo.table]
        data = collection.find_one({
            '_id': ObjectId(request.params['objectid'])
        })
        data['_id'] = str(data['_id'])
        return data

    def get_modelinfo(self, request):
        return request.app.models['user']

    def get_schema(self, jsonschema):
        schema = Object.from_json(
            jsonschema,
            config={
                '': {
                    'exclude': {
                        'annotation',
                        'salt',
                        'preferences',
                    }
                },
                'email': {
                    'validators': [validate_unique('email')],
                },
                '_id': { 'readonly': True },
                'loginname': { 'readonly': True },
                'state': { 'readonly': True },
                'creation_date': { 'readonly': True },
            }
        )
        return schema()

    def get_form(self, request, modelinfo, data=None) -> deform.form.Form:
        """Returns a form
        """
        schema = self.get_schema(modelinfo.schema.json)
        bound = schema.bind(request=request, data=data)
        form = deform.form.Form(bound, buttons=self.buttons)
        return form

    @html('form', default_template=form_template)
    def GET(self, request) -> dict:
        modelinfo = self.get_modelinfo(request)
        data = self.get_initial_data(request, modelinfo)
        form = self.get_form(request, modelinfo, data=data)
        return {
            "error": None,
            "rendered_form": form.render(data)
        }

    @trigger('cancel', title="Cancel", order=2)
    def cancel(self, request):
        return Response.redirect('/')

    @trigger('edit', title="Edit", order=1)
    def edit(self, request):
        try:
            modelinfo = self.get_modelinfo(request)
            data = self.get_initial_data(request, modelinfo)
            form = self.get_form(request, modelinfo, data=data)
            appstruct = form.validate(request.data.form)
            password_manager = PasswordManager()
            collection = request.app.dbconn.database[user.table]
            result_id = collection.update_one({
                **appstruct,
                'password': password_manager.create(appstruct["password"])
            }).inserted_id
            return Response.redirect('/')
        except deform.exception.ValidationFailure as e:
            return {
                "error": None,
                "rendered_form": e.render()
            }
