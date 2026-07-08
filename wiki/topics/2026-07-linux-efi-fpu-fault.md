---
slug: linux-efi-fpu-fault
first_seen: 2026-07-08
tags: [Linux, EFI, FPU]
cves: [CVE-2026-46290]
---

Linux x86 EFI 런타임 서비스에서 FPU(부동소수점 연산기) 소프트IRQ 변경(d02198550423 커밋) 후 **그레이스풀 폴트 처리 오류**. `kernel_fpu_begin()`이 `fpregs_lock()`을 호출하면서 fault handler 스택 동적 할당이 정상 작동하지 않아 EFI 런타임 서비스 중 예외 발생 시 **장애 처리 실패**.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-46290) — CVE-2026-46290 공개 (CVSS 5.5)

## 관련
