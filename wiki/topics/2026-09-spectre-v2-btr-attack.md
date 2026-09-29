---
slug: spectre-v2-btr-attack
first_seen: 2026-09-29
tags: [CPU취약점, 제로데이, 메모리누출, 학술공개]
cves: []
---

**VUSec**과 **Scuola Superiore Sant'Anna** 학술 그룹이 **Spectre-v2** CPU 취약점의 새로운 변형 **Branch Target Reuse(BTR) 공격**을 공개했다. JIT 엔진·언어 런타임·OS 커널 전반에 영향을 미치며, 웹 브라우저와 Linux 커널의 기존 방어를 우회할 수 있다. Intel 시스템에서 Linux root 패스워드 해시를 **3~5분 내에 탈취 가능**한 실제 악용 잠재력을 입증했다.

## 타임라인

- 2026-09-29 [The Hacker News](https://thehackernews.com/2026/09/new-spectre-v2-btr-attack-leaks-linux.html) — VUSec·Scuola Superiore Sant'Anna Spectre-v2 BTR 공격 공개, JIT·런타임·커널 영향, 기존 방어 우회
- 2026-09-29 [BleepingComputer](https://www.bleepingcomputer.com/news/security/new-spectre-v2-attack-variant-leaks-linux-root-password-hash-in-minutes/) — BTR 공격으로 Intel Linux 시스템 root 패스워드 해시 3~5분 평균 탈취
