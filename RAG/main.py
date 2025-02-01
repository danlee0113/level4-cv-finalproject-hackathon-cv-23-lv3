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
import pickle
import warnings

PDF_DIR="/data/ephemeral/home/dataset/SKHynix"
DB_INDEX = "RAPTOR_CLAUDE_1"
DOTENV_PATH="/data/ephemeral/home/.env"
PROJECT_NAME="hackathon-module"

LLM_INFO_DIR="/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/json_cache/llm_info.json"
EMBEDDING_INFO_DIR="/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/json_cache/embeddings_info.json"

embeddings, llm=load_json(EMBEDDING_INFO_DIR, LLM_INFO_DIR)




# 경고 메시지 무시
warnings.filterwarnings("ignore")

# API 키 정보 로드
load_dotenv(dotenv_path=DOTENV_PATH)

# 프로젝트 이름을 입력합니다.
logging.langsmith(PROJECT_NAME)


# FAISS 인덱스 로드
index = faiss.read_index(f"{DB_INDEX}/index.faiss")

# FAISS 저장된 메타데이터 로드
with open(f"{DB_INDEX}/index.pkl", "rb") as f:
    metadata = pickle.load(f)

docstore, index_to_docstore_id = metadata
# FAISS 벡터스토어 재구성 (올바른 방식)
vectorstore = FAISS(embedding_function=embeddings, index=index, docstore=docstore, index_to_docstore_id=index_to_docstore_id)



# retriever 생성 (main)
retriever = vectorstore.as_retriever(search_kwargs={"k": 10})


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
        - Example financial terms include: "세전", "세후", "계속사업이익", "사업이익".
        - Pay attention to whether the question includes specific terms like "세전", "세후", or "계속사업이익".
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

# RAG 체인 정의
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)


query="SK하이닉스는 HBM CAPA가 거의 다 Sold Out된 상황에서, 2025년 추가적인 수요에 어떻게 대응할 계획인가요?"

def query_to_answer(query,rag_chain):
    '''
    Chat-GPT처럼 한 번에 답변이 나오지 않고 되는대로 출력을 하기를 원하면 stream을 return하고,
    한 번에 출력하기를 원하면 answer를 return해야 함.
    답변이 길면 stream 방식이 더 적합해 stream return하기로 결정.
    '''
    answer = rag_chain.stream(query)
    stream_response(answer)
    return stream_response(answer)



query_to_answer(query, rag_chain)