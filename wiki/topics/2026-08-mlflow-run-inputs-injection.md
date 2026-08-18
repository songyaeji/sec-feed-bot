---
slug: mlflow-run-inputs-injection
first_seen: 2026-08-17
tags: [권한검증우회, AI플랫폼, 데이터조작]
cves: [CVE-2026-69146]
---

# MLflow — 실행 입력 메타데이터 권한 검증 우회

AI 엔지니어링 플랫폼 **MLflow** 3.13.0~3.15.0 버전에서 LogInputs가 BEFORE_REQUEST_HANDLERS에 빠져 있다. 인증된 모든 사용자가 다른 사용자의 run_id로 POST /api/2.0/mlflow/runs/log-inputs을 호출하여 필수 UPDATE 권한 없이 임의로 DatasetInput 레코드를 데이터셋 라니지(lineage) 메타데이터에 주입할 수 있다. 데이터 출처 추적 정보 조작으로 감시 회피 가능.

## 타임라인

- 2026-08-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-69146) — CVE-2026-69146 CVSS 6.5 공개, 크로스 사용자 run-inputs 메타데이터 주입 취약점 확인
