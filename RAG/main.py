from utils.file_utils import format_docs
from modules.embeddings import load_json
from langchain_teddynote.messages import stream_response
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_teddynote import logging
from dotenv import load_dotenv
import faiss
import json
import pickle
import warnings
import random 
import numpy as np

RANDOM_SEED = 34
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
# 설정 변수들
DB_INDEX = "RAPTOR_CLAUDE_1_3500_400"
DOTENV_PATH = "/data/ephemeral/home/.env"
PROJECT_NAME = "hackathon-module"
LLM_INFO_DIR = "/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/json_cache/llm_info.json"
EMBEDDING_INFO_DIR = "/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/json_cache/embeddings_info.json"

# LLM 및 임베딩 로드
embeddings, llm = load_json(EMBEDDING_INFO_DIR, LLM_INFO_DIR)

warnings.filterwarnings("ignore")

# API 키 정보 로드
load_dotenv(dotenv_path=DOTENV_PATH)

# 프로젝트 이름 로깅
logging.langsmith(PROJECT_NAME)

# FAISS 인덱스 로드
index = faiss.read_index(f"{DB_INDEX}/index.faiss")

# FAISS 메타데이터 로드
with open(f"{DB_INDEX}/index.pkl", "rb") as f:
    metadata = pickle.load(f)
docstore, index_to_docstore_id = metadata

vectorstore = FAISS(
    embedding_function=embeddings, index=index, docstore=docstore, index_to_docstore_id=index_to_docstore_id
)

# 프롬프트 정의
prompt = PromptTemplate.from_template(
    """
    You are an AI assistant specializing in Question-Answering (QA) tasks within a Retrieval-Augmented Generation (RAG) system. 
    You are given PDF documents. Your primary mission is to answer questions based on provided context.
    Ensure your response is concise and directly addresses the question without any additional narration.
    
    ###
    
    Your final answer should be written concisely (but include important numerical values, technical terms, jargon, and names).
    
    # Steps
    
    1. Carefully read and understand the context provided.
    2. Identify the key information related to the question within the context.
    3. Analyze the user's question to identify the specific financial term(s) being referenced.
            - Example financial terms include: "세전", "세후", "영업 이익", "순이익", "EPS", "매출", "DPS", "EBITDA".
            - Pay attention to whether the question includes specific terms like "세전", "세후", "영업 이익", "순이익", "EPS", "매출", "DPS", "EBITDA".
            - Please note the monetary units used in the context (e.g., often written as '단위: 억원', '단위: 십억원') and ensure that your answer uses the same units consistently.
    4. Identify if the question explicitly mentions periods (e.g., quarterly, yearly).
            - If the question mentions "quarters" or "specific periods," prioritize analyzing the quarterly table.
            - If no period is specified, provide an overview but ensure quarterly data is referenced when applicable.
    5. Formulate a concise answer based on the relevant information.
    6. Ensure your final answer directly addresses the question.
    7. You must refer to the table carefully.
    8. If asked by period, answer by period and then give the total at the end.
    9. Be sure to organize it clearly, don't write it at length.
    10. If there is a word referring to a period in the question, you should carefully refer to the table for the corresponding period.
    11. If a specific period comes up, you have to search and answer even if you change it to a quarter.
    12. You should include numerical values in your answer.
    
    # Output Format:
    [General introduction of the answer]
    [Comprehensive answer to the question]
    
    ###
    
    Remember:
    - It's crucial to base your answer solely on the **PROVIDED CONTEXT**. 
    - DO NOT use any external knowledge or information not present in the given materials.
    
    ###
    
    # Here is the user's QUESTION that you should answer:
    {question}
    
    # Here is the CONTEXT that you should use to answer the question:
    {context}
    
    [Note]
    - Answer should be written in Korean.
    - You should carefully refer to the quarterly outlook table.
    - Tables are critical for answering questions involving numerical values or periods. Reference them explicitly.
    
    # Your final ANSWER to the user's QUESTION:"""
)

# FAISS 검색 설정 (k=10으로 검색)
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})

# RAG 체인 설정 (입력은 단순 문자열로 받음)
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

def query_to_answer_for_eval(query, rag_chain):
    """RAG 시스템에서 질문을 받아 JSON 형식으로 답변을 생성하는 함수"""

    print(f"\n[DEBUG] 입력 query: {query}")

    # 1. FAISS 검색을 통해 문서 가져오기 (출력용으로 context 확보)
    retrieved_docs = retriever.get_relevant_documents(query)
    print(f"[DEBUG] 검색된 문서 개수: {len(retrieved_docs)}")

    source_documents = []
    for i, doc in enumerate(retrieved_docs):
        if isinstance(doc.page_content, dict):
            content_str = json.dumps(doc.page_content, ensure_ascii=False)
        elif isinstance(doc.page_content, str):
            content_str = doc.page_content
        else:
            print(f"[ERROR] 예상치 못한 데이터 타입: {type(doc.page_content)}")
            content_str = str(doc.page_content)
        source_documents.append(content_str)

    if not source_documents:
        source_documents = ["No relevant documents found."]
    print(f"[DEBUG] 변환된 source_documents: {source_documents[:3]}")

    if isinstance(query, dict):
        query = json.dumps(query, ensure_ascii=False)
    print(f"[DEBUG] 변환된 query: {query}")

    try:
        print("[DEBUG] RAG 체인 실행 중...")
        # 체인에는 단순 문자열 query를 전달합니다.
        answer = rag_chain.invoke(query)
        print(f"[DEBUG] 생성된 answer: {answer}")
    except Exception as e:
        print(f"[ERROR] rag_chain.invoke() 호출 중 오류 발생: {e}")
        return {
            "context": source_documents,
            "answer": "Error: Unable to generate answer."
        }

    response_json = {
        "context": source_documents,
        "answer": answer
    }
    return response_json

# 대화형 입력 루프
while True:
    query = input("질문 입력: ")
    if query.lower() == "done":
        print("챗봇 종료!")
        break
    rag_result = query_to_answer_for_eval(query, rag_chain)
    print(json.dumps(rag_result, ensure_ascii=False, indent=4))
    print()
