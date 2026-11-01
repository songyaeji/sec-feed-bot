---
slug: beta9-worker-rce
first_seen: 2026-11-01
tags: [컨테이너보안, RCE, 멀티테넌트]
cves: [CVE-2026-120306, CVE-2026-120307]
---

클라우드 컴퓨팅 플랫폼 **Beta9** 빌드 워커에서 두 개 취약점으로 테넌트 격리 우회 가능하다. Buildah OCI 격리 미흡으로 PID 네임스페이스 공유, 파일시스템 접근 우회로 다른 테넌트 파일과 쿠버네티스 토큰 접근 가능. 0.1.756에서 수정됨.

## 타임라인

- 2026-11-01 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-120306) — CVE-2026-120306 CVSS 9.9 Buildah OCI 격리 우회 (0.1.756 패치)
- 2026-11-01 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-120307) — CVE-2026-120307 CVSS 9.9 파일 시스템 접근 우회 심링크 추적 미흡

## 관련

[[vm2-sandbox-breakout]]
