---
slug: claude-code-sandbox-symlink
first_seen: 2026-04-21
tags: [AI코딩에이전트, 샌드박스탈출, symlink, 권한상향]
cves: [CVE-2026-39861]
---

Claude Code v2.1.64 이전 버전에서 샌드박스 프로세스가 워크스페이스 외부를 향하는 symlink 생성 가능. 샌드박스 해제 프로세스가 symlink를 따라가 사용자 확인 없이 임의 위치에 파일 쓰기 가능. 신뢰할 수 없는 콘텐츠로 prompt injection 트리거 필요.

## 타임라인

- 2026-04-21 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-39861) — CVE-2026-39861 공개 (CVSS 10.0, v2.1.64 이상에서 패치)

## 관련

[[ghostapproval-ai-agent-symlink]]
