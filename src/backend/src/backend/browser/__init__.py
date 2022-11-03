from knappe.routing import Router
from knappe.blueprint import Blueprint


router: Blueprint[Router] = Blueprint(Router)


from . import login, users
