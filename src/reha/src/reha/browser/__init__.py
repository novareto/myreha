from knappe.routing import Router
from knappe.blueprint import Blueprint


views: Blueprint[Router] = Blueprint(Router)
