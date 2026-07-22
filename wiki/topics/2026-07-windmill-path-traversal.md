---
slug: windmill-path-traversal
first_seen: 2026-07-22
tags: [제로데이, 경로순회, 오픈소스, 공공악용]
cves: [CVE-2026-29059]
---

오픈소스 개발자 플랫폼 **Windmill**의 경로 순회 취약점이 야생에서 실제 악용 중이다. `/api/w/{workspace}/jobs_u/get_log_file/{filename}` 엔드포인트의 필터링 부족으로 인증 없이 임의 서버 파일에 접근 가능하며, 공급망 공격 진입점이 될 수 있다.

## 타임라인

- 2026-07-22 [The Hacker News](https://thehackernews.com/2026/07/hackers-exploit-windmill-flaw-to-read.html) — CVE-2026-29059: Windmill 미인증 경로 순회 취약점 야생 악용 확인 (CVSS 7.5)

## 관련
