import os
import glob
import pymupdf4llm
from langchain.text_splitter import MarkdownTextSplitter

# PDF를 Markdown으로 변환하고 청크로 나누는 함수
def process_pdf_to_chunks(pdf_path, chunk_size, chunk_overlap):
    """
    PDF 파일을 PyMuPDF4LLM을 사용해 Markdown으로 변환하고,
    MarkdownTextSplitter로 청크로 나눔.
    """
    try:
        # PDF를 Markdown으로 변환
        md_text = pymupdf4llm.to_markdown(pdf_path)

        # MarkdownTextSplitter 초기화
        splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # Markdown을 청크로 나누기
        documents = splitter.create_documents([md_text])
        return [doc.page_content for doc in documents]  # 청크 텍스트만 반환
    except Exception as e:
        print(f"오류 발생: {e}")
        return []

# 디렉토리 내 PDF 파일 처리 함수
def process_pdfs_in_directory(input_dir, chunk_size, chunk_overlap):
    """
    디렉토리 내 모든 PDF 파일을 처리하여 청크 데이터를 생성
    """
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))
    if not pdf_files:
        print(f"경고: {input_dir} 경로에서 PDF 파일을 찾을 수 없습니다.")
        return []

    print(f"\n=== 총 {len(pdf_files)}개의 PDF 파일 처리 시작 ===")
    all_chunks = []

    for i, pdf_file in enumerate(pdf_files, start=1):
        print(f"\n[{i}/{len(pdf_files)}] 처리 중: {os.path.basename(pdf_file)}")
        try:
            # PDF 처리 및 청크 생성
            chunks = process_pdf_to_chunks(pdf_file, chunk_size, chunk_overlap)
            all_chunks.extend(chunks)
            print(f"- 생성된 청크 수: {len(chunks)}")
        except Exception as e:
            print(f"!!! {pdf_file} 처리 중 오류 발생: {e}")
    
    print(f"\n=== 총 {len(pdf_files)}개의 PDF 처리 완료 ===")
    return all_chunks


'''
# 결과 저장 함수
def save_chunks_to_file(chunks, output_file):
    """
    생성된 청크를 텍스트 파일로 저장
    """
    with open(output_file, "w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(chunk + "\n\n")

'''