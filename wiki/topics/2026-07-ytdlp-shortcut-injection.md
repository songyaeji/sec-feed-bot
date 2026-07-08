---
slug: ytdlp-shortcut-injection
first_seen: 2026-07-08
tags: [명령어삽입, 영상다운로더]
cves: [CVE-2026-55404]
---

**yt-dlp**와 **youtube-dl**의 `--write-link`, `--write-url-link`, `--write-desktop-link` 옵션이 메타데이터를 충분히 검증하지 않아, 공격자 제어 URL이나 파일명으로 .url/.desktop 단축파일 생성 시 명령어 삽입이 가능한 취약점. 2026.7.4 이상에서 수정됐다.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-55404) — CVE-2026-55404 공개 (CVSS 7.5)
