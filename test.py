import os
import warnings
from langchain_ollama import OllamaLLM
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

# Prolog
import re
import subprocess
from pyswip import Prolog

# Info: 최종수정: 2025-01-03, 수정자: NangManCat
# Note: 해당 코드는 PDF 파일을 OCR(이미지 기반 PDF를 읽는 라이브러리)를 사용하여 읽고 vectorstore을 생성한 다음,
# Note: 사전에 작업한 rule.txt(건강검진 결과에 따른 판단 기준이 작성된 txt파일) 또한 읽고 merge하여 사전 학습을 시킨 다음,
# Note: doc/doc2.pdf 파일을 읽고 그것을 prolog 언어로 바꾸고,
# Note: 바꾸어진 Prolog 언어는 process_prolog_code 함수를 통해 후처리 되어 적합한 Prolog언어로 바뀌어,
# Note: prolog/output.pl로 저장되는 코드입니다.

# BUG: merge시 오히려 RAG 효과가 떨어지는 문제가 발생
# BUG: OCR된 결과를 Gemma가 제대로 처리하지 못하는 문제가 발생

# Fixme: 이미지 기반 PDF를 읽히는 대신(OCR), 텍스트 기반 파일을 읽히는 것으로 변경


# Prolog 구문 후처리 함수
def process_prolog_code(prolog_code):
    processed_lines = []
    for line in prolog_code.split("\n"):
        line = line.strip()  # 양쪽 공백 제거
        if not line:
            continue  # 빈 줄은 건너뛰기

        # 문자열과 특수문자 처리
        line = re.sub(r"([\w가-힣]+)", r"'\1'", line)  # 문자열을 작은따옴표로 감싸기
        line = re.sub(r"\s*,\s*", ",", line)  # 콤마 양쪽 공백 제거

        # 문장 끝에 . 추가 (이미 있다면 중복 방지)
        if not line.endswith("."):
            line += "."

        processed_lines.append(line)
    return "\n".join(processed_lines)


# PDF 경로 및 OCR 처리
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()  # 텍스트 레이어 추출
        if text.strip():
            full_text += text
        else:
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            text = pytesseract.image_to_string(img, lang="kor")  # 한국어 OCR
            full_text += text

    return full_text


# PDF 로드 및 텍스트 추출
pdf_path = "doc/doc2.pdf"
if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"PDF 파일 {pdf_path}을 찾을 수 없습니다.")

extracted_text = extract_text_from_pdf(pdf_path)

# 텍스트 분리
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
)
docs = text_splitter.create_documents([extracted_text])

# 임베딩 생성
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cuda"},
    encode_kwargs={"normalize_embeddings": True},
)

# 벡터 저장소 초기화 및 저장
vectorstore_path = "vectorstore"
os.makedirs(vectorstore_path, exist_ok=True)
vectorstore = Chroma.from_documents(
    docs, embeddings, persist_directory=vectorstore_path
)
vectorstore.persist()
print("Vectorstore created and persisted.")

# 모델 설정
llm = OllamaLLM(
    model="gemma2:latest",
    temperature=0,
    callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
)

# 검색기 초기화
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# Prompt 템플릿
template = """
You are an AI assistant that specializes in converting text from documents into Prolog statements. Analyze the context carefully and convert it into accurate Prolog code. Ensure that numerical values or descriptive text are directly taken from the context without assumptions. Do not include explanations or emphasis, and only return plain Prolog statements.

Context:
{context}

Instruction:
Convert the above context into Prolog statements, ensuring accurate representation without adding inferred data.

Prolog Code:
"""

prompt = ChatPromptTemplate.from_template(template)


# 문서 포맷 함수
def format_docs(docs):
    return "\n\n".join([d.page_content for d in docs])


# RAG 체인 설정
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 질문 처리
query = "내 건강검진결과서를 prolog어로 바꿔줘"
answer = rag_chain.invoke(query)

# print("Query:", query)
# print("Answer:", answer)

# Prolog 코드 후처리
formatted_answer = process_prolog_code(answer)

# 출력 파일 경로 설정
output_dir = "prolog"
output_file = os.path.join(output_dir, "output.pl")

# 폴더가 없으면 생성
os.makedirs(output_dir, exist_ok=True)

# 파일에 저장
with open(output_file, "w", encoding="utf-8") as file:
    file.write(answer)

print(f"Answer saved to {output_file}")

# Prolog 실행
try:
    # Prolog 명령 실행
    prolog_command = f"swipl -s {output_file} -g halt"
    subprocess.run(prolog_command, shell=True, check=True)
    print(f"Prolog file {output_file} consulted successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error occurred while consulting Prolog file: {e}")
