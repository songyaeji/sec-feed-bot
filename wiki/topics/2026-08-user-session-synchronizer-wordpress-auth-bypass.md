---
slug: user-session-synchronizer-wordpress-auth-bypass
first_seen: 2026-08-15
tags: [WordPress, 인증우회, 플러그인, 암호화오류]
cves: [CVE-2026-15341]
---

User Session Synchronizer WordPress 플러그인 1.4.0 이하에서 synchronize_session() 함수가 매 요청마다 실행되며, AES-256-CBC 암호화 키 생성 실패로 키가 md5('') 같은 예측 불가능한 값으로 저장되어 미인증 사용자가 임의 사용자(관리자 포함)로 로그인 가능. CVSS 9.8.

## 타임라인

- 2026-08-15 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15341) — CVE-2026-15341 공개, 암호화 키 생성 오류로 미인증 계정 탈취 취약점 확인
