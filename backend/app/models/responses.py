from pydantic import BaseModel


class DetailMessage(BaseModel):
    detail: str
