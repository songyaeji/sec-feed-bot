---
slug: crawl4ai-docker-rce
first_seen: 2026-07-06
tags: [AI도구, LLM파이프라인, 컨테이너보안, RCE]
cves: [CVE-2026-57572]
---

LLM 친화 웹 크롤러 **Crawl4AI** 0.9.0 이전의 Docker API 서버가 요청 기반 Chromium 스위치를 검증 없이 전달해 --no-zygote 스위치로 자식 프로세스 포크/실행 명령 치환 공격을 허용한다. 기본 미인증 상태에서 컨테이너 런타임 사용자 권한으로 임의 명령 실행 가능.

## 타임라인

- 2026-07-06 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-57572) — CVE-2026-57572 공개, CVSS 10.0, Docker API 미인증 명령 주입
