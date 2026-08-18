---
slug: mlflow-ssrf-webhook-test
first_seen: 2026-08-17
tags: [SSRF, AI플랫폼, 내부서비스, 정보유출]
cves: [CVE-2026-64849]
---

# MLflow — 웹훅 테스트 SSRF 내부 서비스 접근

AI 엔지니어링 플랫폼 **MLflow** 3.15.0 이전 버전의 인증 없는 POST /api/2.0/mlflow/webhooks/{id}/test 엔드포인트에서 SSRF 취약점이 발견됐다. _validate_webhook_url()은 원본 URL만 검증하지만 mlflow/webhooks/delivery.py에서 리다이렉트를 따르고 호스트명을 다시 해석하면서 검증된 주소 고정이 없다. 공격자가 내부 또는 클라우드 메타데이터 서비스에 접근해 응답 상태코드와 본문을 탈취 가능.

## 타임라인

- 2026-08-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-64849) — CVE-2026-64849 CVSS 9.3 공개, 웹훅 테스트 SSRF 취약점 확인
