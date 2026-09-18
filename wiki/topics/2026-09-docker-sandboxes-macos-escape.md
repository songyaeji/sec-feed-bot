---
slug: docker-sandboxes-macos-escape
first_seen: 2026-09-17
tags: [VM탈출, macOS, 권한상향]
cves: [CVE-2026-77179]
---

**Docker** Sandboxes 가상머신에서 실행되는 악성 코드가 공유 프로젝트 디렉터리를 벗어나 호스트 macOS의 다른 파일들을 읽고 수정할 수 있는 중대 탈출 취약점. 공격이 성공하면 호스트 VM 프로세스의 권한(일반 사용자 계정)으로 파일 시스템 전체에 접근 가능하다. 개발자는 Docker를 통해 컨테이너 격리를 신뢰하고 프로젝트 폴더를 공유하는데, 이 취약점은 그 기본 전제를 무너뜨린다.

## 타임라인

- 2026-09-17 [The Hacker News](https://thehackernews.com/2026/09/critical-docker-sandboxes-flaw-lets.html) — Docker Sandboxes 취약점 CVE-2026-77179 공개, 가상머신 공유 폴더 격리 우회

## 관련
