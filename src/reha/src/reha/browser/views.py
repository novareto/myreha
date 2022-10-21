from knappe.response import Response
from . import router


@router.register('/')
def index(request):
    return Response.html(200, body="I am an index")
