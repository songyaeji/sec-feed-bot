---
slug: claude-code-dont-ask-again-leak
first_seen: 2026-11-07
tags: [Anthropic, APIkey노출, 개발자보안, 설정파일]
cves: []
---

**Anthropic**의 **Claude Code** 개발 도구에서 '다시 묻지 않음' 옵션으로 승인한 명령이 **API 키**·**비밀번호** 포함 평문 상태로 프로젝트 설정 파일에 저장되어 **GitHub**에 노출된 사건. **1,122개 공개 저장소**에서 민감 정보가 접근 가능했다.

## 타임라인

- 2026-11-07 [The Hacker News](https://thehackernews.com/2026/11/claude-codes-dont-ask-again-file.html) — **Apiiro** 발견, **Claude Code** 승인 명령의 **평문 저장** 취약점, **1,122개 GitHub 저장소** 노출, **API 키**·**비밀번호** 탈취 위험

## 관련
