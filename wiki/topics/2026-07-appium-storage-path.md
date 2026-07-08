---
slug: appium-storage-path
first_seen: 2026-07-08
tags: [경로순회, 테스트자동화]
cves: [CVE-2026-58192]
---

**Appium** 자동화 프레임워크 1.1.6 이전 버전의 저장소 플러그인이 POST `/storage/delete` 핸들러에서 사용자 제공 name을 검증하지 않고 `path.join(storageRoot, name)` 및 `fs.rimraf()`에 직접 전달하여, 공격자가 경로 순회로 임의 디렉터리를 삭제할 수 있는 취약점.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-58192) — CVE-2026-58192 공개 (CVSS 8.6)
