from bson import ObjectId
from pydantic import Field
from pydantic_core import core_schema
from typing import Annotated, Any


class _PyObjectId(ObjectId):
    """
    Custom ObjectId type that integrates with Pydantic v2.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, *args):
        """
        Returns the schema to validate and serialize ObjectId fields.
        """

        schema = core_schema.union_schema(
            [
                # Allowed types
                core_schema.is_instance_schema(ObjectId),
                core_schema.str_schema(),
            ]
        )

        return core_schema.no_info_after_validator_function(cls.validate, schema)

    @classmethod
    def validate(cls, value: Any) -> "PyObjectId":
        """
        Custom validation logic for ObjectId.
        Converts valid strings to ObjectId or raises an error.
        """

        if issubclass(cls, type(value)):
            return value
        if isinstance(value, str):
            try:
                return cls(value)
            except Exception:
                raise ValueError(f"Invalid ObjectId: {value}")
        raise TypeError(f"Expected ObjectId or str, got {type(value).__name__}")


PyObjectId = Annotated[
    _PyObjectId, Field(..., json_schema_extra={"example": "6998f7089f53dfcad057695b"})
]
