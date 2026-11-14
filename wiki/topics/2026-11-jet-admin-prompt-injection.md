---
slug: jet-admin-prompt-injection
first_seen: 2026-11-13
tags: [AI보안, 환경변수유출, 자격증명탈취, 프롬프트주입]
cves: [CVE-2026-123965]
---

**Jet Admin** Cloud Platform의 모든 버전에서 프롬프트 주입 취약점으로 무료 계정 사용자가 .env 설정파일 노출 및 중요 자격증명(API 키, 데이터베이스 암호) 탈취 가능. 2026년 10월 29일 샌드박스 우회로 완화되었으나 공개 이전 장시간 악용 가능성.

## 타임라인

- 2026-10-29 [내부 리포트](https://nvd.nist.gov/vuln/detail/CVE-2026-123965) — Jet Admin 샌드박스 컴포넌트 완화 조치 적용
- 2026-11-13 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-123965) — CVE-2026-123965 Jet Admin 프롬프트 주입 취약점 공개 (CVSS 9.9)

## 관련

[[llmjacking]]
