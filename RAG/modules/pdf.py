import os
import glob
from modules.extractor import extract_tables_with_camelot, extract_text_with_pdfplumber
# PDF에서 텍스트와 표 추출 함수
def extract_pdf_data(pdf_path):
    """
    PDF에서 텍스트는 pdfplumber, 표는 camelot으로 추출하여 통합
    """
    texts = extract_text_with_pdfplumber(pdf_path)
    tables = extract_tables_with_camelot(pdf_path)
    return {'texts': texts, 'tables': tables, 'filename': os.path.basename(pdf_path)}

# 디렉토리 내 PDF 파일 처리 함수
def process_multiple_pdfs(directory_path):
    """
    디렉토리 내 모든 PDF 파일을 처리하는 함수
    """
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    if not pdf_files:
        print(f"경고: {directory_path} 경로에서 PDF 파일을 찾을 수 없습니다.")
        return []
        
    print(f"\n=== 총 {len(pdf_files)}개의 PDF 파일 처리 시작 ===")
    all_results = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        filename = os.path.basename(pdf_file)
        print(f"\n[{i}/{len(pdf_files)}] 처리 중: {filename}")
        
        try:
            result = extract_pdf_data(pdf_file)
            all_results.append(result)
            
            print(f"- 추출된 표 개수: {len(result['tables'])}")
            print(f"- 추출된 텍스트 조각 수: {len(result['texts'])}")
            
            # 첫 번째 표 미리보기
            if result['tables']:
                print("\n첫 번째 표 미리보기:")
                print(result['tables'][0]['data'].head())
            
        except Exception as e:
            print(f"!!! {filename} 처리 중 오류 발생: {str(e)}")
            continue
            
    print(f"\n=== 총 {len(all_results)}/{len(pdf_files)} 개의 PDF 처리 완료 ===")
    return all_results