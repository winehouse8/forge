# Code Audit Findings

## Summary

전체 코드베이스를 감사한 결과, 핵심 아키텍처는 건전하나 **사용되지 않는 컴포넌트**와 **문서 불일치**를 발견했습니다.

## Issues Found

### 1. 사용되지 않는 서브에이전트 (High Priority)

**파일:**
- `.claude/agents/web-researcher.md`
- `.claude/agents/academic-researcher.md`
- `.claude/agents/fact-checker.md`

**문제:**
- 메인 스킬 (`deep-research/SKILL.md`)에서 이 에이전트들을 호출하지 않음
- `allowed-tools`에 `Task`가 있지만 실제 사용 없음
- 메인 스킬이 직접 `WebSearch`, `WebFetch` 사용

**증거:**
```bash
$ grep -n "Task\|web-researcher\|academic-researcher\|fact-checker" .claude/skills/deep-research/SKILL.md
5:allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep, Task, Skill
# Task tool 사용 코드 없음
```

**영향:**
- 메모리 낭비 (사용 안 되는 정의 파일)
- 문서 혼란 (README/CLAUDE.md에서 서브에이전트 언급)
- 유지보수 부담

**권장 조치:**
- 서브에이전트 파일 삭제
- 또는 메인 스킬이 실제로 사용하도록 구현

### 2. 문서 불일치 (Medium Priority)

**문제:**
- README.md 라인 79-103: 서브에이전트가 아키텍처에 포함된 것처럼 표시
- CLAUDE.md 라인 80-84: 서브에이전트 목록 명시
- 실제로는 메인 스킬만 사용

**영향:**
- 개발자 혼란
- 잘못된 기대치

### 3. 중복 로직 (Low Priority)

**파일:**
- 에이전트 정의: 신뢰도 점수 (web-researcher.md:45-53)
- config.json: 신뢰도 점수 (config.json:50-59)
- 메인 스킬: 신뢰도 평가 로직 (SKILL.md:102-116)

**문제:**
- 동일한 신뢰도 점수가 3곳에 정의됨
- 일관성 유지 어려움

## Components Status

### ✅ Working Correctly

1. **Stop Hook** (`.claude/hooks/stop-hook.py`)
   - Ralph Loop 패턴 올바르게 구현
   - status="running"일 때만 차단
   - 일반 세션에서는 종료 허용

2. **Main Skill** (`deep-research/SKILL.md`)
   - 자기 재귀 호출 올바름
   - 9단계 사이클 명확
   - 상태 관리 로직 건전

3. **Helper Skills**
   - `dr/SKILL.md`: 단순 wrapper, 문제 없음
   - `research-status/SKILL.md`: 읽기 전용, 문제 없음
   - `research-resume/SKILL.md`: 로직 명확
   - `research-report/SKILL.md`: 로직 명확

4. **Config** (`config.json`)
   - 모든 설정값 합리적
   - Loop drift 임계값 적절

### ❌ Unused / Redundant

1. **Subagents** (`.claude/agents/*.md`)
   - 완전히 사용되지 않음
   - 삭제 후보

2. **Thinking Tools Reference** (`.claude/skills/deep-research/references/thinking_tools.md`)
   - 메인 스킬에 사고 도구 표 포함되어 있음 (SKILL.md:183-191)
   - 별도 파일 필요성 확인 필요

## Recommendations

### Option A: 서브에이전트 삭제 (권장)

**이유:**
- 현재 아키텍처가 잘 작동함
- 메인 스킬이 직접 WebSearch/WebFetch 사용하는 것이 더 단순
- 서브에이전트 없이도 병렬 검색 가능

**작업:**
1. `.claude/agents/` 디렉토리 삭제
2. README.md 아키텍처 다이어그램에서 서브에이전트 제거
3. CLAUDE.md에서 서브에이전트 언급 제거
4. config.json의 신뢰도 점수 유지 (메인 스킬에서 참조)

### Option B: 서브에이전트 활성화

**이유:**
- 모듈화된 구조
- 각 에이전트가 전문화된 작업 수행
- Haiku 모델 사용으로 비용 절감

**작업:**
1. 메인 스킬에 Task tool 호출 추가
2. temp 파일 통합 로직 구현
3. 에이전트 간 데이터 흐름 명확화

**권장: Option A** - 현재 단순한 구조가 더 효과적이고 안정적

## Next Steps

1. Task #5: 리팩토링 실행 (Option A)
2. Task #6: 문서 업데이트
3. Task #7: 테스트
