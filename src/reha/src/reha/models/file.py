import typing as t
from datetime import datetime
from pydantic import BaseModel, Field
from . import ObjectId


class File(BaseModel):

    id: ObjectId = Field(
        alias="_id",
        default_factory=ObjectId,
    )

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

    creation_date: t.Optional[datetime] = Field(
        default_factory=datetime.now,
        title="Erstelldatum"
    )

    annotation: t.Optional[t.Dict] = None

    @property
    def title(self):
        return f"File({self.az}, {self.uid!r})"

    def __repr__(self):
        return self.title
