---
slug: linux-sched-fork-deadline
first_seen: 2026-06-24
tags: [스케줄러, 초기화오류, 공정성]
cves: [CVE-2026-52980]
---

Linux 스케줄러 EEVDF(earliest eligible virtual deadline first) 공정성 엔진에서 포크된 태스크의 rel_deadline 초기화 누락으로 야기되는 데드라인 오버플로우. 포크 후 첫 enqueue에서 rel_deadline 설정으로 vruntime이 비정상 커져 yield 후 스택 버퍼 오버플로우로 cfs_rq 손상.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52980) — sched fair fork rel_deadline 초기화 누락 공개

## 관련
