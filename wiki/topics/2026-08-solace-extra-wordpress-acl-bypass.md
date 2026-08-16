---
slug: solace-extra-wordpress-acl-bypass
first_seen: 2026-08-16
tags: [WordPress, 권한상향, 플러그인취약점]
cves: [CVE-2026-18316]
---

# Solace Extra WordPress — 권한검증 우회 데이터 삭제·위변조

**Solace Extra** WordPress 플러그인 1.6.0 이하의 import_zip() 함수가 nonce만 검증하고 capability 체크 없이 wp_ajax_nopriv_에서 등록되어, Subscriber 이상 권한 사용자가 네비게이션 메뉴, 사이드바 위젯, 테마 설정, Elementor 템플릿을 대량 삭제·위변조 및 임의 데모 콘텐츠 임포트 가능.

## 타임라인

- 2026-08-16 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-18316) — CVE-2026-18316 CVSS 9.1 공개, 권한검증 부재로 인한 대규모 데이터 손상 가능 확인
