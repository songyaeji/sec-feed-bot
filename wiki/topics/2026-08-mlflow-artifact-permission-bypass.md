---
slug: mlflow-artifact-permission-bypass
first_seen: 2026-08-17
tags: [권한검증우회, AI플랫폼, 데이터유출]
cves: [CVE-2026-69148]
---

# MLflow — 아티팩트 권한 검증 우회

AI 엔지니어링 플랫폼 **MLflow** 3.15.0 이전 버전의 CreateModelVersion 엔드포인트에서 권한 검증이 불완전하다. _validate_source_run()과 _validate_source_model()이 경로 포함만 검증하고 다른 사용자의 아티팩트 디렉터리를 참조하는 모델 버전을 생성할 수 있다. 인증된 사용자가 GET /model-versions/get-artifact를 통해 필수 READ 권한 없이 다른 사용자의 파일에 접근 가능.

## 타임라인

- 2026-08-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-69148) — CVE-2026-69148 CVSS 7.1 공개, 크로스 사용자 아티팩트 접근 권한 검증 우회 확인
