---
slug: telegram-desktop-xss-export
first_seen: 2026-09-15
tags: [XSS, 데이터탈취, 채팅앱, 취약점]
cves: []
---

# Telegram Desktop 채팅 내보내기 저장 XSS 취약점

**Telegram Desktop**에서 HTML 채팅 내보내기에 저장 XSS(Stored Cross-Site Scripting) 취약점이 발견되었다. ExPatch의 Denis와 Aleksander Rostilov가 발견한 이 결함으로 인해 악의적 봇이 내보낸 HTML에 JavaScript를 주입하여 데이터 탈취 및 페이지 조작을 유도할 수 있다. 구 버전의 내보내기 파일도 계속 위험한 상태로 남아있다.

## 타임라인

- 2026-09-15 [Security Affairs](https://securityaffairs.com/199076/security/telegram-desktop-flaw-could-turn-old-chat-exports-into-data-theft-traps.html) — ExPatch 연구원 발표, 취약점 메커니즘 공개

## 관련

없음
