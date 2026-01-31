---
name: rabbit-hole
description: 토끼굴 탐험가. 흥미를 따라 깊이 파고들며 끊임없이 새로운 발견을 추구합니다. 처음엔 어디를 팔지 모르니 여러 구멍을 시도하고, 흥미로운 것을 발견하면 깊이 파고, 더 흥미로운 것이 나타나면 즉시 pivot합니다.
argument-hint: [research question]
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep, Skill
---

# 🐰 Rabbit Hole Explorer

## 🎯 핵심 철학

```
처음엔 어디를 팔지 모름
  ↓
여러 구멍 시도 (발산)
  ↓
"오, 이거!" 발견
  ↓
깊이 파기 (수렴)
  ↓
"또 저것도!" 발견
  ↓
더 흥미로운 쪽으로 pivot
  ↓
계속...
```

**3가지 원칙:**
1. **흥미를 따라가세요** - 順序 말고 흥미 순
2. **멈추지 마세요** - 사용자가 중단할 때까지, 의문점이 하나라도 남았으면 계속
3. **자유롭게** - 규칙은 가이드일 뿐, 직관을 믿으세요

**🚨 Ralph Loop 철칙:**
- **절대 스스로 종료하지 마세요**
- pending holes가 없어도 "열린 질문"이 있으면 새 hole 생성
- explored holes에 "아직 모름"이 있으면 재탐색
- current_knowledge.md에 의문이 남았으면 계속
- **오직 사용자만 탐험을 중단할 수 있습니다**

---

## 🔄 사이클 (4단계)

```
1. LOAD  - 상태 + 지식 컨텍스트 로드
2. DIG   - 자유 탐색
3. SAVE  - 상태 저장 + 지식 업데이트 + 출력
4. LOOP  - 다음으로
```

---

## 1. LOAD

### 1.1 세션 관리

```python
from .research.session_manager import SessionManager
import json

sm = SessionManager()

if "$ARGUMENTS" != "":
    # 새 질문 제공됨
    question = "$ARGUMENTS"
    existing_sessions = sm.list_sessions()

    # 유사 세션 체크 후 새 세션 생성 또는 이어하기
    session_id = sm.create_session(question)

    # 초기 구멍 생성 (Extended Thinking으로 질문 분해)
    # goal 필드: 이 hole에서 알고 싶은 것 (이해도 평가 기준)
    initial_holes = [
        {
            "id": "hole_1",
            "topic": "aspect_1",
            "goal": "이 관점에서 핵심 원리와 적용 방법 파악",  # 필수!
            "interest": 0.85,
            "knowledge_type": "prior"
        },
        {
            "id": "hole_2",
            "topic": "aspect_2",
            "goal": "구체적인 구현 방법과 trade-off 이해",
            "interest": 0.80,
            "knowledge_type": "prior"
        },
    ]
else:
    # 이어하기
    current = sm.get_current_session()
    session_id = current["id"]

# 세션 디렉토리
session_path = sm.get_session_path(session_id)

# ═══════════════════════════════════════════════════════════════
# 🔑 세션 ID는 UserPromptSubmit hook에서 자동 저장됨
# ═══════════════════════════════════════════════════════════════
# 사용자가 /rh 명령 입력 시:
#   → UserPromptSubmit hook이 session_id를 .research/current/.session_id에 저장
#   → stop-hook이 session_id 일치 여부로 Ralph Loop 적용
#   → 다른 Claude Code 세션은 Ralph Loop에 걸리지 않음
#
# 자세한 내용: .claude/hooks/user-prompt-submit-hook.py 참조
# ═══════════════════════════════════════════════════════════════
```

### 1.2 Knowledge Context 로드 (핵심!)

**세 가지를 로드 (모두 세션 디렉토리 내):**
1. **Global Knowledge** - `{session_path}/current_knowledge.md` (전체 연구 흐름)
2. **Parent Knowledge** - 현재 hole의 parent 보고서 (상위 맥락)
3. **Current Knowledge** - 현재 hole의 기존 보고서 (이전 탐색 기록)

