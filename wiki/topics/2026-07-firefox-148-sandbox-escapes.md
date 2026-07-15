---
slug: firefox-148-sandbox-escapes
first_seen: 2026-07-15
tags: [브라우저취약점, 샌드박스탈출, RCE]
cves: [CVE-2026-2760, CVE-2026-2761, CVE-2026-2768, CVE-2026-2776, CVE-2026-2778]
---

**Firefox 148** 및 **Thunderbird 148** 보안 업데이트에서 5개의 중대한 샌드박스 탈출 취약점이 수정되었다. Graphics(WebRender), Storage(IndexedDB), Telemetry, DOM Core 컴포넌트의 경계 조건 오류로 인해 공격자가 브라우저 샌드박스를 벗어나 시스템 권한으로 임의 코드 실행이 가능했다.

## 타임라인

- 2026-02-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-2760) — Firefox 148/ESR 115.33/140.8, Thunderbird 148/140.8에서 5개 샌드박스 탈출 취약점 수정
  - CVE-2026-2760: Graphics WebRender 경계 조건
  - CVE-2026-2761: Graphics WebRender 오류
  - CVE-2026-2768: Storage IndexedDB 샌드박스 탈출
  - CVE-2026-2776: Telemetry External Software 경계 조건
  - CVE-2026-2778: DOM Core & HTML 경계 조건

## 관련

[[mozilla-firefox-security]]
