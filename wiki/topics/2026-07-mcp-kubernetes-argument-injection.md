---
slug: mcp-kubernetes-argument-injection
first_seen: 2026-07-10
tags: [권한상향, 클러스터손상, 인프라, 원격코드실행]
cves: [CVE-2026-61459]
---

**MCP Server Kubernetes** < 3.9.0의 argument injection 취약점. kubectl 구조화 도구(`kubectl_get`, `kubectl_describe`, `kubectl_delete`)에서 `resourceType`과 `name` 파라미터 앞의 대시(`-`) 유효성 검증 부재. 공격자가 `--server` 플래그를 삽입해 kubectl 명령을 공격자 제어 API 서버로 리다이렉트. **결과: 클러스터 운영자의 bearer 토큰 탈취 및 전체 클러스터 손상** (CVSS 9.8).

## 타임라인

- 2026-07-10 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-61459) — CVE-2026-61459 공개

## 관련
