# Research Skill 계획서 v1

## 목표
사용자가 질문을 던지면, 스스로 끝내지 않고 **사용자가 중단할 때까지** 무한루프로 검색-분석-가설수립-재검색을 반복하며 점진적으로 답에 근접해나가는 리서치봇 스킬

---

## 핵심 설계 원칙

### 1. 사고 프레임워크 (Thinking Tools)
| 도구 | 적용 방식 |
|------|-----------|
| **과학적 방법론** | 관찰 → 가설 → 실험(검색) → 분석 → 수정된 가설 |
| **오컴의 면도날** | 복잡한 설명보다 단순한 설명 우선, 불필요한 가정 제거 |
| **제1원칙** | 기존 가정을 버리고 근본 원리부터 재구성 |
| **반증 가능성** | 가설을 반박할 수 있는 증거도 적극 탐색 |

### 2. 무한루프 아키텍처 (Ralph 방식 참고)

```
┌─────────────────────────────────────────────────────────┐
│                    research.sh (메인 루프)               │
│  ┌─────────────────────────────────────────────────┐   │
│  │  while [ $iteration -lt $MAX_ITERATIONS ]; do   │   │
│  │      claude --skill research_cycle              │   │
│  │      # 각 사이클은 새로운 컨텍스트              │   │
│  │      # 상태는 파일로 유지                        │   │
│  │  done                                            │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

**핵심: 매 반복마다 fresh context + 파일 기반 메모리**

---

## 파일 구조

```
~/.claude/skills/research/
├── research.skill.md          # 스킬 정의 (단일 사이클)
├── research.sh                # 무한루프 실행 스크립트
└── templates/
    └── state_template.json    # 상태 파일 템플릿

