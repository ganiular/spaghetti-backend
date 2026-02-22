from typing import Mapping

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class InvalidParameterException(Exception):
    def __init__(self, field_errors: Mapping[str, list[str]]):
        self.field_errors = field_errors

    def get_content(self):
        return {"message": "Invalid Parameter", "field_errors": self.field_errors}


async def invalid_parameter_handler(request: Request, exc: InvalidParameterException):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST, content=exc.get_content()
    )


def register_exceptions(app: FastAPI):
    app.exception_handlers[InvalidParameterException] = invalid_parameter_handler
