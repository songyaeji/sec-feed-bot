---
slug: mindsdb-ai-agent-rce
first_seen: 2026-08-14
tags: [AI에이전트, 미인증접근, 원격코드실행, CVSS10.0]
cves: [CVE-2026-73678]
---

# MindsDB AI 에이전트 미인증 원격코드실행

**MindsDB** 플랫폼 v26.1.0 이하의 **Anton** AI 에이전트에서 사용자 입력을 검증 없이 Python 코드로 실행하는 **scratchpad 도구** 취약점으로, 미인증 공격자가 원격코드실행에 성공할 수 있다. 공격자는 미인증 PUT /api/v1/settings/ 엔드포인트로 LLM API 키를 설정하고 POST /api/v1/responses/로 악의적 프롬프트를 전송해 데스크톱 애플리케이션 사용자 권한으로 OS 명령을 실행하며 SSH 키·저장된 자격증명·환경 시크릿을 탈취할 수 있다.

## 타임라인

- 2026-08-14 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-73678) — CVE-2026-73678 MindsDB Minds Platform scratchpad exec() RCE 공개 (CVSS 10.0)

## 관련

[[mcp-server-ai-exfiltration]] — AI 에이전트 정보탈취
