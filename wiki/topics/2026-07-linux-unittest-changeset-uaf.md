---
slug: linux-unittest-changeset-uaf
first_seen: 2026-07-08
tags: [Linux, devicetree, UAF]
cves: [CVE-2026-46288]
---

Linux 커널 devicetree 단위 테스트 `of_unittest_changeset()` 함수에서 **해제 후 사용(UAF)** 취약점. `parent` 변수가 `nchangeset`과 동일한 `struct device_node`를 가리키고 있으나, `of_node_put(nchangeset)` 호출로 노드를 해제한 후 `parent` 포인터로 계속 접근하면서 메모리 손상 발생.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46288) — CVE-2026-46288 공개 (CVSS 8.4)

## 관련
