---
slug: apache-airflow-celeryexecutor-rce
first_seen: 2026-11-13
tags: [원격코드실행, 인증우회, Celery, 워크플로우자동화]
cves: [CVE-2026-68982]
---

**Apache Airflow** CeleryExecutor의 deadline-alert 콜백 기능이 작업 인증 토큰을 검증하지 않아 Celery 브로커에 접근 가능한 공격자가 위조 콜백을 등록해 모든 **CeleryExecutor 워커**에서 Airflow 자격증명 없이 임의 코드 실행 가능. 영향받는 배포는 3.4.0 이상으로 즉시 업그레이드 필수.

## 타임라인

- 2026-11-09 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-68982) — CVE-2026-68982 Apache Airflow CeleryExecutor 콜백 토큰 미검증 RCE 공개 (CVSS 9.8)

## 관련
