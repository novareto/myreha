import typing as t
from reha.app.models import ObjectId, Field, Model
from . import models


@models.register('document')
class Document(Model):

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

    content_type: t.Optional[str] = None
    item: t.Optional[t.Dict] = None

    @property
    def title(self):
        return f"{self.content_type}"

    def __repr__(self):
        return f"Document({self.docid}, {self.content_type!r})"

    def __post_init__(self):
        if self.creation_date is None:
            self.creation_date = datetime.now()
