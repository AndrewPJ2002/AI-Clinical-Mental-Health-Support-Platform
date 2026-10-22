#response /request schemas

from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr

#response schema for user creation
class UserCreate(BaseModel):
    email: str
    password: str

#response schema for user login
class UserResponse(BaseModel):
    id: int
    email: str

# backend returns after login
class Token(BaseModel):
    access_token: str
    token_type: str

class ChatCreate(BaseModel):
    title: str = "New chat"


# React sends this to backend to create a new message in the chat
class MessageCreate(BaseModel):
    content: str


class ChatRead(BaseModel):
    id: int
    title: str

    model_config = ConfigDict(from_attributes=True)


class MessageTurnResponse(BaseModel):
    chat_id: int
    user_message: str
    assistant_message: str
    risk_level: Literal["high", "medium", "low"]
