import typing as t
import pathlib
from chameleon.zpt.loader import TemplateLoader
from chameleon.zpt.template import PageTemplateFile
from knappe.blueprint import Blueprint
from knappe.decorators import html
from knappe.events import Subscribers
from knappe.request import RoutingRequest as Request
from knappe.ui import SlotExpr, slot, UI, Layout
from reha.app.lifecycle import RequestCreatedEvent


subscribers: Blueprint[Subscribers] = Blueprint(Subscribers)


PageTemplateFile.expression_types['slot'] = SlotExpr


TEMPLATES = TemplateLoader(
    str(pathlib.Path(__file__).parent / "templates"),
    default_extension=".pt"
)


#@slot.register
#@html('header')
#def header(request: Request, view: t.Any, context: t.Any, name: t.Literal['header']):
#    return {'title': 'This is a header'}


BasicUI = UI(
    templates=TEMPLATES,
    layout=Layout(TEMPLATES['master']),
)


@subscribers.subscribe(RequestCreatedEvent)
def apply_theme(event):
    event.request.context['ui'] = BasicUI
