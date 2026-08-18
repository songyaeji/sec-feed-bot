---
slug: ray-project-code-injection
first_seen: 2026-08-17
tags: [Ray, 코드인젝션, RCE, ML프레임워크]
cves: [CVE-2025-62593]
---

# Ray 프로젝트 — 코드 인젝션 원격실행

분산 계산 프레임워크 **Ray**에서 개발 도구로 사용 중인 시스템이 코드 인젝션을 통해 원격코드 실행에 노출됨. Firefox/Safari를 통한 공격이 가능하며, ML 개발 도구체인 보안 위험.

## 타임라인

- 2026-08-17 [CISA KEV](https://nvd.nist.gov/vuln/detail/CVE-2025-62593) — CVE-2025-62593 공개 원격코드실행 취약점
- 2026-08-18 [The Hacker News](https://thehackernews.com/2026/08/cisa-flags-actively-exploited-ray-flaw.html) — CISA 공개 악용 목록(KEV)에 등재 확인
