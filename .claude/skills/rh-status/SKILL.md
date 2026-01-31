---
name: rh-status
description: 현재 토끼굴 탐험 상태를 확인합니다. 어떤 구멍을 파는 중인지, 큐에 무엇이 있는지, 발견 지도를 보여줍니다.
allowed-tools: Read, Bash
---

# 🐰 rh-status: 토끼굴 탐험 상태

현재 토끼굴 탐험 상태를 확인합니다.

## 📊 출력 정보

1. **현재 파는 구멍**
   - 어떤 주제인지
   - depth (얼마나 깊이 팠는지)
   - 興미 점수
   - 이해도

2. **큐 상태 (興미 순)**
   - 다음 파볼 구멍들
   - 興미 점수 순서
   - 우선순위

3. **발견 지도**
   - 어떤 구멍에서 어떤 구멍이 발견되었는지
   - 트리 구조로 시각화

4. **진행 상황**
   - 총 몇 개 구멍 파봤는지
   - 큐에 대기 중인 것
   - iteration, budget

---

## 실행

```python
import json
from pathlib import Path

# .research/state.json 읽기
state_path = Path(".research/state.json")

if not state_path.exists():
    print("📭 아직 탐험을 시작하지 않았습니다.")
    print("   /rh \"궁금한 주제\"로 시작하세요!")
    exit(0)

state = json.load(open(state_path))

# curiosity_queue 읽기
queue_path = Path(".research/curiosity_queue.json")
if queue_path.exists():
    queue = json.load(open(queue_path))
else:
    queue = {"holes": [], "current": None}

# 출력
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🐰 Rabbit Hole Status")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

# 현재 파는 구멍
current_hole_id = queue.get("current")
if current_hole_id:
    current_hole = next(
        (h for h in queue["holes"] if h["id"] == current_hole_id),
        None
    )
    if current_hole:
        print(f"🕳️ 현재 파는 중:")
        print(f"   {current_hole['id']} \"{current_hole['topic']}\"")
        print(f"   depth: {current_hole.get('depth', 0)}")
        print(f"   興미: {current_hole.get('interest', 0.0):.2f}")
        print(f"   이해도: {current_hole.get('understanding', 0)*100:.0f}%")
        print()
else:
    print("🕳️ 현재: 구멍 선택 중...")
    print()

# 큐 상태 (興미 순)
pending_holes = [
    h for h in queue["holes"]
    if h.get("status") != "explored" and h["id"] != current_hole_id
]
pending_holes.sort(key=lambda h: h.get("interest", 0.0), reverse=True)

if pending_holes:
    print("📊 큐 (興미 순):")
    for i, hole in enumerate(pending_holes[:5], 1):
        icon = "🔥" if hole.get("interest", 0) > 0.85 else "📌"
        next_mark = " ← 다음!" if i == 1 else ""
        print(f"   {i}. {icon} {hole['id']}: \"{hole['topic']}\" ({hole.get('interest', 0.0):.2f}){next_mark}")

    if len(pending_holes) > 5:
        print(f"   ... +{len(pending_holes) - 5}개 더")
    print()
else:
    print("📊 큐: 비었음 (새 구멍 발견 필요)")
    print()

# 발견 지도 (간단 버전)
explored = [h for h in queue["holes"] if h.get("status") == "explored"]
print(f"🗺️ 발견 지도:")
print(f"   파본 구멍: {len(explored)}개 ✅")
print(f"   큐 대기: {len(pending_holes)}개 📌")
print(f"   총 발견: {len(queue['holes'])}개")
print()
print(f"   자세한 지도: /rh-map")
print()

# 진행 상황
iteration = state.get("iteration", {}).get("current", 0)
max_iter = state.get("iteration", {}).get("max", 100)
budget = state.get("metrics", {}).get("cost_estimate_usd", 0.0)
budget_limit = 10.0

print(f"📈 진행:")
print(f"   ⏱️ Iteration: #{iteration} / {max_iter}")
print(f"   💰 Budget: ${budget:.2f} / ${budget_limit:.2f}")

print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
```
