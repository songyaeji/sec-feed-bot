---
slug: mariadb-rce
first_seen: 2026-08-03
tags: [데이터베이스, RCE, 갈레라클러스터, 원격코드실행, 크리티컬]
cves: [CVE-2026-49261, CVE-2026-85746, CVE-2026-85748, CVE-2026-92262]
---

# MariaDB wsrep_notify_cmd 원격코드실행

MariaDB 커뮤니티 포크의 여러 버전에서 **wsrep_notify_cmd** 설정 활성화 시 노드 이름에 포함된 셸 명령이 직접 실행되는 원격코드실행(RCE) 취약점이 발견되었다. CVSS 10.0의 심각한 취약점으로, Galera 클러스터 환경에서 악의적 노드 가입으로 악용 가능하다. 패치된 버전으로 업그레이드하거나 wsrep_notify_cmd를 비활성화하여 완화 가능하다.

## 타임라인

- 2026-06-11 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-49261) — CVE-2026-49261 공개 (CVSS 10.0, 영향받는 버전: 10.6.1~10.6.26, 10.11.1~10.11.17, 11.4.1~11.4.11, 11.8.1~11.8.7, 12.3.1)
- 2026-10-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-85746) — CVE-2026-85746: ST_AsText 버퍼 오버플로우, 깊게 중첩된 GeometryCollections 처리 시 메모리 손상 (CVSS 9.9)
- 2026-10-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-85748) — CVE-2026-85748: SYS_REFCURSOR 처리 use-after-free, 다량의 커서 열기 후 페치 시 RCE 가능 (CVSS 9.9)
- 2026-10-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-92262) — CVE-2026-92262: #mysql50# 접두사 바이패스로 테이블명 인코딩 우회, 파일 접근·손상·유출·RCE 가능 (CVSS 9.9)

## 관련

없음
