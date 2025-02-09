from fastapi import APIRouter, Request, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from ..database import get_db
from .. import crud
from ..rag.web_search import web_search
from ..rag.web_summarize import summarize_article

templates = Jinja2Templates(directory="app/templates")

router = APIRouter(
    prefix="/news",
    tags=["news"]
)

@router.get("/search", response_class=JSONResponse)
def search_news(query: str = Query(..., description="검색할 뉴스 키워드 입력")):
    """사용자가 입력한 키워드에 맞는 뉴스를 검색하고 요약하여 반환"""
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="검색어를 입력해야 합니다.")

    # Tavily API를 사용하여 뉴스 검색
    search_results = web_search.search(query) 

    print(f"🔎 검색된 뉴스 개수: {len(search_results)}")  # 디버깅

    if not search_results:
        return {"keyword": query, "news": []}

    # 🔹 최대 5개의 뉴스만 처리하도록 제한
    limited_results = search_results  

    summarized_news = []
    for news in limited_results:
        title = news.get("title", "제목 없음")
        url = news.get("url", "")

        if not url:
            continue

        # ✅ 뉴스 기사 요약 수행 (웹에서 기사 내용 가져와 요약)
        summary_result = summarize_article(url)
        final_summary = summary_result["summary"]
        sentiment_score = summary_result["sentiment"]

        summarized_news.append({
            "title": title,
            "summary": final_summary,
            "sentiment": sentiment_score,
            "link": url
        })

    return {"keyword": query, "news": summarized_news}

@router.get("", name="news", response_class=HTMLResponse)
def show_news(request: Request, db: Session = Depends(get_db)):
    """뉴스 페이지 렌더링 (검색 기능 추가)"""
    
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)
    
    user = crud.get_user(db, user_id)
    if not user:
        return RedirectResponse(url="/login", status_code=303)
    
    chat_sessions = []
    if user_id:
        chat_sessions = db.query(crud.models.ChatSession).filter_by(user_id=user_id).all()
    
    return templates.TemplateResponse(
        "news_is.html",
        {
            "request": request,
            "chat_sessions": chat_sessions
        }
    )
