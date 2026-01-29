# Deep Research Skill

무한 반복 심층 리서치 봇 for Claude Code

**Ralph Loop 패턴 기반 자율 연구 에이전트** - 사용자가 중단할 때까지 자동으로 검색-분석-가설수립을 반복합니다.

## ✅ 검증 완료

- **Ralph Loop 작동 확인**: 3회 연속 자동 iteration 실행 성공
- **자기 재귀 호출**: Skill tool을 통한 무한 루프 구현
- **Stop Hook 통합**: 외부 검증 기반 종료 제어
- **상태 지속성**: JSON 파일 기반 세션 관리

## Quick Start

```bash
# 새 연구 시작 (50회 iteration)
./research.sh 50 "연구 질문"

# 기존 연구 재개
./research.sh

# 또는 Claude Code에서 직접
claude /deep-research "연구 질문"
```

## 명령어

| 명령어 | 설명 |
|--------|------|
| `/deep-research [질문]` | 심층 연구 시작 |
| `/dr [질문]` | 단축 명령 |
| `/research-status` | 상태 확인 |
| `/research-resume` | 재개 |
| `/research-report` | 보고서 생성 |

## 컨트롤 키

- `q` : 종료
- `s` : 일시정지

## 데이터 위치

- `.research/state.json` : 현재 상태
- `.research/findings.md` : 발견 사항
- `.research/iteration_logs/` : 반복별 상세 로그
- `RESEARCH_REPORT.md` : 최종 보고서

## 핵심 기능

### 1. 이중 루프 아키텍처
- **외부 루프**: `research.sh` 또는 Stop Hook을 통한 종료 제어
- **내부 루프**: ReAct 패턴 기반 추론-행동 사이클
- **자기 재귀**: Skill tool로 자신을 호출하여 연속 실행

### 2. Ralph Loop 패턴
- LLM의 주관적 "완료" 판단 무시
- 객관적 조건만으로 종료 결정 (max_iterations, status, budget)
- Stop Hook이 종료 시도를 차단하고 계속 실행 강제

### 3. Reflexion 기반 자기개선
- **Actor**: 검색 및 분석 실행
- **Evaluator**: 검색 결과 품질 평가
- **Self-Reflection**: 실패 패턴 학습 및 전략 변경

### 4. Loop Drift 방지
- 검색 히스토리 추적으로 중복 방지
- Reflexion 메모리로 실패 패턴 회피
- 동일 행동 3회 반복 시 전략 자동 변경

## 아키텍처

```
┌─────────────────────────────────────┐
│  사용자 입력 또는 research.sh       │
└──────────────┬──────────────────────┘
               ↓
┌──────────────────────────────────────┐
│  /deep-research Skill (Iteration N)  │
│  ┌────────────────────────────────┐  │
│  │ 1. LOAD    - 상태 로드         │  │
│  │ 2. REFLECT - 분석              │  │
│  │ 3. PLAN    - 검색 계획         │  │
│  │ 4. EXECUTE - 병렬 검색         │  │
│  │ 5. VERIFY  - 교차 검증         │  │
│  │ 6. SYNTHESIZE - 지식 통합      │  │
│  │ 7. SAVE    - 상태 저장         │  │
│  │ 8. OUTPUT  - 결과 출력         │  │
│  │ 9. LOOP    - 종료 체크         │  │
│  └────────────────────────────────┘  │
└──────────────┬──────────────────────┘
               ↓
        종료 조건 만족?
         No ↓    Yes → 종료
    Skill("deep-research", "")
    재귀 호출 → Iteration N+1
```

## 기술 스택

- **Claude Sonnet 4.5**: 메인 추론 엔진
- **LangGraph 패턴**: Cyclical graph 지원
- **Reflexion 프레임워크**: 자기개선 메커니즘
- **Agent Cognitive Compressor**: Bounded memory 관리
- **Golden Dataset**: 품질 평가 기준

## 제한사항

- 예산 제한: $10/세션 (config.json에서 조정)
- Max iterations: 100 (기본값)
- 수동 중단: `q` 또는 `s` 키
