---
slug: ctrlpanel-installer-rce
first_seen: 2026-05-19
tags: [RCE, 호스팅소프트웨어, 미인증공격]
cves: [CVE-2026-34234]
---

호스팅 제공자용 오픈소스 청구 소프트웨어 CtrlPanel 1.1.1 이하에서 설치 프로그램 잠금 검증 우회로 인증 없이 명령을 실행할 수 있는 원격코드 실행 취약점이 발견됐다. CVSS 10.0이며 이미 야생에서 적극 악용 중이다.

## 타임라인
- 2026-05-19 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34234) — CVE-2026-34234 공개, 취약점 분석 및 1.2.0 패치 발표

## 기술 상세
설치 프로그램(`public/installer/index.php`)이 `install.lock` 파일 검증을 하기 전에 폼 핸들러 파일을 포함 및 실행하므로 설치 완료된 서버에서도 설치 엔드포인트에 접근 가능하다. 핸들러가 사용자 입력을 적절히 검증하지 않아 셸 명령에 직접 전달되므로 공격자가 임의 명령을 실행할 수 있다.

## 관련
[[microsoft-july-patch-tuesday]]
