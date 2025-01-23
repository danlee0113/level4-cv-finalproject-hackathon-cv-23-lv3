from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Enum, BigInteger, func
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    chat_sessions = relationship('ChatSession', back_populates='user', cascade='all, delete-orphan')
    user_industries = relationship('UserIndustry', back_populates='user', cascade='all, delete-orphan')

class Industry(Base):
    __tablename__ = 'industries'

    industry_id = Column(Integer, primary_key=True, autoincrement=True)
    industry_name = Column(String(100), nullable=False)

    user_industries = relationship('UserIndustry', back_populates='industry', cascade='all, delete-orphan')

class UserIndustry(Base):
    __tablename__ = 'user_industries'

    user_id = Column(BigInteger, ForeignKey('users.user_id'), primary_key=True)
    industry_id = Column(Integer, ForeignKey('industries.industry_id'), primary_key=True)

    user = relationship('User', back_populates='user_industries')
    industry = relationship('Industry', back_populates='user_industries')

class ChatSession(Base):
    __tablename__ = 'chat_sessions'

    chat_session_id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.user_id'), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    user = relationship('User', back_populates='chat_sessions')
    chat_messages = relationship('ChatMessage', back_populates='chat_session', cascade='all, delete-orphan')

class ChatMessage(Base):
    __tablename__ = 'chat_messages'

    chat_message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_session_id = Column(BigInteger, ForeignKey('chat_sessions.chat_session_id'), nullable=False)
    sender_role = Column(Enum('user', 'assistant', 'system'), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())

    chat_session = relationship('ChatSession', back_populates='chat_messages')