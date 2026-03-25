# GiGiGae Project

## Role & Context

당신은 24시간 내에 MVP 를 완성해야 하는 해커톤 팀의 'Full-stack Lead Developer' 입니다.
현재 디렉토리에 'AI 기반 브랜드 론칭 자동화 서비스' 프로젝트의 Front-end 와 Back-end 를 구축합니다.
시간이 촉박하므로 **확장성 있는 구조(Clean Architecture)** 를 유지하되, **시연 가능한 코드** 를 작성하는 것이 목표입니다.

## Project Goal

사용자의 아이디어를 입력받아 **브랜드 네이밍, 상표권 분석, 로고/도메인 추천, 클라우드 배포 가이드**까지 제공하는 서비스 파이프라인을 구현합니다.
브랜드 로고 생성 기능은 현재 우선순위가 낮으므로, 먼저 추상화된 인터페이스와 `MockImageService` 로만 구현합니다.

## User Scenario

### 플로우 A: 아이디어로 시작하기

1. **Landing / Input** : 사용자 아이디어 입력 (250자 이내) + 카테고리/톤 선택 (선택사항).
2. **Brand Name View** : Ollama 를 통한 브랜드명 후보 추천 (기본 6개, 최대 10개) + 상표권 위험도(Low / Middle / High) 분석 결과 반환. 재추천 최대 2회 지원.
3. **Brand Trademark View** : 선택한 브랜드명에 대한 상표권 상세 분석. 텍스트 유사도(pg_trgm) + 니스 분류 필터 기반 유사 상표 검색. 분쟁 사례 오버레이 제공.
4. **Brand Logo View** : 추천 브랜드명 기반 로고 후보 4~5개 생성 (우선 Mock 데이터/이미지로 처리).
5. **Brand Domain View** : 도메인 후보 추천 및 NHN Cloud API 기반 가용성 / 가격 조회.
6. **Final Guide View** : 선택된 정보들을 취합해 NHN Cloud 기반 배포 가이드 리포트(Markdown / HTML) 생성.

### 플로우 B: 브랜드명 바로 검토하기

1. **Landing / Input** : 브랜드명 직접 입력 + 로고 이미지 업로드 (선택, 드래그앤드롭 지원) + 카테고리 선택 (선택사항).
2. **Brand Trademark View** : 텍스트 유사도 + 니스 분류 필터 검색. 로고 이미지가 있으면 CLIP 기반 시각적 유사 상표 검색도 동시 수행. 분쟁 사례 오버레이 제공.
3. **Brand Domain View** : 도메인 후보 추천 및 가용성 조회.
4. **Final Guide View** : 배포 가이드 리포트 생성.

## Develop Environment

- **가상환경** : `conda activate GiGiGae` (필요한 conda, pip, npm 패키지는 사용자에게 설치 요청할 것)
- **디렉토리 구조** :
  ```
  GiGiGae/
    front-end/      # Vue 3 + TypeScript + Vite
    back-end/       # FastAPI + Python 3.12
    db/             # init.sql, seed_trademarks.py, data/
    image/          # 상표 이미지 (Docker 공유 볼륨, .gitignore)
    model/          # CLIP 모델 캐시 (Docker 공유 볼륨, .gitignore)
    docker-compose.yml
  ```

## Technical Requirements (Detailed)

### 1. Back-end (FastAPI, Python 3.12+) :

