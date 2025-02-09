from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from fastapi.templating import Jinja2Templates
import bcrypt

# 템플릿 객체 생성
templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/profile",
    tags=["profile"]
)

@router.get("/mypage", name="mypage", response_class=HTMLResponse)
def mypage(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")  # 세션에서 user_id 가져오기
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = crud.get_user(db, user_id)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "mypage.html", {"request": request, "user": user}
    )


@router.get("/edit_profile", name="edit_profile_page", response_class=HTMLResponse)
def edit_profile_page(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = crud.get_user(db, user_id)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse(
        "edit_profile.html", {"request": request, "user": user}
    )


@router.post("/edit_profile", name="edit_profile", response_class=HTMLResponse)
def edit_profile(
    request: Request, nickname: str = Form(...), db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = crud.get_user(db, user_id)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # 닉네임 업데이트
    user_update = schemas.UserUpdate(nickname=nickname)
    crud.update_user(db, user, user_update)

    return RedirectResponse(url="/profile/mypage", status_code=303)


@router.get("/change_password", name="change_password_page", response_class=HTMLResponse)
def change_password_page(request: Request):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    return templates.TemplateResponse("change_password.html", {"request": request})


@router.post("/change_password", name="change_password")
def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    user = crud.get_user(db, user_id)
    if not user:
        return RedirectResponse(url="/login", status_code=303)

    # 현재 비밀번호 확인
    if not bcrypt.checkpw(current_password.encode("utf-8"), user.password.encode("utf-8")):
        return templates.TemplateResponse(
            "change_password.html",
            {"request": request, "error": "현재 비밀번호가 올바르지 않습니다."},
        )

    if new_password != confirm_password:
        return templates.TemplateResponse(
            "change_password.html",
            {"request": request, "error": "새 비밀번호가 일치하지 않습니다."},
        )

    # 비밀번호 업데이트
    hashed_new = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    user_update = schemas.UserUpdate(password=hashed_new)
    crud.update_user(db, user, user_update)

    return RedirectResponse(url="/profile/mypage", status_code=303)


@router.get("/logout", name="logout")
def logout(request: Request):
    request.session.clear()  # 세션 초기화
    return RedirectResponse(url="/login", status_code=303)
