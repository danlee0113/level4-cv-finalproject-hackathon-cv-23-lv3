import os
from dotenv import load_dotenv
from langchain_teddynote.tools.tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()

# Tavily API 키 가져오기
api_key = os.getenv("TAVILY_API_KEY")
if not api_key:
    raise ValueError("❌ Tavily API key가 없습니다.")

web_search = TavilySearch(
    api_key=api_key,  # ✅ API 키 추가
    topic="news",
    max_results=2,
    search_depth="advanced",
    include_answer=False,
    include_raw_content=False,
    include_images=False,
    format_output=False,
)

def search_news(query: str):
    """검색어를 받아 Tavily API를 통해 뉴스 검색 수행"""
    if not query.strip():
        raise ValueError("❌ 검색어가 비어 있습니다. 유효한 검색어를 입력하세요.")

    print(f"🔎 Sending API request to Tavily with query: {query}")  # 디버깅용 로그

    response = web_search.search(query)

    print(f"📌 Tavily API response received, {len(response)} results")  # 응답 확인

    # 결과를 5개로 제한
    return response

