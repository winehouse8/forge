# Session Management (Auto-Detection)

**문서:** 14-session-management.md
**최종 수정일:** 2026-02-01
**수정자:** Claude Sonnet 4.5
**관련 파일:** `.research/session_manager.py`, `.claude/skills/deep-research/SKILL.md`

---

## 목차
- [개요](#개요)
- [오컴의 면도날: 단순성 우선](#오컴의-면도날-단순성-우선)
- [자동 세션 감지](#자동-세션-감지)
- [디렉토리 구조](#디렉토리-구조)
- [사용 시나리오](#사용-시나리오)
- [API](#api)

---

## 개요

### 문제점

**이전 구현 (세션 관리 없음):**

```bash
/dr "양자 컴퓨팅"
→ .research/에 저장
→ 10 iterations 진행...

/dr "LangGraph 성능"  ← 새 연구 시작
→ .research/ 덮어쓰기!
→ 양자 컴퓨팅 데이터 전부 손실! ❌
```

**원인:**
- 단일 `.research/` 디렉토리만 사용
- 세션 구분 없음
- 새 연구 시작 = 기존 데이터 초기화

### 해결책

**자동 세션 관리 (Zero-config):**

```bash
/dr "양자 컴퓨팅"
→ 자동 세션 생성
→ research_20260201_143022_quantum

/dr "LangGraph 성능"
→ 자동 세션 생성
→ research_20260201_150512_langgraph
→ 이전 세션(quantum) 자동 보존! ✅

/dr "양자 컴퓨팅"  ← 다시 실행
→ 기존 세션 자동 감지!
→ "계속하기" or "새로 시작" 선택
```

---

## 오컴의 면도날: 단순성 우선

### 핵심 원칙

**사용자가 외워야 할 명령어: 단 하나**

```bash
/dr "질문"
```

**나머지는 모두 자동:**
- 세션 생성
- 유사 세션 감지
- 세션 전환
- 데이터 보존

### 사용자 경험

| 시나리오 | 사용자 행동 | 시스템 동작 |
|---------|-----------|-----------|
| **처음 연구** | `/dr "양자 컴퓨팅"` | 자동 세션 생성 |
| **같은 질문 재실행** | `/dr "양자 컴퓨팅"` | 기존 세션 감지 → 선택지 제공 |
| **유사한 질문** | `/dr "양자 컴퓨터"` | 유사 세션 감지 → 선택지 제공 |
| **다른 질문** | `/dr "LangGraph"` | 새 세션 생성, 이전 세션 보존 |

**선택적 고급 기능:**
- `/research-list` - 세션 목록 확인
- `/research-switch <id>` - 수동 세션 전환

---

## 자동 세션 감지

### 1. 유사도 계산 (Embedding 기반)

```python
from session_manager import SessionManager

sm = SessionManager()

# 새 질문과 기존 세션 비교
similar_sessions, match_type = sm.find_similar_sessions("양자 컴퓨팅 최신 동향")

# match_type:
# - "exact": >0.95 유사도 (거의 동일)
# - "similar": >0.8 유사도 (유사함)
# - "none": <0.8 (다름)
```

### 2. 유사도 기준

| 유사도 | 판정 | 동작 |
|--------|------|------|
| **>0.95** | 거의 동일 (exact) | "계속하기" vs "새로 시작" 선택 |
| **0.8~0.95** | 유사 (similar) | 유사 세션 목록 표시 → 선택 |
| **<0.8** | 다름 (none) | 자동으로 새 세션 생성 |

### 3. 의사결정 플로우

```
질문 입력
    ↓
유사 세션 검색
    ↓
┌───────────┬───────────┬───────────┐
│ Exact     │ Similar   │ None      │
│ (>0.95)   │ (0.8~0.95)│ (<0.8)    │
└───────────┴───────────┴───────────┘
    ↓             ↓            ↓
단일 선택    목록 선택    자동 생성
(계속/새로)  (최대 3개)   (즉시 시작)
```

---

## 디렉토리 구조

### 세션별 격리

```
.research/
├── sessions/
│   ├── research_20260201_143022_quantum/      # Session 1
│   │   ├── state.json
│   │   ├── working_memory.json
│   │   ├── findings.md
│   │   ├── search_history.json
│   │   ├── knowledge_graph.json
│   │   └── archival/
│   │       ├── iteration_001.json
│   │       └── iteration_002.json
│   │
│   ├── research_20260201_150512_langgraph/    # Session 2
│   │   ├── state.json
│   │   ├── working_memory.json
│   │   └── ...
│   │
│   └── index.json  # Session metadata
│
├── current -> sessions/research_20260201_143022_quantum/  # Symlink
│
├── session_manager.py
├── memory_manager.py
├── deduplicate_search.py
└── knowledge_tracker.py
```

### Symlink 활용

**`.research/current` symlink:**
- 현재 활성 세션을 가리킴
- 모든 코드는 `.research/current/`를 통해 접근
- 세션 전환 = symlink 업데이트

**장점:**
- 코드 변경 최소화
- 세션 전환 빠름 (symlink만 변경)
- 하위 호환성 유지

---

## 사용 시나리오

### 시나리오 1: 처음 연구

```bash
$ /dr "양자 컴퓨팅 최신 동향"

→ 새 세션을 시작합니다...
→ Session ID: research_20260201_143022_quantum
→
→ [연구 진행]
```

### 시나리오 2: 같은 질문 재실행 (Exact Match)

```bash
$ /dr "양자 컴퓨팅 최신 동향"

→ 기존 세션 발견! (10 iterations 진행됨)
   "양자 컴퓨팅 최신 동향"

   어떻게 하시겠습니까?

   1. 계속하기 (Recommended)
      기존 연구를 10번째 iteration부터 계속합니다

   2. 새로 시작하기
      새로운 세션을 생성합니다

   선택: _
```

**사용자 선택:**
- `1` 또는 Enter → 기존 세션 재개
- `2` → 새 세션 생성

### 시나리오 3: 유사한 질문 (Similar Match)

```bash
$ /dr "양자 컴퓨터 동향"  # 비슷한 질문

→ 2개의 유사한 세션 발견

   어떤 세션을 사용하시겠습니까?

   1. 기존 세션 계속: 양자 컴퓨팅 최신 동향
      10 iterations | 유사도: 88%

   2. 기존 세션 계속: 양자역학 기초 연구
      5 iterations | 유사도: 82%

   3. 새 세션 시작
      완전히 새로운 연구를 시작합니다

   선택: _
```

### 시나리오 4: 완전히 다른 주제 (No Match)

```bash
$ /dr "LangGraph 성능 비교"

→ 현재 세션: "양자 컴퓨팅..." 일시정지
→ 새 세션 시작: research_20260201_150512_langgraph
→
→ [연구 진행]
```

**이전 세션 자동 보존!**

---

## API

### SessionManager

```python
from session_manager import SessionManager

sm = SessionManager()

# 1. 유사 세션 검색
similar_sessions, match_type = sm.find_similar_sessions("양자 컴퓨팅")
# Returns:
#   similar_sessions = [
#       {"id": "...", "question": "...", "similarity": 0.92, "iteration": 10},
#       ...
#   ]
#   match_type = "exact" | "similar" | "none"

# 2. 세션 생성
session_id = sm.create_session("양자 컴퓨팅 최신 동향", auto_switch=True)

# 3. 세션 전환
sm.switch_session(session_id)

# 4. 현재 세션 조회
current = sm.get_current_session()
# Returns: {"id": "...", "question": "...", "iteration": 10, "status": "running"}

# 5. 세션 목록
sessions = sm.list_sessions()

# 6. 세션 상태 업데이트
sm.update_session_status(session_id, status="running", iteration=5)
```

### 세션 ID 생성 규칙

**포맷:** `research_YYYYMMDD_HHMMSS_slug`

**예시:**
```
질문: "양자 컴퓨팅 최신 동향"
→ research_20260201_143022_quantum

질문: "LangGraph vs CrewAI 성능 비교"
→ research_20260201_150512_langgraph

질문: "사고도구 활용 방법"
→ research_20260201_160133_thinking
```

**Slug 생성:**
- 질문에서 처음 3개 단어 추출
- 소문자 변환, 특수문자 제거
- `_`로 연결

---

## 성능 최적화

### Embedding 캐싱

**문제:** 매번 embedding 계산 비용 높음

**해결:**

```python
# session_manager.py
# 세션 생성 시 질문의 embedding을 index.json에 저장

{
  "sessions": {
    "research_20260201_143022_quantum": {
      "question": "양자 컴퓨팅 최신 동향",
      "question_embedding": [0.123, 0.456, ...],  # 캐싱!
      "created_at": "2026-02-01T14:30:22Z",
      ...
    }
  }
}
```

**효과:**
- 첫 실행: Embedding 계산 (한 번만)
- 이후 실행: 캐시된 embedding 사용
- 비용 절감: N번 실행 시 1/N

### Symlink vs Copy

**Symlink 사용 이유:**

| 방식 | 세션 전환 비용 | 저장공간 | 복잡도 |
|------|--------------|---------|--------|
| **Symlink** | O(1) - 즉시 | 최소 | 낮음 |
| **Copy** | O(N) - 파일 크기 비례 | 2배 | 높음 |

**구현:**

```python
# session_manager.py
def switch_session(self, session_id):
    session_dir = f".research/sessions/{session_id}"

    # Remove old symlink
    os.remove(".research/current")

    # Create new symlink
    os.symlink(session_dir, ".research/current", target_is_directory=True)
```

---

## 하위 호환성

### 기존 데이터 마이그레이션

**문제:** 기존 `.research/` 데이터 손실 방지

**해결:** 첫 실행 시 자동 마이그레이션

```python
# session_manager.py
def _migrate_legacy_data(self):
    """Migrate legacy .research/ data to sessions/"""

    legacy_state = ".research/state.json"

    if os.path.exists(legacy_state) and not os.path.exists(SESSIONS_DIR):
        # Legacy data found
        print("→ Migrating legacy research data...")

        # Read legacy state
        with open(legacy_state, 'r') as f:
            state = json.load(f)

        question = state.get("question", {}).get("original", "Legacy Research")

        # Create session for legacy data
        session_id = self.create_session(question, auto_switch=True)
        session_dir = f".research/sessions/{session_id}"

        # Move legacy files to session
        for file in ["state.json", "findings.md", "search_history.json", ...]:
            if os.path.exists(f".research/{file}"):
                shutil.move(f".research/{file}", f"{session_dir}/{file}")

        print(f"✓ Legacy data migrated to: {session_id}")
```

---

## 테스트

### CLI 테스트

```bash
# 세션 생성
python .research/session_manager.py create "양자 컴퓨팅 최신 동향"

# 세션 목록
python .research/session_manager.py list

# 세션 전환
python .research/session_manager.py switch research_20260201_143022_quantum

# 현재 세션
python .research/session_manager.py current

# 세션 삭제
python .research/session_manager.py delete research_20260201_143022_quantum
```

### 통합 테스트

```bash
# 시나리오 1: 새 세션 자동 생성
/dr "양자 컴퓨팅"
→ 세션 생성 확인

# 시나리오 2: 같은 질문 재실행
/dr "양자 컴퓨팅"
→ 기존 세션 감지 확인
→ 선택지 표시 확인

# 시나리오 3: 다른 질문
/dr "LangGraph"
→ 새 세션 생성 확인
→ 이전 세션 보존 확인

# 시나리오 4: 세션 목록
/research-list
→ 모든 세션 표시 확인
```

---

**다음:** [index.md](./index.md) - 스펙 문서 인덱스 업데이트
