---
name: research-report
description: 현재까지의 연구 결과를 종합한 보고서를 생성합니다.
---

# Research Report Generator

현재까지의 연구 결과를 종합한 보고서를 생성합니다.

## 지침

1. 다음 파일들을 읽습니다:
   - `.research/state.json`
   - `.research/findings.md`
   - `.research/hypotheses.md`
   - `.research/sources.md`
   - `.research/knowledge_graph.json`

2. `RESEARCH_REPORT.md` 파일을 생성/업데이트합니다

## 보고서 형식

```markdown
# Research Report

**생성일**: [날짜]
**연구 질문**: [원본 질문]
**총 Iterations**: N

---

## Executive Summary

[1-2 문단으로 핵심 발견 요약]

---

## 주요 발견

### 확인된 사실 (Verified)

1. [사실 1] ✓✓
   - 소스: [URL1], [URL2]
   - 신뢰도: 0.95

2. [사실 2] ✓✓
   - 소스: [URL3]
   - 신뢰도: 0.90

### 가능성 높음 (Likely)

1. [주장 1] ~
   - 소스: [URL4]
   - 신뢰도: 0.70

### 불확실 (Uncertain)

1. [주장 2] ?
   - 추가 조사 필요

---

## 가설 분석

### 현재 가설

**[가설 내용]**

- 확신도: N%
- 지지 증거: M개
- 반증 증거: K개

#### 지지 증거
1. [증거 1] - [소스]
2. [증거 2] - [소스]

#### 반증 증거
1. [증거 1] - [소스]

### 가설 진화 과정
- v1 (Iteration 1): [초기 가설]
- v2 (Iteration 3): [수정된 가설]
- v3 (Iteration 7): [현재 가설]

---

## 지식 그래프 요약

- 총 개념: N개
- 총 관계: M개
- 발견된 모순: K개

### 핵심 개념
1. [개념 1]
2. [개념 2]
3. [개념 3]

---

## 참고 자료

### 학술 자료
1. [논문 제목] - [저자] ([년도])
   - URL: [링크]
   - 핵심 인용: "[인용문]"

### 웹 자료
1. [제목] - [도메인]
   - URL: [링크]
   - 신뢰도: X.XX

---

## 한계점 및 추가 연구 방향

### 한계점
- [한계 1]
- [한계 2]

### 추가 연구 방향
- [방향 1]
- [방향 2]

---

## 메트릭

- 총 검색: N회
- 총 Iterations: M회
- 확인된 사실: K개
- 예상 비용: $X.XX
- 총 소요 시간: [추정]

---

*이 보고서는 Deep Research Skill v4에 의해 자동 생성되었습니다.*
```

## 파일이 없는 경우

연구 데이터가 없으면:

```
ℹ️  보고서를 생성할 연구 데이터가 없습니다.
   먼저 연구를 시작하세요: /deep-research [질문]
```
