---
slug: avideo-installation-rce
first_seen: 2026-10-28
tags: [AVideo, 설치프로세스, 원격코드실행, 미인증]
cves: [CVE-2026-61564]
---

AVideo 8.1.0 이전 버전의 미인증 설치 엔드포인트 `/install/checkConfiguration.php`에서 요청 매개변수를 PHP 문자열에 직접 삽입해 임의 코드 실행이 가능하다. CVSS 10.0으로 신규 배포 또는 파일 제거 후 악용되며 데이터베이스 연결 설정까지 탈취할 수 있다.

## 타임라인

- 2026-10-28 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-61564) — CVE-2026-61564 공개 (CVSS 10.0), 설치 엔드포인트 PHP 인젝션

## 관련

[[avideo-livestream-rce]]
