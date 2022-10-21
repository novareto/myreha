import logging
import orjson
import typing as t
from datetime import datetime
from bson import ObjectId as BSONObjectId
from pydantic import BaseModel, Field
from pymongo import IndexModel


logger = logging.getLogger(__name__)

JSONValue = t.Union[
    str, int, float, bool, None, t.Dict[str, t.Any], t.List[t.Any]]
JSONType = t.Union[t.Dict[str, JSONValue], t.List[JSONValue]]


class ObjectId(BSONObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not BSONObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return BSONObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class Model(BaseModel):

    id: ObjectId = Field(default_factory=ObjectId, alias="_id")

    creation_date: t.Optional[datetime] = Field(
        default_factory=datetime.now,
        title="Erstelldatum"
    )

    annotation: t.Optional[t.Dict] = None

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  #required for the _id
        json_encoders = {BSONObjectId: str}


class JSONSchema(str):

    __slots__ = ('json',)

    def __new__(cls, schema: str):
        json = orjson.loads(schema)  # done before, to ensure validity
        inst = super().__new__(cls, schema)
        inst.json = json
        return inst

    def __repr__(self):
        return f'<JSONSchema {self.json!r}>'


class ModelMetadata(t.NamedTuple):
    indexes: t.Optional[t.Sequence[IndexModel]] = None


class ModelInfo(t.NamedTuple):
    name: str
    model: Model
    table: str
    schema: JSONSchema
    metadata: dict


class Models(t.Iterable[ModelInfo]):
    """Model registry
    """
    _models = t.MutableMapping[str, ModelInfo]

    def __init__(self):
        self._models = {}

    def __len__(self):
        return len(self._models)

    def __getitem__(self, name: str):
        return self._models[name]

    def __contains__(self, name: str):
        return name in self._models

    def get(self, name):
        return self._models.get(name)

    def remove(self, name: str):
        del self._models[name]

    def add(self,
            name: str,
            model: Model,
            table: t.Optional[str] = None,
            **metadata) -> ModelInfo:

        if name in self._models:
            logger.debug(
                f'Model {name!r} already exists. '
                f'Replacing {self._models[name]} with {model}'
            )

        info = ModelInfo(
            name=name,
            model=model,
            table=table or name,
            schema=JSONSchema(model.schema_json()),
            metadata=ModelMetadata(**metadata)
        )
        self._models[name] = info
        logger.info(f'Added new model {model!r} as {name!r}.')
        return info

    def register(self, name: str, **metadata):
        def model_registration(model: Model):
            self.add(name, model, **metadata)
            return model
        return model_registration

    def __iter__(self):
        return iter(self._models.values())
