---
slug: coolify-rce
first_seen: 2026-07-07
tags: [RCE, Livewire, 인증우회, 쉘인젝션]
cves: [CVE-2026-34037, CVE-2026-34047, CVE-2026-34048, CVE-2026-34034, CVE-2026-34035, CVE-2026-34057, CVE-2026-34058, CVE-2026-34152, CVE-2026-34168, CVE-2026-34171, CVE-2026-42143, CVE-2026-42200]
---

# Coolify 서버 관리 도구: 12개 중대 RCE 취약점

오픈소스 서버·데이터베이스 관리 도구 Coolify에서 발견된 12개 높은 심각도 원격코드실행(RCE) 취약점. Livewire 컴포넌트 인증 부족, 쉘 명령어 인젝션, 스코프 없는 리소스 조회 등으로 인증된 사용자 및 낮은 권한 팀 멤버가 서버 전체를 장악할 수 있음.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34037) — CVE-2026-34037 (CVSS 9.9): cloneTo() Livewire 액션에서 스코프 없는 Eloquent 조회로 인증된 사용자가 임의 리소스 복제
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34047) — CVE-2026-34047 (CVSS 9.9): 터미널 WebSocket 부트스트랩 라우트 인증 미강제로 범위 외 리소스 접근
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34048) — CVE-2026-34048 (CVSS 9.9): 터미널 WebSocket 인증만 검증하고 권한 검증 부재로 저권한 멤버가 터미널 접근
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34034) — CVE-2026-34034 (CVSS 8.8): sentinel_token 설정이 쉘 명령어에 검증 없이 사용되어 쉘 문법 인젝션
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34035) — CVE-2026-34035 (CVSS 8.8): 로그 드레인 시크릿과 환경변수가 쉘 인코딩 없이 명령어에 삽입됨
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34057) — CVE-2026-34057 (CVSS 8.8): 데이터베이스 import Livewire 컴포넌트가 클라이언트 제어 컨테이너·서버 속성을 쉘 명령어에 직접 전달
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34058) — CVE-2026-34058 (CVSS 8.8): Server Resources Livewire 컴포넌트의 공개 메서드가 브라우저에서 직접 컨테이너 ID 파라미터 수락
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34152) — CVE-2026-34152 (CVSS 8.8): 배포 전·후 명령어가 단일따옴표 이스케이프만 하고 SSH heredoc 전송으로 개행 보존되어 인젝션
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34168) — CVE-2026-34168 (CVSS 8.8): LocalPersistentVolume.name이 도커 볼륨 쉘 명령어에 이스케이프 없이 삽입
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-34171) — CVE-2026-34171 (CVSS 8.0): GET /invitations/{uuid} 엔드포인트가 인증 없는 CSRF로 비밀번호 재설정
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-42143) — CVE-2026-42143 (CVSS 8.8): 사용자 제어 볼륨명이 관리 서버 쉘 명령어에 이스케이프·검증 없이 삽입
- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-42200) — CVE-2026-42200 (CVSS 8.8): PostgreSQL 초기화 스크립트 파일명 처리가 경로 제한 부족으로 path traversal

## 관련

[[gitea-docker-auth-bypass]] [[adobe-coldfusion-rce]]
