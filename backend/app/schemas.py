from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=12, max_length=72)
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)


class UserLogin(BaseModel):
    email: str = Field(min_length=3, max_length=320)
    password: str = Field(min_length=1, max_length=1024)


class UserResponse(BaseModel):
    id: int
    email: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChatCreate(BaseModel):
    title: str = "New chat"


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=10000)


class ChatRead(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class MessageTurnResponse(BaseModel):
    chat_id: int
    user_message: str
    assistant_message: str
    risk_level: Literal["high", "medium", "low"]