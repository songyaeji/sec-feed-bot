---
slug: streambert-electron-ipc
first_seen: 2026-08-11
tags: [Electron, 권한상향, 경로검증]
cves: [CVE-2026-48056]
---

**Streambert** 영상 스트리밍 데스크톱 앱 2.5.0 이전 버전에서 IPC 핸들러의 실행 경로 검증이 부족해, 손상된 렌더러 프로세스가 앱 권한으로 임의 바이너리를 실행할 수 있다. CVSS 10.0의 권한상향 취약점이다.

## 타임라인

- 2026-08-11 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-48056) — CVE-2026-48056 공개 (CVSS 10.0, Electron IPC 경로 검증 우회)
