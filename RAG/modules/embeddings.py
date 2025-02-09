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

LLM_INFO_DIR="/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/json_cache/llm_info.json"
EMBEDDING_INFO_DIR="/data/ephemeral/home/level4-cv-finalproject-hackathon-cv-23-lv3/RAG/json_cache/embeddings_info.json"


BATCH_SIZE = 100  # 한 번에 처리할 텍스트 개수


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
    for i in range(0, len(texts), BATCH_SIZE):
        batch_texts = texts[i:i+BATCH_SIZE]
        batch_embeddings = embeddings.embed_documents(batch_texts)
        all_embeddings.extend(batch_embeddings)

    # 임베딩을 numpy 배열로 변환
    text_embeddings_np = np.array(all_embeddings)
    return text_embeddings_np


def embed_cluster_texts(texts):
    # 임베딩 생성
    text_embeddings_np = embed(texts)
    # 클러스터링 수행
    cluster_labels = perform_clustering(text_embeddings_np, 10, 0.1)
    # 결과를 저장할 DataFrame 초기화
    df = pd.DataFrame()
    # 원본 텍스트 저장
    df["text"] = texts
    # DataFrame에 리스트로 임베딩 저장
    df["embd"] = list(text_embeddings_np)
    # 클러스터 라벨 저장
    df["cluster"] = cluster_labels
    return df

# 요약
# (나머지 코드는 변경하지 않았어요)

def embed_cluster_summarize_texts(
    texts: List[str], level: int
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_clusters = embed_cluster_texts(texts)
    expanded_list = []
    for index, row in df_clusters.iterrows():
        for cluster in row["cluster"]:
            expanded_list.append(
                {"text": row["text"], "embd": row["embd"], "cluster": cluster}
            )
    expanded_df = pd.DataFrame(expanded_list)
    all_clusters = expanded_df["cluster"].unique()
    print(f"--Generated {len(all_clusters)} clusters--")

    template = """여기 LangChain 표현 언어 문서의 하위 집합이 있습니다.
    LangChain 표현 언어는 LangChain에서 체인을 구성하는 방법을 제공합니다.
    제공된 문서의 자세한 요약을 제공하십시오.
    문서:
    {context}
    """
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm | StrOutputParser()

    summaries = []
    for i in all_clusters:
        df_cluster = expanded_df[expanded_df["cluster"] == i]
        formatted_txt = fmt_txt(df_cluster)
        summaries.append(chain.invoke({"context": formatted_txt}))

    df_summary = pd.DataFrame(
        {
            "summaries": summaries,
            "level": [level] * len(summaries),
            "cluster": list(all_clusters),
        }
    )
    return df_clusters, df_summary


def recursive_embed_cluster_summarize(  
    texts: List[str], level: int = 1, n_levels: int = 3
) -> Dict[int, Tuple[pd.DataFrame, pd.DataFrame]]:
    results = {}
    df_clusters, df_summary = embed_cluster_summarize_texts(texts, level)
    results[level] = (df_clusters, df_summary)
    unique_clusters = df_summary["cluster"].nunique()
    if level < n_levels and unique_clusters > 1:
        new_texts = df_summary["summaries"].tolist()
        next_level_results = recursive_embed_cluster_summarize(
            new_texts, level + 1, n_levels
        )
        results.update(next_level_results)
    return results 
