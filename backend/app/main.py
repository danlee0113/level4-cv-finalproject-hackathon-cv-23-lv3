# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from .database import init_db
from .routers import users, chats, auth, profile, news  
from app.rag.rag import query_to_answer_for_eval, rag_chain
from .schemas import EvalQuery, EvalResponse

# Jinja2 템플릿 로더 설정
templates = Jinja2Templates(directory="app/templates")

def create_app():
    app = FastAPI(
        title="Chatbot Service",
        description="FastAPI + SQLAlchemy + MySQL + Templates 예시 프로젝트",
        version="0.1.0",
    )

    # DB 초기화
    init_db()

    # SessionMiddleware 추가
    app.add_middleware(
        SessionMiddleware,
        secret_key="your-secret-key",  # 여기에 보안용 비밀 키를 입력
    )

    # 정적 파일 Mount
    # "/static" 경로로 접근 시 app/static 디렉터리에서 파일을 제공
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # 라우터 등록
    app.include_router(users.router)
    app.include_router(chats.router)
    app.include_router(auth.router)
    app.include_router(profile.router)
    app.include_router(news.router)


    # 간단한 예시 라우트 (HTML 렌더링)
    @app.get("/", response_class=HTMLResponse)
    def read_root(request: Request):
        return templates.TemplateResponse("intro.html", {"request": request})
    
    @app.get("/login", response_class=HTMLResponse)
    def login(request: Request):
        return templates.TemplateResponse("login.html", {"request": request})

    @app.get("/register", response_class=HTMLResponse)
    def register(request: Request):
        return templates.TemplateResponse("register.html", {"request": request})
    
    @app.get("/test", response_class=HTMLResponse)
    def register(request: Request):
        return templates.TemplateResponse("register.html", {"request": request})
    
    @app.post("/evaluation", response_model=EvalResponse)
    def evaluate_query(query_data: EvalQuery):
        user_query = query_data.query
        # 평가용 체인(rag_chain_eval)을 인자로 전달하여 평가 API용 답변 생성
        rag_result = query_to_answer_for_eval(user_query, rag_chain)

        return EvalResponse(
            context=rag_result["context"],
            answer=rag_result["answer"]
        )

    return app

app = create_app()


# 실행 명령 예시:
# uvicorn app.main:app --reload
# uvicorn app.main:app --reload --port 9000
# uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload