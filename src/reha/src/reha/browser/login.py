import colander
import deform
from knappe.response import Response
from knappe_deform import FormPage, trigger
from . import router


class LoginSchema(colander.Schema):

    username = colander.SchemaNode(
        colander.String(),
        title="Login")

    password = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.PasswordWidget(),
        title="Password",
        description="Your password")


@router.register('/login')
class Login(FormPage):

    def get_schema(self, request):
        return LoginSchema().bind(request=request)

    @trigger('cancel', title="Cancel", order=2)
    def cancel(self, request):
        return Response.redirect('/')

    @trigger('process', title="Process", order=1)
    def process_credentials(self, request):
        try:
            form = self.get_form(request)
            appstruct = form.validate(request.data.form)
            auth = request.context['authentication']
            user = auth.from_credentials(request, appstruct)
            if user is not None:
                auth.remember(request, user)
                return Response.redirect(request.script_name)

            return {
                "error": "Login failed.",
                "rendered_form": form.render()
            }
        except deform.exception.ValidationFailure as e:
            return {
                "error": None,
                "rendered_form": e.render()
            }
