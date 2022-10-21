from pydantic import BaseModel, Field
from bson import ObjectId as BSONObjectId


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

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True  #required for the _id
        json_encoders = {BSONObjectId: str}
