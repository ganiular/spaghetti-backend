from enum import StrEnum
from typing import Annotated

from pydantic import BeforeValidator, EmailStr


Email = Annotated[EmailStr, BeforeValidator(lambda x: str(x).lower().strip())]


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
