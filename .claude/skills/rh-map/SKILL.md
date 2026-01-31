---
name: rh-map
description: 토끼굴 탐험 지도를 시각화합니다. 어떤 구멍에서 어떤 구멍이 발견되었는지 트리 구조로 보여줍니다.
allowed-tools: Read, Bash
---

# 🗺️ rh-map: 토끼굴 탐험 지도

발견한 구멍들의 관계를 트리 구조로 시각화합니다.

## 범례

- ✅ explored (탐색 완료)
- 🔍 digging (현재 파는 중)
- 🔥 high interest (높은 興미, 다음 후보)
- 📌 queued (큐 대기)
- ⚠️ low interest (낮은 興미)

---

## 실행

```python
import json
from pathlib import Path
from collections import defaultdict

# curiosity_queue 읽기
queue_path = Path(".research/curiosity_queue.json")

if not queue_path.exists():
    print("📭 아직 탐험을 시작하지 않았습니다.")
    print("   /rh \"궁금한 주제\"로 시작하세요!")
    exit(0)

queue = json.load(open(queue_path))
holes = queue.get("holes", [])
current_id = queue.get("current")

if not holes:
    print("📭 아직 구멍을 발견하지 못했습니다.")
    exit(0)

# 트리 구조 만들기
children = defaultdict(list)
roots = []

for hole in holes:
    parent = hole.get("parent")
    if parent:
        children[parent].append(hole)
    else:
        roots.append(hole)

# 아이콘 결정
def get_icon(hole):
    status = hole.get("status", "pending")
    interest = hole.get("interest", 0.0)
    hole_id = hole["id"]

    if hole_id == current_id:
        return "🔍"
    elif status == "explored":
        return "✅"
    elif interest > 0.85:
        return "🔥"
    elif interest < 0.65:
        return "⚠️"
    else:
        return "📌"

# 재귀적으로 트리 출력
def print_tree(hole, prefix="", is_last=True):
    icon = get_icon(hole)
    connector = "└─" if is_last else "├─"

    # 현재 구멍 출력
    print(f"{prefix}{connector} {icon} {hole['id']} \"{hole['topic']}\" ({hole.get('interest', 0.0):.2f})")

    # 자식 구멍들
    kids = children.get(hole["id"], [])
    kids.sort(key=lambda h: h.get("interest", 0.0), reverse=True)

    for i, child in enumerate(kids):
        is_last_child = (i == len(kids) - 1)
        extension = "    " if is_last else "│   "
        print_tree(child, prefix + extension, is_last_child)

# 출력
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print("🗺️ Rabbit Hole Map")
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
print()

# 루트부터 출력
roots.sort(key=lambda h: h.get("interest", 0.0), reverse=True)
for i, root in enumerate(roots):
    print_tree(root)
    if i < len(roots) - 1:
        print()

print()
print("범례:")
print("  ✅ explored (탐색 완료)")
print("  🔍 digging (현재 파는 중)")
print("  🔥 high interest (높은 興미, 다음 후보)")
print("  📌 queued (큐 대기)")
print("  ⚠️ low interest (낮은 興미)")
print()
print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
```
