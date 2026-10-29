---
slug: avideo-livestream-rce
first_seen: 2026-10-28
tags: [AVideo, 라이브스트리밍, 원격코드실행, 명령인젝션]
cves: [CVE-2026-61567]
---

AVideo 8.1.0 이전 버전의 `/view/videosListToLive.php` 라이브 스트리밍 엔드포인트에서 미인증 원격 공격자가 비디오 목록 응답을 조작해 ffmpeg/ffprobe 명령에 인젝션함으로써 OS 명령을 실행할 수 있다. CVSS 10.0으로 스트리머 화이트리스트 검증을 우회하고 데이터베이스 자격증명도 탈취 가능하다.

## 타임라인

- 2026-10-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-61567) — CVE-2026-61567 공개 (CVSS 10.0), 라이브 스트리밍 엔드포인트 명령 인젝션

## 관련

[[avideo-installation-rce]]
