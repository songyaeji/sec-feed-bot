---
slug: joyfill-npm-devpopper-rat
first_seen: 2026-07-29
tags: [npm, 공급망, 악성코드, RAT]
cves: []
---

npm 생태계의 **@joyfill** 네임스페이스 패키지 2개가 침해되어 **DEV#POPPER** 원격접근트로잔을 배포하고 있다. 베타 버전 사용자를 대상으로 한 공급망 공격으로, 악성 코드는 가져오기 시점에 암호화 코드를 복호화해 실행된다.

## 타임라인

- 2026-07-29 [The Hacker News](https://thehackernews.com/2026/07/two-compromised-joyfill-npm-packages.html) — @joyfill/layouts@0.1.2-2773.beta.0, @joyfill/components@4.0.0-rc24-2773-beta.4 침해, DEV#POPPER RAT 배포

## 관련

[[asyncapi-npm-packages-compromise]] — @asyncapi npm 패키지 침해
