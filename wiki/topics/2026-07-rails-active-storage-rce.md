---
slug: rails-active-storage-rce
first_seen: 2026-07-29
tags: [원격코드실행, RailsFramework, 파일접근, RCE]
cves:
  - CVE-2026-66066
---

Ruby on Rails Active Storage 취약점(CVE-2026-66066, CVSS 9.5)으로 미인증 공격자가 특수 이미지 업로드를 통해 서버의 임의 파일 접근 가능. Rails 프로세스 환경, 마스터 키, 데이터베이스 암호, 클라우드 저장소 자격증명 등 민감정보 노출 위험.

## 타임라인

- 2026-07-29 [The Hacker News](https://thehackernews.com/2026/07/critical-rails-flaw-could-let.html) — Ruby on Rails Active Storage CVE-2026-66066 (CVSS 9.5) 미인증 임의 파일 읽기 취약점 패치
- 2026-09-01 [The Hacker News](https://thehackernews.com/2026/09/attackers-exploit-critical-langflow-and.html) — 공격자, Langflow와 Rails 결함 함께 악용 확인 CVSS 9.8 이상 중대도

## 관련
