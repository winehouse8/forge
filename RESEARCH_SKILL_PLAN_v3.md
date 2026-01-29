# Research Skill 계획서 v3

> **기반 연구**: v1/v2 계획서 + 2025년 최신 Deep Research 실증 연구 종합
> - Anthropic Multi-Agent Research System
> - Ralph Wiggum Loop Technique
> - Graphiti Temporal Knowledge Graph
> - DeepResearch Bench / RACE+FACT 평가 프레임워크
> - 프로덕션 실패 사례 및 Loop Drift 방지 기법

---

## 1. 핵심 아키텍처

### 1.1 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    INFINITE LOOP RESEARCH BOT ARCHITECTURE                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              RALPH LOOP CONTROLLER (research.sh)                    │    │
│  │  ┌──────────────────────────────────────────────────────────────┐  │    │
│  │  │  while [ $iteration -lt $MAX_ITERATIONS ]; do                 │  │    │
│  │  │      # 사용자 인터럽트 체크 (q/s 키)                          │  │    │
│  │  │      # completion_promise 체크                                │  │    │
│  │  │      # Loop Drift 탐지                                        │  │    │
│  │  │      claude --skill research_cycle                            │  │    │
│  │  │  done                                                         │  │    │
│  │  └──────────────────────────────────────────────────────────────┘  │    │
│  │  Stop Hook: exit code 2로 종료 차단 → 동일 프롬프트 재주입         │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│                                    ↓                                        │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              LEAD AGENT (Fresh Context per Iteration)               │    │
│  │                                                                      │    │
│  │  1. LOAD: state.json + 최근 3개 iteration 로그                      │    │
│  │  2. REFLECT: Extended Thinking으로 현재 상태 분석                   │    │
│  │  3. PLAN: Query Decomposition + 서브에이전트 전략 수립              │    │
│  │  4. DELEGATE: 3-5개 서브에이전트 병렬 생성                          │    │
│  │  5. SYNTHESIZE: 결과 통합 + 가설 업데이트                           │    │
│  │  6. SAVE: 상태 저장 + 보고서 업데이트                               │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                    │                                        │
│              ┌─────────────────────┼─────────────────────┐                 │
│              ↓                     ↓                     ↓                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐         │
│  │  Web Search      │  │  Academic Search │  │  Verification    │         │
│  │  SubAgent        │  │  SubAgent        │  │  SubAgent        │         │
│  │                  │  │                  │  │                  │         │
│  │  - WebSearch ×3  │  │  - arXiv API     │  │  - 교차 검증     │         │
│  │  - WebFetch      │  │  - Semantic S2   │  │  - 신뢰도 평가   │         │
│  │  - Context7      │  │  - PDF 다운로드  │  │  - 모순 탐지     │         │
│  │  (병렬 도구 호출)│  │  - Read(PDF)     │  │  - 소스 확인     │         │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘         │
│              │                     │                     │                  │
│              └─────────────────────┼─────────────────────┘                 │
│                                    ↓                                        │
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │                    FILE-BASED PERSISTENT MEMORY                     │    │
│  │                                                                      │    │
│  │  .research/                                                          │    │
│  │  ├── state.json              # 핵심 상태 (v3 구조)                  │    │
│  │  ├── knowledge_graph.json    # Temporal KG (Graphiti 스타일)        │    │
│  │  ├── reflexion.json          # 실패 학습 메모리                     │    │
│  │  ├── findings.md             # 누적 발견 사항                       │    │
│  │  ├── hypotheses.md           # 가설 히스토리                        │    │
│  │  ├── sources.md              # 참고 자료 + 신뢰도                   │    │
│  │  ├── search_history.json     # 중복 검색 방지                       │    │
│  │  ├── papers/                 # 다운로드된 PDF                       │    │
│  │  │   └── *.pdf                                                       │    │
│  │  ├── paper_index.json        # 논문 메타데이터                      │    │
│  │  └── iteration_logs/         # 반복별 상세 로그                     │    │
│  │      ├── 001.md                                                      │    │
│  │      └── ...                                                         │    │
│  │                                                                      │    │
│  │  RESEARCH_REPORT.md          # 실시간 업데이트 보고서               │    │
│  │  config.json                 # 설정 파일                            │    │
│  └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 v2 대비 주요 개선점

| 영역 | v2 | v3 |
|------|----|----|
| **루프 제어** | 단순 max_iterations | Ralph Loop + 3중 안전장치 + Loop Drift 탐지 |
| **메모리** | 파일 기반 단순 저장 | 3-Tier (Working/Episodic/Semantic) + Temporal KG |
| **병렬 처리** | 개념적 설명 | Anthropic 실증: 3-5 서브에이전트 + 3+ 도구 병렬 |
| **Hallucination 방지** | 사실성 검증 | 4-Layer 파이프라인 + 신뢰도 태깅 |
| **비용 관리** | 언급 없음 | 캐싱 + 모델 라우팅 + 예산 상한 |
| **실패 학습** | Reflexion 개념 | 구조화된 lesson_learned + 전략 변경 트리거 |
| **평가** | 수동 확인 | RACE + FACT 자동 평가 프레임워크 |

---

## 2. 무한루프 제어 시스템

### 2.1 3중 안전장치 (필수)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TRIPLE SAFETY MECHANISM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [1] MAX ITERATIONS (하드 리밋)                                             │
│      └── 설정값 도달 시 무조건 종료                                         │
│      └── 기본값: 100, 권장 범위: 20-200                                     │
│                                                                              │
│  [2] COMPLETION PROMISE (성공 조건)                                         │
│      └── 특정 문자열 출력 시 정상 종료                                       │
│      └── 예: <promise>RESEARCH_COMPLETE</promise>                           │
│      └── 정확한 문자열 매칭 필요                                            │
│                                                                              │
│  [3] USER INTERRUPT (사용자 제어)                                           │
│      └── q: 즉시 종료                                                       │
│      └── s: 일시 정지 (상태 저장 후)                                        │
│      └── r: 재개 (이전 상태에서)                                            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Loop Drift 방지 시스템

