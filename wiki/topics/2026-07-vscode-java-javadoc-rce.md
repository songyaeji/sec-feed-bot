---
slug: vscode-java-javadoc-rce
first_seen: 2026-07-08
tags: [개발도구, 마크다운 신뢰, RCE]
cves: [CVE-2026-12856]
---

Visual Studio Code용 vscode-java 확장 프로그램의 JavaDoc 호버 마크다운 신뢰 취약점. 확장 프로그램이 JavaDoc 내용의 모든 마크다운을 신뢰하여 처리하기 때문에 악의적인 Java 파일에 숨겨진 명령을 포함한 특수 링크를 삽입하면, 사용자가 JavaDoc 호버의 링크를 클릭할 시 임의 명령 실행 가능.

## 타임라인

- 2026-07-08 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-12856) — CVE-2026-12856 공개 (CVSS 8.8)
