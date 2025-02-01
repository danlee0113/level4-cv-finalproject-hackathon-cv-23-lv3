from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_openai import ChatOpenAI


import pickle

CACHE_DIR= "/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/cache"
MODEL_NAME="gpt-4o-mini-2024-07-18"
 



store = LocalFileStore(CACHE_DIR)

# embeddings 인스턴스를 생성
embeddings = OpenAIEmbeddings(model="text-embedding-3-large", disallowed_special=())

# CacheBackedEmbeddings 인스턴스를 생성
cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
    embeddings, store, namespace=embeddings.model
)


# llm 모델 초기화
llm = ChatOpenAI(
    model=MODEL_NAME, # "gpt-4o-mini-2024-07-18"
    temperature=0,
)

## main.py와 embeddings.py에 필요한 llm, embeddings 변수를 json file로 저장. 

# Embeddings와 LLM의 설정 정보 저장
embeddings_info = {
    "model": "text-embedding-3-large",
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

