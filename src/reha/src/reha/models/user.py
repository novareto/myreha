import enum
import secrets
import typing as t
from datetime import date
from pymongo import IndexModel, DESCENDING
from pydantic import BaseModel, SecretStr, EmailStr
from reha.app.models import ObjectId, Field, Model
from . import models


def salter():
    return secrets.token_hex(8)


class MessagingType(enum.Enum):
    email = "email"
    webpush = "webpush"


class Preferences(BaseModel):

    name: str = Field(
        ...,
        title="Vorname",
        description="Vorname"
    )

    surname: str = Field(
        ...,
        title="Name",
        description="Name"
    )

    birthdate: t.Optional[date] = Field(
        None,
        title="Geburtsdatum"
    )

    privacy: bool = Field(
        default=False,
        title="Datenschutz",
        description=(
            "Bitte best\u00e4tigen Sie hier, dass Sie "
            "die Ausf\u00fchrungen zum Datenschutzgelesen und "
            "akzeptiert haben."
        )
    )

    participation: bool = Field(
        default=False,
        title="Teilnahme",
        description=(
            "Bitte best\u00e4tigen Sie uns hier die Teilnahme "
            "am Online-Verfahren."
        )
    )

    mobile: str = Field(
        default="",
        title="Telefonnummer",
        description="Telefonnummer"
    )

    channels: t.List[MessagingType] = Field(
        default_factory=list,
        title="Channel"
    )

    webpush_subscription: t.Optional[str] = None


@models.register(
    'user',
    indexes=(
        IndexModel([("loginname", DESCENDING)], unique=True),
        IndexModel([("email", DESCENDING)], unique=True),
    )
)
class User(Model):
    """A user object"""

    loginname: str = Field(
        ...,
        title="Anmeldename für Einladungsschreiben"
    )

    password: SecretStr = Field(
        ...,
        title="Passwort"
    )

    salt: str = Field(
        default_factory=salter,
        title=""
    )

    state: t.Optional[str] = Field(
        None,
        title="Status"
    )

    email: t.Optional[EmailStr] = Field(
        None,
        title="E-Mail"
    )

    organization: t.Optional[str] = Field(
        None,
        title="Organization"
    )

    preferences: t.Optional[Preferences] = None

    @property
    def title(self):
        return f"{self.id}, {self.email!r}"

    def __repr__(self):
        return f"User({self.id}, {self.email!r})"