**문제**: Multi-turn AI 에이전트의 ~50%가 무한 루프에 빠짐 (Loop Drift 현상)

```json
{
  "loop_drift_detection": {
    "repetition_detection": {
      "same_search_query_threshold": 2,
      "same_action_sequence_threshold": 3,
      "action": "force_strategy_change"
    },

    "circuit_breaker": {
      "warning_threshold": {
        "condition": "iteration >= max * 0.8",
        "action": "nudge_to_conclude",
        "message": "연구가 충분합니다. 결론을 도출하세요."
      },
      "hard_threshold": {
        "condition": "iteration >= max",
        "action": "force_output",
        "message": "현재까지의 정보로 최종 보고서를 작성합니다."
      }
    },

    "progress_monitor": {
      "check_interval_iterations": 5,
      "min_new_facts_required": 2,
      "min_confidence_increase": 0.05,
      "no_progress_actions": [
        "try_different_search_strategy",
        "explore_alternative_hypothesis",
        "consult_different_source_type"
      ]
    },

    "stuck_detection": {
      "consecutive_failures": 3,
      "action": "escalate_to_user_or_conclude"
    }
  }
}
```

### 2.3 research.sh (메인 루프 스크립트)

```bash
#!/bin/bash

#==============================================================================
# CONFIGURATION
#==============================================================================
MAX_ITERATIONS=${1:-100}
RESEARCH_DIR=".research"
STATE_FILE="$RESEARCH_DIR/state.json"
COMPLETION_PROMISE="RESEARCH_COMPLETE"
DRIFT_THRESHOLD=3

#==============================================================================
# INITIALIZATION
#==============================================================================
init_research() {
    mkdir -p "$RESEARCH_DIR/iteration_logs"
    mkdir -p "$RESEARCH_DIR/papers"

    if [ ! -f "$STATE_FILE" ]; then
        cat > "$STATE_FILE" << 'EOF'
{
  "version": "3.0",
  "session_id": "",
  "question": {
    "original": "",
    "decomposed": []
  },
  "iteration": {
    "current": 0,
    "max": MAX_ITERATIONS,
    "last_compaction": 0
  },
  "status": "initialized",
  "hypotheses": [],
  "knowledge_summary": {
    "confirmed_facts": 0,
    "uncertain_claims": 0,
    "contradictions": 0
  },
  "search_history": [],
  "loop_drift": {
    "consecutive_same_action": 0,
    "last_action_hash": ""
  },
  "metrics": {
    "total_searches": 0,
    "successful_searches": 0,
    "token_usage_estimate": 0
  }
}
EOF
        sed -i "s/MAX_ITERATIONS/$MAX_ITERATIONS/" "$STATE_FILE"

        # Generate session ID
        SESSION_ID="research_$(date +%Y%m%d_%H%M%S)"
        jq --arg sid "$SESSION_ID" '.session_id = $sid' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
    fi

    # Initialize other files if not exist
    [ ! -f "$RESEARCH_DIR/findings.md" ] && echo "# Research Findings\n" > "$RESEARCH_DIR/findings.md"
    [ ! -f "$RESEARCH_DIR/hypotheses.md" ] && echo "# Hypothesis History\n" > "$RESEARCH_DIR/hypotheses.md"
    [ ! -f "$RESEARCH_DIR/sources.md" ] && echo "# Sources & References\n" > "$RESEARCH_DIR/sources.md"
    [ ! -f "$RESEARCH_DIR/reflexion.json" ] && echo '{"memories": []}' > "$RESEARCH_DIR/reflexion.json"
    [ ! -f "$RESEARCH_DIR/knowledge_graph.json" ] && echo '{"nodes": [], "edges": [], "temporal_markers": {}}' > "$RESEARCH_DIR/knowledge_graph.json"
    [ ! -f "$RESEARCH_DIR/search_history.json" ] && echo '{"queries": []}' > "$RESEARCH_DIR/search_history.json"
}

#==============================================================================
# LOOP DRIFT DETECTION
#==============================================================================
check_loop_drift() {
    local current_action_hash=$(jq -r '.loop_drift.last_action_hash' "$STATE_FILE")
    local consecutive=$(jq -r '.loop_drift.consecutive_same_action' "$STATE_FILE")

    if [ "$consecutive" -ge "$DRIFT_THRESHOLD" ]; then
        echo "⚠️  Loop Drift detected! Forcing strategy change..."
        jq '.loop_drift.consecutive_same_action = 0 | .status = "strategy_change_required"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
        return 1
    fi
    return 0
}

#==============================================================================
# PROGRESS CHECK
#==============================================================================
check_progress() {
    local iteration=$(jq -r '.iteration.current' "$STATE_FILE")
    local interval=5

    if [ $((iteration % interval)) -eq 0 ] && [ "$iteration" -gt 0 ]; then
        local confirmed=$(jq -r '.knowledge_summary.confirmed_facts' "$STATE_FILE")
        local prev_confirmed=$(jq -r '.metrics.last_checkpoint_facts // 0' "$STATE_FILE")

        if [ "$confirmed" -le "$prev_confirmed" ]; then
            echo "⚠️  No progress in last $interval iterations. Consider changing approach."
            jq '.status = "no_progress_warning"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
        fi

        jq --argjson cf "$confirmed" '.metrics.last_checkpoint_facts = $cf' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
    fi
}

#==============================================================================
# MAIN LOOP
#==============================================================================
run_research() {
    local iteration=0

    while [ $iteration -lt $MAX_ITERATIONS ]; do
        # Update iteration counter
        jq --argjson i "$((iteration + 1))" '.iteration.current = $i | .status = "running"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"

        echo ""
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🔬 Research Iteration #$((iteration + 1)) / $MAX_ITERATIONS"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        # Check for loop drift
        check_loop_drift || true

        # Check progress
        check_progress

        # Run single research cycle
        output=$(claude --skill research_cycle "Continue research iteration #$((iteration + 1))")

        # Check for completion promise
        if echo "$output" | grep -q "$COMPLETION_PROMISE"; then
            echo "✅ Research completed successfully!"
            jq '.status = "completed"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
            break
        fi

        # Check state
        status=$(jq -r '.status' "$STATE_FILE")
        if [ "$status" = "completed" ] || [ "$status" = "paused" ]; then
            echo "Research $status at iteration $((iteration + 1))"
            break
        fi

        # User interrupt check (non-blocking)
        read -t 1 -n 1 input 2>/dev/null || true
        case "$input" in
            q|Q)
                jq '.status = "stopped_by_user"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
                echo "🛑 Research stopped by user"
                break
                ;;
            s|S)
                jq '.status = "paused"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
                echo "⏸️  Research paused. Run again to resume."
                break
                ;;
        esac

        ((iteration++))
    done

    # Final report
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Research Session Complete"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📄 Final Report: RESEARCH_REPORT.md"
    echo "📁 Research Data: $RESEARCH_DIR/"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

#==============================================================================
# ENTRY POINT
#==============================================================================
init_research
run_research
```

