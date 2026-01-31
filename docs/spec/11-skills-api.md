# 스킬 API 명세

**문서:** 11-skills-api.md
**최종 수정일:** 2026-01-31
**관련 파일:** `.claude/skills/*/SKILL.md`

---

## 목차
- [스킬 개요](#스킬-개요)
- [deep-research (메인)](#deep-research-메인)
- [dr (단축 명령)](#dr-단축-명령)
- [research-status](#research-status)
- [research-resume](#research-resume)
- [research-report](#research-report)

---

## 스킬 개요

### 스킬 목록

| 스킬 | 명령 | 용도 | 파일 |
|------|------|------|------|
| **deep-research** | `/deep-research [질문]` | 메인 연구 스킬 | `.claude/skills/deep-research/SKILL.md` |
| **dr** | `/dr [질문]` | deep-research 단축 | `.claude/skills/dr/SKILL.md` |
| **research-status** | `/research-status` | 상태 확인 | `.claude/skills/research-status/SKILL.md` |
| **research-resume** | `/research-resume` | 재개 | `.claude/skills/research-resume/SKILL.md` |
| **research-report** | `/research-report` | 보고서 생성 | `.claude/skills/research-report/SKILL.md` |

---

## deep-research (메인)

### 메타데이터

```yaml
---
name: deep-research
description: 사용자가 중단할 때까지 무한 반복하며 주제를 심층 연구합니다.
argument-hint: [research question]
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep, Skill
---
```

### 호출 방법

```bash
# Claude Code에서
/deep-research [연구 질문]

# 예시
/deep-research GPT-4의 주요 기능은 무엇인가?
/deep-research 양자 컴퓨팅의 최신 동향
```

### 동작

1. **첫 호출:**
   - `$ARGUMENTS`를 연구 질문으로 사용
   - state.json 초기화
   - 질문 분해 (Query Decomposition)

2. **재귀 호출 (LOOP 단계):**
   - state.json의 `question.original` 사용
   - `$ARGUMENTS` 무시
   - 이전 상태 로드

### 9단계 사이클

**상세:** [04-research-cycle.md](./04-research-cycle.md)

```
1. LOAD      → state.json 읽기
2. REFLECT   → Extended Thinking
3. PLAN      → 검색 쿼리 3-5개 생성
4. EXECUTE   → 병렬 WebSearch/Fetch
5. VERIFY    → 4계층 검증
6. SYNTHESIZE → 지식 그래프 업데이트
7. SAVE      → 모든 파일 저장
8. OUTPUT    → 진행 상황 출력
9. LOOP      → Skill("deep-research", "")
```

### 종료 조건

**파일:** `.claude/skills/deep-research/SKILL.md:216-223`

```markdown
다음 중 **하나라도** 해당하면 종료:
- ❌ status가 "completed", "paused", "stopped_by_user", "budget_exceeded"
- ❌ current >= max_iter
- ❌ budget > 10.0

**그 외 모든 경우: 계속 실행**
```

### 출력 형식

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Iteration #N 완료
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 이번 발견:
   - ✓✓ [발견 1] (소스1, 소스2, 소스3)
   - ✓ [발견 2] (소스1)

📈 현재 가설: [가설 내용]
   확신도: 85% | 지지 증거: 5개 | 반증: 1개

🎯 다음 계획: [다음 iteration 계획]

📊 진행도: 75% (비용: $0.52 / $10.00)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## dr (단축 명령)

### 메타데이터

```yaml
---
name: dr
description: /deep-research의 단축 명령어
argument-hint: [research question]
allowed-tools: Skill
---
```

### 호출 방법

```bash
/dr [연구 질문]

# deep-research와 동일
/dr GPT-4란?
```

### 동작

**파일:** `.claude/skills/dr/SKILL.md`

```markdown
다음 스킬을 즉시 호출합니다:

Skill(skill="deep-research", args="$ARGUMENTS")
```

**구현:**

```
/dr "양자 컴퓨팅"
    ↓
Skill("deep-research", "양자 컴퓨팅")
    ↓
deep-research 스킬 실행
```

---

## research-status

### 메타데이터

```yaml
---
name: research-status
description: 현재 연구 세션의 상태를 확인합니다.
allowed-tools: Read, Bash
---
```

### 호출 방법

```bash
/research-status
```

### 동작

**파일:** `.claude/skills/research-status/SKILL.md`

```markdown
1. .research/state.json 읽기
2. 다음 정보 출력:
   - 현재 iteration (N/MAX)
   - 상태 (running/paused/completed)
   - 진행도 (%)
   - 예산 ($X.XX / $Y.YY)
   - 현재 가설 목록
   - 다음 계획
```

### 출력 예시

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Research Status
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔢 Iteration: 15 / 100
📊 Status: running
📈 Progress: 60% (3/5 sub-questions answered)
💰 Budget: $1.25 / $10.00 (12.5%)

🎯 Current Hypotheses:
   1. hyp_001: GPT-4는 대규모 언어 모델이다
      Confidence: 95%
      Evidence: 8 supporting, 1 contradicting

   2. hyp_002: 양자 컴퓨터는 2030년 실용화 예상
      Confidence: 70%
      Evidence: 5 supporting, 3 contradicting

📋 Next Actions:
   - 양자 내성 암호화 조사
   - 주요 기업 개발 현황 확인

🔍 Metrics:
   - Queries executed: 45
   - Sources found: 120
   - Verified facts: 32
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## research-resume

### 메타데이터

```yaml
---
name: research-resume
description: 일시정지된 연구 세션을 재개합니다.
allowed-tools: Read, Edit, Skill
---
```

### 호출 방법

```bash
/research-resume
```

### 동작

**파일:** `.claude/skills/research-resume/SKILL.md`

```markdown
1. state.json 읽기
2. status 확인:
   - "paused" → "running"으로 변경
   - "stopped_by_user" → "running"으로 변경
   - "running" → 이미 실행 중 (경고)
   - "completed" → 완료됨 (재개 불가)
3. deep-research 스킬 호출
```

### 예시

```bash
# 연구 중단 (s 키)
# status: running → paused

# 재개
/research-resume

# 출력:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔄 Resuming Research...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Previous state:
- Iteration: 15 / 100
- Last action: Searching for quantum computing papers

Resuming from iteration 16...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# deep-research 자동 호출
```

---

## research-report

### 메타데이터

```yaml
---
name: research-report
description: 현재까지의 연구 결과를 종합한 보고서를 생성합니다.
allowed-tools: Read, Write
---
```

### 호출 방법

```bash
/research-report
```

### 동작

**파일:** `.claude/skills/research-report/SKILL.md`

```markdown
1. 모든 연구 파일 읽기:
   - state.json
   - findings.md
   - hypotheses.md
   - knowledge_graph.json
   - sources.md

2. 보고서 생성 (RESEARCH_REPORT.md):
   - Executive Summary
   - 주요 발견 사항
   - 가설 및 확신도
   - 지식 그래프 다이어그램
   - 참고 문헌
   - 메타데이터

3. RESEARCH_REPORT.md 저장
```

### 출력 파일

**파일:** `RESEARCH_REPORT.md`

**구조:**

```markdown
# Research Report: [연구 질문]

**Generated:** 2026-01-31 15:30:00
**Iterations:** 50 / 100
**Status:** Running
**Budget:** $4.25 / $10.00

---

## Executive Summary

[3-5 문장 요약]

---

## Key Findings

### High Confidence (✓✓)

1. **GPT-4는 2023년 3월 14일 출시되었다**
   - Sources: openai.com, techcrunch.com, theverge.com
   - Confidence: 0.95

2. **Transformer 아키텍처 기반**
   - Sources: arxiv.org/abs/1706.03762, openai.com
   - Confidence: 0.98

### Medium Confidence (✓)

[...]

### Low Confidence (~)

[...]

---

## Hypotheses

### hyp_001: GPT-4는 대규모 언어 모델이다
- **Confidence:** 95%
- **Supporting Evidence:** 8
- **Contradicting Evidence:** 1

[상세 설명]

---

## Knowledge Graph

```
[Mermaid 다이어그램 또는 텍스트 표현]
```

---

## Sources

### Academic Papers (15)
1. Attention Is All You Need (Vaswani et al., 2017)
2. [...]

### Official Documentation (8)
1. OpenAI GPT-4 Page
2. [...]

### News Articles (23)
[...]

---

## Metadata

- Total iterations: 50
- Total queries: 150
- Total sources: 320
- Verified facts: 45
- Cost: $4.25
```

---

## 스킬 개발 가이드

### 새 스킬 생성

```bash
mkdir -p .claude/skills/my-skill
cat > .claude/skills/my-skill/SKILL.md << 'EOF'
---
name: my-skill
description: [설명]
argument-hint: [힌트]
allowed-tools: [도구 목록]
---

# My Skill

[스킬 로직]
EOF
```

### 스킬 메타데이터 필드

| 필드 | 필수 | 설명 | 예시 |
|------|------|------|------|
| `name` | ✅ | 스킬 이름 (파일명과 일치) | `deep-research` |
| `description` | ✅ | 스킬 설명 | `심층 연구 수행` |
| `argument-hint` | ❌ | 인수 힌트 | `[research question]` |
| `allowed-tools` | ✅ | 허용된 도구 목록 | `WebSearch, Read, Write` |

### 도구 제약

**deep-research에서 허용된 도구:**
```
WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep, Skill
```

**금지된 도구:**
```
Task (서브에이전트 제거됨)
```

---

## API 일관성

### 명명 규칙

- **스킬 이름:** 소문자, 하이픈 구분 (`deep-research`)
- **파일명:** `SKILL.md` (대문자)
- **디렉토리:** `.claude/skills/[skill-name]/`

### 출력 형식

**모든 스킬은 통일된 출력 형식 사용:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[제목]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[내용]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

**다음:** [12-hooks-api.md](./12-hooks-api.md) - Hooks API 명세
