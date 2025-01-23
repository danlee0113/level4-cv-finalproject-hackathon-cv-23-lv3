from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class IndustryBase(BaseModel):
    industry_name: str

class Industry(IndustryBase):
    industry_id: int

    class Config:
        orm_mode = True

class ChatSessionBase(BaseModel):
    user_id: int

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSession(ChatSessionBase):
    chat_session_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ChatMessageBase(BaseModel):
    chat_session_id: int
    sender_role: str
    message: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    chat_message_id: int
    created_at: datetime

    class Config:
        orm_mode = True 