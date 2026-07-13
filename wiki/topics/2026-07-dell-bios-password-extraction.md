---
slug: dell-bios-password-extraction
first_seen: 2026-07-11
tags: [Dell, BIOS, 물리보안]
cves: [CVE-2026-40639]
---

Dell의 특정 클라이언트 플랫폼에서 BIOS 암호를 평문으로 추출할 수 있는 취약점이 발견되었다. DVAR 설정 저장소와 SystemPwSmm SMM 드라이버의 결함으로 인해 물리 접근만으로 SPI 플래시 덤프에서 관리자/사용자 암호를 밀리초 내에 복구할 수 있다. BIOS 인증 우회는 시스템 복구 경로 장악으로 이어질 수 있다.

## 타임라인

- 2026-07-11 [GBHackers](https://gbhackers.com/dell-bios-flaw-extract-plaintext-password-brute-force/) — Dell BIOS CVE-2026-40639 평문 패스워드 추출 취약점, DSA-2026-197 패치
