---
slug: mozilla-linux-signing-key-compromise
first_seen: 2026-08-11
tags: [Mozilla, Firefox, Thunderbird, 배포서명, 공급망보안]
cves: []
---

**Mozilla**가 Linux용 **Firefox**·**Thunderbird** 다운로드 서명에 쓰는 **GPG 암호화 키**를 폐기했다. 개발자가 실수로 비암호화 상태의 키를 회사의 비공개 코드 저장소에 커밋한 후 신뢰성이 손상되었으며, 새 서명 키로 전환하는 과정에서 배포판 무결성 검증 절차에 일시적 영향이 생겼다.

## 타임라인

- 2026-08-11 [The Hacker News](https://thehackernews.com/2026/08/mozilla-revokes-firefox-and-thunderbird.html) — Mozilla가 Linux 서명 키 폐기 및 키 노출 경위 공개
- 2026-08-11 [BleepingComputer](https://www.bleepingcomputer.com/news/security/mozilla-updates-gpg-key-for-signing-firefox-thunderbird-releases-after-exposure/) — Mozilla GPG 키 업데이트 및 새 서명 체계 전환

## 관련
