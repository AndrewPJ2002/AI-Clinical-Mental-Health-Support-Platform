#response /request schemas

from pydantic import BaseModel, EmailStr

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
class messageCreate(BaseModel):
    content: str
