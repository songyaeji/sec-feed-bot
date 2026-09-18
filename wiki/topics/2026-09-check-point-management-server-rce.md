---
slug: check-point-management-server-rce
first_seen: 2026-09-17
tags: [원격코드실행, 인증우회, 네트워크보안]
cves: []
---

**Check Point** Security Management Server·Log Server에 미인증 공격자가 루트 권한으로 임의 코드를 실행할 수 있는 중대 취약점 발견. 해당 서버는 방화벽 정책 및 관리자 접근 제어를 담당하는 핵심 인프라로, 성공적 공격 시 네트워크 보안 전체가 위협된다. Check Point는 **LivePatch** 업데이트 채널을 통해 수정안을 배포했으며 현재까지 악용 사례는 없다고 발표했다.

## 타임라인

- 2026-09-17 [The Hacker News](https://thehackernews.com/2026/09/critical-check-point-management-server.html) — Check Point 방화벽 Management Server 미인증 원격코드실행 취약점 공개, LivePatch 수정 배포
- 2026-09-18 [Security Affairs](https://securityaffairs.com/199279/security/check-point-fixes-critical-cve-2026-91843-allowing-root-code-execution.html) — CVE-2026-91843 공식 공지 CVSS 9.8 비인증 루트 권한 코드실행

## 관련
