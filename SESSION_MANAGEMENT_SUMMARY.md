# Session Management Implementation (v5.1)

**날짜:** 2026-02-01
**원칙:** 오컴의 면도날 (Occam's Razor)
**핵심:** 단순성 우선 - 사용자가 외울 명령어는 단 하나

---

## 🎯 문제 정의

### 기존 문제 (v5.0)

```bash
/dr "양자 컴퓨팅"  → .research/에 저장
/dr "LangGraph"   → .research/ 덮어쓰기 → 데이터 손실! ❌
```

**원인:**
- 단일 `.research/` 디렉토리만 사용
- 세션 구분 없음
- 새 연구 시작 = 기존 데이터 초기화

---

## ✅ 해결책: 자동 세션 관리

### 핵심 원칙: "질문만으로 모든 것 해결"

```bash
/dr "질문"  ← 이것만 알면 됨!
```

**자동 처리:**
1. 유사 세션 검색 (임베딩 유사도)
2. 충돌 시에만 선택지 제공
3. 없으면 자동 생성
4. 데이터 자동 보존

---

## 📊 사용 시나리오

### 1. 처음 연구

```bash
/dr "양자 컴퓨팅"
→ 새 세션 자동 생성
→ research_20260201_143022_quantum
```

### 2. 같은 질문 재실행

```bash
/dr "양자 컴퓨팅"
→ 기존 세션 발견! (10 iterations)
→
→ 1. 계속하기 (Recommended)
→ 2. 새로 시작하기
→
→ 선택: [Enter = 계속]
```

### 3. 유사한 질문

```bash
/dr "양자 컴퓨터"  # 88% 유사
→ 유사한 세션 발견
→
→ 1. 기존 세션: "양자 컴퓨팅" (88%)
→ 2. 새 세션 시작
→
→ 선택: _
```

### 4. 다른 주제

```bash
/dr "LangGraph"
→ 자동 새 세션 생성
→ 이전 세션 자동 보존! ✅
```

---

## 🏗️ 구현 내용

### 신규 파일

| 파일 | 용도 |
|------|------|
| `.research/session_manager.py` | 세션 관리, 유사도 검색 |
| `docs/spec/14-session-management.md` | 세션 관리 스펙 |
| `.claude/skills/research-list/SKILL.md` | 세션 목록 (선택적) |
| `.claude/skills/research-switch/SKILL.md` | 세션 전환 (선택적) |

### 수정 파일

| 파일 | 변경 내용 |
|------|----------|
| `.claude/skills/deep-research/SKILL.md` | LOAD 단계: 자동 세션 감지 추가 |
| `.research/memory_manager.py` | Symlink 기반 경로로 변경 |
| `docs/spec/index.md` | Session Management 추가 |

### 디렉토리 구조

```
.research/
├── sessions/
│   ├── research_20260201_143022_quantum/
│   │   ├── state.json
│   │   ├── working_memory.json
│   │   ├── findings.md
│   │   └── archival/
│   ├── research_20260201_150512_langgraph/
│   │   └── ...
│   └── index.json  # 세션 메타데이터
├── current -> sessions/research_20260201_143022_quantum/  # Symlink
├── session_manager.py
└── memory_manager.py
```

---

## 🔧 기술 구현

### 1. 유사도 검색 (Embedding 기반)

```python
from session_manager import SessionManager

sm = SessionManager()

# 자동으로 기존 세션과 비교
similar_sessions, match_type = sm.find_similar_sessions("양자 컴퓨팅")

# match_type:
# - "exact": >0.95 유사도
# - "similar": 0.8~0.95 유사도
# - "none": <0.8
```

### 2. 자동 세션 생성

```python
# Session ID 생성 규칙
# Format: research_YYYYMMDD_HHMMSS_slug

"양자 컴퓨팅 최신 동향" → research_20260201_143022_quantum
"LangGraph 성능 비교" → research_20260201_150512_langgraph
```

### 3. Symlink 기반 접근

```python
# 모든 파일 접근은 .research/current/ 를 통해
CURRENT_SESSION_DIR = ".research/current"  # Symlink

# 세션 전환 = Symlink 업데이트
os.remove(".research/current")
os.symlink("sessions/new_session_id", ".research/current")
```

**장점:**
- 코드 변경 최소화
- 세션 전환 O(1)
- 하위 호환성 유지

---

## 📈 성능 최적화

### Embedding 캐싱

```json
// .research/sessions/index.json
{
  "sessions": {
    "research_20260201_143022_quantum": {
      "question": "양자 컴퓨팅 최신 동향",
      "question_embedding": [0.123, 0.456, ...],  // 캐싱!
      ...
    }
  }
}
```

**효과:**
- 첫 실행: Embedding 계산 (1회)
- 이후: 캐시 사용
- 비용 절감: N번 실행 시 1/N

---

## 🎯 사용자 경험

### 필수 명령어: 단 하나

```bash
/dr "질문"
```

### 선택적 고급 기능

```bash
/research-list              # 세션 목록
/research-switch <id>       # 세션 수동 전환
```

### 오컴의 면도날 체크

| 기준 | 평가 |
|------|------|
| **단순성** | ✅ 명령어 1개만 필수 |
| **자동화** | ✅ 세션 관리 자동 |
| **안전성** | ✅ 데이터 손실 없음 |
| **직관성** | ✅ 같은 질문 = 같은 세션 |
| **선택권** | ✅ 필요시에만 개입 |

---

## 🧪 테스트 방법

### CLI 테스트

```bash
# 세션 생성
python .research/session_manager.py create "양자 컴퓨팅"

# 세션 목록
python .research/session_manager.py list

# 유사 세션 검색 (추가 필요)
python .research/session_manager.py find "양자 컴퓨터"
```

### 통합 테스트

```bash
# 1. 새 세션
/dr "양자 컴퓨팅"
→ 세션 생성 확인

# 2. 같은 질문
/dr "양자 컴퓨팅"
→ 기존 세션 감지, 선택지 표시

# 3. 다른 질문
/dr "LangGraph"
→ 새 세션 생성, 이전 세션 보존

# 4. 세션 목록
/research-list
→ 모든 세션 표시
```

---

## 🔄 마이그레이션

### 기존 데이터 자동 마이그레이션

**첫 실행 시:**

```python
# session_manager.py __init__
if os.exists(".research/state.json") and not os.exists(SESSIONS_DIR):
    # Legacy data 발견
    self._migrate_legacy_data()
```

**동작:**
1. 기존 `.research/state.json` 감지
2. 질문 추출
3. 새 세션 생성
4. 기존 파일 이동
5. Symlink 생성

**결과:**
- 데이터 손실 없음
- 자동으로 세션 시스템 전환
- 사용자 개입 불필요

---

## 📊 비교: Before vs After

### Before (v5.0 - 세션 없음)

```bash
명령어: /dr "질문"
동작: .research/에 바로 저장
문제: 새 연구 시작 → 기존 데이터 덮어쓰기
해결: 수동으로 백업 필요
```

### After (v5.1 - 자동 세션)

```bash
명령어: /dr "질문"  (동일!)
동작:
  1. 유사 세션 자동 검색
  2. 있으면 → 선택지 제공
  3. 없으면 → 자동 생성
결과: 데이터 손실 없음, 자동 보존
사용자: 아무것도 안 해도 됨!
```

---

## 🎉 결론

### 구현 완료

✅ **자동 세션 관리** - 유사도 기반 감지
✅ **단일 명령어** - `/dr "질문"` 하나만
✅ **데이터 보존** - 자동으로 모든 세션 보존
✅ **오컴의 면도날** - 최대한 단순하게

### 사용자 혜택

- **편리성**: 명령어 1개만 외우면 됨
- **안전성**: 데이터 손실 걱정 없음
- **자동화**: 세션 관리 신경 안 써도 됨
- **선택권**: 필요할 때만 선택

### 다음 단계

- [x] Session Manager 구현
- [x] SKILL.md 자동 감지 통합
- [x] 스펙 문서 작성
- [ ] 테스트 실행
- [ ] 사용자 피드백 수집

---

**참고:**
- 스펙 문서: `docs/spec/14-session-management.md`
- 구현: `.research/session_manager.py`
- 통합: `.claude/skills/deep-research/SKILL.md`
