
from pydantic import BaseModel
from typing import Union

class Contact(BaseModel):
    uId: int
    phoneNumber: str = ""
    email: str = ""
    linkedId: int
    linkPrecedence: str
    createdAt: int
    updatedAt: Union[int, None] = None
    deletedAt: Union[int, None] = None

class Request(BaseModel):
    email: str
    phoneNumber: str
