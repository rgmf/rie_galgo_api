from pydantic import BaseModel


class Error404Model(BaseModel):
    detail: str
