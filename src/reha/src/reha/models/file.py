import typing as t
from datetime import datetime
from pydantic import Field
from pymongo import IndexModel, DESCENDING
from reha.app.models import ObjectId, Model
from . import models


@models.register(
    'file',
    indexes=(IndexModel([("az", DESCENDING)], unique=True),)
)
class File(Model):

    user: ObjectId = Field(
        ...,
        title="Personen-ID aus der Fachanwendung",
    )

    az: str = Field(
        ...,
        title="Aktenzeichen",
    )

    mnr: str = Field(
        ...,
        title="Mitgliedsnummer zu diesem Versicherungsfall",
    )

    vid: str = Field(
        ...,
        title="Versichertenfall-ID (intern)",
    )

    state: t.Optional[str] = Field(
        default=None,
    )

    @property
    def title(self):
        return f"File({self.az}, {self.uid!r})"

    def __repr__(self):
        return self.title
