---
slug: mattermost-board-privilege-escalation
first_seen: 2026-08-17
tags: [권한상승, 협업플랫폼, 권한검증우회]
cves: [CVE-2026-9816]
---

# Mattermost — 보드 멤버 권한 검증 우회

협업 플랫폼 **Mattermost** 11.7.6, 10.11.21, 11.8.3 이전 버전에서 BoardMember.Scheme* 필드에 대한 서버 측 검증이 부족하다. POST /api/v2/boards/{boardID}/members와 POST /api/v2/teams/{teamID}/archive/import 경로에서 보드 편집자 또는 게스트가 아닌 팀 멤버가 임의 사용자에게 보드 관리자 권한을 부여할 수 있다. 권한 검증이 삽입·아카이브 복원 경로에서 모두 우회되어 권한 상승 가능.

## 타임라인

- 2026-08-17 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-9816) — CVE-2026-9816 CVSS 8.3 공개, 보드 멤버 권한 검증 우회 (Mattermost Advisory MMSA-2026-00685)
