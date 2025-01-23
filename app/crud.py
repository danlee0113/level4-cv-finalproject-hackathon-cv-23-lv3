from sqlalchemy.orm import Session
from . import models, schemas

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, email=user.email, password=user.password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_industry(db: Session, industry_id: int):
    return db.query(models.Industry).filter(models.Industry.industry_id == industry_id).first()

def create_chat_session(db: Session, chat_session: schemas.ChatSessionCreate):
    db_chat_session = models.ChatSession(user_id=chat_session.user_id)
    db.add(db_chat_session)
    db.commit()
    db.refresh(db_chat_session)
    return db_chat_session

def create_chat_message(db: Session, chat_message: schemas.ChatMessageCreate):
    db_chat_message = models.ChatMessage(
        chat_session_id=chat_message.chat_session_id,
        sender_role=chat_message.sender_role,
        message=chat_message.message
    )
    db.add(db_chat_message)
    db.commit()
    db.refresh(db_chat_message)
    return db_chat_message 
    
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()