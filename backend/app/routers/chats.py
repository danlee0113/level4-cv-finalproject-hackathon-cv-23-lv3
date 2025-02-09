# app/routers/chats.py

from fastapi import APIRouter, Depends, HTTPException, status, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from fastapi.templating import Jinja2Templates

# DB 연결, CRUD, 스키마 import
from ..database import get_db
from .. import crud, schemas

# RAG(main.py)에 정의된 함수 import (경로는 상황에 맞게 수정)
# 예: from app.rag.main import query_to_answer, rag_chain
# main.py에 query_to_answer(), rag_chain 등이 정의되어 있어야 합니다.
from app.rag.rag import query_to_answer, rag_chain


templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/chats",
    tags=["chats"]
)

@router.get("", name="show_user_chats", response_class=HTMLResponse)
def show_user_chats(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = crud.get_user(db, user_id)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # 1) 해당 사용자의 모든 채팅 세션 가져오기
    chat_sessions = (
        db.query(crud.models.ChatSession)
        .filter(crud.models.ChatSession.user_id == user_id)
        .order_by(crud.models.ChatSession.created_at.desc())  
        .all()
    )

    # 2) 각 세션마다 첫 번째 'user' 메시지를 찾아서 session.first_message 에 저장
    for session in chat_sessions:
        first_user_message = (
            db.query(crud.models.ChatMessage)
            .filter(
                crud.models.ChatMessage.chat_session_id == session.chat_session_id,
                crud.models.ChatMessage.sender_role == "user"
            )
            .order_by(crud.models.ChatMessage.created_at.asc())
            .first()
        )
        session.first_message = first_user_message.message if first_user_message else None

    # 3) 템플릿에 chat_sessions (with first_message) 전달
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "user_id": user_id,
            "chat_sessions": chat_sessions,
        }
    )




@router.post("/", response_model=schemas.ChatSessionResponse)
def create_chat_session(
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    - 채팅 세션 생성
    - user_id를 Form으로 받아서 DB에 새로운 ChatSession을 추가
    """
    user = crud.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chat_session = crud.create_chat_session(db, user_id)
    return chat_session

@router.get("/{chat_session_id}", response_model=schemas.ChatSessionResponse)
def get_chat_session(chat_session_id: int, db: Session = Depends(get_db)):
    """
    - 특정 chat_session_id에 대한 세션 정보 반환
    """
    chat_session = crud.get_chat_session(db, chat_session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    return chat_session

@router.post("/{chat_session_id}/messages", response_model=schemas.ChatMessageResponse)
def create_chat_message(
    chat_session_id: int,
    message_data: schemas.ChatMessageCreate,  # { "sender_role": "user", "message": "사용자 입력" }
    db: Session = Depends(get_db)
):
    """
    1) 사용자 메시지 DB에 저장
    2) RAG 로직 호출 -> 답변 생성
    3) 봇 메시지 DB에 저장
    4) 생성된 봇 메시지를 JSON으로 반환
    """
    # 1) 유효한 채팅 세션인지 확인
    chat_session = crud.get_chat_session(db, chat_session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    # 2) 사용자 메시지 먼저 DB에 저장
    user_msg = crud.create_chat_message(db, chat_session_id, message_data)

    # 3) RAG 로직을 통해 답변 생성
    #    - main.py의 query_to_answer, rag_chain 호출
    user_query = message_data.message
    bot_answer_str = query_to_answer(user_query, rag_chain)
    #  만약 스트리밍 대신 최종답변만 한 번에 받고 싶다면,
    #  bot_answer_str = rag_chain.invoke(user_query)
    #  등으로 교체 가능합니다.

    # 4) RAG가 생성한 답변을 봇 메시지로 DB에 저장
    bot_msg_data = schemas.ChatMessageCreate(
        sender_role="assistant",
        message=bot_answer_str
    )
    bot_msg = crud.create_chat_message(db, chat_session_id, bot_msg_data)

    # 5) 최종적으로 봇 메시지를 반환 (JSON)
    return bot_msg

@router.get("/{chat_session_id}/messages", response_model=list[schemas.ChatMessageResponse])
def get_chat_messages(chat_session_id: int, db: Session = Depends(get_db)):
    """
    - 특정 chat_session_id의 모든 메시지 목록 조회
    """
    chat_session = crud.get_chat_session(db, chat_session_id)
    if not chat_session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    messages = crud.get_chat_messages_by_session(db, chat_session_id)
    return messages
