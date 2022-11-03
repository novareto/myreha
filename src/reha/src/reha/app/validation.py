import wrapt
from knappe.response import Response
from pydantic import BaseModel, ValidationError


def json_validate(model: BaseModel):
    @wrapt.decorator
    def model_validator(wrapped, instance, args, kwargs):
        request = args[0]
        try:
            item = model.parse_obj(request.data.json)
        except ValidationError as e:
            return Response.from_json(400, body=e.json())
        return wrapped(*args, item=item, **kwargs)
    return model_validator
