---
slug: chrome-150-security-patches
first_seen: 2026-07-08
tags: [Chrome, 브라우저, 샌드박스탈출, 메모리손상]
cves: [CVE-2026-15110, CVE-2026-15113, CVE-2026-15107, CVE-2026-15112, CVE-2026-15114, CVE-2026-15116, CVE-2026-15118, CVE-2026-15119, CVE-2026-15120, CVE-2026-15122, CVE-2026-15123, CVE-2026-15125, CVE-2026-15126, CVE-2026-15129, CVE-2026-15132, CVE-2026-15133]
---

# Google Chrome 150 중대 보안 패치

**Google Chrome** 150.0.7871.115 버전에서 10개의 중대 보안 취약점이 수정됨. 대부분 원격 공격자가 악의적 HTML 페이지로 트리거할 수 있는 메모리 손상 및 샌드박스 탈출 취약점. CVSS 8.3~8.8로 모두 높은 심각도.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15119) — CVE-2026-15119: Chrome GetUserMedia 레이스 컨디션 샌드박스 탈출
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15120) — CVE-2026-15120: Chrome Core 사용 후 해제 샌드박스 탈출
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15122) — CVE-2026-15122: Chrome Codecs 입력 검증 부재 샌드박스 탈출
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15123) — CVE-2026-15123: Chrome DOM 부적절한 구현 힙 손상
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15125) — CVE-2026-15125: Chrome Forms 부적절한 구현 샌드박스 내 임의 코드 실행
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15126) — CVE-2026-15126: Chrome Forms 사용 후 해제 샌드박스 내 임의 코드 실행
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15129) — CVE-2026-15129: Chrome Views 사용 후 해제 힙 손상 (Critical)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15133) — CVE-2026-15133: Chrome InterestGroups 사용 후 해제 샌드박스 내 임의 코드 실행
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15110) — CVE-2026-15110: Chrome Extensions 사용 후 해제 힙 손상
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15132) — CVE-2026-15132: Chrome V8 미초기화 사용 샌드박스 내 임의 코드 실행
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15113) — CVE-2026-15113: Chrome Android Autofill 사용 후 해제 샌드박스 탈출
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15107) — CVE-2026-15107: Chrome IndexedDB 사용 후 해제 샌드박스 내 임의 코드 실행
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15112) — CVE-2026-15112: Chrome Ozone 사용 후 해제 힙 손상 (Critical)
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15114) — CVE-2026-15114: Chrome Codecs 범위 초과 읽기/쓰기 힙 손상
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15116) — CVE-2026-15116: Chrome Actor 사용 후 해제 샌드박스 내 임의 코드 실행
- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-15118) — CVE-2026-15118: Chrome Input 사용 후 해제 샌드박스 내 임의 코드 실행
