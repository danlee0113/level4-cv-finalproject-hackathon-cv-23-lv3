import pandas as pd
from modules.cluster import perform_clustering
from langchain_openai import ChatOpenAI


def fmt_txt(df: pd.DataFrame) -> str:
    """
    주어진 DataFrame에서 텍스트 문서를 단일 문자열로 포맷팅하는 함수입니다.

    Args:
        df (pd.DataFrame): 포맷팅할 텍스트 문서를 포함한 DataFrame

    Returns:
        str: 텍스트 문서들을 특정 구분자로 결합한 단일 문자열
    """
    unique_txt = df["text"].tolist()
    return "--- --- \n --- --- ".join(unique_txt)


def format_docs(docs):
    formatted = "\n\n".join(f"<document>{doc.page_content}</document>" for doc in docs)
    print("Formatted Documents (Contexts):")
    print(formatted)  # 포맷팅된 컨텍스트 출력
    return formatted
