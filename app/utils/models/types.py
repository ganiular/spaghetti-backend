from typing import Annotated

from pydantic import BeforeValidator, EmailStr


Email = Annotated[EmailStr, BeforeValidator(lambda x: str(x).lower().strip())]
