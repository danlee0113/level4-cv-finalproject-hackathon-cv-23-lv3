from pdf import process_pdfs_in_directory
from embeddings import recursive_embed_cluster_summarize, load_json
from langchain_community.vectorstores import FAISS

import time 

PDF_DIR="/data/ephemeral/home/dataset/"
DB_INDEX = "RAPTOR_CLAUDE_1_3500_400" 
pdf_directory = PDF_DIR # 데이터 위치 
LLM_INFO_DIR="/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/json_cache/llm_info.json"
EMBEDDING_INFO_DIR="/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/json_cache/embeddings_info.json"
BATCH_SIZE= 100


embeddings, llm=load_json(EMBEDDING_INFO_DIR, LLM_INFO_DIR)



# PDF 처리 및 청크 생성
texts_split = process_pdfs_in_directory(pdf_directory, chunk_size=3500, chunk_overlap=400)

# 트리 구축 (main)
leaf_texts = texts_split.copy()

# 재귀적으로 임베딩, 클러스터링 및 요약을 수행하여 결과를 얻음
results = recursive_embed_cluster_summarize(leaf_texts, level=1, n_levels=3)

# DB, VectorStore

all_texts = leaf_texts.copy()

# 레벨을 정렬하여 순회
for level in sorted(results.keys()):
    # 현재 레벨의 DataFrame에서 요약을 추출
    summaries = results[level][1]["summaries"].tolist()
    # 현재 레벨의 요약을 all_texts에 추가합니다.
    all_texts.extend(summaries)

# 이제 all_texts를 사용하여 FAISS vectorstore를 구축합니다.


# FAISS 초기화 (첫 번째 배치를 이용)
first_batch_texts = all_texts[:BATCH_SIZE]
first_batch_embeddings = embeddings.embed_documents(first_batch_texts)
vectorstore = FAISS.from_texts(texts=first_batch_texts, embedding=embeddings)

# 나머지 데이터 배치로 추가
for i in range(BATCH_SIZE, len(all_texts), BATCH_SIZE):
    batch_texts = all_texts[i:i + BATCH_SIZE]
    batch_embeddings = embeddings.embed_documents(batch_texts)
    vectorstore.add_texts(texts=batch_texts, embeddings=batch_embeddings)
    time.sleep(1)  # API Rate Limit을 피하기 위해 1초 대기

# 벡터스토어 저장
vectorstore.save_local(folder_path=DB_INDEX)