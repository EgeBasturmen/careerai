from pydantic import BaseModel


class ErrorDetail(BaseModel):
    code: str
    message: str
    status_code: int


class ErrorResponse(BaseModel):
    error: ErrorDetail