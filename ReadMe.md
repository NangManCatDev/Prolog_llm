# 🌟 Prolog_LLM 통합 프로젝트 🌟

## 🛠️ 개요
이 프로젝트는 **Prolog**와 **대형 언어 모델(LLM)**을 통합하여 자연어 이해를 통해 논리적 추론 작업을 수행하는 것을 목표로 합니다. 프로젝트의 핵심 파일은 `run.py`이며, Prolog 및 LLM과의 상호작용을 담당합니다. `run.py`에서 호출되는 주요 Python 스크립트와 함수들로 구성되어 있습니다.

---

## 📂 프로젝트 구조
### 핵심 파일
- **`run.py`**: Prolog-LLM 통합의 핵심 실행 파일로, 주요 논리 실행 및 데이터 처리를 담당.
- **호출되는 스크립트 및 함수**:
  - 📜 **`prolog_executor.py`**: Prolog 쿼리를 실행하고 결과를 반환.
  - 🛠️ **`query_to_prolog.py`**: 자연어 쿼리를 Prolog 형식으로 변환.
  - 💾 **`vectorstore.py`**: 데이터 저장 및 관리.
  - 🔄 **`vectorstore_to_prolog.py`**: 벡터 데이터를 Prolog 쿼리 형식으로 변환.

---

## 🚀 진행 상황
- **코드 구현**:
  - `run.py`를 중심으로 Prolog-LLM 통합을 위한 주요 기능 구현 완료.
  - Prolog 쿼리 실행 및 결과 반환 기능 정상 동작.
- **데이터 관리**:
  - 벡터 저장소와 Prolog 간의 데이터 변환 및 통합 완료.

---

## 🎯 다음 단계
1. **`run.py`**와 관련 스크립트의 테스트 케이스 확장.
2. `ReadMe.md` 파일에 **`run.py` 사용법**과 주요 기능 설명 추가.

---

## 📌 유지 관리자
- **NangManCatDev**  
- **저장소:** [Prolog_llm](https://github.com/NangManCatDev/Prolog_llm)

---

