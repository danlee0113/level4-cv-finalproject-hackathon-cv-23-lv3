# /home/std2/LabQ/labqv1/backend/app/rag/rag.py
from app.rag.utils.file_utils import format_docs
from app.rag.modules.embeddings import load_json
from langchain_teddynote.messages import stream_response
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_teddynote import logging
from dotenv import load_dotenv
import faiss
import pickle
import warnings
import json


DB_INDEX = "VecDB/vecdb" # 뒤의 숫자는 차례대로 chunk size와 chunk overlap을 의미
DOTENV_PATH="/data/ephemeral/home/.env" # 환경 변수 경로
PROJECT_NAME="hackathon-module" # Langsmith에서 추적될 프로젝트의 이름 

LLM_INFO_DIR="/workspace/fastapi-server/app/rag/json_cache/llm_info.json" # 사용할 LLM 선언에 필요한 정보 
EMBEDDING_INFO_DIR="/workspace/fastapi-server/app/rag/json_cache/embeddings_info.json" # 사용할 embedding에 대한 정보 

embeddings, llm=load_json(EMBEDDING_INFO_DIR, LLM_INFO_DIR)

# 경고 메시지 무시
warnings.filterwarnings("ignore")

# API 키 정보 로드
load_dotenv(dotenv_path=DOTENV_PATH)

# 프로젝트 이름을 입력합니다.
logging.langsmith(PROJECT_NAME)


# FAISS 인덱스 로드
index = faiss.read_index(f"/workspace/fastapi-server/{DB_INDEX}/index.faiss")

# FAISS에 저장된 메타데이터 로드
with open(f"/workspace/fastapi-server/{DB_INDEX}/index.pkl", "rb") as f:
    metadata = pickle.load(f)
docstore, index_to_docstore_id = metadata

# FAISS 벡터스토어 재구성 (올바른 방식)
vectorstore = FAISS(embedding_function=embeddings, index=index, docstore=docstore, index_to_docstore_id=index_to_docstore_id)

# retriever 생성 (main)
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})


# 프롬프트 정의
prompt = PromptTemplate.from_template(
    """
    You are an AI assistant specializing in Question-Answering (QA) tasks within a Retrieval-Augmented Generation (RAG) system. 
    You are given PDF documents. Your primary mission is to answer questions based on the provided context.
    Ensure your response is concise and directly addresses the question without any additional narration.

    ###

    Your final answer should be written concisely (but include important numerical values, technical terms, jargon, and names).

    # Steps

    ## Retrieval Process (Ensure the best context selection)
    1. Ensure the selected contexts **collectively** capture the essential information required to answer the question.
    2. Verify that the retrieved contexts **directly address the user’s question** rather than providing excessive or irrelevant details.
    3. Filter out unnecessary information and **prioritize clarity and precision** in the extracted data.
    4. Maintain a reasonable balance in the length and number of retrieved contexts, avoiding information overload.

    ## Answer Generation Process
    5. Carefully read and understand the context provided.
    6. Identify the key information related to the question within the context.
    7. Analyze the user's question to identify the specific financial term(s) being referenced.
        - Example financial terms include: "세전", "세후", "계속사업이익", "사업이익".
        - Pay attention to whether the question includes specific terms like "세전", "세후", or "계속사업이익".
    8. Identify if the question explicitly mentions periods (e.g., quarterly, yearly).
        - If the question mentions "quarters" or "specific periods," prioritize analyzing the quarterly table.
        - If no period is specified, provide an overview but ensure quarterly data is referenced when applicable.
    9. Formulate a **concise and factually accurate** answer based on the relevant information.
    10. Ensure the final answer is **logically structured**, **free of contradictions**, and **avoids unnecessary repetition**.
    11. Always refer to the table carefully when answering numerical or period-based questions.
    12. **When extracting numerical values from the table, always maintain the original unit.**
        - **The provided financial data is in '십억 원' (billions of KRW).**
        - **DO NOT convert values into '억 원' (hundreds of millions of KRW).**
    13. **If the table includes values in '십억 원', you MUST use '십억 원' when answering.**
    14. **Before finalizing the response, verify that all numerical values are in '십억 원' and not in '억 원'.**
    15. If asked by period, **answer by period first, then provide the total at the end**.
    16. If a period-related term is included in the question, double-check the table to extract the corresponding data.
    17. If a **specific period is mentioned**, answer using the relevant quarter even if a different timeframe is provided.

    ## Ensuring Quality and Accuracy
    18. **Verify factual correctness** by strictly relying on the provided context. Do not introduce external information.
    19. **Ensure all essential points** required by the question and the Ground Truth answer are addressed.
    20. **Include proper citations** for any referenced claims, numerical values, or data sources.
    21. **Format the answer appropriately** based on the question type:
        - Use **tables** for numerical comparisons.
        - Use **lists** for structured points.
        - Keep responses **concise yet informative** for textual explanations.
    22. **Enhance user understanding** by adding helpful contextual insights when relevant, as long as they remain factually accurate.

    # Output Format:
    [General introduction of the answer]
    [Comprehensive answer to the question]
    [Source of context(출처)]
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

    # Your final ANSWER to the user's QUESTION:
    """

)

# RAG 체인 정의
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)



def query_to_answer(query,rag_chain):
    '''
    Chat-GPT처럼 한 번에 답변이 나오지 않고 되는대로 출력을 하기를 원하면 stream을 return하고,
    한 번에 출력하기를 원하면 answer를 return해야 함.
    답변이 길면 stream 방식이 더 적합해 stream return하기로 결정.
    '''
    answer = rag_chain.stream(query)
    result = stream_response(answer, True)

    print("\nresult :", type(result))
    # print("\nresult :", result)

    return result


def query_to_answer_for_eval(query, rag_chain):
    """RAG 시스템에서 질문을 받아 JSON 형식으로 답변을 생성하는 함수"""

    # 1. FAISS 검색을 통해 문서 가져오기 (출력용으로 context 확보)
    retrieved_docs = retriever.get_relevant_documents(query)

    source_documents = []
    for i, doc in enumerate(retrieved_docs):
        if isinstance(doc.page_content, dict):
            content_str = json.dumps(doc.page_content, ensure_ascii=False)
        elif isinstance(doc.page_content, str):
            content_str = doc.page_content
        else:
            print(f"[ERROR] 예상치 못한 데이터 타입: {type(doc.page_content)}")
            content_str = str(doc.page_content)
        source_documents.append(content_str) # context로 추가

    if not source_documents:
        source_documents = ["No relevant documents found."]

    if isinstance(query, dict):
        query = json.dumps(query, ensure_ascii=False)

    try:
        answer = rag_chain.invoke(query)
    except Exception as e:
        print(f"[ERROR] rag_chain.invoke() 호출 중 오류 발생: {e}")
        return {
            "context": source_documents,
            "answer": "Error: Unable to generate answer."
        }

    response_json = { # 출력 형식에 맞춰 반환 
        "context": source_documents,
        "answer": answer
    }
    return response_json






'''
# 대화형 입력 루프
while True:
    query = input("질문 입력 : ")

    if query == "Done.":
        print("챗봇 종료!")
        break

    query_to_answer(query, rag_chain)
    print()
'''