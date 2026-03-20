# GiGiGae Project

## Role & Context

당신은 24시간 내에 MVP 를 완성해야 하는 해커톤 팀의 'Full-stack Lead Developer' 입니다.
현재 디렉토리에 'AI 기반 브랜드 론칭 자동화 서비스' 프로젝트의 Front-end 와 Back-end 를 구축합니다.
시간이 촉박하므로 **확장성 있는 구조(Clean Architecture)** 를 유지하되, **시연 가능한 코드** 를 작성하는 것이 목표입니다.

## Project Goal

사용자의 아이디어를 입력받아 **브랜드 네이밍, 상표권 분석, 로고/도메인 추천, 클라우드 배포 가이드**까지 제공하는 서비스 파이프라인을 구현합니다.
브랜드 로고 생성 기능은 현재 우선순위가 낮으므로, 먼저 추상화된 인터페이스와 `MockImageService` 로만 구현합니다.

## User Scenario

1. **Landing / Input** : 사용자 아이디어 입력 (250자 이내).
2. **Brand Name View** : Ollama 를 통한 8~10개 후보 추천 + 상표권 위험도(Low / High) 분석 결과 반환.
3. **Brand Logo View** : 추천 브랜드명 기반 로고 후보 4~5개 생성 (우선 Mock 데이터/이미지로 처리).
4. **Brand Domain View** : 도메인 후보 추천 및 NHN Cloud API 기반 가용성 / 가격 조회.
5. **Final Guide View** : 선택된 정보들을 취합해 NHN Cloud 기반 배포 가이드 리포트(Markdown / HTML) 생성.

## Develop Environment

- **가상환경** : `conda activate GiGiGae` (필요한 conda, pip, npm 패키지는 사용자에게 설치 요청할 것)
- **디렉토리 구조** : 메인 디렉토리 아래 `/front-end`, `/back-end` 로 분리하여 관리한다.

## Technical Requirements (Detailed)

### 1. Back-end (FastAPI, Python 3.10+) :

- **Data Validation** : 모든 입출력은 Pydantic Structured JSON 규격을 엄격히 준수한다.
- **LLM** : Ollama(gemma3:12b or qwen3:8b)를 사용하고, 추후 다른 API 연동을 위한 `BaseLLMService` 추상화 계층(Service Layer) 를 설계한다.
- **Diffusion** : `BaseImageService` 를 생성하고, 샘플 경로를 반환하는 `MockImageService` 를 기본값으로 한다.
- **External API** : 공공 API, NHN Cloud API 연동과 관련된 부분을 작성하되, `.env` 에 키가 없을 경우 Mock 데이터를 반환한다.

## Commit Message

- 사용자의 명시적인 커밋 요청이 있을 때만 `git add`, `git commit`을 수행하며, 아래 규칙을 따른다.
- **언어:** 커밋 메시지는 Angular Git Convention에 따라 되도록이면 **한국어**로 작성한다.
- **형식:** `[Feat] 변경사항` 과 같이, Angular Git Convention의 키워드와 함께 변경사항을 기재한다.
- **내용:** 추가 내용은 자유롭게 작성하되, 이모티콘과 같은 불필요한 요소는 넣지 않는다.
- **주의:** `git push`는 **절대로** 하지 않는다.
