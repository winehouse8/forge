# 🐰 Rabbit-Hole

심층 연구 자동화 에이전트

## 실행

```bash
# 새 연구 시작
./rabbit-hole.sh "연구하고 싶은 질문"

# 이어하기
./rabbit-hole.sh --resume
```

## 결과 확인

```bash
# 지식 맵
cat .research/current/summary.md

# 보고서 생성
./rh-report.sh
```

## 중단/재개

- `Ctrl+C` 로 중단
- `./rabbit-hole.sh --resume` 로 재개
