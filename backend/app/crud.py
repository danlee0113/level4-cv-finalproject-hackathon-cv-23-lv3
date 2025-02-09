# app/crud.py
from sqlalchemy.orm import Session

from . import models, schemas


# ========== User ==========
def create_user(db: Session, user_data: schemas.UserCreate):
    new_user = models.User(
        nickname=user_data.nickname,  # 변경됨
        email=user_data.email,
        password=user_data.password  # 실제로는 bcrypt 해싱 권장
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.user_id == user_id).first()

def update_user(db: Session, user: models.User, user_update: schemas.UserUpdate):
    if user_update.nickname is not None:  # 변경됨
        user.nickname = user_update.nickname
    if user_update.password is not None:
        user.password = user_update.password
    db.commit()
    db.refresh(user)
    return user

def delete_user(db: Session, user: models.User):
    db.delete(user)
    db.commit()


# ========== ChatSession ==========
def create_chat_session(db: Session, user_id: int):
    new_session = models.ChatSession(user_id=user_id)
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session

def get_chat_session(db: Session, chat_session_id: int):
    return db.query(models.ChatSession).filter(models.ChatSession.chat_session_id == chat_session_id).first()


# ========== ChatMessage ==========
def create_chat_message(db: Session, chat_session_id: int, msg_data: schemas.ChatMessageCreate):
    new_msg = models.ChatMessage(
        chat_session_id=chat_session_id,
        sender_role=msg_data.sender_role,
        message=msg_data.message
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg

def get_chat_messages_by_session(db: Session, chat_session_id: int):
    return db.query(models.ChatMessage).filter(models.ChatMessage.chat_session_id == chat_session_id).all()
