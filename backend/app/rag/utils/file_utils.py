import pandas as pd
from langchain_core.messages import AIMessageChunk


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


def format_docs_for_eval(docs):
    tokens = []
    for doc in docs:
        # 각 문서에 대해 AIMessageChunk 객체를 생성합니다.
        token = AIMessageChunk(content=f"<document>{doc.page_content}</document>")
        # 문서 조각 정보를 token에 추가합니다.
        token.source_document = doc
        tokens.append(token)
    
    print("Formatted Documents for Evaluation (Contexts):")
    for token in tokens:
        print(token.content)
    return tokens