from enum import StrEnum
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, BeforeValidator, EmailStr, Field


Email = Annotated[EmailStr, BeforeValidator(lambda x: str(x).lower().strip())]
TrimedStr = Annotated[str, BeforeValidator(lambda x: str(x).strip())]


class OrderedStrEnum(StrEnum):
    def __lt__(self, other):
        if not isinstance(other, OrderedStrEnum):
            raise TypeError("Cannot compare", type(self), "with", type(other))

        for role in self.__class__:
            if self == role:
                return False
            if other == role:
                return True
        return False

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        return not self == other and not self < other

    def __ge__(self, other):
        return self == other or self > other


class _Pagination(BaseModel):
    limit: int = Field(50, ge=1, le=100, description="Max number of items to return")
    skip: int = 100


Pagination = Annotated[_Pagination, Query()]
