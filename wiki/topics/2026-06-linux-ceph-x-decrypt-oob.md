---
slug: linux-ceph-x-decrypt-oob
first_seen: 2026-06-24
tags: [네트워크버그, 범위초과접근, Ceph]
cves: [CVE-2026-52956]
---

Linux 커널 net/ceph의 `__ceph_x_decrypt()` 함수에서 복호화 평문 크기 검증 부재로 인한 범위 초과 메모리 접근. ciphtertext_len이 ceph_x_encrypt_header 크기보다 작으면 hdr->magic 읽기 시 범위 초과 접근 발생 가능. 복호화 평문이 헤더 크기 이상인지 확인하여 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52956) — Linux libceph 패치 공개

## 관련

[[linux-ceph-choose-args-null]]
