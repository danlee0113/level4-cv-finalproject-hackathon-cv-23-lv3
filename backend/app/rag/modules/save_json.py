from langchain_openai import OpenAIEmbeddings
from langchain.embeddings import CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from langchain_openai import ChatOpenAI



CACHE_DIR= "/workspace/fastapi-server/app/rag/cache"
MODEL_NAME="gpt-4o-mini"
 



store = LocalFileStore(CACHE_DIR)

# embeddings 인스턴스를 생성
embeddings = OpenAIEmbeddings(model="text-embedding-3-small", disallowed_special=())

# CacheBackedEmbeddings 인스턴스를 생성
cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
    embeddings, store, namespace=embeddings.model
)


# llm 모델 초기화
llm = ChatOpenAI(
    model=MODEL_NAME, # "gpt-4o-mini"
    temperature=0,
)

## main.py와 embeddings.py에 필요한 llm, embeddings 변수를 json file로 저장. 

# Embeddings와 LLM의 설정 정보 저장
embeddings_info = {
    "model": "text-embedding-3-small",
    "namespace": "some_namespace",  # 필요한 추가 정보 포함
}

llm_info = {
    "model_name": MODEL_NAME,
    "temperature": 0,
}

# JSON 파일에 저장
import json

with open("/workspace/fastapi-server/app/rag/json_cache/embeddings_info.json", "w") as f:
    json.dump(embeddings_info, f)

with open("/workspace/fastapi-server/app/rag/json_cache/llm_info.json", "w") as f:
    json.dump(llm_info, f)

print("Embedding, LLM에 대한 정보 json 파일로 저장 완료!")

