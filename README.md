# Deep Research Skill

무한 반복 심층 리서치 봇 for Claude Code

## Quick Start

```bash
# 새 연구 시작 (50회 iteration)
./research.sh 50 "연구 질문"

# 기존 연구 재개
./research.sh
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
- `RESEARCH_REPORT.md` : 최종 보고서
