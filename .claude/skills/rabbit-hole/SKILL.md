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
1. **흥미를 따라가세요** - 順序 말고 興미 순
2. **멈추지 마세요** - 사용자가 중단할 때까지
3. **자유롭게** - 규칙은 가이드일 뿐, 직관을 믿으세요

---

## 🔄 사이클 (4단계)

```
1. LOAD  - 상태 로드
2. DIG   - 자유 탐색
3. SAVE  - 상태 저장 + 출력
4. LOOP  - 다음으로
```

---

## 1. LOAD

**현재 상태 확인:**

```bash
cat .research/state.json 2>/dev/null || echo '{"iteration":{"current":0}}'
cat .research/curiosity_queue.json 2>/dev/null || echo '{"holes":[]}'
cat .research/info_hubs.json 2>/dev/null || echo '{"hubs":[]}'
```

**첫 실행 시:**
```python
# 초기 질문 분해
question = "$ARGUMENTS"

# 여러 초기 구멍 생성 (Extended Thinking)
initial_holes = [
    {"topic": "aspect_1", "interest": 0.85, "depth": 0},
    {"topic": "aspect_2", "interest": 0.80, "depth": 0},
    {"topic": "aspect_3", "interest": 0.75, "depth": 0}
]

# curiosity_queue.json에 저장
```

**이어서 실행 시:**
```python
# 기존 큐 로드
holes = load_queue()
current_hole = select_most_interesting(holes)  # 興미 높은 것
```

---

## 2. DIG (핵심!)

**철학: 자유롭게 탐색하되, 출처는 꼭 확보**

### 구멍 선택 (직관)

Extended Thinking으로 가장 끌리는 구멍 선택:
```
큐:
- hole_4 "Majorana" (興미: 0.90, depth: 0)
- hole_7 "Kitaev" (興미: 0.80, depth: 0)
- hole_2 "비용" (興미: 0.65, depth: 1)

직관: "Majorana가 가장 흥미로워!"
→ hole_4 선택
```

### 탐색 프로세스 (자유롭게)

```
1. 쿼리 생성 (Extended Thinking)
   - 어떻게 팔까?
   - 여러 각도 시도 (이론, 실험, 응용, 비교...)
   - 발산 도구: 제1원칙, SCAMPER, Matrix of Thought, TRIZ
   - 3-5개 쿼리 생성

2. 검색 전략 (depth 기반)

   depth 0-1 (발산 모드):
   - 일반 검색만
   - 목표: 새로운 구멍 발견

   depth 2+ (수렴 모드):
   - 일반 30% + 허브 한정 70%
   - 목표: 깊은 이해, 검증

3. 병렬 검색
   WebSearch(q1)  # 병렬
   WebSearch(q2)  # 병렬
   WebSearch(q3)  # 병렬

4. 발견 & 검증
   - 검색 결과 읽으며 새 개념 발견
   - 興미 판단 (직관 + 가이드)
   - 출처 확인 (필수!)
   - 교차 검증 (3개 소스 권장)

5. 이해 구축
   - 정보 종합
   - 수렴 도구: 오컴의 면도날, 베이지안, 반증 가능성, 변증법
   - 간단명료하게

6. 판단
   - 더 팔까? (depth++)
   - 다른 구멍으로? (pivot)
```

### depth 기반 검색 (예시)

```python
# 관련 허브 조회
hubs = get_hubs_for_topic(hole.topic)  # info_hubs.json
hub_domains = [h.domain for h in hubs[:3]]

if hole.depth <= 1:
    # 발산: 넓게 탐색
    WebSearch("Majorana fermion what is")
    WebSearch("Majorana vs Dirac")
    WebSearch("Majorana experiment")
else:
    # 수렴: 깊게 파기
    WebSearch("Majorana braiding")  # 일반 (30%)
    WebSearch("Majorana topological",
              allowed_domains=hub_domains)  # 허브 (70%)
    WebSearch("Majorana qubit error",
              allowed_domains=hub_domains)
```

### 새 구멍 발견 (興미 판단)

**직관 + 간단한 가이드:**

```
발견: "Kitaev chain model"

Extended Thinking:
- 얼마나 근본적? (높음/중간/낮음)
- 원래 질문과 연결? (직결/연관/간접)
- 새로운 개념? (완전/들어봤음/아는것)
- 구체적? (데이터/방법론/추상)

직관: "Majorana의 기초 모델이네! 흥미롭다!"
→ 興미: 0.80 (높음)
→ 0.80 > 0.70 → 큐 추가!
```

**임계값: 0.70** (이하는 무시)

### 출처 검증 (필수!)

**규칙:**
```
1. 모든 사실적 주장 → 출처 필수
   - ✅ "GPT-4는 2023년 3월 출시 (openai.com)"
   - ❌ "GPT-4는 2023년 3월 출시" ← 출처 없으면 안 씀!

2. 교차 검증 (권장)
   - 1개 소스: 신뢰도 0.6 (낮음)
   - 2개 소스: 신뢰도 0.8 (중간)
   - 3개+ 소스: 신뢰도 0.95 (높음)

3. 태그
   - ✓✓ VERIFIED (3개+ 소스)
   - ✓ HIGH (1-2개 소스)
   - ? UNCERTAIN (출처 없음 → 쓰지 마!)
```