프로젝트 디렉토리/
├── .research/
│   ├── state.json             # 현재 리서치 상태
│   ├── findings.md            # 누적된 발견 사항
│   ├── hypotheses.md          # 가설 히스토리
│   ├── sources.md             # 참고 자료 목록
│   └── iteration_logs/        # 각 반복의 상세 로그
│       ├── 001.md
│       ├── 002.md
│       └── ...
└── RESEARCH_REPORT.md         # 최종/중간 보고서
```

---

## 상태 관리 (state.json)

```json
{
  "question": "원본 질문",
  "iteration": 5,
  "max_iterations": 100,
  "status": "running",  // running | paused | completed

  "current_hypothesis": {
    "statement": "현재 가설",
    "confidence": 0.7,
    "supporting_evidence": [],
    "contradicting_evidence": []
  },

  "knowledge_graph": {
    "confirmed_facts": [],
    "uncertain_claims": [],
    "disproven_claims": []
  },

  "next_actions": [
    {"type": "search", "query": "다음 검색어", "reason": "이유"},
    {"type": "verify", "claim": "검증할 주장", "method": "방법"}
  ],

  "thinking_mode": "first_principles",  // scientific | occam | first_principles | falsification
  "search_depth": "deep"  // shallow | medium | deep
}
```

---

## 단일 사이클 플로우 (research.skill.md)

```
┌──────────────────────────────────────────────────────────┐
│  1. LOAD STATE                                           │
│     - state.json, findings.md, hypotheses.md 읽기        │
│     - 현재 iteration 확인                                │
├──────────────────────────────────────────────────────────┤
│  2. REFLECT (이전 사이클 분석)                           │
│     - 지금까지 알게 된 것은?                             │
│     - 아직 모르는 것은?                                  │
│     - 현재 가설의 신뢰도는?                              │
├──────────────────────────────────────────────────────────┤
│  3. PLAN (다음 행동 계획)                                │
│     - 어떤 사고 도구를 적용할지 선택                     │
│     - 검색 전략 수립                                     │
│     - 검증할 가설 선정                                   │
├──────────────────────────────────────────────────────────┤
│  4. EXECUTE (검색 및 분석)                               │
│     - WebSearch: 일반 웹 검색                            │
│     - WebFetch: 특정 URL 내용 분석                       │
│     - Context7: 기술 문서 검색                           │
│     - (확장) Exa, Grep.app 등                            │
├──────────────────────────────────────────────────────────┤
│  5. SYNTHESIZE (종합)                                    │
│     - 새로운 정보를 기존 지식과 통합                     │
│     - 가설 업데이트 또는 새 가설 생성                    │
│     - 모순점 식별                                        │
├──────────────────────────────────────────────────────────┤
│  6. SAVE STATE                                           │
│     - state.json 업데이트                                │
│     - findings.md에 새 발견 추가                         │
│     - iteration_logs/NNN.md 작성                         │
│     - RESEARCH_REPORT.md 업데이트                        │
├──────────────────────────────────────────────────────────┤
│  7. OUTPUT (사용자에게 보고)                             │
│     - 이번 사이클 요약                                   │
│     - 현재 가설 상태                                     │
│     - 다음 사이클 예고                                   │
│     - "계속하려면 Enter, 중단하려면 'stop' 입력"         │
└──────────────────────────────────────────────────────────┘
```

---

## 검색 도구 선택 (Oh My OpenCode 참고)

| 도구 | 용도 | 구현 방식 |
|------|------|-----------|
| **WebSearch** | 일반 웹 검색 | Claude Code 내장 |
| **WebFetch** | 특정 페이지 심층 분석 | Claude Code 내장 |
| **Context7** | 기술 문서, 라이브러리 문서 | MCP (이미 연결됨) |
| **Exa** | 시맨틱 검색, 고품질 결과 | MCP 추가 필요 |
| **Grep.app** | GitHub 코드 검색 | MCP 또는 API |
| **arXiv/Scholar** | 학술 논문 검색 | WebFetch로 대체 가능 |

### 우선순위
1. **Phase 1**: WebSearch + WebFetch + Context7 (현재 가능)
2. **Phase 2**: Exa MCP 추가 (고품질 시맨틱 검색)
3. **Phase 3**: 학술 검색 통합

---

## 학술 자료 검색 (Academic Search)

### 지원 소스

| 소스 | API | 커버리지 | 특징 | 비용 |
|------|-----|----------|------|------|
| **arXiv** | ✅ 공식 | CS, 물리, 수학 | PDF 직접 다운로드 | 무료 |
| **Semantic Scholar** | ✅ 공식 | 225M+ 논문 | TLDR, 인용관계, 추천 | 무료 |
| **PubMed** | ✅ 공식 | 의학, 생명과학 | 36M+ 논문 | 무료 |
| **Google Scholar** | ❌ 없음 | 가장 넓음 | WebSearch로 우회 | 무료 |
| **OpenAlex** | ✅ 공식 | 250M+ | 완전 오픈, 메타데이터 풍부 | 무료 |

### PDF 읽기 전략

```
┌─────────────────────────────────────────────────────────────┐
│  1. 검색 (Search)                                           │
│     - Semantic Scholar API: 시맨틱 검색 + TLDR              │
│     - arXiv API: 최신 CS/AI 논문                            │
│     - WebSearch: "site:arxiv.org {query}"                   │
│     - WebSearch: "site:semanticscholar.org {query}"         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  2. 메타데이터 확인 (Metadata)                              │
│     - WebFetch(arxiv.org/abs/XXXX) → 제목, 저자, Abstract   │
│     - Semantic Scholar API → 인용수, 영향력, 관련 논문      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  3. PDF 다운로드 (Download)                                 │
│     - curl -L -o paper.pdf https://arxiv.org/pdf/XXXX      │
│     - 저장 위치: .research/papers/                          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────┐
│  4. 전문 분석 (Read & Analyze)                              │
│     - Read("/path/to/paper.pdf") → 전체 내용                │
│     - 핵심 내용 추출, 가설 검증에 활용                       │
└─────────────────────────────────────────────────────────────┘
```

### config.json 학술 검색 설정

```json
{
  "academic": {
    "enabled": true,
    "sources": ["arxiv", "semantic_scholar", "pubmed", "openalex"],
    "auto_download_pdf": true,
    "pdf_storage_path": ".research/papers/",
    "max_papers_per_query": 5,

    "arxiv": {
      "enabled": true,
      "categories": ["cs.AI", "cs.LG", "cs.CL"]  // 관심 카테고리
    },

    "semantic_scholar": {
      "enabled": true,
      "api_key_env": "S2_API_KEY",  // 선택적 (높은 rate limit)
      "include_tldr": true,
      "include_citations": true
    },

    "pubmed": {
      "enabled": false  // 의학 연구 시 활성화
    }
  }
}
```

### 학술 검색 스킬 프롬프트

```markdown
## 학술 자료 검색 시

1. **검색 쿼리 생성**
   - 일반 검색: WebSearch("site:arxiv.org {키워드}")
   - 시맨틱 검색: Semantic Scholar API 호출