**💡 Phase 1: LLMLingua 압축 적용 (컨텍스트 50-60% 감소)**

```python
# ═══════════════════════════════════════════════════════════════
# 🔧 LLMLingua 초기화 (세션당 한 번)
# ═══════════════════════════════════════════════════════════════
try:
    from llmlingua import PromptCompressor

    compressor = PromptCompressor(
        model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
        use_llmlingua2=True  # 3-6배 빠른 LLMLingua-2 사용
    )
    compression_enabled = True
    print("✓ LLMLingua-2 압축 활성화 (컨텍스트 50-60%↓)")
except ImportError:
    print("⚠ LLMLingua 미설치 (pip install llmlingua accelerate)")
    compression_enabled = False

def compress_if_enabled(text, rate=0.5, force_tokens=['\n', '-', '**', '|', '#']):
    """압축 가능하면 압축, 아니면 원본 반환"""
    if not compression_enabled or not text:
        return text
    try:
        result = compressor.compress_prompt(
            text,
            rate=rate,
            force_tokens=force_tokens  # 마크다운 구조 보존
        )
        return result['compressed_prompt']
    except Exception as e:
        print(f"⚠ 압축 실패, 원본 사용: {e}")
        return text

# ═══════════════════════════════════════════════════════════════
# 🌐 1. Global Knowledge 로드 + 압축 (세션 내)
# ═══════════════════════════════════════════════════════════════
global_knowledge_raw = read(f"{session_path}/current_knowledge.md")
global_knowledge = compress_if_enabled(
    global_knowledge_raw,
    rate=0.5  # 50%로 압축 (핵심 정보, 덜 압축)
)
print(global_knowledge)  # 압축된 버전 출력

# ═══════════════════════════════════════════════════════════════
# 🔍 2. 현재 hole 선택
# ═══════════════════════════════════════════════════════════════
queue = json.load(open(f"{session_path}/curiosity_queue.json"))
holes_dict = {h["id"]: h for h in queue["holes"]}

current_hole = select_most_interesting(queue["holes"])  # pending 중 흥미 높은 것

# ═══════════════════════════════════════════════════════════════
# 📌 3. Parent Knowledge 로드 + 압축 (있으면)
# ═══════════════════════════════════════════════════════════════
if current_hole.get("parent"):
    parent_id = current_hole["parent"]
    parent_hole = holes_dict[parent_id]
    parent_report_path = f"{session_path}/holes/{parent_id}_{slugify(parent_hole['topic'])}.md"

    if exists(parent_report_path):
        parent_report_raw = read(parent_report_path)
        parent_report = compress_if_enabled(
            parent_report_raw,
            rate=0.33  # 33%로 압축 (맥락만 필요, 더 공격적)
        )
        print(f"\n📌 Parent Knowledge (압축됨): {parent_hole['topic']}")
        print(parent_report[:800])  # 앞부분만

# ═══════════════════════════════════════════════════════════════
# 📝 4. Current Hole Knowledge 로드 + 압축 (있으면 - 재탐색 시)
# ═══════════════════════════════════════════════════════════════
current_report_path = f"{session_path}/holes/{current_hole['id']}_{slugify(current_hole['topic'])}.md"

if exists(current_report_path):
    current_report_raw = read(current_report_path)
    current_report = compress_if_enabled(
        current_report_raw,
        rate=0.4  # 40%로 압축 (60% 감소, 균형)
    )
    print(f"\n📝 이전 탐색 기록 (압축됨): {current_hole['topic']} (depth {current_hole['depth']})")
    print(current_report)  # 압축된 버전 전체
```

### 1.3 출력 예시

