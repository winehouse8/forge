# CLAUDE.md

Claude Code 프로젝트 설정 파일입니다.

---

## 프로젝트 소개

**Pathfinder Research**는 심층 연구 자동화를 위한 독립 CLI 도구입니다.

> Claude Code 스킬이 아닙니다. 터미널에서 직접 실행하세요.

---

## 사용법

```bash
# 새 연구 시작
./bin/pathfinder-research "연구 질문"

# 중단된 연구 재개
./bin/pathfinder-research --resume

# 진행 상황 확인
./bin/pathfinder-status

# 보고서 생성
./bin/pathfinder-report

# 오래된 세션 정리
./bin/pathfinder-cleanup
```

---

## 프로젝트 구조

```
forge/
├── bin/                    # CLI 도구 (사용자용)
│   ├── pathfinder-research
│   ├── pathfinder-status
│   ├── pathfinder-report
│   └── pathfinder-cleanup
├── lib/                    # 내부 스크립트
│   ├── init-session.sh
│   └── generate-prompt.sh
├── prompts/                # Claude 프롬프트
│   ├── research-cycle.md
│   └── report.md
├── .research/              # 연구 데이터 (실행 시 생성)
└── .claude/
    └── settings.json
```

---

## 작동 원리

1. `pathfinder-research`가 Claude CLI를 반복 호출
2. 각 호출에서 하나의 반복 수행: SPAWN → SELECT → EXPLORE → SAVE
3. 상태는 `.research/current/`에 저장
4. iteration >= 50 이고 pending holes가 없으면 완료

---

## 연구 데이터

```
.research/current/
├── holes.json      # 상태 (pending, explored, iteration)
├── summary.md      # 지식 맵
├── claims/         # claim_N.md 파일들
└── evidence/       # ev_N.md 파일들
```

---

## 아키텍처

[Ralph Loop](https://github.com/snarktank/ralph) 패턴 기반:
- 외부 오케스트레이터(bash)가 Claude를 반복 호출
- 각 호출은 독립적
- 상태는 파일시스템에 저장

---

## 개발자 참고

### 새 기능 추가 시

1. CLI 도구는 `bin/`에
2. 내부 스크립트는 `lib/`에
3. Claude 프롬프트는 `prompts/`에

### 테스트

```bash
# 세션 생성 테스트
./lib/init-session.sh "테스트 질문"

# 상태 표시 테스트
./bin/pathfinder-status

# 정리 테스트 (드라이런)
./bin/pathfinder-cleanup --dry-run

# 테스트 데이터 삭제
rm -rf .research
```
