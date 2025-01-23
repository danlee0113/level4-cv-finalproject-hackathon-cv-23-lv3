from fastapi import FastAPI, Request, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import Base, User
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
from fastapi_login import LoginManager
import logging
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

print("Starting FastAPI application...")
# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="frontend/templates")

# 정적 파일 경로 설정 (절대 경로 사용)
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# 데이터베이스 세션 생성
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 세션 관리 설정
SECRET = "your-secret-key"
manager = LoginManager(SECRET, token_url="/login", use_cookie=True)

# 사용자 로드 함수
@manager.user_loader
def load_user(email: str, db: Session = Depends(get_db)):
    return db.query(User).filter(User.email == email).first()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application!"} 

@app.get("/login", response_class=HTMLResponse, name="login")
async def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login", response_class=HTMLResponse, name="login")
async def login_post(request: Request, db: Session = Depends(get_db)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    
    try:
        # 데이터베이스에서 사용자 검색
        user = db.query(User).filter(User.email == email).first()
        
        # 사용자와 비밀번호 검증
        if user and user.password == password:
            print("로그인 성공")
            response = RedirectResponse(url="/chat", status_code=303)  # chat으로 리다이렉트
            manager.set_cookie(response, email)  # 세션에 사용자 저장
            # 세션 정보 출력
            print(f"생성된 세션: {email}")  # 세션에 저장된 이메일 출력
            return response
        else:
            error = f"이메일 또는 비밀번호가 잘못되었습니다. 입력된 이메일: {email}, 입력된 비밀번호: {password}"
            if user:
                error += f", 데이터베이스에서 찾은 사용자: {user.email}, 비밀번호: {user.password}"
            return templates.TemplateResponse("login.html", {"request": request, "error": error})
    except Exception as e:
        error = f"서버 오류가 발생했습니다: {e}"
        return templates.TemplateResponse("login.html", {"request": request, "error": error})

@app.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),
    nickname: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...)
):
    # 닉네임 길이 검사
    if len(nickname) < 2 or len(nickname) > 10:
        return templates.TemplateResponse("register.html", {"request": request, "error": "닉네임은 2-10자 사이여야 합니다"})

    # 비밀번호 형식 검사
    if not password.isalnum() or not all(c.islower() or c.isdigit() for c in password):
        return templates.TemplateResponse("register.html", {"request": request, "error": "비밀번호는 영문 소문자와 숫자만 사용 가능합니다"})

    # 비밀번호 일치 검사
    if password != confirm_password:
        return templates.TemplateResponse("register.html", {"request": request, "error": "비밀번호가 일치하지 않습니다"})

    # 이미 등록된 이메일인지 확인
    db = next(get_db())
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "이미 등록된 이메일입니다."})

    # 사용자 생성 로직 구현 (DB 저장 등)
    new_user = User(email=email, password=password, username=nickname)
    db.add(new_user)
    db.commit()

    # 회원가입 성공 시 로그인 페이지로 리다이렉트
    return RedirectResponse(url="/login", status_code=303)

@app.get("/chat", response_class=HTMLResponse)
async def chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/mypage", response_class=HTMLResponse)
async def mypage(request: Request, user: User = Depends(manager)):
    # 실제 운영 환경에서는 DB에서 사용자 정보를 가져와야 함
    print(f"로그인된 사용자: {user.email}")
    db = next(get_db())
    user_info = db.query(User).filter(User.email == user.email).first()
    
    if not user_info:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    return templates.TemplateResponse("mypage.html", {"request": request, "user": user})

@app.get("/logout", response_class=HTMLResponse, name="logout")
async def logout(request: Request):
    response = templates.TemplateResponse("login.html", {"request": request, "message": "로그아웃되었습니다."})
    response.delete_cookie("fastapi_login")  # 세션 쿠키 삭제 (쿠키 이름은 실제 사용 중인 이름으로 변경)
    return response

@app.get("/edit_profile", response_class=HTMLResponse)
async def edit_profile(request: Request, user: User = Depends(manager)):
    # 사용자 정보를 템플릿에 전달
    return templates.TemplateResponse("edit_profile.html", {"request": request, "user": user})

@app.post("/edit_profile", response_class=HTMLResponse)
async def update_profile(
    request: Request,
    user: User = Depends(manager),
    nickname: str = Form(...)
):
    # 사용자 닉네임 업데이트 로직 구현
    db = next(get_db())
    user_info = db.query(User).filter(User.email == user.email).first()
    
    if user_info:
        user_info.nickname = nickname
        db.commit()
        return RedirectResponse(url="/mypage", status_code=303)
    else:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

@app.get("/change_password", response_class=HTMLResponse)
async def change_password(request: Request, user: User = Depends(manager)):
    return templates.TemplateResponse("change_password.html", {"request": request})

@app.post("/change_password", response_class=HTMLResponse)
async def update_password(
    request: Request,
    user: User = Depends(manager),
    current_password: str = Form(...),
    confirm_password: str = Form(...),
    new_password: str = Form(...)
):
    db = next(get_db())
    user_info = db.query(User).filter(User.email == user.email).first()
    
    if user_info:
        if user_info.password == current_password:  # 비밀번호 확인
            if new_password == confirm_password:
                user_info.password = new_password  # 비밀번호 업데이트
                db.commit()
                return RedirectResponse(url="/mypage", status_code=303)
            else:
                return templates.TemplateResponse("change_password.html", {"request": request, "error": "새 비밀번호가 일치하지 않습니다."})
        else:
            return templates.TemplateResponse("change_password.html", {"request": request, "error": "현재 비밀번호가 잘못되었습니다."})
    else:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)