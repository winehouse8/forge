# Pathfinder Research

Claude를 사용한 심층 연구 자동화 CLI 도구입니다.

## 요구사항

- macOS 또는 Linux
- Python 3 (macOS에 기본 설치됨)
- [Claude CLI](https://github.com/anthropics/claude-code) 설치 및 설정 완료

## 빠른 시작

```bash
# 새 연구 시작
./bin/pathfinder-research "양자 컴퓨팅의 실용적 응용 분야는?"

# 상태 확인
./bin/pathfinder-status

# 지식 맵 보기
cat .research/current/summary.md

# 최종 보고서 생성
./bin/pathfinder-report
```

## 명령어

| 명령어 | 설명 |
|--------|------|
| `pathfinder-research "질문"` | 새 연구 세션 시작 |
| `pathfinder-research --resume` | 중단된 세션 이어하기 |
| `pathfinder-research "질문" 30` | 30회 반복으로 제한 |
| `pathfinder-status` | 현재 연구 진행 상황 표시 |
| `pathfinder-report` | 최신 세션 보고서 생성 |
| `pathfinder-report {경로}` | 특정 세션 보고서 생성 |
| `pathfinder-cleanup` | 오래된/빈 세션 삭제 |
| `pathfinder-cleanup --dry-run` | 삭제 대상 미리보기 |

## 작동 방식

1. **외부 루프**: `pathfinder-research`가 Claude를 반복 호출
2. **각 반복**: Claude가 SPAWN → SELECT → EXPLORE → SAVE 사이클 수행
3. **상태 저장**: 모든 데이터는 `.research/current/`에 저장
4. **완료 조건**: iteration >= 50 이고 pending holes가 없을 때 종료

### 연구 사이클 (반복당)

```
SPAWN   → pending < 3이면 새로운 연구 구멍(hole) 생성
SELECT  → 가장 흥미로운 hole 선택
EXPLORE → WebSearch로 정보 검색, 기존 claim과 비교 평가
SAVE    → evidence 작성, claim 업데이트, summary 갱신
```

## 프로젝트 구조

```
forge/
├── bin/                    # CLI 도구
│   ├── pathfinder-research # 메인 연구 드라이버
│   ├── pathfinder-status   # 진행 상황 확인
│   ├── pathfinder-report   # 보고서 생성
│   └── pathfinder-cleanup  # 세션 정리
├── lib/                    # 내부 스크립트
│   ├── init-session.sh     # 세션 초기화
│   └── generate-prompt.sh  # 프롬프트 생성
├── prompts/                # Claude 프롬프트
│   ├── research-cycle.md   # 반복당 지침
│   └── report.md           # 보고서 생성 지침
└── .research/              # 연구 데이터 (실행 시 생성)
    ├── current/            # 현재 활성 세션 (symlink)
    └── sessions/           # 모든 연구 세션
```

## 연구 데이터 구조

각 세션이 생성하는 파일:

```
.research/sessions/research_YYYYMMDD_HHMMSS/
├── holes.json      # 연구 상태 (pending, explored, iteration)
├── summary.md      # 지식 맵 (200줄 이내)
├── claims/         # 개별 주장 (claim_1.md, claim_2.md, ...)
└── evidence/       # 뒷받침 증거 (ev_1.md, ev_2.md, ...)
```

### holes.json

```json
{
  "question": "원래 연구 질문",
  "pending": [...],
  "explored": [...],
  "next_id": 1,
  "iteration": 0
}
```

### Claim 강도

- `> 0.8` (strong): 높은 신뢰도, 여러 1차 출처 확인
- `0.4-0.8` (uncertain): 중간 신뢰도, 추가 검증 필요
- `<= 0.4` (weak): 낮은 신뢰도, 회의적 접근 필요

### Evidence 권위도

- `0.8-1.0`: 논문, 공식 문서 (1차 출처)
- `0.4-0.7`: 블로그, 리뷰 (2차 출처)
- `< 0.4`: 출처 불명 (낮은 신뢰)

## 중단 및 재개

- `Ctrl+C`로 언제든 중단 가능
- `pathfinder-research --resume`으로 이어하기

## 세션 관리

```bash
# 세션 목록 보기
ls .research/sessions/

# 오래된 세션(7일 이상), 빈 세션, 테스트 세션 정리
./bin/pathfinder-cleanup

# 삭제 전 미리보기
./bin/pathfinder-cleanup --dry-run
```

## 설정

`.claude/settings.json`에서 커스터마이즈:

- `model`: 사용할 Claude 모델
- `permissions`: 파일 접근 규칙

## 아키텍처

[Ralph Loop](https://github.com/snarktank/ralph) 패턴 기반:

- 외부 오케스트레이터(bash)가 Claude를 반복 호출
- 각 호출은 독립적 (1회 반복)
- 상태는 파일시스템에 저장
- 컨텍스트 한계를 넘는 장시간 연구 가능

## 문제 해결

### "Iteration stuck" 에러

Claude가 `holes.json`을 업데이트하지 않음. 확인 사항:
- Claude CLI 작동 확인: `claude --version`
- `.claude/settings.json` 권한 설정 확인

### "No session to resume" 에러

활성 세션이 없음. 새로 시작:
```bash
./bin/pathfinder-research "질문"
```

### 빈 결과

- `.research/current/summary.md`에서 진행 상황 확인
- `./bin/pathfinder-status`로 상세 정보 확인
- WebSearch를 위한 인터넷 연결 확인

## 라이센스

MIT
