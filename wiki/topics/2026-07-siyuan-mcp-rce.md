---
slug: siyuan-mcp-rce
first_seen: 2026-07-25
tags: [RCE, MCP, 미인증접근]
cves: [CVE-2026-66012]
---

# SiYuan MCP 미인증 원격명령실행

Publish 서버가 익명 모드로 활성화된 SiYuan에서 /mcp 엔드포인트의 접근 제어가 부족해 원격 인증 없이 31개 MCP 도구를 조작 가능. 파일 읽쓰기·삭제·이름변경으로 workspace 전체 접근 가능하며, conf.json에서 accessAuthCode·api.token·cookieKey를 평문 추출해 데스크톱 관리자 권한 탈취 가능.

## 타임라인

- 2026-07-25 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-66012) — CVE-2026-66012 공개 (CVSS 10.0)

## 관련

없음
