# 설정 가이드

**문서:** 08-configuration.md
**최종 수정일:** 2026-01-31
**관련 파일:** `config.json`, `.claude/settings.json`

---

## 목차
- [설정 파일 개요](#설정-파일-개요)
- [config.json](#configjson)
- [.claude/settings.json](#claudesettingsjson)
- [설정 변경 가이드](#설정-변경-가이드)
- [환경별 설정](#환경별-설정)

---

## 설정 파일 개요

### 파일 역할

| 파일 | 용도 | 수정 빈도 | 영향 범위 |
|------|------|----------|----------|
| `config.json` | 연구 전략, 예산, 검증 규칙 | 높음 | 연구 동작 |
| `.claude/settings.json` | Claude Code 설정, 권한, 훅 | 낮음 | 시스템 동작 |

---

## config.json

### 전체 구조

**파일:** `config.json`

```json
{
  "version": "4.0",

  "loop_control": {
    "max_iterations": 100,
    "completion_promise": "<promise>RESEARCH_COMPLETE</promise>",
    "auto_stop": false,
    "loop_drift_prevention": {
      "same_query_threshold": 2,
      "same_action_threshold": 3,
      "no_progress_iterations": 5
    }
  },

  "search": {
    "parallel_count": 3,
    "max_retries": 2,
    "strategies": {
      "web": {
        "enabled": true,
        "fetch_full_content": true
      },
      "academic": {
        "enabled": true,
        "sources": ["arxiv", "semantic_scholar"],
        "auto_download_pdf": true,
        "max_papers_per_query": 3
      },
      "verification": {
        "enabled": true,
        "search_contradictions": true
      }
    }
  },

  "memory": {
    "compaction_threshold": 0.8,
    "compaction_interval": 5,
    "knowledge_graph_enabled": true,
    "reflexion_enabled": true
  },

  "verification": {
    "require_sources": true,
    "min_source_count": 2,
    "cross_validation": true,
    "credibility_scores": {
      "arxiv.org": 0.95,
      "nature.com": 0.98,
      "ieee.org": 0.95,
      "acm.org": 0.95,
      "github.com": 0.70,
      "medium.com": 0.50,
      "wikipedia.org": 0.75,
      "default": 0.30
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
    "token_cost_estimates": {
      "input_per_1k": 0.003,
      "output_per_1k": 0.015
    }
  },

  "output": {
    "verbosity": "normal",
    "show_confidence": true,
    "inline_citations": true,
    "progress_dashboard": true
  }
}
```

---

### loop_control

**목적:** 무한 루프 제어 및 Loop Drift 방지

```json
"loop_control": {
  "max_iterations": 100,
  "completion_promise": "<promise>RESEARCH_COMPLETE</promise>",
  "auto_stop": false,
  "loop_drift_prevention": {
    "same_query_threshold": 2,
    "same_action_threshold": 3,
    "no_progress_iterations": 5
  }
}
```

**필드 설명:**

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `max_iterations` | integer | 100 | 최대 반복 횟수 |
| `completion_promise` | string | (설정값) | 완료 시 출력할 프롬프트 (현재 미사용) |
| `auto_stop` | boolean | false | 자동 종료 활성화 여부 (현재 false) |
| `same_query_threshold` | integer | 2 | 같은 쿼리 반복 허용 횟수 |
| `same_action_threshold` | integer | 3 | 같은 행동 반복 허용 횟수 |
| `no_progress_iterations` | integer | 5 | 진전 없음 허용 횟수 |

**사용 예:**

```bash
# 짧은 연구 (20회)
jq '.loop_control.max_iterations = 20' config.json > tmp.json
mv tmp.json config.json

# 긴 연구 (500회)
jq '.loop_control.max_iterations = 500' config.json > tmp.json
mv tmp.json config.json
```

**성능 영향:**

| 설정값 | 예상 시간 | 예상 비용 |
|--------|----------|----------|
| 20 iterations | 40분 - 1시간 | $0.80 - $1.00 |
| 100 iterations | 3-5시간 | $3.00 - $5.00 |
| 500 iterations | 15-25시간 | $15.00 - $25.00 |

---

### search

**목적:** 검색 전략 및 병렬 처리 설정

```json
"search": {
  "parallel_count": 3,
  "max_retries": 2,
  "strategies": {
    "web": {
      "enabled": true,
      "fetch_full_content": true
    },
    "academic": {
      "enabled": true,
      "sources": ["arxiv", "semantic_scholar"],
      "auto_download_pdf": true,
      "max_papers_per_query": 3
    },
    "verification": {
      "enabled": true,
      "search_contradictions": true
    }
  }
}
```

**필드 설명:**

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `parallel_count` | integer | 3 | 병렬 검색 수 (1-5 권장) |
| `max_retries` | integer | 2 | 실패 시 재시도 횟수 |
| `web.enabled` | boolean | true | 웹 검색 활성화 |
| `web.fetch_full_content` | boolean | true | WebFetch로 전체 내용 추출 |
| `academic.enabled` | boolean | true | 학술 검색 활성화 |
| `academic.sources` | array | ["arxiv", "semantic_scholar"] | 학술 소스 목록 |
| `academic.auto_download_pdf` | boolean | true | PDF 자동 다운로드 |
| `academic.max_papers_per_query` | integer | 3 | 쿼리당 최대 논문 수 |
| `verification.enabled` | boolean | true | 검증 검색 활성화 |
| `verification.search_contradictions` | boolean | true | 반증 증거 자동 탐색 |

**튜닝 가이드:**

**1. 속도 우선 (빠른 연구)**

```json
{
  "parallel_count": 5,
  "max_retries": 1,
  "strategies": {
    "web": {"enabled": true, "fetch_full_content": false},
    "academic": {"enabled": false},
    "verification": {"enabled": false}
  }
}
```

**효과:**
- ✅ 2배 빠름 (iteration당 1-1.5분)
- ❌ 정확도 하락
- ❌ 학술적 근거 부족

---

**2. 정확도 우선 (심층 연구)**

```json
{
  "parallel_count": 3,
  "max_retries": 3,
  "strategies": {
    "web": {"enabled": true, "fetch_full_content": true},
    "academic": {
      "enabled": true,
      "auto_download_pdf": true,
      "max_papers_per_query": 5
    },
    "verification": {"enabled": true, "search_contradictions": true}
  }
}
```

**효과:**
- ✅ 높은 정확도
- ✅ 학술적 근거 풍부
- ❌ 느림 (iteration당 3-4분)
- ❌ 비용 증가

---

**3. 균형 설정 (기본값)**

```json
{
  "parallel_count": 3,
  "max_retries": 2,
  "strategies": {
    "web": {"enabled": true, "fetch_full_content": true},
    "academic": {
      "enabled": true,
      "auto_download_pdf": true,
      "max_papers_per_query": 3
    },
    "verification": {"enabled": true}
  }
}
```

---

### memory

**목적:** 메모리 관리 및 지식 그래프 설정

```json
"memory": {
  "compaction_threshold": 0.8,
  "compaction_interval": 5,
  "knowledge_graph_enabled": true,
  "reflexion_enabled": true
}
```

**필드 설명:**

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `compaction_threshold` | number | 0.8 | 컴팩션 시작 임계값 (0-1) |
| `compaction_interval` | integer | 5 | 컴팩션 주기 (iterations) |
| `knowledge_graph_enabled` | boolean | true | 지식 그래프 활성화 |
| `reflexion_enabled` | boolean | true | Reflexion 메모리 활성화 |

**컴팩션 동작:**

```
Iteration 5:
  findings.md 크기: 85% (임계값 초과)
  → 자동 컴팩션 실행
  → 중복 제거, 요약 생성
  → 크기: 85% → 60%
```

**비활성화 시나리오:**

```json
{
  "knowledge_graph_enabled": false,
  "reflexion_enabled": false
}
```

**효과:**
- ✅ 20% 빠름 (그래프 업데이트 생략)
- ✅ 파일 수 감소
- ❌ 지식 구조화 없음
- ❌ 실패 학습 없음

---

### verification

**목적:** 4계층 검증 시스템 설정

```json
"verification": {
  "require_sources": true,
  "min_source_count": 2,
  "cross_validation": true,
  "credibility_scores": {
    "arxiv.org": 0.95,
    "nature.com": 0.98,
    "ieee.org": 0.95,
    "acm.org": 0.95,
    "github.com": 0.70,
    "medium.com": 0.50,
    "wikipedia.org": 0.75,
    "default": 0.30
  },
  "confidence_tags": {
    "verified": "✓✓",
    "high": "✓",
    "likely": "~",
    "uncertain": "?",
    "contradicted": "⚠"
  }
}
```

**필드 설명:**

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `require_sources` | boolean | true | 출처 필수 여부 |
| `min_source_count` | integer | 2 | 최소 소스 개수 (검증용) |
| `cross_validation` | boolean | true | 교차 검증 활성화 |
| `credibility_scores` | object | (설정값) | 도메인별 신뢰도 점수 |
| `confidence_tags` | object | (설정값) | 신뢰도 태그 기호 |

**신뢰도 점수 추가:**

```bash
# 새 도메인 추가
jq '.verification.credibility_scores["sciencedirect.com"] = 0.92' \
  config.json > tmp.json
mv tmp.json config.json
```

**신뢰도 점수 가이드라인:**

| 점수 범위 | 카테고리 | 예시 |
|----------|----------|------|
| 0.95 - 1.00 | 최고 신뢰 학술지 | nature.com, science.org |
| 0.90 - 0.94 | 고신뢰 학술 | arxiv.org, ieee.org, acm.org |
| 0.80 - 0.89 | 기술 뉴스 (상) | techcrunch.com, wired.com |
| 0.70 - 0.79 | 기술 뉴스 (중) | theverge.com, github.com |
| 0.60 - 0.69 | 일반 뉴스 | forbes.com, bloomberg.com |
| 0.50 - 0.59 | 블로그 (신뢰) | medium.com (인증된 저자) |
| 0.30 - 0.49 | 블로그 (일반) | 개인 블로그 |
| 0.00 - 0.29 | 낮은 신뢰도 | 출처 불명 |

---

### cost_control

**목적:** 예산 관리 및 비용 제어

```json
"cost_control": {
  "budget_per_session_usd": 10.0,
  "warning_threshold": 0.8,
  "hard_stop_threshold": 0.95,
  "token_cost_estimates": {
    "input_per_1k": 0.003,
    "output_per_1k": 0.015
  }
}
```

**필드 설명:**

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `budget_per_session_usd` | number | 10.0 | 세션당 최대 예산 (USD) |
| `warning_threshold` | number | 0.8 | 경고 임계값 (0-1) |
| `hard_stop_threshold` | number | 0.95 | 강제 종료 임계값 (0-1) |
| `input_per_1k` | number | 0.003 | Input 토큰 1K당 비용 |
| `output_per_1k` | number | 0.015 | Output 토큰 1K당 비용 |

**동작:**

```
비용 진행:
$0 → $8.00 (80%) → ⚠️ 경고 출력
$8.00 → $9.50 (95%) → 🛑 강제 종료
```

**예산 조정 시나리오:**

| 연구 규모 | 권장 예산 | 설정 |
|----------|----------|------|
| 빠른 조사 (20 iter) | $1 - $2 | `"budget_per_session_usd": 2.0` |
| 일반 연구 (100 iter) | $5 - $10 | `"budget_per_session_usd": 10.0` |
| 심층 연구 (500 iter) | $20 - $50 | `"budget_per_session_usd": 50.0` |

---

### output

**목적:** 출력 형식 및 상세도 제어

```json
"output": {
  "verbosity": "normal",
  "show_confidence": true,
  "inline_citations": true,
  "progress_dashboard": true
}
```

**필드 설명:**

| 필드 | 타입 | 기본값 | 설명 |
|------|------|--------|------|
| `verbosity` | string | "normal" | 출력 상세도 (minimal/normal/verbose) |
| `show_confidence` | boolean | true | 신뢰도 점수 표시 |
| `inline_citations` | boolean | true | 인라인 출처 표시 |
| `progress_dashboard` | boolean | true | 진행 대시보드 표시 |

**verbosity 비교:**

**minimal:**
```
Iteration #5 완료
새 발견: 3개
진행도: 75%
```

**normal (기본값):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Iteration #5 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 이번 발견:
   - ✓✓ GPT-4는 Transformer 기반 (openai.com, arxiv.org)
   - ✓ 175B 파라미터 사용 (techcrunch.com)

📈 현재 가설: GPT-4는 대규모 언어 모델이다
   확신도: 85% | 지지 증거: 5개 | 반증: 1개

🎯 다음 계획: 반증 증거 탐색
📊 진행도: 75% (비용: $0.52 / $10.00)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**verbose:**
```
[위 내용 + 추가 정보]
- 검색 쿼리 목록 (3개)
- 각 쿼리별 결과 개수
- WebFetch URL 목록
- 검증 세부 과정
- Reflexion 메모리 업데이트 내용
```

---

## .claude/settings.json

### 전체 구조

**파일:** `.claude/settings.json`

```json
{
  "skills": {
    "paths": [".claude/skills"]
  },

  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 .claude/hooks/stop-hook.py"
          }
        ]
      }
    ]
  },

  "permissions": {
    "allow": [
      "Read(.research/**)",
      "Write(.research/**)",
      "Edit(.research/**)",
      "Bash(curl -L -o .research/papers/*.pdf *)",
      "Bash(jq * .research/*.json)",
      "WebFetch",
      "WebSearch"
    ],
    "deny": [
      "Bash(rm -rf .research)",
      "Edit(.git/**)",
      "Read(.env)",
      "Write(.env)"
    ],
    "ask": [
      "Bash(git push *)",
      "Bash(rm *)"
    ]
  }
}
```

---

### skills

**목적:** 스킬 디렉토리 경로 지정

```json
"skills": {
  "paths": [".claude/skills"]
}
```

**스킬 디렉토리 구조:**

```
.claude/skills/
├── deep-research/
│   ├── SKILL.md
│   └── references/
│       └── thinking_tools.md
├── dr/
│   └── SKILL.md
├── research-status/
│   └── SKILL.md
├── research-resume/
│   └── SKILL.md
└── research-report/
    └── SKILL.md
```

---

### hooks

**목적:** Claude Code 훅 설정 (Ralph Loop 구현)

```json
"hooks": {
  "Stop": [
    {
      "hooks": [
        {
          "type": "command",
          "command": "python3 .claude/hooks/stop-hook.py"
        }
      ]
    }
  ]
}
```

**동작:**

```
Claude Code 종료 시도
         ↓
Stop Hook 실행 (python3 .claude/hooks/stop-hook.py)
         ↓
.research/state.json 확인
         ↓
status == "running"?
  Yes → exit 1 (종료 차단, Ralph Loop 유지)
  No  → exit 0 (종료 허용)
```

**상세:** [03-ralph-loop.md](./03-ralph-loop.md) 참조

---

### permissions

**목적:** 도구 사용 권한 제어

```json
"permissions": {
  "allow": [...],
  "deny": [...],
  "ask": [...]
}
```

**allow (자동 허용):**

```json
"allow": [
  "Read(.research/**)",
  "Write(.research/**)",
  "Edit(.research/**)",
  "Bash(curl -L -o .research/papers/*.pdf *)",
  "Bash(jq * .research/*.json)",
  "WebFetch",
  "WebSearch"
]
```

**패턴 설명:**

| 패턴 | 의미 | 예시 |
|------|------|------|
| `Read(.research/**)` | `.research/` 하위 모든 파일 읽기 허용 | `Read(.research/state.json)` |
| `Write(.research/**)` | `.research/` 하위 파일 쓰기 허용 | `Write(.research/findings.md)` |
| `Bash(curl ...)` | 특정 패턴의 bash 명령 허용 | PDF 다운로드 |
| `WebFetch` | 모든 WebFetch 허용 | 무제한 |

---

**deny (거부):**

```json
"deny": [
  "Bash(rm -rf .research)",
  "Edit(.git/**)",
  "Read(.env)",
  "Write(.env)"
]
```

**보안 원칙:**

- ❌ `.research/` 디렉토리 삭제 금지
- ❌ `.git/` 디렉토리 수정 금지
- ❌ `.env` 파일 접근 금지

---

**ask (사용자 확인 필요):**

```json
"ask": [
  "Bash(git push *)",
  "Bash(rm *)"
]
```

**동작:**

```
스킬: Bash("git push origin main")
         ↓
사용자에게 확인 요청
         ↓
사용자: [승인 / 거부]
```

---

## 설정 변경 가이드

### 예산 변경

```bash
# $10 → $20으로 증가
jq '.cost_control.budget_per_session_usd = 20.0' config.json > tmp.json
mv tmp.json config.json
```

---

### 병렬 검색 수 변경

```bash
# 3개 → 5개로 증가 (더 빠름)
jq '.search.parallel_count = 5' config.json > tmp.json
mv tmp.json config.json
```

---

### 학술 검색 비활성화

```bash
# 웹 검색만 사용 (빠르지만 정확도 하락)
jq '.search.strategies.academic.enabled = false' config.json > tmp.json
mv tmp.json config.json
```

---

### 최대 iteration 변경

```bash
# 100 → 50으로 감소
jq '.loop_control.max_iterations = 50' config.json > tmp.json
mv tmp.json config.json
```

---

### 신뢰도 점수 추가

```bash
# sciencedirect.com 추가
jq '.verification.credibility_scores["sciencedirect.com"] = 0.92' \
  config.json > tmp.json
mv tmp.json config.json
```

---

## 환경별 설정

### 개발 환경 (빠른 테스트)

**config.dev.json:**

```json
{
  "loop_control": {
    "max_iterations": 10,
    "loop_drift_prevention": {
      "same_query_threshold": 1,
      "same_action_threshold": 2,
      "no_progress_iterations": 3
    }
  },
  "search": {
    "parallel_count": 2,
    "strategies": {
      "web": {"enabled": true, "fetch_full_content": false},
      "academic": {"enabled": false},
      "verification": {"enabled": false}
    }
  },
  "cost_control": {
    "budget_per_session_usd": 1.0
  },
  "output": {
    "verbosity": "verbose"
  }
}
```

**사용:**

```bash
cp config.dev.json config.json
./research.sh 10 "테스트 질문"
```

---

### 프로덕션 환경 (심층 연구)

**config.prod.json:**

```json
{
  "loop_control": {
    "max_iterations": 500,
    "loop_drift_prevention": {
      "same_query_threshold": 2,
      "same_action_threshold": 3,
      "no_progress_iterations": 5
    }
  },
  "search": {
    "parallel_count": 3,
    "strategies": {
      "web": {"enabled": true, "fetch_full_content": true},
      "academic": {
        "enabled": true,
        "auto_download_pdf": true,
        "max_papers_per_query": 5
      },
      "verification": {"enabled": true}
    }
  },
  "cost_control": {
    "budget_per_session_usd": 50.0
  },
  "output": {
    "verbosity": "normal"
  }
}
```

---

### CI/CD 환경 (자동화 테스트)

**config.ci.json:**

```json
{
  "loop_control": {
    "max_iterations": 5,
    "auto_stop": true
  },
  "search": {
    "parallel_count": 1,
    "strategies": {
      "web": {"enabled": true, "fetch_full_content": false},
      "academic": {"enabled": false},
      "verification": {"enabled": false}
    }
  },
  "cost_control": {
    "budget_per_session_usd": 0.5
  },
  "output": {
    "verbosity": "minimal"
  }
}
```

---

## 설정 검증

### JSON 유효성 검사

```bash
# config.json 검증
jq empty config.json && echo "✓ Valid JSON" || echo "✗ Invalid JSON"

# .claude/settings.json 검증
jq empty .claude/settings.json && echo "✓ Valid JSON" || echo "✗ Invalid JSON"
```

---

### 설정 값 범위 검사

```bash
# max_iterations 범위 확인 (1-1000)
max_iter=$(jq '.loop_control.max_iterations' config.json)
if [ "$max_iter" -lt 1 ] || [ "$max_iter" -gt 1000 ]; then
  echo "⚠️ max_iterations must be between 1 and 1000"
fi

# budget 범위 확인 (0.1-100)
budget=$(jq '.cost_control.budget_per_session_usd' config.json)
if (( $(echo "$budget < 0.1" | bc -l) )); then
  echo "⚠️ budget too low (minimum: $0.1)"
fi
```

---

## 트러블슈팅

### 설정 파일 손상

**증상:**
```
Error: Invalid JSON in config.json
```

**해결:**

```bash
# 백업에서 복구
cp config.json.backup config.json

# 또는 기본값으로 재생성
cat > config.json << 'EOF'
{
  "version": "4.0",
  "loop_control": {"max_iterations": 100},
  ...
}
EOF
```

---

### 권한 거부 오류

**증상:**
```
Error: Permission denied for Write(.research/state.json)
```

**해결:**

```bash
# .claude/settings.json 확인
jq '.permissions.allow' .claude/settings.json

# 권한 추가
jq '.permissions.allow += ["Write(.research/**)"]' \
  .claude/settings.json > tmp.json
mv tmp.json .claude/settings.json
```

---

**다음:** [09-testing.md](./09-testing.md) - 테스트 시나리오 및 검증
