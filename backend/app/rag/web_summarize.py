from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser
from langchain.document_loaders import WebBaseLoader
from langchain_core.prompts import ChatPromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from dotenv import load_dotenv


# API 키 정보 로드
load_dotenv()


class StreamCallback(BaseCallbackHandler):
    def on_llm_new_token(self, token, **kwargs):
        print(token, end="", flush=True)


prompt = ChatPromptTemplate.from_template(
    """Article: {ARTICLE}
You will generate increasingly concise, entity-dense summaries of the above article. 

Repeat the following 2 steps 5 times. 

Step 1. Identify 1-3 informative entities (";" delimited) from the article which are missing from the previously generated summary. 
Step 2. Write a new, denser summary of identical length which covers every entity and detail from the previous summary plus the missing entities. 

A missing entity is:
- relevant to the main story, 
- specific yet concise (50 words or fewer), 
- novel (not in the previous summary), 
- faithful (present in the article), 
- anywhere (can be located anywhere in the article).

Guidelines:

- The first summary should be long (8-10 sentences, ~200 words) yet highly non-specific, containing little information beyond the entities marked as missing. Use overly verbose language and fillers (e.g., "this article discusses") to reach ~200 words.
- Make every word count: rewrite the previous summary to improve flow and make space for additional entities.
- Make space with fusion, compression, and removal of uninformative phrases like "the article discusses".
- The summaries should become highly dense and concise yet self-contained, i.e., easily understood without the article. 
- Missing entities can appear anywhere in the new summary.
- Never drop entities from the previous summary. If space cannot be made, add fewer new entities. 

Additionally, evaluate the sentiment score of the news article on a scale from 1 (very negative) to 5 (very positive).

### Sentiment Analysis Criteria:
- **Score 5 (Very Positive)**: The article conveys overwhelmingly positive news, such as major success, innovation, economic growth, or social improvement.
- **Score 4 (Positive)**: The article contains mostly positive content but includes some minor neutral or negative aspects.
- **Score 3 (Neutral)**: The article presents a balanced view with both positive and negative elements or lacks strong emotional tone.
- **Score 2 (Negative)**: The article primarily discusses challenges, concerns, or risks, though it may include minor positive aspects.
- **Score 1 (Very Negative)**: The article focuses on crises, failures, or major negative events, creating a strongly pessimistic tone.

### Sentiment Scoring Examples:
- **"한국 경제 성장률 5% 달성, 사상 최대 투자 유치"** → **Score: 5 (Very Positive)**
- **"정부, 경제 지원 정책 발표…일부 전문가 회의적"** → **Score: 4 (Positive)**
- **"주가 등락 반복…경제 불확실성 여전"** → **Score: 3 (Neutral)**
- **"기업 투자 감소, 경기 둔화 우려"** → **Score: 2 (Negative)**
- **"대규모 구조조정, 실업률 급등"** → **Score: 1 (Very Negative)**

Each entry in the output JSON should include a "Sentiment_Score" key to provide the sentiment rating.

Remember, use the exact same number of words for each summary.
Answer in JSON. The JSON should be a list (length 4) of dictionaries whose keys are "Missing_Entities" and "Denser_Summary" and "Sentiment_Score".
Use only KOREAN language to reply.
Return the response in JSON format as a list (length 4) of dictionaries with the keys:  
- "Missing_Entities" (new informative entities)  
- "Denser_Summary" (progressively refined summary)  
- "Sentiment_Score" (the sentiment score from 1 to 5)  
"""
)


# Create the chain, including
chain = (
    prompt
    | ChatOpenAI(
        temperature=0,
        model="gpt-4o-mini-2024-07-18",
        streaming=True,
        callbacks=[StreamCallback()],
    )
    | JsonOutputParser()
)

def summarize_article(article_url: str):
    """🔍 URL을 받아 뉴스 기사 요약"""
    try:
        loader = WebBaseLoader(article_url)
        docs = loader.load()
        content = docs[0].page_content

        print(f"📢 Summarizing content from URL: {article_url} (Length: {len(content)})")

        result = chain.invoke({"ARTICLE": content})
        final_summary = result[-1]["Denser_Summary"]
        sentiment_score = result[-1]["Sentiment_Score"]

        return {
            "summary": final_summary,
            "sentiment": sentiment_score
        }
    
    except Exception as e:
        print(f"❌ 요약 실패: {e}")
        return {
            "summary": "요약을 생성할 수 없습니다. 원문을 확인하세요.",
            "sentiment": None
        }
