# 배포 가이드

**문서:** 10-deployment.md
**최종 수정일:** 2026-01-31
**관련 파일:** `research.sh`, `config.json`, `.claude/`

---

## 목차
- [사전 요구사항](#사전-요구사항)
- [설치 가이드](#설치-가이드)
- [설정 검증](#설정-검증)
- [첫 실행](#첫-실행)
- [프로덕션 배포](#프로덕션-배포)

---

## 사전 요구사항

### 필수 소프트웨어

| 소프트웨어 | 최소 버전 | 확인 명령 | 설치 방법 |
|----------|----------|----------|----------|
| **Claude Code** | Latest | `claude --version` | https://claude.ai/download |
| **Python** | 3.7+ | `python3 --version` | https://python.org |
| **jq** | 1.6+ | `jq --version` | `brew install jq` (macOS) |
| **curl** | 7.0+ | `curl --version` | 시스템 기본 제공 |
| **bc** | 1.0+ | `bc --version` | `brew install bc` (macOS) |

---

### 환경 변수

| 변수 | 필수 여부 | 설명 | 설정 방법 |
|------|----------|------|----------|
| `ANTHROPIC_API_KEY` | ✅ 필수 | Claude API 키 | Claude Code가 자동 관리 |
| `DEBUG_MODE` | ❌ 선택 | 디버그 출력 활성화 | `export DEBUG_MODE=1` |

---

### 시스템 요구사항

| 리소스 | 최소 | 권장 |
|--------|------|------|
| **RAM** | 4GB | 8GB+ |
| **디스크** | 1GB | 5GB+ (논문 다운로드 시) |
| **네트워크** | 필수 | 안정적인 인터넷 연결 |

---

## 설치 가이드

### Step 1: 저장소 클론

```bash
# HTTPS
git clone https://github.com/your-org/pathfinder.git
cd pathfinder/forge

# 또는 SSH
git clone git@github.com:your-org/pathfinder.git
cd pathfinder/forge
```

---

### Step 2: 의존성 확인

```bash
# 모든 필수 도구 확인
./check-dependencies.sh
```

**check-dependencies.sh:**
```bash
#!/bin/bash

echo "Checking dependencies..."

# Claude Code
if command -v claude &> /dev/null; then
  echo "✅ Claude Code: $(claude --version)"
else
  echo "❌ Claude Code not found"
  echo "   Install from: https://claude.ai/download"
  exit 1
fi

# Python
if command -v python3 &> /dev/null; then
  echo "✅ Python: $(python3 --version)"
else
  echo "❌ Python not found"
  exit 1
fi

# jq
if command -v jq &> /dev/null; then
  echo "✅ jq: $(jq --version)"
else
  echo "❌ jq not found"
  echo "   Install: brew install jq"
  exit 1
fi

# curl
if command -v curl &> /dev/null; then
  echo "✅ curl: $(curl --version | head -n1)"
else
  echo "❌ curl not found"
  exit 1
fi

# bc
if command -v bc &> /dev/null; then
  echo "✅ bc: $(bc --version | head -n1)"
else
  echo "❌ bc not found"
  echo "   Install: brew install bc"
  exit 1
fi

echo ""
echo "All dependencies satisfied!"
```

---

### Step 3: 디렉토리 생성

```bash
# .research 디렉토리 생성 (자동으로 생성되지만 미리 만들 수도 있음)
mkdir -p .research
mkdir -p .research/iteration_logs
mkdir -p .research/papers
```

---

### Step 4: 설정 확인

```bash
# config.json 유효성 검사
jq empty config.json && echo "✅ config.json valid" || echo "❌ config.json invalid"

# .claude/settings.json 유효성 검사
jq empty .claude/settings.json && echo "✅ settings.json valid" || echo "❌ settings.json invalid"
```

---

### Step 5: Stop Hook 권한 설정

```bash
# Python 스크립트 실행 권한
chmod +x .claude/hooks/stop-hook.py

# 테스트 실행
echo '{}' | python3 .claude/hooks/stop-hook.py
echo "Exit code: $?"
# 예상: Exit code 0 (state.json 없음)
```

---

## 설정 검증

### 설정 체크리스트

```bash
#!/bin/bash
# validate-setup.sh

echo "=========================================="
echo "Pathfinder Setup Validation"
echo "=========================================="

# 1. 디렉토리 구조
echo "1. Checking directory structure..."
dirs=(".claude" ".claude/hooks" ".claude/skills" ".research")
for dir in "${dirs[@]}"; do
  if [ -d "$dir" ]; then
    echo "  ✅ $dir"
  else
    echo "  ❌ $dir (missing)"
  fi
done

# 2. 필수 파일
echo ""
echo "2. Checking required files..."
files=(
  "config.json"
  ".claude/settings.json"
  ".claude/hooks/stop-hook.py"
  ".claude/skills/deep-research/SKILL.md"
  "research.sh"
)
for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✅ $file"
  else
    echo "  ❌ $file (missing)"
  fi
done

# 3. JSON 유효성
echo ""
echo "3. Validating JSON files..."
if jq empty config.json 2>/dev/null; then
  echo "  ✅ config.json"
else
  echo "  ❌ config.json (invalid)"
fi

if jq empty .claude/settings.json 2>/dev/null; then
  echo "  ✅ .claude/settings.json"
else
  echo "  ❌ .claude/settings.json (invalid)"
fi

# 4. Stop Hook 테스트
echo ""
echo "4. Testing Stop Hook..."
rm -f .research/state.json
result=$(echo '{}' | python3 .claude/hooks/stop-hook.py 2>&1)
exit_code=$?
if [ $exit_code -eq 0 ]; then
  echo "  ✅ Stop Hook (exit 0 when no state)"
else
  echo "  ❌ Stop Hook (expected 0, got $exit_code)"
fi

echo ""
echo "=========================================="
echo "Validation Complete"
echo "=========================================="
```

**실행:**
```bash
chmod +x validate-setup.sh
./validate-setup.sh
```

---

## 첫 실행

### Quick Start (테스트 실행)

```bash
# 짧은 테스트 (5 iterations, 10분, $1 예산)
./research.sh 5 "GPT-4란 무엇인가?"
```

**예상 동작:**

```
🔬 Starting Deep Research...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Iteration: 1/5
Budget: $0.00/$1.00
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[연구 진행...]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Iteration #1 완료
🔍 이번 발견:
   - ✓✓ GPT-4는 2023년 3월 14일 출시 (openai.com, techcrunch.com)
   - ✓ Transformer 아키텍처 기반 (arxiv.org)
...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### 결과 확인

```bash
# 상태 확인
cat .research/state.json | jq '.'

# 발견 사항 확인
cat .research/findings.md

# 비용 확인
cat .research/state.json | jq '.metrics.cost_estimate_usd'
```

---

### 문제 해결

**문제 1: "command not found: claude"**

```bash
# Claude Code 설치 확인
which claude

# 설치되지 않았다면
# https://claude.ai/download 에서 다운로드
```

---

**문제 2: "Permission denied: stop-hook.py"**

```bash
# 실행 권한 부여
chmod +x .claude/hooks/stop-hook.py

# Python 경로 확인
which python3
```

---

**문제 3: "state.json: No such file"**

```bash
# .research 디렉토리 생성
mkdir -p .research

# 다시 실행
./research.sh 5 "테스트 질문"
```

---

## 프로덕션 배포

### 설정 최적화

**config.prod.json:**

```json
{
  "version": "4.0",
  "loop_control": {
    "max_iterations": 100,
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
        "max_papers_per_query": 3
      },
      "verification": {"enabled": true}
    }
  },
  "cost_control": {
    "budget_per_session_usd": 10.0
  }
}
```

**적용:**

```bash
cp config.prod.json config.json
```

---

### 백업 전략

**자동 백업 스크립트:**

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR=".research_backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="research_${TIMESTAMP}"

mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/${BACKUP_NAME}.tar.gz" .research/

echo "Backup created: $BACKUP_DIR/${BACKUP_NAME}.tar.gz"

# 30일 이상 된 백업 삭제
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

**cron 설정 (매일 자동 백업):**

```bash
# crontab -e
0 2 * * * cd /path/to/pathfinder/forge && ./backup.sh
```

---

### 모니터링

**연구 진행 모니터링:**

```bash
# 실시간 상태 확인
watch -n 5 'cat .research/state.json | jq "{iteration: .iteration, status: .status, budget: .metrics.cost_estimate_usd}"'
```

**비용 모니터링:**

```bash
# 비용 알림 (80% 도달 시)
while true; do
  budget=$(jq '.metrics.cost_estimate_usd' .research/state.json 2>/dev/null || echo 0)
  limit=$(jq '.cost_control.budget_per_session_usd' config.json)

  threshold=$(echo "$limit * 0.8" | bc)

  if (( $(echo "$budget > $threshold" | bc -l) )); then
    echo "⚠️ Budget warning: \$$budget / \$$limit"
    # 알림 전송 (예: Slack, Email)
  fi

  sleep 60
done
```

---

### 로그 관리

**로그 로테이션:**

```bash
#!/bin/bash
# rotate-logs.sh

# iteration_logs 압축
cd .research/iteration_logs
tar -czf "logs_$(date +%Y%m%d).tar.gz" *.md
rm *.md

# papers 정리 (90일 이상)
cd ../papers
find . -name "*.pdf" -mtime +90 -delete
```

---

### 성능 튜닝

**고속 모드 (속도 우선):**

```json
{
  "search": {
    "parallel_count": 5,
    "strategies": {
      "web": {"enabled": true, "fetch_full_content": false},
      "academic": {"enabled": false},
      "verification": {"enabled": false}
    }
  }
}
```

**정확도 모드 (품질 우선):**

```json
{
  "search": {
    "parallel_count": 3,
    "strategies": {
      "web": {"enabled": true, "fetch_full_content": true},
      "academic": {
        "enabled": true,
        "max_papers_per_query": 5
      },
      "verification": {"enabled": true, "search_contradictions": true}
    }
  }
}
```

---

## 운영 체크리스트

### 일일 점검

- [ ] `.research/` 디렉토리 크기 확인 (< 1GB)
- [ ] 비용 누적 확인
- [ ] 에러 로그 확인
- [ ] 백업 상태 확인

### 주간 점검

- [ ] 이전 주 연구 결과 아카이빙
- [ ] 디스크 공간 확인
- [ ] 설정 최적화 검토
- [ ] Stop Hook 동작 테스트

### 월간 점검

- [ ] 전체 시스템 업데이트
- [ ] 비용 분석 및 예산 재조정
- [ ] 사용 패턴 분석
- [ ] 문서 업데이트

---

## 업그레이드 가이드

### v3.0 → v4.0 업그레이드

**주요 변경사항:**
- 서브에이전트 제거
- Stop Hook 개선
- config.json 구조 변경

**업그레이드 단계:**

```bash
# 1. 백업
cp -r .research .research.backup.v3
cp config.json config.json.v3.backup

# 2. 새 버전 다운로드
git pull origin master

# 3. config.json 마이그레이션
# (수동으로 설정 복사)

# 4. Stop Hook 업데이트
chmod +x .claude/hooks/stop-hook.py

# 5. 테스트
./validate-setup.sh
```

---

## 보안 고려사항

### API 키 관리

- ✅ Claude Code가 자동으로 API 키 관리
- ❌ `.env` 파일에 API 키 저장 금지
- ❌ git에 API 키 커밋 금지

---

### 권한 설정

```bash
# .research 디렉토리 권한
chmod 700 .research

# Stop Hook 실행 권한만
chmod 755 .claude/hooks/stop-hook.py
```

---

### .gitignore 설정

```gitignore
# .gitignore

# 연구 데이터 (민감 정보 포함 가능)
.research/
.research_backups/

# 임시 파일
*.tmp
tmp.json

# 환경 변수
.env
.env.local

# 백업
*.backup
*.tar.gz
```

---

**완료:** 프로덕션 배포 준비 완료
