from pydantic import BaseModel, Field, validator
from typing import Optional


class RegistrationModel(BaseModel):
    login: str
    password: str

    @validator("login")
    def validate_login(cls, login: str) -> str:
        assert " " not in login, "No spaces allowed in login"
        return login




class BaseUserModel(BaseModel):
    id: str
    login: str




class UserModel(BaseUserModel):
    id: str
    login: str
    bills: int
    balance: int
    password: str





class AuthUserModel(BaseModel):
    username: str
    password: str


