import colander
import deform
from knappe.response import Response
from knappe.decorators import html
from knappe_deform import FormPage, trigger
from jsonschema_colander import schema_fields
from . import router


@router.register("/")
@html('listing')
def index(request):
    users = []
    return {
        'users': [user for user in users if user.title.startswith(query)]
    }


@router.register("/", methods=('POST',))
def search(request):
    data = self.request.extract()
    query = data.form.get('search')
    users = self.get_users(query)
    return self.request.app.ui.render_template(
        PageTemplate('<div metal:use-macro="macros.listing" />'),
        self.request,
        brains=users,
        listing_title=query and f"Users (search for {query})" or "Users"
    )



def validate_unique_loginname(node, value, **kwargs):
    request = node.bindings["request"]
    db = request.app.dbconn
    User = request.app.models['user']
    import pdb
    pdb.set_trace()


@router.register('/user.add')
class AddUserForm(FormPage):

    def get_form(self, request, modelinfo=None) -> deform.form.Form:
        if modelinfo is None:
            modelinfo = request.app.models['user']
        schema = schema_fields(modelinfo.schema.json)().bind(request=request)
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
            print(collection.insert_one(appstruct).inserted_id)
        except deform.exception.ValidationFailure as e:
            return {
                "error": None,
                "rendered_form": e.render()
            }
