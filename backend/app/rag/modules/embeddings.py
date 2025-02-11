import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))) # utils module을 인식하지 못해서 경로 추가.

from typing import Dict, List, Tuple
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings
from langchain_openai import ChatOpenAI

from utils.file_utils import fmt_txt
from modules.cluster import perform_clustering

import numpy as np
import pandas as pd
import json

LLM_INFO_DIR="/workspace/fastapi-server/app/rag/json_cache/llm_info.json"
EMBEDDING_INFO_DIR="/workspace/fastapi-server/app/rag/json_cache/embeddings_info.json"


BATCH_SIZE = 100  # 한 번에 처리할 텍스트 개수 (최대 토큰 에러가 나서 나누어서 처리해야 함)


def load_json(embed_dir, llm_dir):
    with open(embed_dir, "r") as f:
        embeddings_info = json.load(f)

    with open(llm_dir, "r") as f:
        llm_info = json.load(f)
    
    # Embeddings 초기화
    embeddings = OpenAIEmbeddings(model=embeddings_info["model"], disallowed_special=())
    
    # LLM 초기화
    llm = ChatOpenAI(
        model=llm_info["model_name"],
        temperature=llm_info["temperature"]
    )

    print("객체 재생성 완료!")

    return embeddings, llm


embeddings, llm =load_json(EMBEDDING_INFO_DIR, LLM_INFO_DIR)

def embed(texts: List[str]) -> np.ndarray:
    """
    주어진 텍스트 리스트를 임베딩 벡터로 변환합니다. (배치 처리 추가)

    Args:
        texts (List[str]): 임베딩할 텍스트 리스트

    Returns:
        np.ndarray: 텍스트의 임베딩 벡터를 포함하는 numpy 배열
                   shape은 (텍스트 개수, 임베딩 차원)입니다.
    """
    all_embeddings = []
    for i in range(0, len(texts), BATCH_SIZE): # batch 별로 텍스트 처리
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_embeddings = embeddings.embed_documents(batch_texts)
        all_embeddings.extend(batch_embeddings)

    # 임베딩을 numpy 배열로 변환
    text_embeddings_np = np.array(all_embeddings)
    return text_embeddings_np


def embed_cluster_texts(texts):
    text_embeddings_np = embed(texts) # 임베딩 생성
    cluster_labels = perform_clustering(text_embeddings_np, 10, 0.1)# 클러스터링 수행
    df = pd.DataFrame()
    df["text"] = texts # 원본 텍스트 저장
    df["embd"] = list(text_embeddings_np)# DataFrame에 리스트로 임베딩 저장
    df["cluster"] = cluster_labels
    return df

# 요약

def embed_cluster_summarize_texts(
    texts: List[str], level: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_clusters = embed_cluster_texts(texts)

    # 클러스터를 확장하여 새로운 DataFrame을 생성
    expanded_list = []
    for index, row in df_clusters.iterrows():
        for cluster in row["cluster"]:
            expanded_list.append(
                {"text": row["text"], "embd": row["embd"], "cluster": cluster}
            )
    expanded_df = pd.DataFrame(expanded_list)

    # 생성된 클러스터 수 확인
    all_clusters = expanded_df["cluster"].unique()
    print(f"--Generated {len(all_clusters)} clusters--")

    # LangChain을 사용한 요약 생성 템플릿
    template = """여기 LangChain 표현 언어 문서의 하위 집합이 있습니다.
    LangChain 표현 언어는 LangChain에서 체인을 구성하는 방법을 제공합니다.
    제공된 문서의 자세한 요약을 제공하십시오.
    문서:
    {context}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()

    # 각 클러스터별로 요약 생성
    summaries = []
    for i in all_clusters:
        df_cluster = expanded_df[expanded_df["cluster"] == i]
        formatted_txt = fmt_txt(df_cluster)  # 클러스터 내 텍스트를 포맷팅
        summaries.append(chain.invoke({"context": formatted_txt})) # LLM을 사용한 요약 생성

    # 요약 결과를 DataFrame으로 저장
    df_summary = pd.DataFrame(
        {
            "summaries": summaries,
            "level": [level] * len(summaries),
            "cluster": list(all_clusters),
        }
    )
    return df_clusters, df_summary


# 재귀적으로 텍스트를 클러스터링하고 요약하는 함수
def recursive_embed_cluster_summarize(  
    texts: List[str], level: int = 1, n_levels: int = 3
) -> Dict[int, Tuple[pd.DataFrame, pd.DataFrame]]:
    results = {}
    df_clusters, df_summary = embed_cluster_summarize_texts(texts, level)
    results[level] = (df_clusters, df_summary) # 결과 저장

    # 생성된 클러스터 수 확인
    unique_clusters = df_summary["cluster"].nunique()

    # 재귀적으로 요약 진행 (최대 n_levels까지)
    if level < n_levels and unique_clusters > 1:
        new_texts = df_summary["summaries"].tolist() # 현재 레벨에서 생성된 요약을 다음 레벨의 입력으로 사용
        next_level_results = recursive_embed_cluster_summarize(
            new_texts, level + 1, n_levels
        )
        results.update(next_level_results) # 재귀적으로 얻은 결과 합치기
    return results 
