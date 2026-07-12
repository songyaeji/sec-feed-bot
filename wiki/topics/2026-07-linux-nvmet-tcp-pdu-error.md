---
slug: linux-nvmet-tcp-pdu-error
first_seen: 2026-07-10
tags: [커널버그, 오류처리, NVMe]
cves: [CVE-2026-52989]
---

Linux 커널 nvmet-tcp 드라이버의 오류 처리 부재. `nvmet_tcp_build_pdu_iovec()` 함수가 범위 초과 PDU 길이 또는 오프셋 감지 시 치명 오류 신호를 보내지만 호출자에게 반환값 없음(void). 호출자는 오류 인식 불가로 cmd->recv_msg.msg_iter을 미초기화 상태로 유지. (CVSS 9.8)

## 타임라인

- 2026-06-24 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-52989) — Linux nvmet-tcp 패치 공개

## 관련
