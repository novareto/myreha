import enum
import secrets
import hashlib
import base64
import typing as t
from datetime import date
from pymongo import IndexModel, DESCENDING
from pydantic import BaseModel, EmailStr, validator
from reha.app.models import Field, Model
from . import models


def is_hash(pw: str) -> bool:
    return pw.startswith('__hash__') and len(pw) == 200


def hash_password(password: str) -> str:
    salt = b'__hash__' + hashlib.sha256(
        secrets.token_bytes(60)
    ).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        27500,
        dklen=64
    )
    return base64.b64encode(pwdhash).decode('utf-8')


def verify_password(stored: str, challenger: str) -> bool:
    """Verify a stored password against one provided by user"""
    salt = stored[:72]
    stored_password = stored[72:]
    pwdhash = hashlib.pbkdf2_hmac(
        'sha256',
        challenger.encode('utf-8'),
        salt.encode('ascii'),
        27500,
        dklen=64
    )
    pwdhash = base64.b64encode(pwdhash).decode('utf-8')
    return pwdhash == stored


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

    password: str = Field(
        ...,
        title="Passwort"
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

    @validator('password')
    def hash_password(cls, pw: str) -> str:
        if is_hash(pw):
            return pw
        return hash_password(pw)

    def __repr__(self):
        return f"User({self.id}, {self.email!r})"