2. **관련 논문 필터링**
   - 인용수, 출판년도, 관련성으로 상위 3-5개 선정

3. **PDF 다운로드 및 분석**
   ```bash
   curl -L -o .research/papers/{paper_id}.pdf {pdf_url}
   ```

4. **핵심 내용 추출**
   - Abstract, Introduction, Conclusion 우선 분석
   - 방법론, 실험 결과는 필요시 상세 분석

5. **인용 정보 기록**
   - sources.md에 논문 정보 추가
   - 가설 검증에 사용된 근거로 기록
```

### 학술 검색 예시 플로우

```
사용자 질문: "Transformer의 attention mechanism이 왜 효과적인가?"

Iteration 1:
  WebSearch("site:arxiv.org transformer attention mechanism why effective")
  → arxiv.org/abs/1706.03762 발견 (Attention Is All You Need)

Iteration 2:
  WebFetch("https://arxiv.org/abs/1706.03762") → 메타데이터 확인
  curl → .research/papers/1706.03762.pdf 다운로드
  Read(".research/papers/1706.03762.pdf") → 전문 분석

Iteration 3:
  Semantic Scholar API → 이 논문을 인용한 주요 후속 연구 검색
  → "Why Self-Attention?" 등 분석 논문 발견

Iteration 4:
  후속 논문들 PDF 다운로드 및 분석
  → 가설 업데이트: "Self-attention은 O(1) path length로 장거리 의존성 학습에 유리"
```

### 논문 저장 구조

```
.research/
├── papers/
│   ├── 1706.03762.pdf          # Attention Is All You Need
│   ├── 1810.04805.pdf          # BERT
│   └── 2005.14165.pdf          # GPT-3
├── paper_index.json            # 다운로드된 논문 메타데이터
└── citations.md                # 인용 정보 정리
```

### paper_index.json 예시

```json
{
  "1706.03762": {
    "title": "Attention Is All You Need",
    "authors": ["Vaswani et al."],
    "year": 2017,
    "source": "arxiv",
    "pdf_path": ".research/papers/1706.03762.pdf",
    "abstract_summary": "Transformer 아키텍처 제안...",
    "citations": 90000,
    "used_in_iterations": [2, 5, 8],
    "key_findings": ["Self-attention으로 RNN 대체", "병렬화 가능"]
  }
}
```

---

## 무한루프 스크립트 (research.sh)

```bash
#!/bin/bash

# 설정
MAX_ITERATIONS=${1:-100}
RESEARCH_DIR=".research"
STATE_FILE="$RESEARCH_DIR/state.json"

# 초기화
init_research() {
    mkdir -p "$RESEARCH_DIR/iteration_logs"

    if [ ! -f "$STATE_FILE" ]; then
        cat > "$STATE_FILE" << 'EOF'
{
  "question": "",
  "iteration": 0,
  "max_iterations": MAX_ITERATIONS,
  "status": "running",
  "current_hypothesis": null,
  "knowledge_graph": {
    "confirmed_facts": [],
    "uncertain_claims": [],
    "disproven_claims": []
  },
  "next_actions": []
}
EOF
        sed -i "s/MAX_ITERATIONS/$MAX_ITERATIONS/" "$STATE_FILE"
    fi
}

