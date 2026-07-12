---
slug: linux-tls-strparser-leak
first_seen: 2026-06-24
tags: [TLS, 메모리누수, 오프로드]
cves: [CVE-2026-52974]
---

Linux TLS 오프로드 설정 실패 시 strparser 초기화 anchor skb 누수 발생. tls_set_device_offload_rx() 실패 후 tls_sw_free_resources_rx()가 tls_strp_init()에서 할당한 anchor skb를 해제하지 않음. 해당 코드 경로는 오프로드 시작 실패 전용으로 tls_strp_done()이 호출되지 않음.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52974) — TLS strparser anchor skb 메모리 누수 공개

## 관련
