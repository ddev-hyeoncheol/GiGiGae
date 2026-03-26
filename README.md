# NameCraft AI

AI 기반 브랜드 론칭 자동화 서비스. 사용자의 아이디어를 입력받아 브랜드 네이밍, 상표권 분석, 도메인 추천, 클라우드 배포 가이드까지 제공하는 올인원 플랫폼입니다.

## 주요 기능

### 1. 브랜드명 추천
- 사용자 아이디어를 Ollama LLM으로 분석하여 창의적인 브랜드명 후보 추천
- 기본 4개, 최대 10개까지 추천 가능
- 재추천 최대 2회 지원 (중복 제외)
- 각 후보에 대한 설명 및 태그 제공

### 2. 상표권 분석
- PostgreSQL + pg_trgm 기반 텍스트 유사도 검색
- 니스 분류 필터를 통한 업종별 상표 분석
- CLIP 이미지 임베딩을 활용한 시각적 유사 상표 검색
- 상표권 위험도 판별 (상표 안심 / 상표 주의 / 상표 위험)
- 분쟁 사례 오버레이 제공

### 3. 도메인 추천 및 가용성 조회
- 브랜드명 기반 도메인 후보 자동 생성
- NHN Cloud Domain API를 활용한 실시간 가용성 및 가격 조회
- 다양한 TLD 옵션 지원 (.com, .co.kr, .kr, .net 등)

### 4. 클라우드 배포 가이드
- NHN Cloud 기반 4단계 서비스 론칭 가이드
  1. DNS Plus (도메인 관리)
  2. Object Storage (콘텐츠 저장소)
  3. Email (이메일 서비스)
  4. Certificate Manager (SSL/TLS 인증서)
- KIPRIS 상표 출원 링크 제공

## 기술 스택

### Backend
- **프레임워크**: FastAPI (Python 3.12+)
- **API 서버**: Uvicorn
- **데이터 검증**: Pydantic
- **데이터베이스**: PostgreSQL + pgvector (pg_trgm, vector 확장)
- **비동기**: asyncpg
- **LLM**: Ollama (gemma3:4b)
- **이미지 임베딩**: CLIP (ViT-B/32)

### Database
- **이미지**: pgvector/pgvector:pg16
- **확장**: pg_trgm (텍스트 유사도), vector (이미지 임베딩)
- **인덱스**: GIN(pg_trgm), HNSW(pgvector cosine)

### Frontend
- **프레임워크**: Vue 3 (Composition API + TypeScript)
- **빌드 도구**: Vite
- **상태 관리**: Pinia
- **라우팅**: Vue Router

### Infrastructure
- **컨테이너화**: Docker Compose
- **외부 API**: NHN Cloud Domain API

## 디렉토리 구조

```
GiGiGae/
├── back-end/                  # FastAPI 백엔드
│   ├── app/
│   │   ├── api/              # 엔드포인트 라우터
│   │   │   ├── recommend.py
│   │   │   ├── trademark.py
│   │   │   └── domain.py
│   │   ├── schemas/          # Pydantic 데이터 모델
│   │   │   ├── recommend.py
│   │   │   ├── trademark.py
│   │   │   └── domain.py
│   │   ├── services/         # 비즈니스 로직
│   │   │   ├── recommend_service.py
│   │   │   ├── trademark_service.py
│   │   │   └── domain_service.py
│   │   ├── plugins/          # 외부 도구 플러그인
│   │   │   ├── ollama_plugin.py
│   │   │   ├── clip_plugin.py
│   │   │   └── nhn_domain_plugin.py
│   │   ├── core/             # 핵심 설정 및 유틸
│   │   │   ├── config.py
│   │   │   ├── constants.py
│   │   │   ├── exceptions.py
│   │   │   └── database.py
│   │   ├── utils/            # 공통 유틸리티
│   │   │   ├── prompts.py
│   │   │   └── logger.py
│   │   └── main.py
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── .env.example
│   └── back-end.md
│
├── front-end/                 # Vue 3 프론트엔드
│   ├── src/
│   │   ├── api/              # API 클라이언트
│   │   │   ├── client.ts
│   │   │   ├── recommend.ts
│   │   │   ├── trademark.ts
│   │   │   ├── domain.ts
│   │   │   ├── types.ts
│   │   │   └── index.ts
│   │   ├── stores/           # Pinia 상태 관리
│   │   │   └── wizard.ts
│   │   ├── components/       # Vue 컴포넌트
│   │   │   ├── AppLogo.vue
│   │   │   ├── ChipSelect.vue
│   │   │   ├── LoadingOverlay.vue
│   │   │   ├── NavButtons.vue
│   │   │   ├── PageHeader.vue
│   │   │   ├── StepIndicator.vue
│   │   │   ├── DarkModeToggle.vue
│   │   │   ├── TrademarkChecklist.vue
│   │   │   └── TrademarkMatchTable.vue
│   │   ├── views/            # 페이지 뷰
│   │   │   ├── HomeView.vue
│   │   │   ├── BrandNameView.vue
│   │   │   ├── BrandTrademarkView.vue
│   │   │   ├── BrandDomainView.vue
│   │   │   └── FinalGuideView.vue
│   │   ├── composables/      # Vue Composables
│   │   │   ├── useDarkMode.ts
│   │   │   └── useTrademarkChecklist.ts
│   │   ├── utils/            # 유틸리티
│   │   │   └── niceClassMapping.ts
│   │   ├── App.vue
│   │   ├── main.ts
│   │   └── style.css
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── .env.example
│   └── front-end.md
│
├── db/                        # 데이터베이스
│   ├── init.sql              # 초기 스키마
│   ├── seed_trademarks.py    # 데이터 적재 스크립트
│   ├── data/                 # 상표 데이터 (xlsx)
│   └── pgdata/               # PostgreSQL 데이터 (Docker 볼륨)
│
├── image/                     # 상표 이미지 (Docker 공유 볼륨)
├── model/                     # CLIP 모델 캐시 (Docker 공유 볼륨)
│
├── docker-compose.yml         # Docker Compose 설정
├── CLAUDE.md                  # 프로젝트 명세
└── README.md                  # 이 파일
```

