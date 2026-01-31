# Pathfinder Deep Research - 스펙 문서 인덱스

**버전:** 5.0 (Memory Blocks Enhanced)
**최종 수정일:** 2026-02-01
**상태:** ✅ Production Ready + RESEARCH_REPORT Recommendations Applied

---

## 📚 문서 구조 안내

이 문서는 **프로그레시브 디스클로저(Progressive Disclosure)** 기법을 사용합니다.
필요한 정보만 선택적으로 읽을 수 있도록 주제별로 분리되어 있습니다.

---

## 🎯 빠른 시작

| 역할 | 읽어야 할 문서 |
|------|---------------|
| **처음 사용하는 사람** | [01-overview.md](./01-overview.md) → [07-configuration.md](./07-configuration.md) → [09-deployment.md](./09-deployment.md) |
| **기능 추가/수정** | [02-architecture.md](./02-architecture.md) → 해당 기능 문서 → [08-testing.md](./08-testing.md) |
| **버그 수정** | [02-architecture.md](./02-architecture.md) → 해당 컴포넌트 문서 → [08-testing.md](./08-testing.md) |
| **성능 최적화** | [02-architecture.md](./02-architecture.md) → [04-research-cycle.md](./04-research-cycle.md) |
| **보안 감사** | [05-verification.md](./05-verification.md) → [07-configuration.md](./07-configuration.md) |

---

## 📖 전체 문서 목록

### 1. 개요 및 아키텍처

| 문서 | 설명 | 읽는 시점 |
|------|------|----------|
| [01-overview.md](./01-overview.md) | 제품 개요, 핵심 가치, 사용 사례 | 프로젝트 이해 필요 시 |
| [02-architecture.md](./02-architecture.md) | 이중 루프 아키텍처, 컴포넌트 구조 | 코드 수정 전 필수 |

### 2. 핵심 기능 상세

| 문서 | 설명 | 읽는 시점 |
|------|------|----------|
| [03-ralph-loop.md](./03-ralph-loop.md) | Ralph Loop 패턴 구현 상세 | 무한 루프 로직 수정 시 |
| [04-research-cycle.md](./04-research-cycle.md) | 9단계 연구 사이클 상세 | 연구 프로세스 수정 시 |
| [05-verification.md](./05-verification.md) | 4계층 검증 시스템, 신뢰도 평가 | 검증 로직 수정 시 |
| [06-loop-drift.md](./06-loop-drift.md) | Loop Drift 방지 및 Reflexion | 반복 방지 로직 수정 시 |

### 3. 데이터 및 설정

| 문서 | 설명 | 읽는 시점 |
|------|------|----------|
| [07-data-schemas.md](./07-data-schemas.md) | state.json, reflexion.json 등 스키마 | 상태 파일 구조 확인 필요 시 |
| [08-configuration.md](./08-configuration.md) | config.json, settings.json 설정 가이드 | 설정 변경 필요 시 |

### 4. 개발 및 운영

| 문서 | 설명 | 읽는 시점 |
|------|------|----------|
| [09-testing.md](./09-testing.md) | 테스트 시나리오, 검증 방법 | 테스트 작성/실행 시 |
| [10-deployment.md](./10-deployment.md) | 배포 가이드, 환경 설정 | 배포 준비 시 |

### 5. API 및 확장

| 문서 | 설명 | 읽는 시점 |
|------|------|----------|
| [11-skills-api.md](./11-skills-api.md) | 스킬 API 명세 (/dr, /research-status 등) | 스킬 수정/추가 시 |
| [12-hooks-api.md](./12-hooks-api.md) | Stop Hook API 명세 | Hook 수정 시 |
| [13-native-function-calling.md](./13-native-function-calling.md) | Native Function Calling (2025-2026 표준) | 도구 호출 최적화 시 |
| [14-session-management.md](./14-session-management.md) | 세션 관리 (자동 감지, Zero-config) | 세션 관련 작업 시 |

---

## 🔍 주제별 빠른 찾기

### 🆕 Memory Blocks (v5 신규)
- **3-Tier 아키텍처**: [07-data-schemas.md](./07-data-schemas.md) > "Memory Blocks Architecture"
- **Observation Masking**: [04-research-cycle.md](./04-research-cycle.md) > "LOAD 단계"
- **Working Memory**: [07-data-schemas.md](./07-data-schemas.md) > "working_memory.json"
- **Archival Memory**: [04-research-cycle.md](./04-research-cycle.md) > "SAVE 단계"

### 🆕 Native Function Calling
- **ReAct vs Native**: [13-native-function-calling.md](./13-native-function-calling.md) > "비교"
- **병렬 호출**: [13-native-function-calling.md](./13-native-function-calling.md) > "Best Practices"
- **성능 개선**: [13-native-function-calling.md](./13-native-function-calling.md) > "성능 비교"

### 🆕 Session Management (v5.1 신규)
- **자동 세션 감지**: [14-session-management.md](./14-session-management.md) > "자동 세션 감지"
- **단일 명령어**: [14-session-management.md](./14-session-management.md) > "오컴의 면도날"
- **유사도 기반**: [14-session-management.md](./14-session-management.md) > "유사도 계산"
- **데이터 손실 방지**: [14-session-management.md](./14-session-management.md) > "디렉토리 구조"

### Ralph Loop 관련
- **무한 루프 구현**: [03-ralph-loop.md](./03-ralph-loop.md) > "Stop Hook 구현"
- **종료 조건**: [03-ralph-loop.md](./03-ralph-loop.md) > "종료 결정 로직"
- **자기 재귀 호출**: [03-ralph-loop.md](./03-ralph-loop.md) > "Skill Tool 재귀"

