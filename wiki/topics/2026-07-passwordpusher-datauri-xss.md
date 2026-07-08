---
slug: passwordpusher-datauri-xss
first_seen: 2026-07-08
tags: [XSS, 피싱, 자격증명탈취]
cves: [CVE-2026-59802]
---

**PasswordPusher** 2.8.1 이전의 안전한 비밀번호 공유 도구가 URL push 페이로드의 `webpage_url` 필드에서 데이터 URI 스킴(`data:text/html`)을 검증하지 않아, 공격자가 임의 JavaScript를 실행하는 **XSS**를 할 수 있는 취약점. 피해자가 공유 링크를 클릭하면 자격증명 탈취나 피싱이 가능하다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-59802) — CVE-2026-59802 공개 (CVSS 8.2)
