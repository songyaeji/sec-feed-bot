---
slug: linux-fsnotify-inode-ref
first_seen: 2026-06-24
tags: [파일시스템감시, 참조누수, 마크관리]
cves: [CVE-2026-52990]
---

Linux fsnotify 파일시스템 감시 기능의 fsnotify_recalc_mask() 함수에서 __fsnotify_recalc_mask() 반환값 미처리 시 inode 참조 누수. HAS_IREF 플래그 전환 시 반환되는 inode 포인터를 fsnotify_drop_object()로 해제하지 않아 umount 시 무한 대기.

## 타임라인
- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52990) — fsnotify inode 참조 누수 공개

## 관련