**출처별 신뢰도:**
- Peer-reviewed (Nature, Science): 0.9
- 공식 발표: 0.85
- Preprint (arXiv): 0.75
- 전문 뉴스: 0.7
- 블로그: 0.5

### 허브 발견 & 관리

**검색 중 고품질 소스 발견 시:**
```python
# 허브 후보 판단 (Extended Thinking)
if domain이 전문적이고 유용하면:
    # info_hubs.json에 추가
    {
        "domain": "arxiv.org",
        "category": "academic",
        "quality_score": 0.90,
        "notes": "물리학, CS 논문"
    }
```

---

## 3. SAVE

```python
# 구멍 상태 업데이트
update_hole(
    hole_id=selected_hole.id,
    depth=selected_hole.depth + 1,
    status="explored",
    understanding=0.75
)

# 큐 저장
save_queue()  # curiosity_queue.json

# 허브 저장
save_hubs()  # info_hubs.json

# state.json 업데이트
state["iteration"]["current"] += 1

# 진행 상황 출력
print(f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐰 Rabbit Hole #{state['iteration']['current']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🕳️ 탐험: "{selected_hole.topic}"

💡 발견:
  - "new_hole_1" (興미 0.85)
  - "new_hole_2" (興미 0.75)

✓✓ 검증:
  - 핵심 사실 1 (3개 소스)
  - 핵심 사실 2 (2개 소스)

📊 큐: {len(queue)}개 구멍 대기
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")
```

---

## 4. LOOP

```python
# 종료 조건 체크
if state["status"] == "running" and iteration < max_iter:
    # 다음 구멍으로!
    Skill(skill="rabbit-hole", args="")
else:
    print("🐰 탐험 종료!")
```

**종료 조건:**
- status == "stopped_by_user"
- iteration >= max_iterations
- curiosity_queue 비었음

**그 외: 계속!**

---

## 📋 데이터 구조

### curiosity_queue.json

```json
{
  "holes": [
    {
      "id": "hole_1",
      "topic": "Majorana fermion",
      "interest": 0.90,
      "depth": 0,
      "parent": null,
      "status": "pending",
      "source": "initial_question"
    },
    {
      "id": "hole_2",
      "topic": "Kitaev chain",
      "interest": 0.80,
      "depth": 0,
      "parent": "hole_1",
      "status": "pending",
      "source": "search_result_3"
    }
  ]
}
```

### info_hubs.json

```json
{
  "hubs": [
    {
      "id": "hub_1",
      "domain": "arxiv.org",
      "name": "arXiv",
      "category": "academic",
      "quality_score": 0.95,
      "hit_count": 12,
      "notes": "물리학, CS, 수학 논문"
    }
  ],
  "category_index": {
    "academic": ["hub_1", "hub_2"],
    "tech": ["hub_3"]
  }
}
```

---

## 💡 완전 예시

```markdown
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🐰 Iteration 1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## LOAD
큐에서 선택: "Majorana fermion" (興미 0.90, depth 0)

## DIG

### 탐색 전략 (depth 0 → 발산 모드)

Extended Thinking:
"Majorana가 뭐지? 여러 각도로 파보자"
- 기본 개념: "what is"
- 비교: "vs Dirac"
- 실험: "experiment"
- 응용: "quantum computing"

### 검색 (병렬)
WebSearch("Majorana fermion what is")
WebSearch("Majorana vs Dirac fermion")
WebSearch("Majorana zero modes experiment")
WebSearch("Majorana topological quantum")

### 발견

검색 결과 1 (Nature):
"Majorana fermions are quasi-particles...
 described by Kitaev chain model..."

→ 💡 발견: "Kitaev chain model"
   興미: 0.80 (근본적 모델!)
   → 큐 추가!

검색 결과 3 (arXiv):
"Microsoft's topological qubit project..."

→ 💡 발견: "Microsoft topological qubit"
   興미: 0.85 (실용화 직결!)
   → 큐 추가!

→ 🏛️ 허브 발견: "arxiv.org" (고품질)
   → info_hubs.json 추가!

### 검증

주장: "Majorana는 토폴로지 큐비트 핵심"

✓✓ VERIFIED (3개 소스):
- Nature 논문
- Science 논문
- Microsoft 공식 블로그

### 이해

"Majorana = 자기 자신이 반입자인 준입자.
 Kitaev chain으로 모델링.
 토폴로지 양자 컴퓨팅의 핵심 요소.
 Microsoft가 구현 시도 중."

이해도: 75%

### 판단

더 팔까?
- 기본 개념 이해 완료 ✓
- 새 구멍 2개 발견 ✓
- Microsoft 쪽이 더 흥미로운데? (0.85 > 0.80)

→ Pivot to "Microsoft topological qubit"!

## SAVE

큐 업데이트:
- hole_1 "Majorana": explored (depth 1)
- hole_2 "Kitaev chain": pending (新)
- hole_3 "Microsoft qubit": pending (新)

## LOOP

다음: hole_3 "Microsoft qubit" (興미 0.85)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 인수 처리

- 첫 실행: `$ARGUMENTS` = 연구 질문
- 이후: state.json 사용 (args 무시)

---

**흥미를 따라 끝없이 파고들기!** 🐰🕳️✨
