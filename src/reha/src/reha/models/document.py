import typing as t
from datetime import datetime
from pydantic import BaseModel, Field
from . import ObjectId


class Document(BaseModel):

    id: ObjectId = Field(
        alias="_id",
        default_factory=ObjectId,
    )

    az: ObjectId = Field(
        ...,
        title="Aktenzeichen",
    )

    user: ObjectId = Field(
        ...,
        title="Personen-ID aus der Fachanwendung",
    )

    state: t.Optional[str] = Field(
        default=None,
    )

    creation_date: t.Optional[datetime] = Field(
        default_factory=datetime.now,
        title="Erstelldatum"
    )

    content_type: t.Optional[str] = None
    item: t.Optional[t.Dict] = None
    annotation: t.Optional[t.Dict] = None

    @property
    def title(self):
        return f"{self.content_type}"

    def __repr__(self):
        return f"Document({self.docid}, {self.content_type!r})"

    def __post_init__(self):
        if self.creation_date is None:
            self.creation_date = datetime.now()
