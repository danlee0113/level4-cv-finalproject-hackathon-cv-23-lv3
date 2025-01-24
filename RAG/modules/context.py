
import os
import pandas as pd
from langchain_text_splitters import RecursiveCharacterTextSplitter
from modules.extractor import table_to_json, table_to_readable_text
# 컨텍스트 생성 함수
def create_context_with_tables_optimized(results):
    """
    표와 텍스트를 포함한 컨텍스트 생성 (행/열 보존)
    """
    contexts = []
    
    for result in results:
        # 텍스트 처리
        text_content = []
        for text in result['texts']:
            text_content.append(f"[Page {text['page']}] {text['content']}")
        
        # 표 처리
        table_content = []
        for table in result['tables']:
            readable_text = table_to_readable_text(table_to_json(table['data']))
            table_desc = (
                f"[Table {table['table_number']} on Page {table['page']}]\n"
                f"{readable_text}"
            )
            table_content.append(table_desc)
        
        # 파일별 컨텍스트 결합
        file_context = {
            "text": "\n".join(text_content),
            "tables": table_content
        }
        contexts.append(file_context)
    
    return contexts

# 텍스트 및 표 청크 생성
def split_contexts_optimized(contexts, chunk_size=2000, chunk_overlap=200):
    """
    텍스트와 표 데이터를 분리하여 청크로 분할
    """
    text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    all_splits = []
    for context in contexts:
        # 텍스트 청크 분리
        text_chunks = text_splitter.split_text(context.get("text", ""))
        
        # 표 청크 분리
        table_chunks = []
        for table in context.get("tables", []):
            table_chunks.extend(text_splitter.split_text(table))
        
        # 텍스트와 표 청크를 통합
        all_splits.extend(text_chunks + table_chunks)
    
    return all_splits

# 결과 저장 함수
def save_results_to_excel(results, texts_split, output_directory):
    """
    추출된 결과와 청크를 엑셀 파일로 저장
    """
    os.makedirs(output_directory, exist_ok=True)
    
    for result in results:
        filename = result['filename'].replace('.pdf', '')
        excel_path = os.path.join(output_directory, f"{filename}_extracted2.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            # 표 저장
            for i, table in enumerate(result['tables']):
                sheet_name = f"Table_{i+1}_Page_{table['page']}"
                table['data'].to_excel(writer, sheet_name=sheet_name, index=False)
            
            # 텍스트 저장
            texts_df = pd.DataFrame(result['texts'])
            texts_df.to_excel(writer, sheet_name='Texts', index=False)
            
            # 청크 저장
            chunks_df = pd.DataFrame({"chunk": texts_split})
            chunks_df.to_excel(writer, sheet_name='Chunks', index=True)