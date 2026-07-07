---
slug: vllm-image-metadata
first_seen: 2026-07-07
tags: [AI, LLM, 정보유출]
cves: [CVE-2026-12491]
---

대규모언어모델(LLM) 추론 라이브러리 **vLLM**의 이미지 처리 취약점(CVSS 4.8). 이미지를 RGB로 변환할 때 EXIF 방향 정보와 PNG 투명도(tRNS) 메타데이터를 부적절하게 처리하면서 정보 유출이 발생한다.

## 타임라인

- 2026-07-07 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-12491) — CVE-2026-12491 공개

## 관련
