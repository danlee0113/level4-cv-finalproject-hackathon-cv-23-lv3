import pandas as pd
import pdfplumber
import camelot
import json


# 표 데이터 정리 함수
def clean_table(df):
    """
    표 데이터 정리 (빈 값 제거 및 공백 정리)
    """
    if df is None:
        return pd.DataFrame()
    
    # 빈 행/열 제거
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)
    
    # 문자열의 공백 및 줄바꿈 제거
    df = df.applymap(lambda x: " ".join(str(x).split()) if isinstance(x, str) else x)
    return df

# 텍스트 추출 함수 (pdfplumber)
def extract_text_with_pdfplumber(pdf_path):
    """
    pdfplumber를 사용하여 PDF에서 텍스트를 추출
    """
    texts = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text_content = page.extract_text()
                if text_content:
                    texts.append({'content': text_content.strip(), 'page': page_num})
    except Exception as e:
        print(f"pdfplumber 오류: {e}")
    return texts

# 표 추출 함수 (camelot)
def extract_tables_with_camelot(pdf_path):
    """
    camelot을 사용하여 PDF에서 표를 추출
    """
    tables = []
    try:
        table_list = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
        for i, table in enumerate(table_list):
            df = table.df.applymap(lambda x: x.replace("\n", " ") if isinstance(x, str) else x)
            tables.append({
                'table_number': i + 1,
                'page': table.parsing_report['page'],
                'data': clean_table(df)
            })
    except Exception as e:
        print(f"camelot 오류: {e}")
    return tables

# 표 데이터를 JSON 형태로 변환
def table_to_json(table):
    """
    표 데이터를 JSON 형식으로 변환
    """
    return table.to_json(orient="split", force_ascii=False)  # 행/열 정보 유지

# JSON 데이터를 사람이 읽기 쉬운 텍스트로 변환
def table_to_readable_text(json_data):
    """
    JSON 데이터를 사람이 읽기 쉬운 텍스트로 변환
    """
    parsed = json.loads(json_data)
    columns = parsed["columns"]
    data = parsed["data"]
    
    # 컬럼 출력
    readable_text = "|".join(map(str,columns)) + "\n"
    readable_text += "-" * (len(columns) * 10) + "\n"
    
    # 행 출력
    for row in data:
        readable_text += "|".join(map(str, row)) + "\n"
    
    return readable_text


