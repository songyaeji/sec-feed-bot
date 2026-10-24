---
slug: dgraph-unauthenticated-rce
first_seen: 2026-04-06
tags: [GraphQL, 데이터베이스, 미인증RCE]
cves: [CVE-2026-34976]
---

**Dgraph** 오픈소스 분산 GraphQL 데이터베이스의 restoreTenant 관리자 뮤테이션이 인증 미들웨어에서 누락되어 완전히 미인증 상태. 공격자가 임의 백업 소스 URL(로컬 파일시스템 포함), S3/MinIO 자격증명, 암호화 키 파일 경로, Vault 자격증명 파일 경로를 제어하여 전체 데이터베이스 덮어쓰기, 서버 파일 읽기, SSRF 공격 가능. 패치: 25.3.1

## 타임라인

- 2026-04-06 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34976) — CVE-2026-34976 공개, Dgraph 25.3.1 이전 버전 영향

## 관련