## 사용자 시나리오

### 플로우 A: 아이디어로 시작하기

1. **입력**: 사용자 아이디어 입력 (250자 이내) + 카테고리/톤 선택 (선택사항)
2. **브랜드명 추천**: Ollama를 통한 브랜드명 후보 추천 + 상표권 위험도 분석
3. **상표 분석**: 선택한 브랜드명에 대한 상세 상표 분석
4. **도메인 조회**: 도메인 후보 추천 및 가용성 확인
5. **최종 가이드**: 선택된 정보 취합 및 NHN Cloud 배포 가이드 생성

### 플로우 B: 브랜드명 직접 검토하기

1. **입력**: 브랜드명 직접 입력 + 로고 이미지 업로드 (선택, 드래그앤드롭 지원) + 카테고리 선택 (선택사항)
2. **상표 분석**: 텍스트 유사도 + 니스 분류 필터 검색. 로고 이미지가 있으면 CLIP 기반 시각적 유사 상표 검색도 동시 수행
3. **도메인 조회**: 도메인 후보 추천 및 가용성 확인
4. **최종 가이드**: 배포 가이드 리포트 생성

## 빠른 시작

### 필수 환경

- Docker & Docker Compose
- Python 3.12+ (로컬 개발 시)
- Node.js 18+ (프론트엔드 개발 시)
- Ollama (별도 실행, Docker 호스트에서 포트 11434로 접근 가능)

### 1. 저장소 클론 및 환경 설정

```bash
git clone <repository-url>
cd GiGiGae

# 환경 변수 파일 생성
cp back-end/.env.example back-end/.env
cp front-end/.env.example front-end/.env
```

### 2. 환경 변수 설정

**back-end/.env**
```
DB_PASSWORD=<your-secure-password>
OLLAMA_BASE_URL=http://host.docker.internal:11434
NHN_DOMAIN_API_KEY=<your-nhn-api-key>
NHN_DOMAIN_API_SECRET=<your-nhn-api-secret>
DEBUG=true
```

**front-end/.env**
```
API_URL=http://localhost:9000
```

### 3. Docker Compose로 실행

```bash
docker-compose up -d
```

서비스가 실행되면:
- 프론트엔드: http://localhost:5173
- 백엔드 API: http://localhost:9000
- PostgreSQL: localhost:5432

### 4. 데이터베이스 초기화

```bash
# 데이터 적재 (선택사항)
docker exec back-end python db/seed_trademarks.py
```

## API 엔드포인트

### 브랜드 추천

```
POST /api/v1/recommend/brand
Content-Type: application/json

{
  "brand_idea": "string (최대 250자)",
  "brand_category": "string?",
  "brand_tone": "string?",
  "count": "integer? (기본: 4, 최대: 10)",
  "exclude": "string[]?"
}
```

**응답**
```json
{
  "brand_candidates": [
    {
      "brand_name": "string",
      "brand_description": "string",
      "brand_tags": ["string"],
      "trademark": {
        "risk": "Low | Middle | High | unchecked",
        "match_count": "integer"
      }
    }
  ]
}
```

### 상표 검색

```
POST /api/v1/trademark/search
Content-Type: application/json

{
  "brand_name": "string",
  "nice_classes": "integer[]?",
  "threshold": "float?"
}
```

**응답**
```json
{
  "brand_name": "string",
  "risk": "Low | Middle | High | unchecked",
  "matches": [
    {
      "trademark_name": "string",
      "nice_class": "integer",
      "similarity": "float (0.0~1.0)",
      "image_path": "string?"
    }
  ]
}
```

### 도메인 추천

