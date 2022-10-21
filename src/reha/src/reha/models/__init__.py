from reha.app.models import Models
from knappe.blueprint import Blueprint


models: Blueprint[Models] = Blueprint(Models)


from . import document, user, file
