import colander
import deform
from knappe.response import Response
from knappe_deform import FormPage, trigger
from . import views


class LoginSchema(colander.Schema):

    username = colander.SchemaNode(
        colander.String(),
        title="Login")

    password = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.PasswordWidget(),
        title="Password",
        description="Your password")


@views.register('/login')
class Login(FormPage):

    schema = LoginSchema

    @trigger('cancel', title="Cancel")
    def cancel(self, request):
        return Response.redirect('/')

    @trigger('process', title="Process")
    def process_credentials(self, request):
        try:
            form = self.get_form(request)
            appstruct = form.validate(request.data.form)
            auth = request.context['authentication']
            user = auth.from_credentials(request, appstruct)
            if user is not None:
                auth.remember(request, user)
                return Response.redirect("/")

            return {
                "error": "Login failed.",
                "rendered_form": form.render()
            }
        except deform.exception.ValidationFailure as e:
            return {
                "error": None,
                "rendered_form": e.render()
            }
