from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_openai import ChatOpenAI


import pickle

CACHE_DIR= "/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/cache"
MODEL_NAME="gpt-4o-mini-2024-07-18"
LLM_PICKLE_DIR="/data/ephemeral/home/pickles/llm.pkl" # pickle 파일이 저장될 경로 (github에 올라가면 안됨.)
EMBEDDING_PICKLE_DIR="/data/ephemeral/home/pickles/embeddings.pkl" 



store = LocalFileStore(CACHE_DIR)

# embeddings 인스턴스를 생성
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", disallowed_special=())

# CacheBackedEmbeddings 인스턴스를 생성
cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
    embeddings, store, namespace=embeddings.model
)


# llm 모델 초기화
llm = ChatOpenAI(
    model=MODEL_NAME, # "gpt-4o-mini-2024-07-18"
    temperature=0,
)

## main.py와 embeddings.py에 필요한 llm, embeddings 변수를 pickle file로 저장. 

# Embeddings와 LLM의 설정 정보 저장
embeddings_info = {
    "model": "text-embedding-3-small",
    "namespace": "some_namespace",  # 필요한 추가 정보 포함
}

llm_info = {
    "model_name": "gpt-4o-mini-2024-07-18",
    "temperature": 0,
}

# JSON 파일에 저장
import json

with open("/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/json_cache/embeddings_info.json", "w") as f:
    json.dump(embeddings_info, f)

with open("/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/json_cache/llm_info.json", "w") as f:
    json.dump(llm_info, f)

print("Embedding, LLM에 대한 정보 json 파일로 저장 완료!")