**처음 탐색하는 hole:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Current Knowledge
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 연구: rabbit-hole 성능 향상 방법?
## 핵심 발견
- LLMLingua-2: 3-6x 빠른 압축 (BERT 기반)
...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Parent: hole_6 "LLMLingua"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MS Research의 프롬프트 압축 기법...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕳️ 현재: hole_11 "LLMLingua-2" (depth 0, 첫 탐색)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**재탐색하는 hole (depth > 0):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 Current Knowledge
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[global knowledge]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 Parent: hole_6 "LLMLingua"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[parent 보고서 앞부분]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 이전 탐색 기록: hole_11 (depth 1)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# LLMLingua-2

## [Iter 2] 탐색
**쿼리:** "LLMLingua-2 implementation"
**발견:** token classification 방식
**아직 모름:** 구체적 API 사용법
**이해도:** 0.5

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🕳️ 현재: hole_11 계속 탐색 (depth 1 → 2)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 2. DIG (핵심!)

**철학: 자유롭게 탐색하되, 기존 지식과 비교하며**

### 2.1 구멍 선택 (직관)

Extended Thinking으로 가장 끌리는 구멍 선택:
```
큐:
- hole_11 "LLMLingua-2" (흥미: 0.93, depth: 0)
- hole_18 "UCB 공식" (흥미: 0.93, depth: 0)
- hole_7 "Claude API" (흥미: 0.92, depth: 0)

직관: "LLMLingua-2가 가장 실용적!"
→ hole_11 선택
```

### 2.2 탐색 프로세스

**💡 Phase 2: GPTCache 검색 캐싱 (비용 50%↓, 속도 2-4배↑)**

```python
# ═══════════════════════════════════════════════════════════════
# 🔧 GPTCache 초기화 (세션당 한 번)
# ═══════════════════════════════════════════════════════════════
try:
    from gptcache import Cache
    from gptcache.manager import get_data_manager, CacheBase, VectorBase
    from gptcache.similarity_evaluation.distance import SearchDistanceEvaluation

    cache_base = CacheBase('sqlite', sql_url=f"sqlite:///{session_path}/search_cache.db")
    vector_base = VectorBase('faiss', dimension=384)
    data_manager = get_data_manager(cache_base, vector_base)

    search_cache = Cache()
    search_cache.init(
        data_manager=data_manager,
        similarity_evaluation=SearchDistanceEvaluation(
            threshold=0.85  # 85% 이상 유사하면 캐시 히트
        )
    )
    caching_enabled = True
    print("✓ GPTCache 활성화 (검색 비용 50%↓, 속도 2-4배↑)")
except ImportError:
    print("⚠ GPTCache 미설치 (pip install gptcache)")
    caching_enabled = False

def cached_web_search(query):
    """캐싱된 WebSearch - 유사 쿼리 자동 재사용"""
    if not caching_enabled:
        return WebSearch(query)

    try:
        # 1. 캐시 확인
        cached = search_cache.get(query)
        if cached:
            print(f"  ✓ 캐시 히트: {query[:60]}...")
            return cached

        # 2. 캐시 미스 → 검색 실행
        print(f"  → 검색 실행: {query}")
        result = WebSearch(query)

        # 3. 캐시 저장 (다음 번 사용)
        search_cache.set(query, result)
        return result
    except Exception as e:
        print(f"⚠ 캐싱 실패, 직접 검색: {e}")
        return WebSearch(query)
```

**탐색 단계:**

