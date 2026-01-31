# 데이터 스키마

**문서:** 07-data-schemas.md
**최종 수정일:** 2026-02-01
**수정자:** Claude Sonnet 4.5
**관련 파일:** `.research/*.json`, `.research/*.md`, `.research/archival/*.json`

---

## 목차
- [스키마 개요](#스키마-개요)
- [Memory Blocks Architecture](#memory-blocks-architecture)
- [state.json](#statejson)
- [working_memory.json](#working_memoryjson)
- [search_history.json](#search_historyjson)
- [reflexion.json](#reflexionjson)
- [knowledge_graph.json](#knowledge_graphjson)
- [마크다운 파일](#마크다운-파일)

---

## 스키마 개요

### 파일 목록

| 파일 | 형식 | 용도 | 생성 시점 | Memory Tier |
|------|------|------|----------|-------------|
| `state.json` | JSON | 전체 연구 상태 | 첫 실행 | - |
| `working_memory.json` | JSON | 최근 10 iterations (HOT) | 첫 실행 | **Working** |
| `findings.md` | Markdown | 핵심 발견 (truncated) | 첫 실행 | **Semantic** |
| `archival/iteration_NNN.json` | JSON | 전체 iteration 로그 | 매 iteration | **Archival** |
| `search_history.json` | JSON | 검색 중복 방지 | 첫 실행 | - |
| `reflexion.json` | JSON | 실패 학습 메모리 | 첫 실행 | - |
| `knowledge_graph.json` | JSON | 지식 그래프 | 첫 실행 | - |
| `hypotheses.md` | Markdown | 가설 히스토리 | 첫 실행 | Semantic |
| `sources.md` | Markdown | 참고 자료 목록 | 첫 실행 | Semantic |

---

## Memory Blocks Architecture

**기반:** Letta Memory Blocks + JetBrains Observation Masking 연구

### 3-Tier 구조

```
┌─────────────────────────────────────────────────────┐
│ Working Memory (HOT)                                 │
│ - working_memory.json                                │
│ - 최근 10 iterations만 유지                          │
│ - Observation masking 적용 (67% context 절감)       │
│ - 컨텍스트에 항상 로드됨                             │
└─────────────────────────────────────────────────────┘
           ↓ (10개 초과 시 자동 이동)
┌─────────────────────────────────────────────────────┐
│ Semantic Memory (STRUCTURED)                        │
│ - findings.md (핵심 발견만 30개)                     │
│ - hypotheses.md (가설 목록)                         │
│ - sources.md (참고 자료)                            │
│ - Truncated context로 로드                          │
└─────────────────────────────────────────────────────┘
           ↓ (필요 시만 접근)
┌─────────────────────────────────────────────────────┐
│ Archival Memory (COLD)                              │
│ - archival/iteration_001.json                       │
│ - archival/iteration_002.json                       │
│ - ...                                               │
│ - 전체 iteration 상세 로그                          │
│ - 필요 시 검색/복원 가능                             │
└─────────────────────────────────────────────────────┘
```

### 효과

| 지표 | 개선 효과 |
|------|----------|
| **컨텍스트 크기** | 67% 감소 (JetBrains Research) |
| **Cost Saving** | Summarization과 동등 |
| **Problem-solving** | 유지 (변동 없음) |
| **메모리 계층화** | 3-tier 구조로 효율화 |

---

## working_memory.json

### 스키마

**파일:** `.research/working_memory.json`

**용도:** 최근 10 iterations만 유지하는 HOT memory (Observation masking)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["version", "window_size", "iterations"],
  "properties": {
    "version": {
      "type": "string",
      "const": "1.0"
    },
    "window_size": {
      "type": "integer",
      "const": 10,
      "description": "Observation window (JetBrains Research recommendation)"
    },
    "iterations": {
      "type": "array",
      "maxItems": 10,
      "description": "최근 10개 iteration만 유지, 오래된 것은 archival로 이동",
      "items": {
        "type": "object",
        "required": ["iteration", "timestamp", "findings", "queries"],
        "properties": {
          "iteration": {
            "type": "integer",
            "minimum": 0
          },
          "timestamp": {
            "type": "string",
            "format": "date-time"
          },
          "findings": {
            "type": "array",
            "description": "이번 iteration의 발견 사항",
            "items": {
              "type": "object",
              "properties": {
                "text": {"type": "string"},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "source": {"type": "string"}
              }
            }
          },
          "queries": {
            "type": "array",
            "description": "실행된 검색 쿼리",
            "items": {"type": "string"}
          },
          "active_hypotheses": {
            "type": "array",
            "description": "이 iteration의 active hypotheses (Top 5)",
            "items": {"type": "string"},
            "maxItems": 5
          },
          "next_actions": {
            "type": "array",
            "description": "다음 iteration 계획",
            "items": {"type": "string"}
          }
        }
      }
    },
    "last_updated": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

### 예시 데이터

```json
{
  "version": "1.0",
  "window_size": 10,
  "iterations": [
    {
      "iteration": 5,
      "timestamp": "2026-02-01T14:15:00Z",
      "findings": [
        {
          "text": "LangGraph가 144 tokens/7초로 최고 효율",
          "confidence": 0.95,
          "source": "aimultiple.com"
        },
        {
          "text": "ReAct는 30% 성공률로 구식",
          "confidence": 0.95,
          "source": "arxiv.org/2405.13966"
        }
      ],
      "queries": [
        "LangGraph performance benchmarks",
        "ReAct prompting success rate 2025"
      ],
      "active_hypotheses": ["hyp_001", "hyp_003", "hyp_005"],
      "next_actions": [
        "LangGraph migration 비용 조사",
        "Native function calling 구현 사례 검색"
      ]
    },
    {
      "iteration": 6,
      "timestamp": "2026-02-01T14:18:32Z",
      "findings": [
        {
          "text": "Observation masking (10 turns) 최적",
          "confidence": 0.95,
          "source": "blog.jetbrains.com/research"
        }
      ],
      "queries": [
        "site:arxiv.org context management LLM agents",
        "observation masking vs summarization"
      ],
      "active_hypotheses": ["hyp_001", "hyp_003", "hyp_002"],
      "next_actions": [
        "Memory Blocks 구조 조사",
        "HybridRAG 성능 검증"
      ]
    }
  ],
  "last_updated": "2026-02-01T14:18:32Z"
}
```

### Observation Masking 동작

```python
# memory_manager.py 자동 처리
mm = MemoryManager()

# Iteration 추가
mm.update_working_memory(
    iteration=11,
    findings=[...],
    queries=[...],
    active_hypotheses=[...],
    next_actions=[...]
)

# 동작:
# 1. working_memory.json에 iteration 11 추가
# 2. 총 11개가 되어 window_size (10) 초과
# 3. 가장 오래된 iteration (1)을 .research/archival/iteration_001.json로 이동
# 4. working_memory.json에는 iterations 2-11만 유지 (10개)
```

**효과:**
- 컨텍스트 크기: 67% 감소
- Cost saving + problem-solving ability 유지
- 필요 시 archival에서 과거 데이터 복원 가능

---

## state.json

### 스키마

**파일:** `.research/state.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["status", "question", "iteration", "active_hypotheses", "all_hypotheses", "metrics"],
  "properties": {
    "status": {
      "type": "string",
      "enum": [
        "initialized",
        "running",
        "paused",
        "completed",
        "stopped_by_user",
        "budget_exceeded"
      ],
      "description": "현재 연구 상태"
    },
    "question": {
      "type": "object",
      "required": ["original", "sub_questions"],
      "properties": {
        "original": {
          "type": "string",
          "description": "원본 연구 질문"
        },
        "sub_questions": {
          "type": "array",
          "items": {"type": "string"},
          "description": "분해된 서브 질문들"
        },
        "answered_count": {
          "type": "integer",
          "description": "답변된 서브 질문 수"
        }
      }
    },
    "iteration": {
      "type": "object",
      "required": ["current", "max"],
      "properties": {
        "current": {
          "type": "integer",
          "minimum": 0,
          "description": "현재 iteration 번호"
        },
        "max": {
          "type": "integer",
          "minimum": 1,
          "description": "최대 iteration 수"
        }
      }
    },
    "active_hypotheses": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Priority Score 상위 5개 가설 ID 배열",
      "maxItems": 5
    },
    "all_hypotheses": {
      "type": "array",
      "items": {
        "$ref": "#/definitions/hypothesis"
      },
      "description": "전체 가설 목록 (active + inactive)"
    },
    "next_actions": {
      "type": "array",
      "items": {"type": "string"},
      "description": "다음 iteration에서 수행할 작업"
    },
    "metrics": {
      "type": "object",
      "properties": {
        "cost_estimate_usd": {
          "type": "number",
          "minimum": 0,
          "description": "예상 비용 (USD)"
        },
        "queries_executed": {
          "type": "integer",
          "minimum": 0
        },
        "sources_found": {
          "type": "integer",
          "minimum": 0
        },
        "verified_facts": {
          "type": "integer",
          "minimum": 0
        }
      }
    },
    "created_at": {
      "type": "string",
      "format": "date-time"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time"
    }
  },
  "definitions": {
    "hypothesis": {
      "type": "object",
      "required": ["id", "statement", "confidence"],
      "properties": {
        "id": {
          "type": "string",
          "pattern": "^hyp_[0-9]{3}$"
        },
        "statement": {
          "type": "string",
          "description": "가설 내용"
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "확신도 (0-1)"
        },
        "priority_score": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "우선순위 점수 (Confidence 50% + Evidence Density 30% + Recency 20%)"
        },
        "supporting_evidence": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "source": {"type": "string"},
              "summary": {"type": "string"}
            }
          }
        },
        "contradicting_evidence": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "source": {"type": "string"},
              "summary": {"type": "string"}
            }
          }
        },
        "last_updated_iteration": {
          "type": "integer",
          "minimum": 0
        }
      }
    }
  }
}
```

---

### 예시 데이터

```json
{
  "status": "running",
  "question": {
    "original": "양자 컴퓨팅의 최신 동향은?",
    "sub_questions": [
      "양자 컴퓨터의 현재 기술 수준은?",
      "주요 응용 분야는?",
      "상용화 전망은?",
      "기술적 한계는?",
      "경쟁 업체들은?"
    ],
    "answered_count": 3
  },
  "iteration": {
    "current": 5,
    "max": 100
  },
  "active_hypotheses": ["hyp_001", "hyp_003", "hyp_005", "hyp_002", "hyp_007"],
  "all_hypotheses": [
    {
      "id": "hyp_001",
      "statement": "양자 컴퓨터는 암호화 알고리즘을 위협할 것이다",
      "confidence": 0.85,
      "priority_score": 0.78,
      "supporting_evidence": [
        {
          "source": "nature.com",
          "summary": "Shor's algorithm으로 RSA 해독 가능 증명"
        },
        {
          "source": "ieee.org",
          "summary": "실험적으로 RSA 취약성 확인"
        }
      ],
      "contradicting_evidence": [
        {
          "source": "arxiv.org",
          "summary": "실용화까지 10년 이상 소요 예상"
        }
      ],
      "last_updated_iteration": 5
    }
  ],
  "next_actions": [
    "양자 내성 암호화(Post-Quantum Cryptography) 조사",
    "주요 기업의 양자 컴퓨터 개발 현황 확인"
  ],
  "metrics": {
    "cost_estimate_usd": 0.45,
    "queries_executed": 15,
    "sources_found": 42,
    "verified_facts": 12
  },
  "created_at": "2026-01-31T14:00:00Z",
  "updated_at": "2026-01-31T14:15:23Z"
}
```

---

### 상태 전이

```
initialized → running → completed
     ↓            ↓
     ↓         paused → running
     ↓            ↓
     ↓      stopped_by_user
     ↓            ↓
  budget_exceeded
```

**전이 조건:**

| 전이 | 조건 | 트리거 |
|------|------|--------|
| `initialized → running` | 첫 iteration 시작 | research.sh 실행 |
| `running → paused` | 사용자 's' 키 입력 | research.sh |
| `paused → running` | 재개 명령 | ./research.sh (resume) |
| `running → completed` | status 수동 설정 | 사용자 명령 |
| `running → stopped_by_user` | 사용자 'q' 키 입력 | research.sh |
| `running → budget_exceeded` | 예산 초과 | research.sh |

---

## search_history.json

### 스키마

**파일:** `.research/search_history.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["queries"],
  "properties": {
    "queries": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["iteration", "query", "normalized", "result_count", "timestamp"],
        "properties": {
          "iteration": {
            "type": "integer",
            "minimum": 0
          },
          "query": {
            "type": "string",
            "description": "원본 쿼리"
          },
          "normalized": {
            "type": "string",
            "description": "정규화된 쿼리 (소문자, 공백 제거)"
          },
          "strategy": {
            "type": "string",
            "enum": ["web", "academic", "verification"]
          },
          "result_count": {
            "type": "integer",
            "minimum": 0
          },
          "new_sources": {
            "type": "integer",
            "minimum": 0,
            "description": "새로 발견한 소스 수"
          },
          "timestamp": {
            "type": "string",
            "format": "date-time"
          }
        }
      }
    }
  }
}
```

---

### 예시 데이터

```json
{
  "queries": [
    {
      "iteration": 1,
      "query": "quantum computing applications",
      "normalized": "quantumcomputingapplications",
      "strategy": "web",
      "result_count": 10,
      "new_sources": 8,
      "timestamp": "2026-01-31T14:05:12Z"
    },
    {
      "iteration": 2,
      "query": "quantum computing limitations",
      "normalized": "quantumcomputinglimitations",
      "strategy": "web",
      "result_count": 8,
      "new_sources": 5,
      "timestamp": "2026-01-31T14:08:34Z"
    },
    {
      "iteration": 3,
      "query": "site:arxiv.org quantum supremacy",
      "normalized": "sitearxivorgquantumsupremacy",
      "strategy": "academic",
      "result_count": 5,
      "new_sources": 5,
      "timestamp": "2026-01-31T14:11:56Z"
    }
  ]
}
```

---

### 정규화 규칙

```python
def normalize_query(query: str) -> str:
    """
    쿼리를 정규화하여 중복 탐지에 사용
    """
    # 1. 소문자 변환
    normalized = query.lower()

    # 2. 특수 연산자 제거
    normalized = re.sub(r'site:\S+', '', normalized)
    normalized = re.sub(r'filetype:\S+', '', normalized)

    # 3. 공백 및 특수문자 제거
    normalized = re.sub(r'[^a-z0-9]', '', normalized)

    return normalized
```

**예시:**

| 원본 쿼리 | 정규화 결과 |
|-----------|------------|
| `"Quantum Computing"` | `"quantumcomputing"` |
| `"quantum computing applications"` | `"quantumcomputingapplications"` |
| `"site:arxiv.org quantum"` | `"quantum"` |
| `"quantum-computing (2023)"` | `"quantumcomputing2023"` |

---

## reflexion.json

### 스키마

**파일:** `.research/reflexion.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["iterations", "learned_rules"],
  "properties": {
    "iterations": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["iteration", "action", "outcome"],
        "properties": {
          "iteration": {"type": "integer"},
          "action": {
            "type": "string",
            "description": "수행한 행동"
          },
          "goal": {
            "type": "string",
            "description": "행동의 목표"
          },
          "outcome": {
            "type": "string",
            "enum": ["success", "partial", "failure"]
          },
          "reason": {
            "type": "string",
            "description": "실패/성공 이유"
          },
          "lesson": {
            "type": "string",
            "description": "학습된 교훈"
          },
          "adjustment": {
            "type": "string",
            "description": "적용할 조정 사항"
          }
        }
      }
    },
    "learned_rules": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["rule", "confidence"],
        "properties": {
          "rule": {
            "type": "string",
            "description": "학습된 규칙"
          },
          "situations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "적용 가능한 상황들"
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "success_rate": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "applied_count": {
            "type": "integer",
            "minimum": 0
          },
          "success_count": {
            "type": "integer",
            "minimum": 0
          },
          "learned_iteration": {
            "type": "integer",
            "minimum": 0
          }
        }
      }
    }
  }
}
```

---

### 예시 데이터

```json
{
  "iterations": [
    {
      "iteration": 2,
      "action": "WebSearch(\"quantum computing applications\")",
      "goal": "실용적 응용 사례 10개 이상 발견",
      "outcome": "partial",
      "reason": "일반적 설명만 반환, 구체적 사례 3개만 발견",
      "lesson": "쿼리가 너무 광범위하면 구체성 부족",
      "adjustment": "산업 분야를 명시: 'quantum computing in cryptography'"
    },
    {
      "iteration": 3,
      "action": "WebSearch(\"site:arxiv.org quantum supremacy\")",
      "goal": "학술적 근거 확보",
      "outcome": "success",
      "reason": "관련 논문 5개 발견, 모두 고신뢰도",
      "lesson": "기술 주제는 arxiv 검색이 효과적",
      "adjustment": "다음부터 기술 주제는 학술 검색 우선"
    }
  ],
  "learned_rules": [
    {
      "rule": "기술 주제는 학술 검색(arxiv) 우선",
      "situations": [
        "기술적 근거 필요",
        "논문 인용 필요",
        "신뢰도 중요"
      ],
      "confidence": 0.90,
      "success_rate": 0.85,
      "applied_count": 4,
      "success_count": 3,
      "learned_iteration": 3
    },
    {
      "rule": "쿼리에 산업/분야 명시하면 구체적 결과",
      "situations": [
        "응용 사례 필요",
        "실용적 정보 필요"
      ],
      "confidence": 0.75,
      "success_rate": 0.80,
      "applied_count": 3,
      "success_count": 2,
      "learned_iteration": 2
    }
  ]
}
```

---

## knowledge_graph.json

### 스키마

**파일:** `.research/knowledge_graph.json`

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["nodes", "edges"],
  "properties": {
    "nodes": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["id", "label", "type", "confidence"],
        "properties": {
          "id": {
            "type": "string",
            "pattern": "^[a-z_]+_[0-9]{3}$"
          },
          "label": {
            "type": "string",
            "description": "노드 이름"
          },
          "type": {
            "type": "string",
            "enum": [
              "concept",
              "technology",
              "person",
              "organization",
              "event",
              "publication"
            ]
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "sources": {
            "type": "array",
            "items": {"type": "string"}
          },
          "added_iteration": {
            "type": "integer",
            "minimum": 0
          },
          "metadata": {
            "type": "object",
            "additionalProperties": true
          }
        }
      }
    },
    "edges": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["from", "to", "relation", "confidence"],
        "properties": {
          "from": {
            "type": "string",
            "description": "시작 노드 ID"
          },
          "to": {
            "type": "string",
            "description": "끝 노드 ID"
          },
          "relation": {
            "type": "string",
            "enum": [
              "based_on",
              "enables",
              "part_of",
              "developed_by",
              "published_by",
              "contradicts",
              "supports"
            ]
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          },
          "sources": {
            "type": "array",
            "items": {"type": "string"}
          },
          "added_iteration": {
            "type": "integer",
            "minimum": 0
          }
        }
      }
    }
  }
}
```

---

### 예시 데이터

```json
{
  "nodes": [
    {
      "id": "gpt4_001",
      "label": "GPT-4",
      "type": "technology",
      "confidence": 0.98,
      "sources": ["openai.com", "arxiv.org"],
      "added_iteration": 1,
      "metadata": {
        "release_date": "2023-03-14",
        "organization": "OpenAI"
      }
    },
    {
      "id": "transformer_001",
      "label": "Transformer Architecture",
      "type": "concept",
      "confidence": 0.98,
      "sources": ["arxiv.org/abs/1706.03762"],
      "added_iteration": 2,
      "metadata": {
        "paper": "Attention Is All You Need",
        "year": 2017
      }
    },
    {
      "id": "openai_001",
      "label": "OpenAI",
      "type": "organization",
      "confidence": 0.99,
      "sources": ["openai.com"],
      "added_iteration": 1
    }
  ],
  "edges": [
    {
      "from": "gpt4_001",
      "to": "transformer_001",
      "relation": "based_on",
      "confidence": 0.95,
      "sources": ["openai.com", "arxiv.org"],
      "added_iteration": 2
    },
    {
      "from": "gpt4_001",
      "to": "openai_001",
      "relation": "developed_by",
      "confidence": 0.99,
      "sources": ["openai.com"],
      "added_iteration": 1
    }
  ]
}
```

---

## 마크다운 파일

### findings.md

**파일:** `.research/findings.md`

**구조:**

```markdown
# Research Findings

## Iteration 1 (2026-01-31 14:05)

### 핵심 발견
- ✓✓ GPT-4는 2023년 3월 14일 출시되었다 (openai.com, techcrunch.com, theverge.com)
- ✓ GPT-4는 Transformer 아키텍처 기반이다 (openai.com, arxiv.org)
- ~ GPT-4의 파라미터 수는 비공개이나 175B로 추정된다 (techcrunch.com)

### 가설 업데이트
- hyp_001: 확신도 70% → 85% (지지 증거 2개 추가)

### 다음 계획
- 반증 증거 탐색: "GPT-4 limitations"
- 학술 논문 검색: arxiv.org

---

## Iteration 2 (2026-01-31 14:08)

### 핵심 발견
- ✓ GPT-4는 멀티모달 모델이다 (이미지 입력 가능) (openai.com)
- ⚠ GPT-4의 AGI 달성 여부는 논란이 있다
  - 지지: wired.com (일부 전문가)
  - 반대: nature.com (대다수 전문가)

...
```

---

### hypotheses.md

**파일:** `.research/hypotheses.md`

**구조:**

```markdown
# Research Hypotheses

## Active Hypotheses

### hyp_001: GPT-4는 대규모 언어 모델이다
- **확신도:** 95%
- **상태:** Active
- **지지 증거:**
  - ✓✓ Transformer 기반 (openai.com, arxiv.org)
  - ✓ 대규모 파라미터 (techcrunch.com)
  - ✓ Pre-training + Fine-tuning (arxiv.org)
- **반증 증거:**
  - (없음)
- **마지막 업데이트:** Iteration 3

### hyp_002: 양자 컴퓨터는 2030년까지 실용화될 것이다
- **확신도:** 60%
- **상태:** Under Investigation
- **지지 증거:**
  - ~ 주요 기업 투자 증가 (forbes.com)
  - ~ 기술 발전 속도 (nature.com)
- **반증 증거:**
  - ✓ 기술적 장벽 여전히 높음 (ieee.org)
  - ~ 전문가 예측 2035년 이후 (arxiv.org)
- **마지막 업데이트:** Iteration 5

---

## Completed Hypotheses

### hyp_003: GPT-4는 오픈소스이다
- **확신도:** 0% (기각됨)
- **상태:** Rejected
- **반증 증거:**
  - ✓✓ OpenAI는 GPT-4를 오픈소스로 공개하지 않았다 (openai.com)
- **기각 시점:** Iteration 2
```

---

### sources.md

**파일:** `.research/sources.md`

**구조:**

```markdown
# Research Sources

## Academic Papers

### Transformer Architecture
- **제목:** Attention Is All You Need
- **저자:** Vaswani et al.
- **출처:** arxiv.org/abs/1706.03762
- **연도:** 2017
- **신뢰도:** 0.98
- **인용 횟수:** 50,000+
- **사용 Iteration:** 2, 3, 5

### GPT-4 Technical Report
- **제목:** GPT-4 Technical Report
- **저자:** OpenAI
- **출처:** arxiv.org/abs/2303.08774
- **연도:** 2023
- **신뢰도:** 0.98
- **인용 횟수:** 2,000+
- **사용 Iteration:** 1, 2

---

## Official Documentation

### OpenAI GPT-4 Page
- **URL:** https://openai.com/gpt-4
- **도메인 신뢰도:** 0.98
- **내용:** GPT-4 공식 발표, 기능 설명
- **사용 Iteration:** 1, 2, 3

---

## News Articles

### TechCrunch - GPT-4 Launch
- **URL:** https://techcrunch.com/2023/03/14/gpt-4-launch
- **도메인 신뢰도:** 0.85
- **발행일:** 2023-03-14
- **사용 Iteration:** 1

### The Verge - GPT-4 Review
- **URL:** https://theverge.com/...
- **도메인 신뢰도:** 0.80
- **발행일:** 2023-03-15
- **사용 Iteration:** 1

---

## Downloaded Papers

### Quantum Supremacy
- **파일:** `.research/papers/quantum_supremacy_2019.pdf`
- **출처:** nature.com
- **다운로드:** Iteration 4
- **페이지:** 15
- **주요 내용:** Google의 양자 우월성 달성 주장
```

---

## iteration_logs/

**파일:** `.research/iteration_logs/NNN.md`

**구조:**

```markdown
# Iteration 5 Log

**시작 시간:** 2026-01-31 14:15:00
**종료 시간:** 2026-01-31 14:17:32
**소요 시간:** 2분 32초

---

## 1. LOAD

### 상태 로드
- state.json: 읽기 성공
- search_history.json: 14개 쿼리 확인
- reflexion.json: 3개 학습 규칙 확인

---

## 2. REFLECT

### Extended Thinking

현재 상황:
- 4개 iteration 완료
- 가설 2개 진행 중
- 확신도: 85% (hyp_001), 60% (hyp_002)

미해결 질문:
- 양자 컴퓨터 실용화 시기 불명확
- GPT-4의 AGI 여부 논란

다음 접근:
- 양자 컴퓨터: 전문가 예측 추가 조사
- GPT-4: AGI 정의 명확화 필요

---

## 3. PLAN

### 검색 쿼리

1. "quantum computer commercialization timeline"
2. "site:arxiv.org post-quantum cryptography"
3. "GPT-4 AGI debate expert opinions"

### 전략
- Web Search (최신 동향)
- Academic Search (기술적 근거)
- Verification (논란 교차 확인)

---

## 4. EXECUTE

### WebSearch Results

Query 1: "quantum computer commercialization timeline"
- 결과: 8개
- 새 소스: 5개
- 유용성: 높음

Query 2: "site:arxiv.org post-quantum cryptography"
- 결과: 6개
- 새 소스: 6개
- 유용성: 매우 높음

Query 3: "GPT-4 AGI debate expert opinions"
- 결과: 10개
- 새 소스: 7개
- 유용성: 중간

---

## 5. VERIFY

### 검증 결과

발견 1: "양자 컴퓨터는 2030-2035년 실용화 예상"
- 소스: nature.com, forbes.com, ieee.org (3개)
- 신뢰도: 0.82
- 태그: ✓ HIGH

발견 2: "GPT-4는 AGI가 아니다 (대다수 전문가 의견)"
- 소스: nature.com, science.org (2개)
- 신뢰도: 0.88
- 태그: ✓✓ VERIFIED

---

## 6. SYNTHESIZE

### Knowledge Graph 업데이트
- 노드 추가: 2개
- 엣지 추가: 3개

### 가설 업데이트
- hyp_002: 확신도 60% → 70% (지지 증거 3개 추가)

---

## 7. SAVE

### 파일 업데이트
- state.json: ✓
- findings.md: ✓ (2개 발견 추가)
- search_history.json: ✓ (3개 쿼리 추가)
- knowledge_graph.json: ✓
- reflexion.json: ✓

---

## 8. OUTPUT

📊 Iteration #5 완료
🔍 이번 발견: 2개 (✓✓: 1개, ✓: 1개)
📈 가설 업데이트: hyp_002 확신도 70%
🎯 다음 계획: 양자 내성 암호화 조사
📊 진행도: 75% (비용: $0.52 / $10.00)

---

## 9. LOOP

### 종료 조건 체크
- status: running ✓
- iteration: 5 / 100 ✓
- budget: $0.52 / $10.00 ✓

**결정:** 계속 실행

### Skill 재호출
Skill("deep-research", "")
```

---

## 스키마 검증

### JSON Schema 검증 도구

```bash
# state.json 검증
ajv validate -s state.schema.json -d .research/state.json

# 모든 JSON 파일 검증
for file in .research/*.json; do
  echo "Validating $file..."
  ajv validate -s "${file%.json}.schema.json" -d "$file"
done
```

---

## 백업 및 복구

### 백업 스크립트

```bash
#!/bin/bash
# backup-research.sh

BACKUP_DIR=".research_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

cp -r .research/* "$BACKUP_DIR/"

echo "Backup created: $BACKUP_DIR"
```

### 복구 스크립트

```bash
#!/bin/bash
# restore-research.sh

if [ -z "$1" ]; then
  echo "Usage: $0 <backup_dir>"
  exit 1
fi

BACKUP_DIR="$1"

cp -r "$BACKUP_DIR"/* .research/

echo "Restored from: $BACKUP_DIR"
```

---

**다음:** [08-configuration.md](./08-configuration.md) - 설정 가이드
