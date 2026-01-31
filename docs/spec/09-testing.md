# 테스트 가이드

**문서:** 09-testing.md
**최종 수정일:** 2026-01-31
**관련 파일:** `.research/`, `config.json`, `.claude/hooks/stop-hook.py`

---

## 목차
- [테스트 전략](#테스트-전략)
- [Stop Hook 테스트](#stop-hook-테스트)
- [연구 사이클 테스트](#연구-사이클-테스트)
- [Loop Drift 테스트](#loop-drift-테스트)
- [검증 시스템 테스트](#검증-시스템-테스트)
- [통합 테스트](#통합-테스트)

---

## 테스트 전략

### 테스트 계층

```
┌─────────────────────────────────────┐
│  E2E 테스트 (통합)                   │
│  - 전체 연구 세션 실행               │
│  - 실제 WebSearch/Fetch 사용         │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  컴포넌트 테스트                     │
│  - Stop Hook                         │
│  - 연구 사이클 단계별                │
│  - Loop Drift 탐지                   │
└─────────────────────────────────────┘
         ↓
┌─────────────────────────────────────┐
│  단위 테스트                         │
│  - 개별 함수/로직                    │
│  - 데이터 스키마 검증                │
└─────────────────────────────────────┘
```

---

## Stop Hook 테스트

### 테스트 케이스

**파일:** `.claude/hooks/stop-hook.py`

**관련:** [03-ralph-loop.md](./03-ralph-loop.md)

---

### TC-SH-001: state.json 없음

**목적:** 일반 Claude Code 세션에서 종료 허용 확인

**전제 조건:**
```bash
# state.json 존재하지 않음
rm -f .research/state.json
```

**실행:**
```bash
echo '{}' | python3 .claude/hooks/stop-hook.py
echo "Exit code: $?"
```

**예상 결과:**
```
{"decision": "allow", "reason": "No active research session"}
Exit code: 0
```

**검증:**
- ✅ Exit code = 0 (종료 허용)
- ✅ decision = "allow"

---

### TC-SH-002: status = "initialized"

**목적:** 초기화 상태에서 종료 허용 확인

**전제 조건:**
```bash
cat > .research/state.json << 'EOF'
{
  "status": "initialized",
  "iteration": {"current": 0, "max": 100}
}
EOF
```

**실행:**
```bash
echo '{}' | python3 .claude/hooks/stop-hook.py
echo "Exit code: $?"
```

**예상 결과:**
```
Exit code: 0
```

**검증:**
- ✅ Exit code = 0 (종료 허용)

---

### TC-SH-003: status = "running"

**목적:** 연구 진행 중 종료 차단 확인 (Ralph Loop)

**전제 조건:**
```bash
cat > .research/state.json << 'EOF'
{
  "status": "running",
  "iteration": {"current": 5, "max": 100}
}
EOF
```

**실행:**
```bash
echo '{}' | python3 .claude/hooks/stop-hook.py
echo "Exit code: $?"
```

**예상 결과:**
```
{"decision": "block", "reason": "🔬 Research in progress..."}
Exit code: 1
```

**검증:**
- ✅ Exit code = 1 (종료 차단)
- ✅ decision = "block"
- ✅ Ralph Loop 유지

---

### TC-SH-004: status = "paused"

**목적:** 일시정지 상태에서 종료 허용 확인

**전제 조건:**
```bash
cat > .research/state.json << 'EOF'
{
  "status": "paused",
  "iteration": {"current": 10, "max": 100}
}
EOF
```

**실행:**
```bash
echo '{}' | python3 .claude/hooks/stop-hook.py
echo "Exit code: $?"
```

**예상 결과:**
```
Exit code: 0
```

**검증:**
- ✅ Exit code = 0 (종료 허용)

---

### TC-SH-005: status = "completed"

**목적:** 완료 상태에서 종료 허용 확인

**전제 조건:**
```bash
cat > .research/state.json << 'EOF'
{
  "status": "completed",
  "iteration": {"current": 50, "max": 100}
}
EOF
```

**실행:**
```bash
echo '{}' | python3 .claude/hooks/stop-hook.py
echo "Exit code: $?"
```

**예상 결과:**
```
Exit code: 0
```

**검증:**
- ✅ Exit code = 0 (종료 허용)

---

### TC-SH-006: Loop Drift 탐지

**목적:** 5회 연속 같은 행동 시 강제 종료

**전제 조건:**
```bash
cat > .research/state.json << 'EOF'
{
  "status": "running",
  "iteration": {"current": 15, "max": 100}
}
EOF

# Stop hook에 loop drift 정보 전달
echo '{"stop_hook_active": true, "iteration": 15, "consecutive_same": 6}' \
  | python3 .claude/hooks/stop-hook.py
```

**예상 결과:**
```
Exit code: 0 (Loop drift 탐지로 종료 허용)
```

**검증:**
- ✅ Exit code = 0
- ✅ Loop drift 탐지

---

### Stop Hook 자동 테스트 스크립트

```bash
#!/bin/bash
# test-stop-hook.sh

echo "=========================================="
echo "Stop Hook Test Suite"
echo "=========================================="

# Test 1: No state file
rm -f .research/state.json
result=$(echo '{}' | python3 .claude/hooks/stop-hook.py 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "✅ TC-SH-001: PASS (No state file)"
else
  echo "❌ TC-SH-001: FAIL (Expected 0, got $exit_code)"
fi

# Test 2: status = initialized
cat > .research/state.json << 'EOF'
{"status": "initialized", "iteration": {"current": 0, "max": 100}}
EOF
result=$(echo '{}' | python3 .claude/hooks/stop-hook.py 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "✅ TC-SH-002: PASS (status=initialized)"
else
  echo "❌ TC-SH-002: FAIL (Expected 0, got $exit_code)"
fi

# Test 3: status = running
cat > .research/state.json << 'EOF'
{"status": "running", "iteration": {"current": 5, "max": 100}}
EOF
result=$(echo '{}' | python3 .claude/hooks/stop-hook.py 2>&1)
exit_code=$?
if [ $exit_code -eq 1 ]; then
  echo "✅ TC-SH-003: PASS (status=running, Ralph Loop)"
else
  echo "❌ TC-SH-003: FAIL (Expected 1, got $exit_code)"
fi

# Test 4: status = paused
cat > .research/state.json << 'EOF'
{"status": "paused", "iteration": {"current": 10, "max": 100}}
EOF
result=$(echo '{}' | python3 .claude/hooks/stop-hook.py 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "✅ TC-SH-004: PASS (status=paused)"
else
  echo "❌ TC-SH-004: FAIL (Expected 0, got $exit_code)"
fi

# Test 5: status = completed
cat > .research/state.json << 'EOF'
{"status": "completed", "iteration": {"current": 50, "max": 100}}
EOF
result=$(echo '{}' | python3 .claude/hooks/stop-hook.py 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "✅ TC-SH-005: PASS (status=completed)"
else
  echo "❌ TC-SH-005: FAIL (Expected 0, got $exit_code)"
fi

# Cleanup
rm -f .research/state.json

echo "=========================================="
echo "Stop Hook Tests Complete"
echo "=========================================="
```

**실행:**

```bash
chmod +x test-stop-hook.sh
./test-stop-hook.sh
```

---

## 연구 사이클 테스트

### TC-RC-001: 9단계 사이클 완전성

**목적:** 1회 iteration에서 9단계 모두 실행 확인

**실행:**
```bash
# config 설정: 1회만 실행
jq '.loop_control.max_iterations = 1' config.json > tmp.json
mv tmp.json config.json

# 연구 시작
./research.sh 1 "테스트 질문: GPT-4란?"
```

**검증:**

1. **LOAD**: `.research/state.json` 생성 확인
   ```bash
   test -f .research/state.json && echo "✅ LOAD" || echo "❌ LOAD"
   ```

2. **REFLECT**: Extended Thinking 사용 확인 (로그)

3. **PLAN**: 검색 쿼리 3-5개 생성 확인
   ```bash
   query_count=$(jq '.queries | length' .research/search_history.json)
   [ $query_count -ge 3 ] && echo "✅ PLAN" || echo "❌ PLAN"
   ```

4. **EXECUTE**: WebSearch 실행 확인
   ```bash
   [ $query_count -gt 0 ] && echo "✅ EXECUTE" || echo "❌ EXECUTE"
   ```

5. **VERIFY**: findings.md에 신뢰도 태그 확인
   ```bash
   grep -E '✓✓|✓|~|\?|⚠' .research/findings.md && echo "✅ VERIFY" || echo "❌ VERIFY"
   ```

6. **SYNTHESIZE**: knowledge_graph.json 업데이트 확인
   ```bash
   test -f .research/knowledge_graph.json && echo "✅ SYNTHESIZE" || echo "❌ SYNTHESIZE"
   ```

7. **SAVE**: 모든 파일 생성 확인
   ```bash
   test -f .research/state.json && \
   test -f .research/findings.md && \
   test -f .research/search_history.json && \
   echo "✅ SAVE" || echo "❌ SAVE"
   ```

8. **OUTPUT**: 진행 상황 출력 확인 (시각 검사)

9. **LOOP**: iteration 카운터 증가 확인
   ```bash
   current=$(jq '.iteration.current' .research/state.json)
   [ $current -eq 1 ] && echo "✅ LOOP" || echo "❌ LOOP"
   ```

---

### TC-RC-002: 병렬 검색 동작

**목적:** 3개 검색이 병렬로 실행되는지 확인

**측정 방법:**

```bash
# 시간 측정
start=$(date +%s)

# 3개 병렬 검색 (스킬 내부)
# (실제로는 스킬이 자동으로 실행)

end=$(date +%s)
duration=$((end - start))

echo "Duration: ${duration}s"

# 예상: 30-40초 (순차라면 90초+)
if [ $duration -lt 60 ]; then
  echo "✅ 병렬 검색 동작 (${duration}s < 60s)"
else
  echo "⚠️ 순차 검색 가능성 (${duration}s >= 60s)"
fi
```

---

## Loop Drift 테스트

### TC-LD-001: 같은 쿼리 2회 반복 탐지

**목적:** search_history.json으로 중복 탐지 확인

**전제 조건:**
```bash
cat > .research/search_history.json << 'EOF'
{
  "queries": [
    {
      "iteration": 1,
      "query": "quantum computing",
      "normalized": "quantumcomputing",
      "result_count": 10
    },
    {
      "iteration": 2,
      "query": "quantum computing",
      "normalized": "quantumcomputing",
      "result_count": 10
    }
  ]
}
EOF
```

**검증 스크립트:**
```bash
# 중복 쿼리 탐지
duplicates=$(jq '.queries | group_by(.normalized) | map(select(length > 1)) | length' \
  .research/search_history.json)

if [ $duplicates -gt 0 ]; then
  echo "✅ 중복 쿼리 탐지됨"
  jq '.queries | group_by(.normalized) | map(select(length > 1))' \
    .research/search_history.json
else
  echo "❌ 중복 탐지 실패"
fi
```

---

### TC-LD-002: Reflexion 메모리 학습

**목적:** 실패 패턴이 reflexion.json에 기록되는지 확인

**실행:**
```bash
# 의도적으로 같은 쿼리 반복 시도
# (실제로는 스킬이 자동 탐지 후 기록)
```

**검증:**
```bash
# reflexion.json 확인
failure_count=$(jq '.iterations | map(select(.outcome == "failure")) | length' \
  .research/reflexion.json)

if [ $failure_count -gt 0 ]; then
  echo "✅ 실패 패턴 기록됨 (${failure_count}개)"
  jq '.iterations | map(select(.outcome == "failure"))' .research/reflexion.json
else
  echo "❌ 실패 기록 없음"
fi
```

---

## 검증 시스템 테스트

### TC-VE-001: 소스 신뢰도 점수 적용

**목적:** 도메인별 신뢰도 점수가 올바르게 적용되는지 확인

**검증 스크립트:**
```python
# test_credibility.py

import json

with open('config.json') as f:
    config = json.load(f)

credibility = config['verification']['credibility_scores']

# 테스트 케이스
test_cases = [
    ("arxiv.org", 0.95),
    ("nature.com", 0.98),
    ("medium.com", 0.50),
    ("unknown.com", 0.30)  # default
]

for domain, expected in test_cases:
    actual = credibility.get(domain, credibility['default'])
    if actual == expected:
        print(f"✅ {domain}: {actual}")
    else:
        print(f"❌ {domain}: expected {expected}, got {actual}")
```

**실행:**
```bash
python3 test_credibility.py
```

---

### TC-VE-002: 신뢰도 태그 부여

**목적:** 소스 수에 따라 올바른 태그가 부여되는지 확인

**검증:**
```bash
# findings.md에서 태그 분포 확인
echo "=== Confidence Tag Distribution ==="
echo "✓✓ (verified): $(grep -c '✓✓' .research/findings.md || echo 0)"
echo "✓ (high): $(grep -c ' ✓ ' .research/findings.md || echo 0)"
echo "~ (likely): $(grep -c ' ~ ' .research/findings.md || echo 0)"
echo "? (uncertain): $(grep -c ' \? ' .research/findings.md || echo 0)"
echo "⚠ (contradicted): $(grep -c ' ⚠ ' .research/findings.md || echo 0)"
```

---

## 통합 테스트

### TC-INT-001: 전체 연구 세션 (5 iterations)

**목적:** 5회 iteration 완전 실행 검증

**실행:**
```bash
# 초기화
rm -rf .research
mkdir -p .research

# config 설정
jq '.loop_control.max_iterations = 5' config.json > tmp.json
mv tmp.json config.json
jq '.cost_control.budget_per_session_usd = 2.0' config.json > tmp.json
mv tmp.json config.json

# 연구 시작
./research.sh 5 "GPT-4의 주요 기능은?"
```

**검증 체크리스트:**

- [ ] 5회 iteration 모두 완료
- [ ] state.json: `iteration.current = 5`
- [ ] search_history.json: 15+ 쿼리 (3/iteration × 5)
- [ ] findings.md: 10+ 발견 사항
- [ ] knowledge_graph.json: 5+ 노드
- [ ] reflexion.json: 학습 규칙 생성
- [ ] 예산 초과 없음 (< $2.00)
- [ ] Loop drift 발생 없음

**검증 스크립트:**
```bash
#!/bin/bash
# verify-integration.sh

echo "=========================================="
echo "Integration Test Verification"
echo "=========================================="

# Iteration count
current=$(jq '.iteration.current' .research/state.json)
echo "Iterations: $current / 5"
[ $current -eq 5 ] && echo "✅" || echo "❌"

# Query count
query_count=$(jq '.queries | length' .research/search_history.json)
echo "Queries: $query_count (expected: 15+)"
[ $query_count -ge 15 ] && echo "✅" || echo "❌"

# Findings count
findings_count=$(grep -c '^- ✓' .research/findings.md || echo 0)
echo "Findings: $findings_count (expected: 10+)"
[ $findings_count -ge 10 ] && echo "✅" || echo "❌"

# Knowledge graph nodes
node_count=$(jq '.nodes | length' .research/knowledge_graph.json)
echo "KG Nodes: $node_count (expected: 5+)"
[ $node_count -ge 5 ] && echo "✅" || echo "❌"

# Budget check
budget=$(jq '.metrics.cost_estimate_usd' .research/state.json)
echo "Budget: \$$budget / \$2.00"
# (bc 비교)

echo "=========================================="
```

---

### TC-INT-002: Ralph Loop 지속성

**목적:** Ralph Loop이 의도치 않게 종료되지 않는지 확인

**실행:**
```bash
# status=running으로 설정하고 5회 실행
jq '.loop_control.max_iterations = 5' config.json > tmp.json
mv tmp.json config.json

./research.sh 5 "양자 컴퓨팅이란?"

# 중간에 Ctrl+C 시도 (Stop Hook이 차단해야 함)
```

**예상 동작:**
```
Iteration 1 실행 중...
  ↓
사용자: Ctrl+C
  ↓
Stop Hook: Exit 1 (차단)
  ↓
Iteration 2 계속 실행...
```

**검증:**
- ✅ Ctrl+C로 종료되지 않음
- ✅ status="running" 유지
- ✅ 5회까지 계속 실행

---

## 성능 벤치마크

### Iteration당 소요 시간

**측정:**
```bash
# iteration_logs/001.md에서 시간 추출
start_time=$(grep "시작 시간" .research/iteration_logs/001.md | cut -d' ' -f3)
end_time=$(grep "종료 시간" .research/iteration_logs/001.md | cut -d' ' -f3)

# 계산 (초 단위)
# ...

echo "Iteration 1 duration: ${duration}s"
```

**기준:**
- ✅ 목표: 2-3분 (120-180초)
- ⚠️ 주의: 3-5분 (병렬 처리 확인 필요)
- ❌ 실패: 5분 이상 (순차 실행 가능성)

---

### 예산 효율성

**측정:**
```bash
# 100 iterations 기준
total_cost=$(jq '.metrics.cost_estimate_usd' .research/state.json)
iterations=$(jq '.iteration.current' .research/state.json)

cost_per_iteration=$(echo "scale=4; $total_cost / $iterations" | bc)

echo "Cost per iteration: \$${cost_per_iteration}"
```

**기준:**
- ✅ 목표: $0.03 - $0.05 / iteration
- ⚠️ 주의: $0.05 - $0.10 / iteration
- ❌ 실패: $0.10+ / iteration

---

## 테스트 자동화

### CI/CD 통합

```yaml
# .github/workflows/test.yml

name: Pathfinder Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          pip install jsonschema

      - name: Test Stop Hook
        run: |
          chmod +x test-stop-hook.sh
          ./test-stop-hook.sh

      - name: Validate JSON schemas
        run: |
          python3 -c "import json; json.load(open('config.json'))"
          python3 -c "import json; json.load(open('.claude/settings.json'))"

      - name: Integration test (mini)
        run: |
          # 소규모 통합 테스트 (5 iterations, $0.50 예산)
          jq '.loop_control.max_iterations = 5' config.json > tmp.json
          mv tmp.json config.json
          jq '.cost_control.budget_per_session_usd = 0.5' config.json > tmp.json
          mv tmp.json config.json

          ./research.sh 5 "Test question"

          # 검증
          chmod +x verify-integration.sh
          ./verify-integration.sh
```

---

**다음:** [10-deployment.md](./10-deployment.md) - 배포 가이드