```
1. 쿼리 생성 (Extended Thinking)
   - current_knowledge.md 참조하여 "이미 아는 것" 확인
   - 아직 모르는 것 위주로 쿼리 생성
   - 3-5개 쿼리

2. 검색 전략 (depth 기반)
   depth 0-1 (발산): 넓게 탐색, 새 구멍 발견
   depth 2+ (수렴): 구체적 쿼리, 깊은 이해, 검증 중심

3. 병렬 검색 (캐싱 적용)
   cached_web_search(q1)  # 병렬, 캐시 자동 체크
   cached_web_search(q2)  # 병렬, 유사 쿼리 재사용
   cached_web_search(q3)  # 병렬, 비용/시간 절감

4. 발견 & 분류
   - 검색 결과를 current_knowledge.md와 비교
   - 이미 아는 것 → knowledge_type: "refined"
   - 새로운 것 → knowledge_type: "new"
   - 출처 확인 (필수!)

5. 이해 구축
   - 정보 종합
   - parent 보고서 및 이전 탐색 기록과 연결
   - 간단명료하게

6. 이해도 평가 & 판단
   hole.goal 대비 달성도 평가:

   """
   goal: "구체적 구현 방법과 API 사용법 파악"

   평가:
   - 구현 방법: ✓ PromptCompressor 클래스 발견
   - API 사용법: ✗ 아직 모름
   → understanding = 0.5
   """

   if understanding >= 0.7:
       status = "explored"  # goal 대부분 달성!
       → 다음 hole로 이동
   else:
       depth += 1
       status = "pending"   # 유지
       → 보고서에 "아직 모름: [goal 중 미달성 부분]" 기록
       → 같은 hole 다시 선택될 수 있음
```

### 2.3 새 구멍 발견 (흥미 판단)

**흥미 공식:**
```
흥미 = 근본성(0.3) + 연결성(0.3) + 신선도(0.25) + 구체성(0.15)

- 근본성: 기초/원리인가
- 연결성: 원래 질문과 연결되는가
- 신선도: current_knowledge.md에 없는 것인가
- 구체성: 데이터/실험이 있는가
```

**규칙:**
- 유사도 > 0.7 → 새 hole 안 만듦 (병합)
- 흥미 > 0.70 → 새 hole 생성
- 모순 발견 시 +0.2 보너스

### 2.4 지식 분류 (knowledge_type)

**current_knowledge.md와 비교하여 판단:**

| 상황 | knowledge_type |
|------|----------------|
| initial_decomposition, 사용자 입력 | `"prior"` |
| current_knowledge.md에 없는 새 개념 | `"new"` |
| 이미 아는 것의 세부사항/정정 | `"refined"` |

```
예시:
발견: "LLMLingua uses BERT for token classification"

current_knowledge.md 확인:
"- LLMLingua-2: 3-6x 빠른 프롬프트 압축 (BERT 기반)"

판단: BERT 기반이라는 건 이미 앎, token classification은 세부사항
→ knowledge_type: "refined"
```

### 2.5 출처 검증 (필수!)

```
1. 모든 사실적 주장 → 출처 필수
   ✅ "LLMLingua-2는 ACL'24 발표 (arxiv.org)"
   ❌ "LLMLingua-2는 좋다" ← 출처 없음!

2. 태그
   ✓✓ VERIFIED (3개+ 소스)
   ✓ HIGH (1-2개 소스)
   ? UNCERTAIN (쓰지 마!)
```

---

## 3. SAVE

### 3.1 상태 저장

```python
# 1. 이해도 평가 (goal 대비 달성도)
"""
Extended Thinking으로 평가:

hole.goal = "구체적 구현 방법과 API 사용법 파악"

체크리스트:
□ 구현 방법 이해? → ✓ (PromptCompressor)
□ API 사용법 이해? → ✗ (아직 모름)

달성: 1/2 = 0.5
"""
understanding = evaluate_goal_completion(current_hole.goal, findings)

# 2. 구멍 상태 업데이트
if understanding >= 0.7:
    # goal 대부분 달성 → 끝!
    update_hole(
        hole_id=current_hole.id,
        depth=current_hole.depth + 1,
        status="explored",
        understanding=understanding
    )
else:
    # goal 미달성 → 계속 파야 함
    update_hole(
        hole_id=current_hole.id,
        depth=current_hole.depth + 1,
        status="pending",  # 유지!
        understanding=understanding
    )
    # 보고서에 "아직 모름: [미달성 goal 항목]" 기록

# 3. 새 구멍 or 병합
for discovery in discoveries:
    if discovery.similarity > 0.7:
        merge_into_hole(discovery, most_similar_hole)
    else:
        create_new_hole(discovery)

# 4. 파일 저장
save(f"{session_path}/curiosity_queue.json", queue)
save(f"{session_path}/state.json", state)
```

