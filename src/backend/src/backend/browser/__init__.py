from knappe.actions import Actions
from knappe.routing import Router
from knappe.blueprint import Blueprint


router: Blueprint[Router] = Blueprint(Router)
actions: Blueprint[Actions] = Blueprint(Actions)


from . import app, users
