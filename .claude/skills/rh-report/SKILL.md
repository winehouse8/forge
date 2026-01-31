---
name: rh-report
description: 토끼굴 탐험 결과를 종합하여 원래 질문에 대한 최종 답변을 생성합니다.
argument-hint: [session_number] (생략 시 최신 세션)
allowed-tools: Read, Bash, AskUserQuestion
---

# 🎯 rh-report: 토끼굴 탐험 결과 종합

지금까지 판 구멍들의 발견 사항을 종합하여 원래 질문에 대한 답변을 도출합니다.

## 실행 순서

### 1. 세션 선택

```python
import json
from pathlib import Path
from datetime import datetime

# 세션 인덱스 로드
index_path = Path(".research/sessions/index.json")

if not index_path.exists():
    print("📭 아직 탐험을 시작하지 않았습니다.")
    print("   /rh \"궁금한 주제\"로 시작하세요!")
    exit(0)

index = json.load(open(index_path))
sessions = index.get("sessions", {})

if not sessions:
    print("📭 저장된 세션이 없습니다.")
    exit(0)

# 세션 목록 정렬 (최신순)
sorted_sessions = sorted(
    sessions.items(),
    key=lambda x: x[1].get("last_accessed", ""),
    reverse=True
)
```

**세션 선택 로직:**

```python
arg = "$ARGUMENTS".strip()

if arg == "":
    # 디폴트: 가장 최신 세션
    selected_id, selected_info = sorted_sessions[0]
    print(f"📂 최신 세션 선택: {selected_id}")

elif arg.isdigit():
    # 숫자로 선택 (1-based)
    idx = int(arg) - 1
    if 0 <= idx < len(sorted_sessions):
        selected_id, selected_info = sorted_sessions[idx]
        print(f"📂 세션 #{arg} 선택: {selected_id}")
    else:
        print(f"❌ 세션 #{arg}가 없습니다. (1-{len(sorted_sessions)} 범위)")
        exit(1)

else:
    # 세션 ID로 직접 선택
    if arg in sessions:
        selected_id = arg
        selected_info = sessions[arg]
        print(f"📂 세션 선택: {selected_id}")
    else:
        print(f"❌ 세션 '{arg}'를 찾을 수 없습니다.")
        exit(1)
```

**세션이 여러 개면 목록 표시 후 선택:**

```python
if len(sorted_sessions) > 1 and arg == "":
    print("\n📋 사용 가능한 세션:")
    print("─" * 50)
    for i, (sid, info) in enumerate(sorted_sessions, 1):
        q = info.get("question", "")[:40]
        status = info.get("status", "unknown")
        iter_count = info.get("iteration", 0)
        last = info.get("last_accessed", "")[:10]
        print(f"  {i}. [{status}] {q}...")
        print(f"     iterations: {iter_count} | last: {last}")
    print("─" * 50)
    print(f"→ 최신 세션 #{1} 사용")
    print("  (다른 세션: /rh-report 2)")
    print()
```

---

### 2. 세션 데이터 로드

```python
# 세션 디렉토리 경로
session_dir = Path(selected_info.get("directory", f".research/sessions/{selected_id}"))

# curiosity_queue.json 로드
queue_path = session_dir / "curiosity_queue.json"

# 세션 디렉토리에 없으면 루트에서 시도 (호환성)
if not queue_path.exists():
    queue_path = Path(".research/curiosity_queue.json")

if not queue_path.exists():
    print(f"❌ {queue_path}를 찾을 수 없습니다.")
    exit(1)

queue = json.load(open(queue_path))
holes = queue.get("holes", [])
initial_question = selected_info.get("question", "")

# 홀별 리포트 디렉토리
holes_dir = session_dir / "holes"
```

---

### 3. 지식 분류 분석

**knowledge_type별 분류:**

```python
prior_holes = [h for h in holes if h.get("knowledge_type") == "prior"]
new_holes = [h for h in holes if h.get("knowledge_type") == "new"]
refined_holes = [h for h in holes if h.get("knowledge_type") == "refined"]

explored = [h for h in holes if h.get("status") == "explored"]
pending = [h for h in holes if h.get("status") == "pending"]
```

**논리 의존성 그래프 (depends_on):**