### 3.2 Hole 보고서 저장

```python
# .research/holes/{hole_id}_{topic_slug}.md
report_path = f".research/holes/{current_hole.id}_{slugify(current_hole.topic)}.md"
write(report_path, hole_report)
```

### 3.3 current_knowledge.md 업데이트 (핵심!)

**매 iteration 끝에 갱신:**

```python
"""
Extended Thinking으로:

1. 이번 iteration에서 새로 알게 된 것
   → "핵심 발견"에 추가 (중요하면)

2. 기존 내용과 충돌/반증
   → "수정/반증된 것"으로 이동, 기존 삭제

3. 100줄 제한 유지 (아래 우선순위로 관리)

4. 파일 덮어쓰기
"""

update_current_knowledge(
    new_findings=this_iteration_findings,
    contradictions=found_contradictions,
    max_lines=100
)

# ═══════════════════════════════════════════════════════════════
# 🔄 Ralph Loop: 의문점 체크 → 새 hole 생성 (필수!)
# ═══════════════════════════════════════════════════════════════
"""
Extended Thinking으로 의문점 확인:

1. current_knowledge.md의 "열린 질문" 확인
   - 답변되지 않은 질문이 있는가?
   - 새로운 각도로 파볼 주제가 있는가?

2. explored holes의 "아직 모름" 섹션 확인
   - goal 미달성 hole이 있는가?
   - 재탐색이 필요한가?

3. 이번 iteration에서 떠오른 새 의문
   - 검색 중 발견한 관련 주제
   - 답변 중 모호한 부분
   - 검증이 필요한 가설

→ 의문이 하나라도 있으면 새 hole 생성!
"""

open_questions = extract_open_questions(current_knowledge)
unexplored_aspects = find_unexplored_aspects(this_iteration_findings)

if open_questions or unexplored_aspects:
    for question in (open_questions + unexplored_aspects):
        if not exists_similar_hole(question, queue["holes"]):
            new_hole = {
                "id": f"hole_{next_id}",
                "topic": question["topic"],
                "goal": question["goal"],
                "interest": calculate_interest(question),  # 0.7+
                "depth": 0,
                "parent": current_hole["id"],
                "status": "pending",
                "source": "open_question",
                "knowledge_type": "new",
                "discovered_at": iteration,
                "understanding": 0.0
            }
            queue["holes"].append(new_hole)
            print(f"💡 새 hole 생성: {new_hole['topic']} (열린 질문 → 탐색)")
```

*100줄 유지 규칙:**

```
섹션 우선순위 (높을수록 유지):

1. 핵심 발견 (절대 삭제 안 함)
   - 단, 오래되고 덜 중요한 것은 한 줄로 압축
   - 예: "LLMLingua-2: BERT 기반 3-6x 빠른 압축" (세부사항 생략)

2. 열린 질문
   - 해결된 질문 → 삭제
   - 새 질문 → 추가

3. 탐구 축 테이블
   - explored 완료된 축은 한 줄 요약으로
   - pending 축은 유지

4. 수정/반증된 것
   - 최근 3개만 유지
   - 오래된 것 삭제

압축 예시:
Before (3줄):
- LLMLingua-2: 3-6x 빠른 프롬프트 압축
- BERT 기반 토큰 분류 방식
- pip install llmlingua로 설치 가능

After (1줄):
- LLMLingua-2: BERT 기반 3-6x 압축 (pip install llmlingua)
```

### 3.4 진행 상황 출력

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐰 Rabbit Hole #{iteration}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕳️ 탐험: "{current_hole.topic}"

