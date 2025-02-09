# app/schemas.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr

# ========== User ==========
class UserBase(BaseModel):
    nickname: str           # 기존 username → nickname
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    nickname: Optional[str] = None  # 기존 username → nickname
    password: Optional[str] = None

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# ========== Industry ==========
class IndustryBase(BaseModel):
    industry_name: str

class IndustryCreate(IndustryBase):
    pass

class IndustryResponse(IndustryBase):
    industry_id: int

    class Config:
        orm_mode = True

# ========== ChatMessage ==========
class ChatMessageBase(BaseModel):
    sender_role: str  # 'user' | 'assistant' | 'system'
    message: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessageResponse(ChatMessageBase):
    chat_message_id: int
    created_at: datetime

    class Config:
        orm_mode = True

# ========== ChatSession ==========
class ChatSessionBase(BaseModel):
    pass

class ChatSessionCreate(ChatSessionBase):
    pass

class ChatSessionResponse(ChatSessionBase):
    chat_session_id: int
    created_at: datetime
    updated_at: datetime
    chat_messages: List[ChatMessageResponse] = []

    class Config:
        orm_mode = True


# ========== Evaluation ==========
class EvalQuery(BaseModel):
    query: str

class EvalResponse(BaseModel):
    context: List[str]
    answer: str