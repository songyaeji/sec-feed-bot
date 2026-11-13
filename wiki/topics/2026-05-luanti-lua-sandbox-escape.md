---
slug: luanti-lua-sandbox-escape
first_seen: 2026-04-23
tags: [게임엔진, 샌드박스탈출, Lua, 악성모드]
cves: [CVE-2026-41196]
---

# Luanti(Minetest) — Lua 샌드박스 탈출 취약점

Luanti(구 Minetest) 오픈소스 복셀 게임 엔진 5.0.0 ~ 5.15.1 버전에 Lua 샌드박스 탈출 취약점이 존재한다. 악의적 모드가 제한된 Lua 환경에서 벗어나 임의의 코드를 실행하고 전체 파일시스템에 접근할 수 있다. 이는 서버 측 모드, 비동기 및 맵생성 환경과 클라이언트 측 모드(CSM)에 모두 영향을 미친다. LuaJIT 사용 시에만 악용 가능하며 5.15.2 버전에서 패치됐다.

## 타임라인

- 2026-04-23 [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-41196) — CVE-2026-41196 공개, CVSS 10.0

## 관련