💡 발견:
  - "new_concept_1" [new] (흥미 0.85)
  - "detail_of_X" [refined]

✓✓ 검증:
  - 핵심 사실 1 (3개 소스)

📝 current_knowledge.md 업데이트됨

📊 큐: {pending_count}개 대기
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 4. LOOP (Ralph Loop - 무한 탐험!)

**🚨 핵심: 절대 스스로 종료하지 마세요!**

```python
# ═══════════════════════════════════════════════════════════════
# 🔄 Ralph Loop: 의문점이 남았으면 무조건 계속!
# ═══════════════════════════════════════════════════════════════

"""
Extended Thinking으로 계속 여부 판단:

Q: 의문점이 남았는가?
   □ pending holes가 있는가?
   □ current_knowledge.md에 "열린 질문"이 있는가?
   □ explored holes 중 understanding < 1.0인 것이 있는가?
   □ 이번 iteration에서 새로운 의문이 떠올랐는가?

→ 하나라도 YES면 무조건 계속!
→ 모두 NO여도 "정말 모든 각도를 탐색했나?" 다시 생각

절대 "충분히 탐색했다"고 임의 판단하지 마세요.
오직 사용자만 탐험을 중단할 수 있습니다!
"""

# 1. pending holes 확인
pending_holes = [h for h in queue["holes"] if h["status"] == "pending"]

# 2. 의문점 확인
open_questions = check_open_questions(current_knowledge)
incomplete_holes = [h for h in queue["holes"]
                    if h["status"] == "explored" and h.get("understanding", 0) < 1.0]

# 3. 상태 확인
state = json.load(open(f"{session_path}/state.json"))

# ═══════════════════════════════════════════════════════════════
# 판단: 계속할 이유가 하나라도 있으면 계속!
# ═══════════════════════════════════════════════════════════════
should_continue = (
    state["status"] == "running" and (
        len(pending_holes) > 0 or           # pending holes 있음
        len(open_questions) > 0 or          # 열린 질문 있음
        len(incomplete_holes) > 0 or        # 미완성 holes 있음
        True  # 🚨 기본값: 항상 계속 (의문 재발견 가능성)
    )
)

if should_continue:
    print(f"\n🔄 다음 iteration 시작 (pending: {len(pending_holes)}, "
          f"열린 질문: {len(open_questions)}, 미완성: {len(incomplete_holes)})")
    Skill(skill="rabbit-hole", args="")
else:
    # 이 블록은 사실상 도달 불가 (should_continue의 마지막 True 때문)
    # 사용자가 명시적으로 중단하지 않는 한 계속됨
    print("🐰 탐험 일시 정지 (사용자 중단 대기)")
```

**🚨 Ralph Loop 종료 조건 (단 하나!):**
- **오직 사용자가 명시적으로 중단 (Ctrl+C, 중단 명령 등)**
- `state["status"] = "stopped_by_user"` (사용자가 설정)

**절대 자동 종료 금지:**
- ❌ "충분히 탐색했다" 판단
- ❌ "curiosity_queue가 비었으니 종료"
- ❌ "모든 holes가 explored"
- ❌ "시간이 오래 걸렸으니 종료"

→ **의문점이 하나라도 남았으면 계속!**
→ **의문점이 없어도 새 각도를 찾아 계속!**
→ **사용자만 탐험을 멈출 수 있습니다!**

---

## 📋 데이터 구조

### 파일 구조

**모든 파일은 세션 디렉토리 내에 위치:**

```
.research/
├── sessions/
│   ├── index.json                 # 세션 목록
│   └── research_YYYYMMDD_HHMMSS_{slug}/   # 세션 디렉토리
│       ├── current_knowledge.md   # 🌐 Global (100줄)
│       ├── curiosity_queue.json   # hole 목록
│       ├── holes/                 # 구멍별 보고서
│       │   ├── hole_1_컨텍스트최적화.md
│       │   └── hole_6_LLMLingua.md
│       └── state.json             # 세션 상태
└── current -> sessions/research_XXX/  # symlink (현재 세션)
```