### 연구 사이클 관련
- **검색 전략**: [04-research-cycle.md](./04-research-cycle.md) > "PLAN 단계"
- **병렬 검색**: [04-research-cycle.md](./04-research-cycle.md) > "EXECUTE 단계"
- **상태 저장**: [04-research-cycle.md](./04-research-cycle.md) > "SAVE 단계"

### 검증 시스템 관련
- **신뢰도 점수**: [05-verification.md](./05-verification.md) > "소스 신뢰도"
- **교차 검증**: [05-verification.md](./05-verification.md) > "Cross-Validation"
- **신뢰도 태그**: [05-verification.md](./05-verification.md) > "Confidence Tagging"

### 데이터 구조 관련
- **state.json 스키마**: [07-data-schemas.md](./07-data-schemas.md) > "State Schema"
- **working_memory.json**: [07-data-schemas.md](./07-data-schemas.md) > "working_memory.json"
- **지식 그래프**: [07-data-schemas.md](./07-data-schemas.md) > "Knowledge Graph"
- **Reflexion 메모리**: [07-data-schemas.md](./07-data-schemas.md) > "Reflexion Schema"

### 설정 관련
- **예산 제어**: [08-configuration.md](./08-configuration.md) > "Cost Control"
- **Loop Drift 임계값**: [08-configuration.md](./08-configuration.md) > "Loop Control"
- **검색 전략**: [08-configuration.md](./08-configuration.md) > "Search Config"

---

## 🛠️ 일반적인 작업 흐름

### 새 기능 추가
```
1. 02-architecture.md 읽기 (아키텍처 이해)
2. 해당 컴포넌트 스펙 문서 확인
3. 코드 구현
4. 해당 스펙 문서 업데이트
5. 09-testing.md 참고하여 테스트 작성
6. 테스트 실행 및 검증
```

### 버그 수정
```
1. 02-architecture.md에서 관련 컴포넌트 위치 파악
2. 해당 컴포넌트 스펙 문서 읽기
3. 버그 원인 파악 (스펙과 구현 비교)
4. 코드 수정
5. 스펙 문서 업데이트 (필요 시)
6. 테스트 검증
```

### 성능 최적화
```
1. 04-research-cycle.md 읽기 (병렬 처리 부분 확인)
2. 02-architecture.md에서 병목 지점 파악
3. 최적화 구현
4. 성능 테스트 (09-testing.md 참고)
5. 스펙 문서 업데이트
```

---

## 📊 문서 의존성 그래프

```
index.md (이 파일)
    │
    ├─→ 01-overview.md (독립)
    │
    ├─→ 02-architecture.md
    │       ├─→ 03-ralph-loop.md
    │       ├─→ 04-research-cycle.md
    │       ├─→ 05-verification.md
    │       └─→ 06-loop-drift.md
    │
    ├─→ 07-data-schemas.md (독립)
    ├─→ 08-configuration.md (독립)
    │
    ├─→ 09-testing.md
    │       └─→ 모든 기능 문서 참조
    │
    ├─→ 10-deployment.md
    │       ├─→ 08-configuration.md
    │       └─→ 09-testing.md
    │
    ├─→ 11-skills-api.md
    └─→ 12-hooks-api.md
```

**읽는 순서 권장:**
1. 전체 이해: `01-overview.md` → `02-architecture.md`
2. 기능 상세: 필요한 기능 문서만 선택적으로
3. 데이터: `07-data-schemas.md` (필요 시)
4. 실행: `08-configuration.md` → `10-deployment.md`

---

## 🔄 문서 업데이트 규칙

### 코드 변경 시 필수 업데이트

| 코드 변경 | 업데이트할 문서 |
|----------|----------------|
| Stop Hook 수정 | `03-ralph-loop.md`, `12-hooks-api.md` |
| 연구 사이클 수정 | `04-research-cycle.md` |
| 검증 로직 수정 | `05-verification.md` |
| state.json 스키마 변경 | `07-data-schemas.md` |
| config.json 변경 | `08-configuration.md` |
| 스킬 추가/수정 | `11-skills-api.md` |

### 문서 버전 관리

모든 스펙 문서 상단에 다음 정보 포함:
```markdown
**최종 수정일:** YYYY-MM-DD
**수정자:** [이름]
**관련 커밋:** [commit hash]
```

---

## ⚠️ 중요 공지

### 단일 진실 공급원 (Single Source of Truth)

- ✅ **스펙 문서 = 진실**
- ❌ 코드만 보고 판단 금지
- ⚠️ 스펙과 코드가 불일치하면 즉시 보고

### 스펙 우선 원칙

```
구현 전: 스펙 확인 → 설계 → 코드
구현 후: 코드 → 스펙 업데이트 → 검증
```

---

## 📞 도움말

### 문서를 읽어도 모르겠다면?
1. `index.md` (이 파일)의 "빠른 찾기" 섹션 확인
2. 관련 문서의 "목차" 활용
3. 문서 내 검색 (`Ctrl+F` / `Cmd+F`)

### 스펙에 없는 내용을 구현해야 한다면?
1. 관련 컴포넌트 스펙 문서에 먼저 추가
2. 구현
3. 테스트
4. 커밋 시 "spec updated" 태그 추가

---

**마지막 업데이트:** 2026-01-31
**다음 리뷰:** 2026-02-07 (1주 후)
