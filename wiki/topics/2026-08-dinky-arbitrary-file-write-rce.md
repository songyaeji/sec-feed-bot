---
slug: dinky-arbitrary-file-write-rce
first_seen: 2026-08-06
tags: [원격코드실행, 기본설정취약점, 빅데이터인프라]
cves: [CVE-2026-70558]
---

데이터 파이프라인 오케스트레이션 도구 **Dinky** v1.2.5의 POST /download/uploadFromRsByLocal 
핸들러에서 경로 검증 없이 파일을 쓸 수 있다. 기본값 토큰(efda1551-7958-4e0f-80a8-dfd107df3e38)이 
소스코드에 하드코드되어 있어 공격자가 HTTP 포트 8888에 접근하면 classpath 파일 변조로 
Flink 서비스 계정 권한 **RCE**를 달성할 수 있다. CVSS 9.8.

## 타임라인

- 2026-08-06 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-70558) — CVE-2026-70558 공개, Dinky v1.2.5 및 개발 브랜치 영향 확인

## 관련

[[fastjson-rce-zero-day]]
