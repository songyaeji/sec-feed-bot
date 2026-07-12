---
slug: linux-i2c-timeout-overflow
first_seen: 2026-06-24
tags: [커널버그, 정수오버플로우, 로컬공격]
cves: [CVE-2026-52948]
---

Linux 커널 fs/i2c의 `I2C_TIMEOUT ioctl` 핸들러에서 정수 오버플로우 취약점. 사용자 입력이 INT_MAX 체크를 통과한 후 10배 곱해져 MSBs 오버플로우 발생, 음수 타임아웃으로 변환되어 SMBus 상태 머신을 손상시키고 로컬 서비스 거부 야기. 사용자 입력을 INT_MAX/10 범위로 제한하여 수정됨.

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52948) — Linux 커널 i2c 패치 공개

## 관련