```
POST /api/v1/recommend/domain
Content-Type: application/json

{
  "brand_name": "string",
  "exclude": "string[]?"
}
```

**응답**
```json
{
  "domain_candidates": [
    {
      "domain_name": "string",
      "domain_reason": "string"
    }
  ]
}
```

### 도메인 가용성 확인

```
POST /api/v1/domain/check
Content-Type: application/json

{
  "domain_name": "string"
}
```

**응답**
```json
{
  "domain_name": "string",
  "available": "boolean",
  "message": "string",
  "price": "integer?",
  "promotion_price": "integer?"
}
```

### 이미지 상표 검색

```
POST /api/v1/trademark/image-search
Content-Type: multipart/form-data

file: <image-file>
```

**응답**
```json
{
  "matches": [
    {
      "trademark_name": "string",
      "similarity": "float (0.0~1.0)",
      "nice_class": "integer",
      "image_path": "string?"
    }
  ]
}
```

### Health Check

```
GET /health
```

**응답**
```json
{
  "status": "ok"
}
```

## 상표권 위험도 판별 기준

| 레벨 | 유사도 범위 | 설명 |
|------|-----------|------|
| Low (상표 안심) | < 0.4 | 유사 상표 거의 없음, 출원 유리 |
| Middle (상표 주의) | 0.4 ~ 0.55 | 일부 유사 상표 존재, 검토 필요 |
| High (상표 위험) | >= 0.55 | 유사 상표 많음, 출원 시 주의 |
| unchecked (미확인) | - | 데이터베이스 미연결 시 |

## 개발 가이드

### 로컬 환경 설정

```bash
# 백엔드 개발 (Python 3.12+ 필수)
cd back-end
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 9000

# 프론트엔드 개발 (Node.js 18+ 필수)
cd front-end
npm install
npm run dev
```

### Docker에서 개발

```bash
# 볼륨 마운트로 라이브 리로드 지원
docker-compose up -d

# 로그 확인
docker-compose logs -f back-end
docker-compose logs -f front-end
```

### 데이터베이스 마이그레이션

```bash
# 컨테이너 접근
docker exec -it db psql -U gigigae -d gigigae

# SQL 실행
\i /docker-entrypoint-initdb.d/init.sql
```

## 프로젝트 구조 및 설계 원칙

### Clean Architecture

- **Separation of Concerns**: API, Services, Plugins, Core로 계층 분리
- **Dependency Injection**: FastAPI와 Pinia를 통한 DI 패턴
- **Plugin Architecture**: Ollama, CLIP, NHN Cloud API를 플러그인으로 관리
- **Error Handling**: 전역 예외 처리기로 규격화된 에러 응답

### 비동기 처리

- **asyncpg**: PostgreSQL 비동기 커넥션 풀
- **asyncio.gather**: 브랜드 추천 후 상표 검색 병렬 실행

### 상태 관리

- **Pinia**: 위자드 전체 상태를 단일 `wizard` store에서 관리
- **로딩 UI**: App.vue 레벨의 글로벌 LoadingOverlay

## 문제 해결

### 백엔드 연결 안 됨

```
"서버에 연결할 수 없습니다. 백엔드가 실행 중인지 확인해주세요."
```

**해결:**
```bash
# 백엔드 서비스 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs back-end

# 재시작
docker-compose restart back-end
```

### Ollama 연결 안 됨

```bash
# Ollama가 호스트에서 실행 중인지 확인
curl http://localhost:11434/api/tags

# Docker에서 호스트 접근 확인
docker-compose exec back-end curl http://host.docker.internal:11434/api/tags
```

### 데이터베이스 초기화 필요

```bash
# pgdata 제거 및 재초기화
rm -rf db/pgdata
docker-compose down
docker-compose up -d db

# 데이터 다시 적재
docker exec back-end python db/seed_trademarks.py
```

## 배포

### NHN Cloud 배포

FinalGuideView에서 제공하는 4단계 가이드를 따라 NHN Cloud에 배포할 수 있습니다:

1. **DNS Plus**: 도메인 등록 및 DNS 설정
2. **Object Storage**: 정적 파일 저장소 설정
3. **Email**: 이메일 서비스 설정
4. **Certificate Manager**: SSL/TLS 인증서 설정

각 단계별 자세한 가이드는 FinalGuideView의 NHN Cloud 배포 섹션을 참고하세요.

## 라이센스

MIT License

## 기여

버그 리포트 및 기능 제안은 GitHub Issues를 통해 제출해주세요.

## 참고 자료

- [CLAUDE.md](./CLAUDE.md) - 프로젝트 명세서
- [back-end/back-end.md](./back-end/back-end.md) - 백엔드 상세 문서
- [front-end/front-end.md](./front-end/front-end.md) - 프론트엔드 상세 문서
- [Ollama Documentation](https://github.com/ollama/ollama)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Documentation](https://vuejs.org/)
