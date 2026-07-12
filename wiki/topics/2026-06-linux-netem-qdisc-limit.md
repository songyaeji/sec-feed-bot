---
slug: linux-netem-qdisc-limit
first_seen: 2026-06-24
tags: [트래픽제어, 큐관리, 스케줄러]
cves: [CVE-2026-52984]
---

Linux netlink 트래픽 제어 netem(network emulation) 큐 한계 검사에서 재정렬 경로 누락. netem_enqueue()가 q->t_len(tfifo 내부 큐)만 검사하고 __qdisc_enqueue_head()로 배치된 sch->q의 패킷 미계산. 재정렬 시 큐 점유율 초과 가능.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52984) — netem 큐 한계 검사 누락 공개

## 관련
