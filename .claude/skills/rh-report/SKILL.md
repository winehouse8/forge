---
name: rh-report
description: 토끼굴 탐험 결과를 종합하여 원래 질문에 대한 최종 답변을 생성합니다.
allowed-tools: Read, Bash
---

# 🎯 rh-report: 토끼굴 탐험 결과 종합

지금까지 판 구멍들의 발견 사항을 종합하여 원래 질문에 대한 답변을 도출합니다.

## 프로세스

1. **수집**: curiosity_queue.json에서 탐색 완료된 구멍들 수집
2. **정리**: 이해도 높은 순으로 핵심 발견 정리
3. **종합**: Extended Thinking + 수렴적 사고 도구로 최종 답변 도출

---

## 실행

```python
import json
from pathlib import Path

# curiosity_queue 읽기
queue_path = Path(".research/curiosity_queue.json")

if not queue_path.exists():
    print("📭 아직 탐험을 시작하지 않았습니다.")
    print("   /rh \"궁금한 주제\"로 시작하세요!")
    exit(0)

queue = json.load(open(queue_path))
holes = queue.get("holes", [])
initial_question = queue.get("initial_question", "")

if not holes:
    print("📭 아직 구멍을 발견하지 못했습니다.")
    exit(0)

# Explored 구멍들만 수집
explored = [h for h in holes if h.get("status") == "explored"]

if not explored:
    print("⚠️  아직 탐색 완료된 구멍이 없습니다.")
    print("   조금 더 파본 후 다시 시도하세요.")
    exit(0)

# 보고서 생성
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🎯 토끼굴 탐험 결과 보고서")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()
print(f"**원래 질문:** \"{initial_question}\"")
print()

# 탐험 요약
pending = [h for h in holes if h.get("status") != "explored"]
print("## 📊 탐험 요약")
print(f"- 파본 구멍: {len(explored)}개 ✅")
print(f"- 큐 대기: {len(pending)}개 📌")
print(f"- 총 발견: {len(holes)}개")
print()

# 핵심 발견 (이해도 높은 순)
explored_sorted = sorted(explored, key=lambda h: h.get("understanding", 0), reverse=True)

print("## 🔍 핵심 발견")
print()

for i, hole in enumerate(explored_sorted[:10], 1):  # 상위 10개만
    topic = hole.get("topic", "")
    understanding = hole.get("understanding", 0)
    findings = hole.get("findings", [])
    depth = hole.get("depth", 0)

    print(f"### {i}. {topic}")
    print(f"(이해도: {understanding*100:.0f}% | depth: {depth})")
    print()

    if findings:
        # 발견 사항 표시 (최대 5개)
        for j, finding in enumerate(findings[:5], 1):
            text = finding.get("text", "")
            source = finding.get("source")
            confidence = finding.get("confidence", 0)

            # 신뢰도 아이콘
            if confidence >= 0.9:
                icon = "✓✓"
            elif confidence >= 0.7:
                icon = "✓"
            elif confidence >= 0.5:
                icon = "~"
            else:
                icon = "?"

            print(f"{j}. {icon} {text}")
            if source:
                print(f"   출처: {source}")

        if len(findings) > 5:
            print(f"   ... +{len(findings) - 5}개 발견 더")
        print()
    else:
        print("- (세부 발견 사항 기록 없음)")
        print()

if len(explored_sorted) > 10:
    print(f"... +{len(explored_sorted) - 10}개 구멍 더 탐색됨")
    print()

# 대기 중인 흥미로운 구멍들
high_interest_pending = [h for h in pending if h.get("interest", 0) > 0.85]
if high_interest_pending:
    print("## 🔥 추가 탐험 후보 (興미 높음)")
    print()
    for hole in high_interest_pending[:3]:
        print(f"- {hole.get('topic', '')} (興미: {hole.get('interest', 0):.2f})")
    print()

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
```

---

## 최종 답변 도출

Extended Thinking을 사용하여 다음을 수행하세요:

### 1. 수렴적 사고 도구 활용

**참고:** `.claude/skills/rabbit-hole/references/convergent_thinking.md`

- **오컴의 면도날**: 복잡한 설명보다 단순한 설명 우선
- **베이지안 추론**: 증거 기반 확신도 계산
  - 단일 신뢰 소스: 0.6
  - 2개 소스 일치: 0.8
  - 3개+ 소스 일치: 0.95
- **반증 가능성**: 반박 증거 고려
- **변증법적 사고**: 대립 관점 통합 (정-반-합)

### 2. 원래 질문에 대한 최종 답변

다음 형식으로 답변을 작성하세요:

```markdown
## 🎯 최종 답변

**질문:** "[원래 질문]"

**답변:**

[핵심 발견들을 종합한 답변]

**확신도:** [0.00-1.00] [태그]
- ✓✓ VERIFIED (0.85+): 다수 신뢰 소스 일치
- ✓ HIGH (0.70-0.84): 단일 신뢰 소스
- ~ LIKELY (0.50-0.69): 추정
- ? UNCERTAIN (<0.50): 불확실

**핵심 근거:**
1. [근거 1] (출처: ...)
2. [근거 2] (출처: ...)
3. [근거 3] (출처: ...)

**제한 사항 / 주의점:**
- [알려진 제한 사항이나 주의할 점]

**추가 탐험 제안 (선택):**
- [아직 파지 않은 흥미로운 구멍이 있다면]
```

### 3. 종합 시 고려사항

- **모순 처리**: 서로 다른 구멍에서 발견한 내용이 충돌하면 변증법적 사고로 통합
- **이해도 가중치**: 이해도가 높은 구멍의 발견에 더 큰 가중치
- **신뢰도 누적**: 같은 내용이 여러 구멍에서 발견되면 확신도 증가
- **깊이 고려**: depth가 깊은 구멍일수록 해당 주제에 대한 통찰이 깊음

---

**사용 예:**

```bash
# 토끼굴 탐험
/rh "양자 컴퓨팅 실용화 시기?"

# (충분히 팠다고 판단)
# 중단 (Ctrl+C 또는 사용자 입력)

# 결과 종합
/rh-report
```