**핵심:** 세션별로 완전 분리 → 여러 연구 동시 진행 가능, 충돌 없음

### curiosity_queue.json

```json
{
  "holes": [
    {
      "id": "hole_6",
      "topic": "LLMLingua",
      "goal": "압축 원리와 실제 적용 방법 파악",
      "keywords": ["압축", "프롬프트", "LLMLingua"],
      "interest": 0.95,
      "depth": 1,
      "parent": "hole_1",
      "status": "explored",
      "source": "websearch",
      "knowledge_type": "new",
      "discovered_at": 1,
      "understanding": 0.90
    }
  ]
}
```

**필수 필드:**
- `goal`: 이 hole에서 알고 싶은 것 (이해도 평가 기준)
- `parent`: 이 hole을 발견한 상위 hole (root면 null)

### current_knowledge.md (100줄 제한)

```markdown
# 연구: [질문]

## 핵심 발견
- [카테고리별 핵심 발견들]

## 탐구 축
| 축 | 핵심 hole | 인사이트 |
|---|----------|---------|
| ... | ... | ... |

## 열린 질문
- [아직 답을 모르는 것들]

## 수정/반증된 것
- [기존 믿음이 틀렸던 것]

---
*iteration N 기준*
```

### Hole 보고서 형식

```markdown
# {topic}

## 메타
- 흥미: 0.90 | 깊이: 2 | 상태: explored
- 부모: [[hole_1]] | 타입: new

## Goal
{이 hole에서 알고 싶은 것}

## 핵심 요약
[이 hole에서 알게 된 것 요약]

## 아직 모름 (status: pending일 때)
- [goal 중 아직 해결 안 된 부분]
- [다음 탐색에서 집중할 것]

---

## [Iter N] 탐색
**쿼리:** "..."
**발견:**
- 💡 새 개념 → [[hole_X]] 생성
- 📝 세부사항 (refined)
**검증:** ✓✓ 사실 (출처1, 출처2)
**이해도:** 0.5 (goal 달성: 구현방법 ✓, API사용법 ✗)

---

## 출처
| 태그 | 소스 | URL |
|------|------|-----|
| ✓✓ | Nature | https://... |
```

---

## 💡 완전 예시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐰 Iteration 3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## LOAD
🌐 current_knowledge.md 로드 (전체 연구 흐름 확인)
📌 Parent: hole_6 "LLMLingua" 보고서 로드
🕳️ 현재: hole_11 "LLMLingua-2 구현" (흥미 0.93)

## DIG

### 검색 (current_knowledge 참조)
이미 아는 것: "LLMLingua-2는 3-6x 빠름, BERT 기반"
모르는 것: 구체적 구현 방법, API 사용법

WebSearch("LLMLingua-2 implementation guide")
WebSearch("llmlingua pip install usage")

### 발견 & 분류
1. "PromptCompressor class" - current_knowledge에 없음 → [new]
2. "token classification approach" - 이미 BERT 기반 언급 → [refined]

### 검증
✓✓ "pip install llmlingua" (GitHub, PyPI, MS Blog)

## SAVE
- hole_11: explored
- current_knowledge.md 업데이트:
  + "PromptCompressor 클래스로 즉시 사용 가능"
- 새 hole 없음 (병합됨)

## LOOP
🔄 다음 iteration 시작 (pending: 8, 열린 질문: 3, 미완성: 2)
다음: hole_18 "UCB 기반 흥미 공식" (흥미 0.93)

🚨 Ralph Loop 활성화: 사용자가 중단할 때까지 무한 탐험!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

**🔥 Ralph Loop 철칙: 흥미를 따라 끝없이 파고들기!** 🐰🕳️✨

**절대 스스로 멈추지 마세요. 의문점이 하나라도 남았으면 계속!**