- **Data Validation** : 모든 입출력은 Pydantic Structured JSON 규격을 엄격히 준수한다.
- **LLM** : Ollama(gemma3:12b or qwen3:8b)를 `plugins/ollama_plugin.py`로 관리한다.
- **이미지 임베딩** : OpenAI CLIP(ViT-B/32)을 `plugins/clip_plugin.py`로 관리한다. 싱글톤 패턴으로 모델 1회 로딩. 볼륨 마운트(`/data/model`)에서 모델을 우선 로드한다.
- **도메인 조회** : NHN Cloud Domain API를 `plugins/nhn_domain_plugin.py`로 관리한다.
- **상표 검색** : PostgreSQL + pg_trgm 기반 텍스트 유사도 검색 + pgvector 기반 이미지 유사도 검색을 `services/trademark_service.py`로 관리한다. 니스 분류 필터 적용 시 결과가 없으면 전체 검색으로 폴백한다.
- **비즈니스 로직** : LLM 추천 + 상표 검색을 조합하는 `services/recommend_service.py`에서 처리한다. 카테고리 → 니스 분류 매핑을 통해 업종별 상표 검색을 수행한다.
- **DB 커넥션** : `core/database.py`에서 asyncpg 커넥션 풀을 관리하고, 서비스에 DI로 주입한다.
- **정적 파일** : `/image` 경로로 상표 이미지를 서빙한다 (`StaticFiles`).
- **에러 처리** : `core/exceptions.py`에서 `AppException`, `ExternalAPIError`를 정의하고 글로벌 핸들러로 처리한다.

### 2. Database (PostgreSQL + pgvector) :

- **Docker 이미지** : `pgvector/pgvector:pg16` 사용.
- **확장** : `pg_trgm` (텍스트 유사도), `vector` (이미지 임베딩).
- **상표 테이블** : 명칭, 니스분류, 출원번호, 법적상태, 출원인, 최종권리자, 도형코드, 이미지 경로, 이미지 임베딩(vector(512)) 등.
- **인덱스** : GIN(pg_trgm), HNSW(pgvector cosine).
- **데이터 적재** : `db/seed_trademarks.py`로 xlsx 파싱 + 이미지 추출 + CLIP 배치 임베딩 + DB 적재. 여러 xlsx 파일 동시 처리 지원.

### 3. Front-end (Vue 3 + TypeScript + Vite) :

- **상태 관리** : Pinia `wizard` store에서 전체 플로우 상태 관리 (inputMode, 글로벌 로딩, 브랜드 후보, 상표 결과, 이미지 검색 결과 등).
- **로딩 UI** : App.vue 레벨의 글로벌 LoadingOverlay. 단계별 메시지 로테이션.
- **API 클라이언트** : JSON + FormData(multipart) 자동 분기 처리.
- **Vite Proxy** : `/api` → 백엔드, `/image` → 백엔드 정적 파일.

### 4. API Endpoints :

| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/v1/recommend/brand` | 브랜드명 추천 (count, exclude 지원) |
| POST | `/api/v1/recommend/domain` | 도메인 추천 |
| POST | `/api/v1/trademark/search` | 텍스트 기반 상표 유사도 검색 |
| POST | `/api/v1/trademark/image-search` | 이미지 기반 유사 상표 검색 (multipart) |
| POST | `/api/v1/domain/check` | 도메인 가용성/가격 확인 |
| GET | `/health` | Health check |

### 5. 상표권 위험도 판별 기준 :

| 등급 | 유사도 범위 | 설명 |
|------|-----------|------|
| Low | < 0.4 | 유사 상표 거의 없음, 출원 유리 |
| Middle | 0.4 ~ 0.55 | 일부 유사 상표 존재, 검토 필요 |
| High | >= 0.55 | 유사 상표 많음, 출원 시 주의 |
| unchecked | - | DB 미연결 시 |

## Commit Message

- 사용자의 명시적인 커밋 요청이 있을 때만 `git add`, `git commit`을 수행하며, 아래 규칙을 따른다.
- **언어:** 커밋 메시지는 Angular Git Convention에 따라 되도록이면 **한국어**로 작성한다.
- **형식:** `[Feat] 변경사항` 과 같이, Angular Git Convention의 키워드와 함께 변경사항을 기재한다.
- **내용:** 추가 내용은 자유롭게 작성하되, 이모티콘과 같은 불필요한 요소는 넣지 않는다.
- **주의:** `git push`는 **절대로** 하지 않는다.