# 메인 루프
run_research() {
    local iteration=0

    while [ $iteration -lt $MAX_ITERATIONS ]; do
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "🔬 Research Iteration #$((iteration + 1))"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        # Claude Code 호출 (새로운 컨텍스트)
        claude --skill research "Continue research cycle #$((iteration + 1))"

        # 상태 확인
        status=$(jq -r '.status' "$STATE_FILE")

        if [ "$status" = "completed" ] || [ "$status" = "paused" ]; then
            echo "Research $status at iteration $((iteration + 1))"
            break
        fi

        # 사용자 인터럽트 체크
        read -t 1 -n 1 input
        if [ "$input" = "q" ] || [ "$input" = "s" ]; then
            jq '.status = "paused"' "$STATE_FILE" > tmp.json && mv tmp.json "$STATE_FILE"
            echo "Research paused by user"
            break
        fi

        ((iteration++))
    done

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 Final Report: RESEARCH_REPORT.md"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# 실행
init_research
run_research
```

---

## 스킬 프롬프트 핵심 (research.skill.md)

```markdown
# Research Skill

당신은 심층 리서치 에이전트입니다.

## 절대 규칙
1. **절대 스스로 종료하지 않습니다** - 사용자가 명시적으로 중단할 때까지 계속합니다
2. 매 사이클마다 반드시 새로운 검색을 수행합니다
3. 가설의 확신도가 95%를 넘어도 반증 증거를 계속 탐색합니다
4. "충분하다"고 판단하지 않습니다 - 항상 더 깊이 파고듭니다

## 사고 도구 적용
- 막히면 → 제1원칙으로 돌아가기
- 정보 과다 → 오컴의 면도날로 정리
- 확신이 생기면 → 반증 가능성 탐색
- 새로운 방향 필요 → 과학적 방법론 재적용

## 출력 형식
매 사이클 끝에 반드시:
1. 이번 사이클 발견 요약 (3줄)
2. 현재 가설 및 확신도
3. 다음 사이클 계획
4. [CONTINUE] 표시 (절대 [END] 표시 금지)
```

---

## 구현 로드맵

### Phase 1: MVP (1-2일)
- [ ] 기본 state.json 구조
- [ ] research.sh 루프 스크립트
- [ ] research.skill.md 프롬프트
- [ ] WebSearch + WebFetch 기반 검색

### Phase 2: 사고 도구 강화 (2-3일)
- [ ] 사고 프레임워크 프롬프트 정교화
- [ ] 가설 추적 시스템
- [ ] 모순 탐지 로직
- [ ] findings.md 자동 정리

### Phase 3: 검색 확장 (3-5일)
- [ ] Exa MCP 연동
- [ ] Context7 활용 최적화
- [ ] 학술 자료 검색 추가
- [ ] 검색 전략 자동 선택

### Phase 4: UX 개선
- [ ] 실시간 진행상황 표시
- [ ] 중간 보고서 자동 생성
- [ ] 이전 리서치 재개 기능
- [ ] 멀티 질문 병렬 처리

---

---

## 검색 전략 심층 분석 (Deep Research 참고)

### 주요 딥리서치 구현체 비교

| 시스템 | 아키텍처 | 병렬화 방식 | 핵심 특징 |
|--------|----------|-------------|-----------|
| **OpenAI Deep Research** | RL 기반 추론 모델 (o3) | 8개 병렬 롤아웃 → 최고 신뢰도 선택 | 5단계 파이프라인, 자기반성 |
| **Claude Research** | 오케스트레이터-워커 | 리드 + 3-5 서브에이전트 병렬 | 90.2% 성능 향상 (vs 단일) |
| **Gemini Deep Research** | 멀티모달 계획 시스템 | 계획 제시 → 승인 → 실행 | 사용자 승인 기반 |

### OpenAI 5단계 파이프라인
```
1. Query Decomposition   - 질문을 서브태스크로 분해
        ↓
2. Agentic Browsing      - 자율적으로 여러 웹 소스 탐색
        ↓
3. Critical Synthesis    - 저신뢰 소스 필터링, 증거 비교
        ↓
4. Structured Output     - 인라인 인용과 함께 구조화
        ↓
5. Iterative Refinement  - 갭 발견시 루프백
```

### Anthropic 멀티에이전트 전략

```
┌─────────────────────────────────────────────────────────────┐
│                    Lead Agent (Opus 4)                      │
│   - Extended Thinking으로 전략 수립                          │
│   - 쿼리 복잡도 평가, 서브에이전트 수 결정                   │
│   - 각 서브에이전트 역할 정의                                │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ↓                 ↓                 ↓
    ┌───────────────┐ ┌───────────────┐ ┌───────────────┐
    │ SubAgent 1    │ │ SubAgent 2    │ │ SubAgent 3    │
    │ (Sonnet 4)    │ │ (Sonnet 4)    │ │ (Sonnet 4)    │
    │               │ │               │ │               │
    │ 병렬 도구호출  │ │ 병렬 도구호출  │ │ 병렬 도구호출  │
    │ (3개 이상)    │ │ (3개 이상)    │ │ (3개 이상)    │
    └───────────────┘ └───────────────┘ └───────────────┘
            │                 │                 │
            └─────────────────┼─────────────────┘
                              ↓
                    ┌─────────────────┐
                    │    Synthesis    │
                    │  (Lead Agent)   │
                    └─────────────────┘
```

**핵심 인사이트:**
- 토큰 사용량이 성능 편차의 **80%를 설명**
- 채팅 대비 에이전트는 **4배**, 멀티에이전트는 **15배** 토큰 사용
- 분리된 컨텍스트 윈도우로 작업 분산이 핵심

### 검색 전략: 광범위 → 좁혀가기 (Broad-to-Narrow)

```
Iteration 1: "AI deep research architecture"
     ↓ 결과 분석
Iteration 2: "OpenAI o3 model web browsing", "Anthropic multi-agent system"
     ↓ 결과 분석
Iteration 3: "o3 query decomposition technique", "Claude subagent parallel tool calling"
     ↓ 결과 분석
Iteration 4: 특정 논문/문서 직접 fetch
```

### Tree of Thoughts + LATS (Language Agent Tree Search)

```
                    [초기 질문]
                         │
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
    [가설 A]        [가설 B]        [가설 C]
    score: 0.7      score: 0.8      score: 0.5
         │               │               │
         │          선택 (UCB)           ✗ 가지치기
         │               │
         │      ┌────────┼────────┐
         │      ↓        ↓        ↓
         │   [B-1]    [B-2]    [B-3]
         │   0.85     0.72     0.68
         │      │
         ...   선택
```

**LATS 핵심:**
- Monte Carlo Tree Search 기반
- UCB (Upper Confidence Bound)로 탐색/활용 균형
- 자기반성으로 피드백 생성
- 유망하지 않은 가지 가지치기

---

## 우리의 검색 전략 설계

### 제안: 하이브리드 접근법

```
┌─────────────────────────────────────────────────────────────────┐
│  Phase 1: Query Decomposition (분해)                            │
│  - 원본 질문에서 3-5개 서브 질문 도출                            │
│  - 각 서브 질문의 우선순위/의존성 파악                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 2: Parallel Search (병렬 검색)                           │
│  - 3-5개 검색을 동시에 실행 (Task tool 병렬 호출)               │
│  - 각 검색 결과의 신뢰도 평가                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 3: Synthesis & Gap Analysis (종합 & 갭 분석)             │
│  - 검색 결과 통합                                                │
│  - 아직 답하지 못한 질문 식별                                    │
│  - 모순점 발견                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Phase 4: Deep Dive (심층 탐색)                                 │
│  - 유망한 소스 WebFetch로 상세 분석                              │
│  - 반증 증거 탐색                                                │
│  - 가설 업데이트                                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
                    [다음 Iteration으로]
```

### 병렬 검색 구현 (Claude Code 내)

```markdown
## 스킬 프롬프트 예시

당신은 이번 iteration에서 다음을 수행합니다:

1. state.json의 next_actions를 읽습니다
2. 병렬로 3-5개 검색을 동시에 실행합니다:

   <parallel_search>
   - WebSearch: "{query_1}"
   - WebSearch: "{query_2}"
   - WebSearch: "{query_3}"
   - WebFetch: "{url_1}" (이전 iteration에서 발견한 유망 URL)
   </parallel_search>

3. 결과를 종합하고 새로운 가설을 수립합니다
4. 다음 iteration의 검색 계획을 세웁니다
```

### 토큰 경제성 고려

| 전략 | 토큰 사용량 | 적합한 상황 |
|------|------------|------------|
| 순차 단일 검색 | 1x | 단순 질문 |
| 병렬 3개 검색 | 3-4x | 일반 리서치 |
| 풀 멀티에이전트 | 10-15x | 복잡한 심층 리서치 |

**우리의 선택: 병렬 3-5개 검색 (중간 수준)**
- 비용 효율적이면서도 충분한 범위 커버
- Claude Code의 병렬 도구 호출 활용

---

## 검색 엔진 설정 (Search Engine Config)

### 지원 검색 엔진

| 엔진 | 타입 | 장점 | 단점 | 비용 |
|------|------|------|------|------|
| **claude** | 키워드 기반 | 설정 불필요, 안정적 | 시맨틱 검색 X | 무료 (포함) |
| **exa** | 시맨틱 검색 | 복잡한 질문에 강함, 본문 포함 | MCP 설정 필요 | $5/1000검색 |
| **hybrid** | 둘 다 사용 | 최고 품질 | 비용 2배 | 혼합 |

### config.json 구조

```json
{
  "search": {
    "engine": "claude",           // "claude" | "exa" | "hybrid"
    "parallel_count": 5,          // 병렬 검색 수 (1-10)
    "fallback": true,             // 실패 시 다른 엔진으로 폴백

    "claude": {
      "enabled": true,
      "fetch_content": true       // WebFetch로 본문도 가져올지
    },

    "exa": {
      "enabled": false,
      "api_key_env": "EXA_API_KEY",  // 환경변수명
      "search_type": "neural",       // "neural" | "keyword" | "auto"
      "results_per_query": 10,       // 쿼리당 결과 수
      "include_contents": true       // 본문 포함 여부
    }
  },

  "research": {
    "max_iterations": 100,
    "thinking_framework": "scientific",  // scientific | first_principles | occam
    "auto_stop": false            // false = 사용자가 중단할 때까지
  }
}
```

### 검색 엔진별 동작 흐름

#### 1. Claude 모드 (기본)
```
research.skill.md:
  ┌─────────────────────────────────────┐
  │  WebSearch("query 1")               │
  │  WebSearch("query 2")               │  ← 병렬 실행
  │  WebSearch("query 3")               │
  └─────────────────────────────────────┘
                  ↓
  ┌─────────────────────────────────────┐
  │  WebFetch(url_1, "관련 내용 추출")   │
  │  WebFetch(url_2, "관련 내용 추출")   │  ← 유망한 URL만
  └─────────────────────────────────────┘
```

#### 2. Exa 모드
```
research.skill.md:
  ┌─────────────────────────────────────┐
  │  exa_search("query 1")              │
  │  exa_search("query 2")              │  ← 병렬 실행
  │  exa_search("query 3")              │     본문 포함 반환
  └─────────────────────────────────────┘
                  ↓
        바로 분석 (추가 fetch 불필요)
```

#### 3. Hybrid 모드 (최고 품질)
```
research.skill.md:
  ┌─────────────────────────────────────┐
  │  WebSearch("query") → 범용 결과     │
  │  exa_search("query") → 시맨틱 결과  │  ← 동시 실행
  └─────────────────────────────────────┘
                  ↓
        결과 병합 + 중복 제거 + 품질 순 정렬
```

### Exa MCP 서버 설정 방법

```json
// ~/.claude/settings.json 또는 .mcp.json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server"],
      "env": {
        "EXA_API_KEY": "${EXA_API_KEY}"
      }
    }
  }
}
```

### 스킬 프롬프트에서 분기 처리

```markdown
# research.skill.md

