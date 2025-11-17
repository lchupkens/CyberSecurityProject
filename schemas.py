from typing import Optional
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserOut(BaseModel):
    email: str
    token: Optional[str] = None