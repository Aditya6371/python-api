from typing import Optional
from pydantic import BaseModel


class LoginUsermodel(BaseModel):
    username: str
    password: str


class RegisterUsermodel(BaseModel):
    username: str
    password: str
    email: str
    full_name: Optional[str] = None
    age: Optional[int] = None
    is_active: bool = True