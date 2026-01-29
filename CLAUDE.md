# Deep Research Project

## Quick Start

```bash
# 새 연구 시작 (최대 50회 iteration)
./research.sh 50 "연구 질문"

# 기존 연구 재개
./research.sh

# 상태 확인
cat .research/state.json | jq .iteration

# 또는 스킬 사용
claude /research-status
```

## 사용 가능한 명령어

| 명령어 | 설명 |
|--------|------|
| `/deep-research [질문]` | 심층 연구 시작 |
| `/dr [질문]` | /deep-research 단축 명령 |
| `/research-status` | 현재 연구 상태 확인 |
| `/research-resume` | 일시정지된 연구 재개 |
| `/research-report` | 연구 보고서 생성 |

## Controls (research.sh 실행 중)

- `q`: 즉시 종료 (상태 저장됨)
- `s`: 일시 정지 (나중에 재개 가능)
- 재개: `./research.sh` 다시 실행

## Research Data Location

| 파일 | 설명 |
|------|------|
| `.research/state.json` | 현재 연구 상태 |
| `.research/findings.md` | 누적 발견 사항 |
| `.research/hypotheses.md` | 가설 히스토리 |
| `.research/sources.md` | 참고 자료 목록 |
| `.research/knowledge_graph.json` | 지식 그래프 |
| `.research/reflexion.json` | 실패 학습 메모리 |
| `.research/search_history.json` | 검색 중복 방지 |
| `.research/iteration_logs/` | 반복별 상세 로그 |
| `.research/papers/` | 다운로드된 PDF |
| `RESEARCH_REPORT.md` | 최종 보고서 |

## 중요 규칙

1. `.research/` 디렉토리는 **절대 삭제하지 마세요** - 연구 데이터 손실
2. 연구 중 수동 파일 수정 금지 - 상태 불일치 발생 가능
3. 예산 한도: $10/세션 (config.json에서 조정 가능)

## 설정 파일

| 파일 | 설명 |
|------|------|
| `config.json` | 스킬 설정 (검색, 메모리, 비용) |
| `.claude/settings.json` | Claude Code 설정 |
| `.claude/skills/deep-research/SKILL.md` | 메인 스킬 정의 |

## 환경 변수

필수:
- `ANTHROPIC_API_KEY`: Claude API 키 (Claude Code에서 자동 사용)

선택:
- `DEBUG_MODE`: 디버그 출력 활성화

## 트러블슈팅

### 연구가 계속 같은 검색을 반복함
→ `.research/search_history.json` 확인
→ Loop drift 방지 규칙이 작동 중인지 확인

### 예산 초과 경고
→ `config.json`의 `cost_control.budget_per_session_usd` 조정

### 상태 파일 손상
→ `.research/state.json` 백업 후 재초기화:
```bash
rm .research/state.json
./research.sh 50 "질문"
```

## 아키텍처

```
research.sh (외부 루프)
    │
    └─→ claude /deep-research (스킬)
            │
            ├─→ WebSearch (병렬 검색)
            ├─→ WebFetch (콘텐츠 수집)
            ├─→ Read/Write (상태 관리)
            │
            └─→ Task (서브에이전트)
                    ├─→ web-researcher
                    ├─→ academic-researcher
                    └─→ fact-checker
```
