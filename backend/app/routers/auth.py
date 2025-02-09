# app/routers/auth.py

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
import bcrypt

templates = Jinja2Templates(directory="app/templates")

router = APIRouter()

@router.get("/login", name="login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", name="login")
def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 사용자 인증 로직
    user = db.query(User).filter(User.email == email).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        # 로그인 성공 시 세션 저장
        request.session["user_id"] = user.user_id  
        return RedirectResponse(url="/chats", status_code=303)
    else:
        # 로그인 실패 시 에러 메시지 표시
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid credentials"}
        )

@router.get("/register", name="register_page", response_class=HTMLResponse)
def register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", name="register_page")
def register(
    request: Request,
    email: str = Form(...),
    nickname: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 비밀번호 확인
    if password != confirm_password:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "비밀번호가 일치하지 않습니다."}
        )
    # 이메일 중복 확인
    user_exists = db.query(User).filter(User.email == email).first()
    if user_exists:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "이미 등록된 이메일입니다."}
        )
    # 비밀번호 해싱
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # 새 사용자 생성
    new_user = User(nickname=nickname, email=email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 가입 성공 후 로그인 페이지로
    return RedirectResponse(url="/login", status_code=303)
