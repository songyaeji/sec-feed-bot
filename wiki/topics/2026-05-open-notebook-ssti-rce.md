---
slug: open-notebook-ssti-rce
first_seen: 2026-05-07
tags: [노트북, SSTI, 템플릿인젝션, Python, Docker]
cves: [CVE-2026-33587]
---

# Open Notebook — 서버 측 템플릿 인젝션 RCE

Open Notebook v1.8.3에서 사용자 정의 변환(transformation) 생성 시 입력 검증이 부족해 서버 측 템플릿 인젝션(SSTI) 취약점이 발생한다. 애플리케이션 사용자가 Python 코드를 직접 실행하고 Docker 컨테이너에서 OS 명령을 실행할 수 있다.

## 타임라인

- 2026-05-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-33587) — CVE-2026-33587 공개, CVSS 10.0

## 관련