## 검색 실행

config.json의 search.engine 값에 따라:

### If engine == "claude":
WebSearch와 WebFetch를 사용합니다.
- WebSearch로 링크 검색
- 유망한 결과에 WebFetch로 상세 내용 수집

### If engine == "exa":
Exa MCP 도구를 사용합니다.
- exa_search로 검색 (본문 포함)
- include_contents: true로 추가 fetch 불필요

### If engine == "hybrid":
두 엔진을 동시에 사용합니다.
- WebSearch + exa_search 병렬 실행
- 결과 병합 후 분석
```

### 런타임 엔진 전환

```bash
# 기본 (Claude)
./research.sh "AI 에이전트 아키텍처"

# Exa 사용
./research.sh --engine exa "AI 에이전트 아키텍처"

# Hybrid 사용
./research.sh --engine hybrid "AI 에이전트 아키텍처"

# config.json 오버라이드
./research.sh --config ./my-config.json "질문"
```

### 비용 추정 대시보드

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Research Session Stats (Iteration #5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Engine: hybrid
Total searches: 25
  - Claude: 15 (free)
  - Exa: 10 ($0.05)

Estimated cost this session: $0.05
Remaining Exa credits: $9.95
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 열린 질문 (결정 필요)

1. **중단 메커니즘**:
   - 옵션 A: 터미널에서 키 입력 감지 (q, s)
   - 옵션 B: 매 사이클 후 프롬프트로 확인
   - 옵션 C: 별도 control 파일 모니터링

2. **컨텍스트 전달 범위**:
   - 옵션 A: state.json만 (최소)
   - 옵션 B: state.json + 최근 3개 iteration 로그
   - 옵션 C: 전체 findings.md 포함 (최대)

3. **가설 신뢰도 계산**:
   - 옵션 A: LLM 자체 판단
   - 옵션 B: 증거 개수 기반 공식
   - 옵션 C: 하이브리드

---

## 다음 단계

1. 이 계획서 검토 및 피드백
2. 열린 질문에 대한 결정
3. Phase 1 MVP 구현 시작
4. 테스트 질문으로 검증