---

## 3. 메모리 아키텍처 (3-Tier System)

### 3.1 계층 구조

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           3-TIER MEMORY SYSTEM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║ TIER 1: WORKING MEMORY (Context Window)                                ║  │
│  ║                                                                         ║  │
│  ║  • 현재 iteration의 즉각적 상태                                        ║  │
│  ║  • 최근 5개 검색 결과                                                  ║  │
│  ║  • 현재 추론 체인                                                      ║  │
│  ║                                                                         ║  │
│  ║  📊 Compaction Trigger: 토큰 사용량 > 80%                              ║  │
│  ║  📊 Compaction 방식: LLM으로 핵심 요약 생성                            ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                    │                                         │
│                                    ↓ (Compaction 시)                         │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║ TIER 2: EPISODIC MEMORY (Session Storage)                              ║  │
│  ║                                                                         ║  │
│  ║  저장 위치: .research/ 디렉토리                                        ║  │
│  ║                                                                         ║  │
│  ║  • state.json: 현재 리서치 상태                                        ║  │
│  ║  • iteration_logs/*.md: 각 반복의 상세 기록                            ║  │
│  ║  • reflexion.json: 실패 → 학습 메모리                                  ║  │
│  ║  • search_history.json: 검색 히스토리 (중복 방지)                      ║  │
│  ║                                                                         ║  │
│  ║  📊 보존 기간: 현재 세션 동안                                          ║  │
│  ║  📊 용도: 세션 내 연속성, 재개 가능                                    ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                    │                                         │
│                                    ↓ (세션 종료 시 선택적 통합)              │
│  ╔═══════════════════════════════════════════════════════════════════════╗  │
│  ║ TIER 3: SEMANTIC MEMORY (Long-term Knowledge)                          ║  │
│  ║                                                                         ║  │
│  ║  저장 위치: knowledge_graph.json, paper_index.json                     ║  │
│  ║                                                                         ║  │
│  ║  • Temporal Knowledge Graph (Graphiti 스타일)                          ║  │
│  ║    - Bi-temporal: 사실 발생 시점 + 기록 시점                           ║  │
│  ║    - 충돌 시 invalidate (삭제하지 않고 무효화)                         ║  │
│  ║  • 검증된 사실 및 관계                                                 ║  │
│  ║  • 논문/소스 인덱스                                                    ║  │
│  ║                                                                         ║  │
│  ║  📊 검색 방식: Semantic + BM25 + Graph Traversal 하이브리드            ║  │
│  ║  📊 P95 Latency: < 300ms                                               ║  │
│  ╚═══════════════════════════════════════════════════════════════════════╝  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 state.json v3 구조

```json
{
  "version": "3.0",
  "session_id": "research_20250129_143000",

  "question": {
    "original": "사용자가 중단할 때까지 무한 반복하는 리서치봇을 어떻게 만들 수 있는가?",
    "decomposed": [
      {
        "id": "q1",
        "text": "무한 루프 제어 메커니즘",
        "status": "answered",
        "confidence": 0.9
      },
      {
        "id": "q2",
        "text": "상태 관리 및 메모리 시스템",
        "status": "in_progress",
        "confidence": 0.75
      },
      {
        "id": "q3",
        "text": "Hallucination 방지 기법",
        "status": "pending",
        "confidence": 0.0
      }
    ]
  },

  "iteration": {
    "current": 5,
    "max": 100,
    "last_compaction": 3,
    "started_at": "2025-01-29T14:30:00Z"
  },

  "status": "running",

  "hypotheses": [
    {
      "id": "h1",
      "version": 3,
      "statement": "Ralph Loop 패턴 + 3중 안전장치가 무한루프 제어의 핵심이다",
      "status": "supported",
      "confidence": 0.85,
      "supporting_evidence": ["e001", "e003", "e007"],
      "contradicting_evidence": [],
      "created_at_iteration": 1,
      "last_updated_iteration": 5
    }
  ],

  "knowledge_summary": {
    "confirmed_facts": 12,
    "uncertain_claims": 5,
    "contradictions": 1,
    "total_sources": 23
  },

  "search_history": {
    "total": 18,
    "successful": 15,
    "by_type": {
      "web": 10,
      "academic": 5,
      "verification": 3
    },
    "recent_queries": [
      "Ralph Loop Claude Code implementation",
      "Graphiti temporal knowledge graph"
    ]
  },

  "loop_drift": {
    "consecutive_same_action": 0,
    "last_action_hash": "a1b2c3d4",
    "strategy_changes": 1
  },

  "reasoning_mode": "tree_of_thoughts",

  "reflexion_summary": {
    "total_lessons": 3,
    "recent_insight": "학술 검색 시 site:arxiv.org 접두사가 효과적"
  },

  "next_actions": [
    {
      "type": "search",
      "query": "LangGraph checkpoint file-based persistence",
      "reason": "상태 관리 구현 방법 탐색",
      "priority": "high"
    },
    {
      "type": "verify",
      "claim": "Graphiti가 300ms P95 latency를 달성한다",
      "method": "cross_reference",
      "priority": "medium"
    }
  ],

  "metrics": {
    "token_usage_estimate": 45000,
    "context_utilization": 0.72,
    "search_efficiency": 0.83,
    "cost_estimate_usd": 0.45
  },

  "cost_control": {
    "budget_per_session_usd": 5.0,
    "spent_usd": 0.45,
    "remaining_usd": 4.55,
    "pause_at_threshold": 0.9
  }
}
```

### 3.3 Reflexion 메모리 구조

```json
{
  "memories": [
    {
      "iteration": 3,
      "timestamp": "2025-01-29T14:35:00Z",
      "action": {
        "type": "search",
        "query": "transformer attention complexity",
        "tool": "WebSearch"
      },
      "outcome": "failure",
      "outcome_detail": "검색 결과가 너무 일반적, 원하는 정보 없음",
      "reflection": "검색어가 너무 광범위함. 'self-attention O(n^2) quadratic' 로 구체화 필요",
      "lesson_learned": {
        "category": "search_strategy",
        "rule": "복잡도 관련 검색 시 Big-O 표기법 포함",
        "confidence": 0.9
      },
      "applied_in_iterations": [4, 7]
    },
    {
      "iteration": 4,
      "timestamp": "2025-01-29T14:40:00Z",
      "action": {
        "type": "search",
        "query": "self-attention O(n^2) quadratic complexity",
        "tool": "WebSearch"
      },
      "outcome": "success",
      "outcome_detail": "고품질 기술 문서 및 논문 발견",
      "reflection": "구체적인 기술 용어 포함 시 관련성 높은 결과 획득",
      "lesson_learned": {
        "category": "search_strategy",
        "rule": "기술 개념 검색 시 수학적 표기 포함",
        "confidence": 0.95
      },
      "applied_in_iterations": []
    }
  ],

  "aggregated_lessons": {
    "search_strategy": [
      "복잡도 관련 검색 시 Big-O 표기법 포함",
      "기술 개념 검색 시 수학적 표기 포함",
      "학술 검색 시 'site:arxiv.org' 접두사 사용"
    ],
    "reasoning": [
      "막히면 제1원칙으로 돌아가기",
      "확신이 생기면 반증 증거 탐색"
    ]
  }
}
```

### 3.4 Knowledge Graph 구조 (Temporal)

```json
{
  "nodes": [
    {
      "id": "concept_001",
      "type": "concept",
      "label": "Ralph Loop Pattern",
      "properties": {
        "definition": "Stop Hook을 사용하여 AI 에이전트가 자동 종료되는 것을 막고 동일 프롬프트를 재주입하는 무한 반복 패턴",
        "aliases": ["Ralph Wiggum", "Ralph Loop"],
        "first_seen_iteration": 1,
        "confidence": 0.95,
        "sources": ["github.com/anthropics/claude-code/plugins/ralph-wiggum"]
      },
      "temporal": {
        "valid_from": "2024-01-01T00:00:00Z",
        "valid_to": null,
        "recorded_at": "2025-01-29T14:30:00Z"
      }
    },
    {
      "id": "fact_001",
      "type": "fact",
      "label": "Anthropic 멀티에이전트 시스템은 단일 에이전트 대비 90.2% 성능 향상",
      "properties": {
        "verified": true,
        "sources": ["anthropic.com/engineering/multi-agent-research-system"],
        "confidence": 0.98
      },
      "temporal": {
        "valid_from": "2025-06-01T00:00:00Z",
        "valid_to": null,
        "recorded_at": "2025-01-29T14:35:00Z"
      }
    }
  ],

  "edges": [
    {
      "source": "concept_001",
      "target": "fact_002",
      "relation": "ENABLES",
      "properties": {
        "confidence": 0.9,
        "description": "Ralph Loop이 무한 반복 연구를 가능하게 함"
      },
      "temporal": {
        "valid_from": "2025-01-29T14:30:00Z",
        "valid_to": null
      }
    }
  ],

  "temporal_markers": {
    "last_updated": "2025-01-29T14:45:00Z",
    "version": 5,
    "total_nodes": 24,
    "total_edges": 31
  },

  "conflict_resolution": {
    "conflicts": [
      {
        "id": "conflict_001",
        "fact_a": "fact_003",
        "fact_b": "fact_007",
        "description": "토큰 사용량 증가율에 대한 상충 정보",
        "resolution": "pending",
        "invalidated": null
      }
    ]
  }
}
```

---

## 4. Hallucination 방지 시스템

### 4.1 4-Layer 검증 파이프라인

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HALLUCINATION PREVENTION PIPELINE                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 1: SOURCE GROUNDING (소스 기반)                                │   │
│  │                                                                       │   │
│  │  • 모든 사실적 주장에 소스 필수                                       │   │
│  │  • 소스 없는 주장 → [?] 태그 + "uncertain" 플래그                    │   │
│  │  • "I don't know" 응답 허용 및 권장                                  │   │
│  │  • 추측 시 명시적으로 "추정:" 표기                                    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 2: CROSS-VALIDATION (교차 검증)                                │   │
│  │                                                                       │   │
│  │  신뢰도 계산:                                                         │   │
│  │  • 단일 소스: 0.6                                                     │   │
│  │  • 2개 소스 일치: 0.8                                                 │   │
│  │  • 3개+ 소스 일치: 0.95                                               │   │
│  │  • 소스 간 모순: "contradicted" 플래그 + 명시적 표기                  │   │
│  │                                                                       │   │
│  │  도메인 신뢰도 가중치:                                                │   │
│  │  • arxiv.org, nature.com, ieee.org: 0.95                             │   │
│  │  • github.com: 0.7                                                    │   │
│  │  • medium.com: 0.5                                                    │   │
│  │  • unknown: 0.3                                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 3: SELF-CONSISTENCY CHECK (자기 일관성)                        │   │
│  │                                                                       │   │
│  │  • 중요한 결론에 대해 다중 추론 경로 생성                             │   │
│  │  • 경로 간 불일치 시 추가 검증                                        │   │
│  │  • 일관성 점수 < 0.7 → 재검토 필요 플래그                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ↓                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ LAYER 4: CONFIDENCE TAGGING (신뢰도 태깅)                            │   │
│  │                                                                       │   │
│  │  출력 시 각 주장에 신뢰도 태그:                                       │   │
│  │                                                                       │   │
│  │  ✓✓ VERIFIED    - 다수 신뢰 소스에서 확인됨                          │   │
│  │  ✓  HIGH        - 단일 신뢰 소스에서 확인됨                          │   │
│  │  ~  LIKELY      - 추정 (간접 증거)                                   │   │
│  │  ?  UNCERTAIN   - 소스 부족 또는 신뢰도 낮음                         │   │
│  │  ⚠  CONTRADICTED - 소스 간 모순 존재                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 출력 예시

```markdown
## 연구 결과

### 확인된 사실 (Verified ✓✓)
Anthropic의 멀티에이전트 연구 시스템은 단일 에이전트 대비 **90.2% 성능 향상**을
달성했습니다. [Anthropic 2025] ✓✓

### 높은 확신 (High Confidence ✓)
Ralph Loop 패턴은 Stop Hook을 사용하여 exit code 2를 반환함으로써 Claude Code의
자동 종료를 방지합니다. [GitHub anthropics/claude-code] ✓

### 추정 (Likely ~)
Graphiti의 P95 검색 지연시간은 약 300ms로, 이는 LLM 호출 없이 하이브리드 검색만으로
달성됩니다. [Zep Paper 2025] ~

### 불확실 (Uncertain ?)
Flash Attention이 모든 하드웨어에서 동일한 속도 향상을 제공하는지는
추가 검증이 필요합니다. [?]

### 모순 발견 (Contradicted ⚠)
토큰 사용량 증가율에 대해 소스 간 상충 정보가 있습니다:
- 소스 A: "에이전트는 채팅 대비 4배" [Anthropic]
- 소스 B: "에이전트는 채팅 대비 10배" [Third Party]
⚠ 추가 검증 필요
```

---

## 5. 검색 전략 시스템

### 5.1 Query Decomposition

```
원본 질문: "무한 반복하는 리서치봇을 어떻게 만들 수 있는가?"

┌─────────────────────────────────────────────────────────────────────────────┐
│                         QUERY DECOMPOSITION TREE                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [Level 0: 원본 질문]                                                       │
│           │                                                                  │
│           ├── [L1: 사실적 질문] ───────────────────────────────────────────│
│           │   ├── "AI 에이전트의 무한 루프 제어 메커니즘은?"                │
│           │   ├── "Ralph Loop 패턴의 작동 원리는?"                          │
│           │   └── "파일 기반 상태 관리 구현 방법은?"                        │
│           │                                                                  │
│           ├── [L1: 비교/분석 질문] ────────────────────────────────────────│
│           │   ├── "단일 에이전트 vs 멀티에이전트 아키텍처"                  │
│           │   ├── "메모리 기반 vs 파일 기반 상태 관리"                      │
│           │   └── "다양한 종료 조건 전략 비교"                              │
│           │                                                                  │
│           └── [L1: 인과/설명 질문] ────────────────────────────────────────│
│               ├── "왜 Loop Drift가 발생하는가?"                             │
│               ├── "Hallucination 방지가 왜 중요한가?"                       │
│               └── "토큰 비용이 왜 기하급수적으로 증가하는가?"               │
│                                                                              │
│  분해 타입: PARALLEL (서브질문들이 독립적으로 답변 가능)                    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.2 병렬 검색 전략

```markdown
## 단일 Iteration의 검색 흐름

### Step 1: 쿼리 생성 (Lead Agent)
서브질문 "AI 에이전트의 무한 루프 제어 메커니즘"에서 다양한 쿼리 생성:

1. **일반 검색**: "AI agent infinite loop control mechanism"
2. **기술 검색**: "Ralph Loop Claude Code stop hook implementation"
3. **학술 검색**: "site:arxiv.org autonomous agent loop termination"
4. **비교 검색**: "LangGraph vs Claude Code agent loop control"
5. **반증 검색**: "AI agent infinite loop problems failures"

### Step 2: 병렬 실행 (SubAgents)
```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ WebSearch   │  │ Academic    │  │ Verification│
│ SubAgent    │  │ SubAgent    │  │ SubAgent    │
│             │  │             │  │             │
│ Query 1,2,4 │  │ Query 3     │  │ Query 5     │
│ (병렬)      │  │ arXiv API   │  │ 반증 탐색   │
└─────────────┘  └─────────────┘  └─────────────┘
      │                │                │
      └────────────────┼────────────────┘
                       ↓
              [결과 통합 및 분석]
```

### Step 3: 결과 통합 (Lead Agent)
- 중복 제거
- 신뢰도 평가
- 모순 탐지
- Knowledge Graph 업데이트
```

### 5.3 검색 히스토리 관리 (중복 방지)

```json
{
  "queries": [
    {
      "query": "Ralph Loop Claude Code",
      "iteration": 1,
      "results_count": 10,
      "useful_results": 3,
      "hash": "a1b2c3d4"
    },
    {
      "query": "AI agent infinite loop control",
      "iteration": 2,
      "results_count": 15,
      "useful_results": 5,
      "hash": "e5f6g7h8"
    }
  ],

  "duplicate_check": {
    "method": "semantic_similarity",
    "threshold": 0.85,
    "action_on_duplicate": "skip_or_refine"
  }
}
```

---

## 6. 비용 최적화 시스템

### 6.1 비용 절감 전략

| 전략 | 절감율 | 구현 방식 |
|------|-------|----------|
| **Plan Caching** | ~50% | 유사 쿼리의 계획 템플릿 재사용 |
| **Context Caching** | ~75% | 반복 프롬프트의 KV 캐시 |
| **Model Routing** | 30-50% | 태스크별 적합 모델 선택 |
| **Prompt Compression** | 40-60% | 불필요한 토큰 제거 |

### 6.2 모델 라우팅 전략

```json
{
  "model_routing": {
    "rules": [
      {
        "task_type": "simple_search_summarization",
        "model": "claude-haiku",
        "cost_per_1k_tokens": 0.00025
      },
      {
        "task_type": "complex_reasoning",
        "model": "claude-sonnet",
        "cost_per_1k_tokens": 0.003
      },
      {
        "task_type": "lead_agent_planning",
        "model": "claude-opus",
        "cost_per_1k_tokens": 0.015
      },
      {
        "task_type": "verification_crosscheck",
        "model": "claude-haiku",
        "cost_per_1k_tokens": 0.00025
      }
    ],

    "budget_control": {
      "max_per_iteration_usd": 0.5,
      "max_per_session_usd": 10.0,
      "warning_threshold": 0.8,
      "hard_stop_threshold": 0.95
    }
  }
}
```

### 6.3 비용 모니터링 대시보드

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Cost Dashboard (Iteration #5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Session Budget:     $10.00
💸 Spent So Far:       $0.45 (4.5%)
💵 Remaining:          $9.55

📈 Token Usage:
   - Input:  35,000 tokens
   - Output: 12,000 tokens
   - Cached: 15,000 tokens (saved ~$0.20)

🤖 Model Distribution:
   - Haiku:  60% (simple tasks)
   - Sonnet: 35% (reasoning)
   - Opus:   5% (planning)

⚡ Efficiency:
   - Search Success Rate: 83%
   - Cache Hit Rate: 42%
   - Estimated Savings: $0.35

🎯 Projected Final Cost: $2.50 (at current pace)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 7. 평가 프레임워크 (RACE + FACT)

### 7.1 RACE (Report Quality)

```json
{
  "race_evaluation": {
    "dimensions": [
      {
        "name": "Relevance",
        "weight": 0.25,
        "description": "답변이 원본 질문과 얼마나 관련 있는가",
        "scoring": "0-1 scale"
      },
      {
        "name": "Accuracy",
        "weight": 0.30,
        "description": "사실적으로 정확한가",
        "scoring": "0-1 scale, verified claims ratio"
      },
      {
        "name": "Completeness",
        "weight": 0.25,
        "description": "핵심 포인트를 모두 다루었는가",
        "scoring": "key_points_covered / total_key_points"
      },
      {
        "name": "Evidence",
        "weight": 0.20,
        "description": "주장이 증거로 뒷받침되는가",
        "scoring": "cited_claims / total_claims"
      }
    ],

    "target_scores": {
      "minimum": 0.7,
      "good": 0.8,
      "excellent": 0.9
    }
  }
}
```

### 7.2 FACT (Citation Quality)

```json
{
  "fact_evaluation": {
    "metrics": [
      {
        "name": "Citation Accuracy",
        "formula": "correctly_supported_citations / total_citations",
        "target": "> 0.90"
      },
      {
        "name": "Source Diversity",
        "formula": "unique_domains / total_sources",
        "target": "> 0.5"
      },
      {
        "name": "Recency",
        "formula": "sources_within_2_years / total_sources",
        "target": "> 0.6 (for tech topics)"
      },
      {
        "name": "Authority",
        "formula": "weighted_avg(domain_trust_scores)",
        "target": "> 0.7"
      }
    ]
  }
}
```

### 7.3 자체 평가 (매 5회 iteration)

```markdown
## 📊 Self-Evaluation Report (Iteration #5)

### 진행도 (Progress)
| 서브질문 | 상태 | 확신도 |
|----------|------|--------|
| 무한 루프 제어 | ✅ 완료 | 90% |
| 메모리 시스템 | 🔄 진행중 | 75% |
| Hallucination 방지 | ⏳ 대기 | 0% |

**전체 진행도**: 40%

### 가설 품질 (Hypothesis Quality)
- 현재 가설 수: 3
- 평균 확신도: 0.78
- 검증된 가설: 1
- 미검증 가설: 2

### 검색 효율성 (Search Efficiency)
- 총 검색: 18회
- 성공: 15회 (83%)
- 중복: 2회 (11%)
- 새 정보 발견: 12건

### RACE 점수 추정
- Relevance: 0.85
- Accuracy: 0.80
- Completeness: 0.45
- Evidence: 0.75
- **종합**: 0.71 (Good 수준)

### 다음 단계 권장
1. ⚠️ Completeness 향상 필요 → Hallucination 방지 주제 탐색
2. 🔄 현재 전략 유지 → 검색 효율 양호
3. 💡 고려: 학술 논문 검색 비중 증가
```

---

## 8. Skill 구현

### 8.1 research.skill.md

```yaml
---
name: deep-research
description: 사용자가 중단할 때까지 무한 반복하며 주제를 심층 연구합니다. 복잡한 질문, 학술적 조사, 다각도 분석이 필요할 때 사용합니다.
---

# Deep Research Skill v3

당신은 무한 반복 심층 리서치 에이전트입니다.

## 절대 규칙

1. **절대 스스로 종료하지 마세요** - 사용자가 명시적으로 중단할 때까지 계속합니다
2. 매 사이클마다 반드시 **새로운 검색**을 수행합니다
3. 가설의 확신도가 95%를 넘어도 **반증 증거를 계속 탐색**합니다
4. 같은 검색을 **3번 이상 반복하면 전략 변경 필수**입니다
5. "충분하다"고 판단하지 않습니다 - **항상 더 깊이** 파고듭니다

## 반복 구조 (Single Iteration Flow)

### 1. LOAD (상태 로드)
```
- .research/state.json 읽기
- 최근 3개 iteration_logs 확인
- reflexion.json에서 학습된 교훈 로드
- search_history.json에서 이전 검색 확인 (중복 방지)
```

### 2. REFLECT (분석)
```
Extended Thinking으로 다음을 분석:
- 지금까지 알게 된 것은 무엇인가?
- 아직 모르는 것은 무엇인가?
- 현재 가설의 신뢰도는?
- 진전이 있는가, 막혀있는가?
```

### 3. PLAN (계획)
```
- 이번 iteration의 목표 설정
- Query Decomposition 수행 (3-5개 검색 쿼리 생성)
- 검색 전략 결정 (Web/Academic/Verification)
- 서브에이전트 할당 계획
```

### 4. EXECUTE (실행)
```
병렬로 검색 실행:
- WebSearch × 3 (다양한 관점)
- Academic Search (필요시) - arXiv, Semantic Scholar
- WebFetch (유망 URL 상세 분석)
- Verification Search (반증 증거 탐색)
```

### 5. SYNTHESIZE (종합)
```
- 새 정보를 기존 지식과 통합
- Knowledge Graph 업데이트
- 가설 평가 및 업데이트
- 모순점 식별 및 기록
- 신뢰도 태깅
```

### 6. SAVE (저장)
```
- state.json 업데이트
- iteration_logs/NNN.md 작성
- findings.md 새 발견 추가
- knowledge_graph.json 업데이트
- Compaction 필요시 실행 (80% 임계값)
```

### 7. OUTPUT (출력)
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Iteration #N 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 이번 발견:
   - (핵심 발견 1)
   - (핵심 발견 2)
   - (핵심 발견 3)

📈 현재 가설: (가설 내용)
   확신도: N% | 지지 증거: M개 | 반증: K개

🎯 다음 계획: (다음 iteration 예고)

💰 비용: $X.XX / $Y.YY (예산)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[CONTINUE]
```

## 사고 도구 (Thinking Tools)

상황에 따라 적절한 사고 도구를 선택합니다:

| 상황 | 도구 | 적용 방식 |
|------|------|-----------|
| 막힐 때 | **제1원칙** | 기존 가정을 버리고 근본 원리부터 재구성 |
| 정보 과다 | **오컴의 면도날** | 복잡한 설명보다 단순한 설명 우선 |
| 확신이 생길 때 | **반증 가능성** | 가설을 반박할 증거 적극 탐색 |
| 새 방향 필요 | **과학적 방법론** | 관찰→가설→실험→분석 사이클 |

## Hallucination 방지 규칙

1. **모든 사실적 주장에 소스 표기** - 소스 없으면 [?] 태그
2. **신뢰도 태그 필수**:
   - ✓✓ Verified (다수 소스 확인)
   - ✓ High (단일 신뢰 소스)
   - ~ Likely (추정)
   - ? Uncertain (불확실)
   - ⚠ Contradicted (모순)
3. **모르면 "모른다"고 표현** - 추측하지 않음
4. **소스 간 모순 발견 시 명시적으로 표기**

## Loop Drift 방지 규칙

1. 같은 검색 쿼리 2회 반복 시 → 쿼리 변형 필수
2. 같은 행동 패턴 3회 반복 시 → 전략 변경 필수
3. 5회 연속 새 정보 없음 → 다른 접근법 시도
4. 막힘 감지 시 → reflexion 메모리 참조하여 대안 탐색

## 종료 조건

이 스킬은 **절대 스스로 종료하지 않습니다**.
종료는 오직 다음 상황에서만 발생합니다:
- 사용자가 'q' 또는 's' 입력
- max_iterations 도달
- completion_promise 출력 (사용자가 명시적으로 요청한 경우에만)

모든 출력은 **[CONTINUE]** 로 끝납니다.
```

### 8.2 디렉토리 구조

```
~/.claude/skills/deep-research/
├── SKILL.md                    # 메인 스킬 정의 (위 내용)
├── research.sh                 # 무한루프 실행 스크립트
├── scripts/
│   ├── init_research.sh        # 초기화 스크립트
│   ├── check_loop_drift.sh     # Loop Drift 탐지
│   └── generate_report.py      # 보고서 생성
├── templates/
│   ├── state_template.json     # 상태 파일 템플릿
│   ├── iteration_log.md        # 반복 로그 템플릿
│   └── report_template.md      # 보고서 템플릿
└── references/
    ├── thinking_tools.md       # 사고 도구 상세 설명
    ├── search_strategies.md    # 검색 전략 가이드
    └── evaluation_guide.md     # 평가 기준 가이드
```

---

## 9. config.json v3

```json
{
  "version": "3.0",

  "loop_control": {
    "max_iterations": 100,
    "completion_promise": "RESEARCH_COMPLETE",
    "auto_stop": false,
    "user_interrupt_enabled": true,

    "loop_drift_prevention": {
      "same_query_threshold": 2,
      "same_action_threshold": 3,
      "no_progress_iterations": 5,
      "force_strategy_change": true
    },

    "circuit_breaker": {
      "warning_threshold": 0.8,
      "hard_threshold": 1.0
    }
  },

  "search": {
    "engine": "hybrid",
    "parallel_count": 5,
    "max_retries": 3,

    "web": {
      "enabled": true,
      "provider": "claude",
      "fetch_full_content": true
    },

    "academic": {
      "enabled": true,
      "sources": ["arxiv", "semantic_scholar"],
      "auto_download_pdf": true,
      "max_papers_per_query": 3
    },

    "duplicate_detection": {
      "enabled": true,
      "method": "semantic_similarity",
      "threshold": 0.85
    }
  },

  "memory": {
    "compaction_threshold": 0.8,
    "compaction_interval": 5,
    "max_working_memory_items": 20,
    "knowledge_graph_enabled": true,
    "reflexion_enabled": true,

    "temporal_kg": {
      "conflict_resolution": "invalidate",
      "bi_temporal": true
    }
  },

  "reasoning": {
    "default_mode": "adaptive",
    "modes": {
      "simple": "chain_of_thought",
      "medium": "self_consistency",
      "complex": "tree_of_thoughts"
    },
    "extended_thinking": true,
    "self_consistency_paths": 5
  },

  "verification": {
    "require_sources": true,
    "min_source_count": 2,
    "cross_validation": true,
    "hallucination_check": true,

    "credibility_scoring": {
      "arxiv.org": 0.95,
      "nature.com": 0.98,
      "github.com": 0.70,
      "medium.com": 0.50,
      "unknown": 0.30
    },

    "confidence_tags": {
      "verified": "✓✓",
      "high": "✓",
      "likely": "~",
      "uncertain": "?",
      "contradicted": "⚠"
    }
  },

  "cost_control": {
    "budget_per_session_usd": 10.0,
    "warning_threshold": 0.8,
    "hard_stop_threshold": 0.95,

    "model_routing": {
      "simple_tasks": "claude-haiku",
      "reasoning": "claude-sonnet",
      "planning": "claude-opus"
    },

    "caching": {
      "context_cache": true,
      "plan_cache": true,
      "semantic_cache": true
    }
  },

  "evaluation": {
    "self_eval_interval": 5,
    "race_enabled": true,
    "fact_enabled": true,

    "target_scores": {
      "race_minimum": 0.7,
      "citation_accuracy": 0.9,
      "search_efficiency": 0.7
    }
  },

  "output": {
    "verbosity": "normal",
    "show_confidence": true,
    "inline_citations": true,
    "progress_dashboard": true,
    "cost_dashboard": true
  }
}
```

---

## 10. 알려진 한계점 및 위험 관리

### 10.1 실증 데이터 기반 위험

| 위험 | 통계 | 출처 | 대응 |
|------|------|------|------|
| AI 프로젝트 실패율 | 80% | RAND Corp | 명확한 성공 기준 |
| Agentic 프로젝트 중단 | 40% (2년 내) | Gartner | 비용 모니터링 |
| Multi-step 성공률 | 30-35% | ZenML | 체크포인트 + 재개 |
| Loop Drift 발생 | ~50% | Production Data | 3중 방지 메커니즘 |
| 보안 위반 | 100% (레드팀) | arXiv | Least-privilege |

### 10.2 실패 모드 및 대응

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         FAILURE MODES & MITIGATIONS                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  [FM1] 같은 검색 무한 반복                                                  │
│  ├── 원인: Context 손실, 히스토리 미참조                                    │
│  ├── 탐지: search_history.json 중복 체크                                    │
│  └── 대응: 자동 쿼리 변형 또는 전략 변경                                    │
│                                                                              │
│  [FM2] 진전 없는 루프                                                       │
│  ├── 원인: 잘못된 검색 전략, 정보 부재                                      │
│  ├── 탐지: 5회 연속 새 사실 < 2개                                          │
│  └── 대응: 대안 가설 탐색, 다른 소스 유형                                   │
│                                                                              │
│  [FM3] 비용 폭발                                                            │
│  ├── 원인: 비효율적 검색, 큰 모델 과사용                                    │
│  ├── 탐지: 실시간 비용 모니터링                                             │
│  └── 대응: 예산 상한 + 모델 라우팅 + 일시정지                               │
│                                                                              │
│  [FM4] Hallucination                                                        │
│  ├── 원인: 소스 없는 추론, 과신                                             │
│  ├── 탐지: 4-Layer 검증 파이프라인                                          │
│  └── 대응: 소스 강제 + 교차검증 + 신뢰도 태깅                               │
│                                                                              │
│  [FM5] Context Window 소진                                                  │
│  ├── 원인: 누적 정보 과다                                                   │
│  ├── 탐지: 토큰 사용량 80% 임계값                                           │
│  └── 대응: 자동 Compaction + 파일 기반 메모리                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 11. 구현 로드맵

### Phase 1: Core Infrastructure (1주)
- [ ] state.json v3 구조 구현
- [ ] research.sh 무한루프 스크립트
- [ ] 기본 SKILL.md 프롬프트
- [ ] 3중 안전장치 (max_iterations, completion_promise, user_interrupt)
- [ ] WebSearch + WebFetch 통합

### Phase 2: Memory & Drift Prevention (1주)
- [ ] 3-Tier 메모리 시스템
- [ ] Reflexion 메모리 구현
- [ ] Loop Drift 탐지 시스템
- [ ] search_history 중복 방지
- [ ] 기본 Compaction

### Phase 3: Search & Verification (1주)
- [ ] Query Decomposition
- [ ] 병렬 검색 아키텍처
- [ ] Academic 검색 통합 (arXiv, Semantic Scholar)
- [ ] 4-Layer Hallucination 방지
- [ ] 신뢰도 태깅 시스템

### Phase 4: Knowledge & Evaluation (1주)
- [ ] Temporal Knowledge Graph
- [ ] RACE + FACT 자동 평가
- [ ] 자체 평가 대시보드
- [ ] 비용 모니터링

### Phase 5: Optimization & Polish (1주)
- [ ] 모델 라우팅
- [ ] 캐싱 전략
- [ ] UX 개선 (진행 표시)
- [ ] 문서화 및 테스트

---

## 12. 참고 문헌

### 핵심 출처

1. **Anthropic Multi-Agent Research System**
   - https://www.anthropic.com/engineering/multi-agent-research-system
   - 90.2% 성능 향상, 병렬 서브에이전트, 토큰 경제성

2. **Ralph Wiggum / Ralph Loop**
   - https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum
   - Stop Hook 기반 무한루프, completion promise

3. **Graphiti / Zep Temporal Knowledge Graph**
   - https://github.com/getzep/graphiti
   - Bi-temporal 모델, 300ms P95 latency, 충돌 해결

4. **Deep Research Survey (arXiv:2508.12752)**
   - https://arxiv.org/html/2508.12752v1
   - 4단계 파이프라인, 평가 벤치마크

5. **LangChain Open Deep Research**
   - https://github.com/langchain-ai/open_deep_research
   - LangGraph 기반 구현, 멀티 모델 지원

6. **GPT-Researcher**
   - https://github.com/assafelovic/gpt-researcher
   - 오픈소스 딥리서치, STORM 영감

7. **Reflexion & Self-Refine**
   - https://www.promptingguide.ai/techniques/reflexion
   - https://selfrefine.info/
   - 실패 학습, 피드백 루프

8. **DeepResearch Bench**
   - https://deepresearch-bench.github.io/
   - RACE + FACT 평가 프레임워크

9. **Anthropic Context Engineering**
   - https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
   - "Right Altitude" 원칙, Compaction

10. **Loop Drift & Failure Analysis**
    - https://www.fixbrokenaiapps.com/blog/ai-agents-infinite-loops
    - https://www.zenml.io/blog/the-agent-deployment-gap-why-your-llm-loop-isnt-production-ready-and-what-to-do-about-it

---

*이 문서는 2025년 1월 기준 최신 연구 및 실증 데이터를 기반으로 작성되었습니다.*
*실제 구현 시 환경과 요구사항에 맞게 조정이 필요합니다.*