```python
# 논리 흐름 분석
def get_dependency_chain(hole_id, holes_dict, visited=None):
    """hole_id가 의존하는 모든 선행 지식 추적"""
    if visited is None:
        visited = set()
    if hole_id in visited:
        return []
    visited.add(hole_id)

    hole = holes_dict.get(hole_id)
    if not hole:
        return []

    deps = hole.get("depends_on", [])
    chain = list(deps)
    for dep in deps:
        chain.extend(get_dependency_chain(dep, holes_dict, visited))
    return chain

holes_dict = {h["id"]: h for h in holes}
```

---

### 4. 보고서 출력

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 토끼굴 탐험 결과 보고서
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📂 세션: {selected_id}
📅 마지막 탐험: {last_accessed}

**원래 질문:** "{initial_question}"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📊 탐험 요약

| 구분 | 수량 |
|------|------|
| 총 발견 | {len(holes)}개 |
| 탐색 완료 | {len(explored)}개 ✅ |
| 큐 대기 | {len(pending)}개 📌 |

### 지식 분류
| 타입 | 수량 | 설명 |
|------|------|------|
| prior | {len(prior_holes)}개 | 연구 전 알던 것 |
| new | {len(new_holes)}개 | 새로 발견한 것 🆕 |
| refined | {len(refined_holes)}개 | 기존 지식 정교화 |

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🆕 새로 알게 된 것 (New Knowledge)

{새로 발견한 hole들을 이해도 순으로 정리}

### 1. {topic} (이해도: {understanding}%)
- **요약:** {summary 또는 notes}
- **의존:** {depends_on 목록}
- **출처:** {source}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 📚 기존 지식 확인/정교화 (Prior/Refined)

{prior, refined hole들}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🔗 논리 흐름 (Dependency Graph)

{depends_on 관계를 트리로 시각화}

예시:
hole_1 컨텍스트 최적화 [prior]
    ↓ depends_on
hole_6 LLMLingua [new]
    ↓ depends_on
hole_11 LLMLingua-2 [new]
    ↓ depends_on
hole_16 Python 구현 [new]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## 🔥 추가 탐험 후보 (興미 높은 pending)

{흥미 > 0.85인 pending holes}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 5. 홀별 리포트 참조 (있는 경우)

```python
# holes/ 디렉토리에서 상세 리포트 읽기
if holes_dir.exists():
    for hole in explored:
        report_file = holes_dir / f"{hole['id']}_{hole['topic'][:20]}.md"
        if report_file.exists():
            # 리포트 내용 참조하여 종합
            report_content = report_file.read_text()
            # Extended Thinking으로 핵심 내용 추출
```

---

### 6. 최종 답변 도출 (Extended Thinking)

Extended Thinking을 사용하여 다음을 수행:

**수렴적 사고 도구 활용:**
- **오컴의 면도날**: 단순한 설명 우선
- **베이지안 추론**: 증거 기반 확신도
- **반증 가능성**: 반박 증거 고려
- **변증법적 사고**: 대립 관점 통합

**최종 답변 형식:**

```markdown
## 🎯 최종 답변

**질문:** "{initial_question}"

**답변:**
[핵심 발견들을 종합한 답변 - 새로 알게 된 것 중심으로]

**확신도:** [0.00-1.00]
- ✓✓ VERIFIED (0.85+): 다수 신뢰 소스 일치
- ✓ HIGH (0.70-0.84): 단일 신뢰 소스
- ~ LIKELY (0.50-0.69): 추정
- ? UNCERTAIN (<0.50): 불확실

**핵심 발견 (NEW):**
1. [새로 알게 된 것 1] (출처: ...)
2. [새로 알게 된 것 2] (출처: ...)

**기존 지식 확인:**
- [prior/refined 중 중요한 것]

**논리 흐름:**
[depends_on 관계로 본 지식 구조]

**제한 사항 / 주의점:**
- [알려진 제한 사항]

**추가 탐험 제안:**
- [흥미 높은 pending holes]
```

---

## 사용 예시

```bash
# 최신 세션 리포트
/rh-report

# 특정 세션 번호로 선택
/rh-report 2

# 세션 ID로 직접 선택
/rh-report research_20260201_052524_현재_users_jaewoo
```
