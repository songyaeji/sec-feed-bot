---
slug: tenable-security-center-multi-rce
first_seen: 2026-08-14
tags: [원격코드실행, 보안솔루션, 명령주입]
cves: [CVE-2026-19626, CVE-2026-19681, CVE-2026-19682]
---

# Tenable Security Center 다중 RCE·명령주입 취약점

**Tenable** **Security Center** 소프트웨어에서 2026-08-14에 **3개의 중대한 원격코드실행(RCE) 및 명령주입 취약점**이 동시에 공개됐다. 보고서 생성 기능의 입력값 검증 부족(CVE-2026-19626), 파일 업로드 처리 로직의 명령주입(CVE-2026-19681), 그리고 가장 심각한 **미인증 사용자의 명령주입**(CVE-2026-19682)으로 공격자가 서비스 계정 권한의 OS 명령을 실행할 수 있다.

## 타임라인

- 2026-08-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-19626) — CVE-2026-19626 Tenable Security Center report generation RCE 공개 (CVSS 9.9)
- 2026-08-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-19681) — CVE-2026-19681 Tenable Security Center file upload command injection 공개 (CVSS 9.9)
- 2026-08-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-19682) — CVE-2026-19682 Tenable Security Center unauthenticated command injection 공개 (CVSS 9.9)

## 관련
