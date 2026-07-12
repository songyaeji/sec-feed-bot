---
slug: linux-ksmbd-durable-uaf
first_seen: 2026-07-10
tags: [커널버그, 사용후해제, SMB]
cves: [CVE-2026-53010]
---

Linux 커널 ksmbd(SMB 서버)의 `smb2_open()` 함수 사용 후 해제 취약점. 영구 파일 디스크립터 재연결 중 `ksmbd_put_durable_fd(fp)`가 이른 참조 해제. 이후 오류 발생(예: `ksmbd_iov_pin_rsp` 실패)이나 스캐빈저 접근 시 fp 속성(create_time 등) 접근 시 use-after-free. (CVSS 9.8)

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-53010) — Linux ksmbd 패치 공개

## 관련
