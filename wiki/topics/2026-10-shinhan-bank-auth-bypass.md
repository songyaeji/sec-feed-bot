---
slug: shinhan-bank-auth-bypass
first_seen: 2026-10-01
tags: [인증우회, 금융권, 국내]
cves: []
---

신한은행 포함 7개 금융기관 6만8천여 명의 고객이 AI 자동화 공격 도구로 인한 인증 우회 공격을 받아 개인정보가 유출됐다. 국내 금융권 최대 규모 연쇄 침해사고로, 외부 노출 시스템과 API 권한검증 허점이 표적이 되었다.

## 타임라인

- 2026-10-01 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208680) — 신한은행 인증우회 2만5천여 명 정보유출 확인, 은행은 긴급조치 완료
- 2026-10-02 [금융보안원](https://news.google.com/rss/articles/CBMib0FVX3lxTE5HZ3JsbVM2d2dWNzk5QXBET3NQLVd1RkZaQ084Sl8wQ2NjSEx5M0JMTTRLWHF0Qk5ib0E3VG9mQzdacFlXLVdBLThnanMwalJ1ZWxRV3BSaGE5Rmh5NGxFOHBVWE9HSWFNYXBGejVOcw?oc=5) — AI 자율 침투 도구 활용 공격 의혹, 금융보안원 모니터링 강화 권고
- 2026-10-02 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208718) — ARTEX 도구로 신한은행·무신사·강남언니 등 금융권 광범위 공격, API 권한검증 허점 악용
- 2026-10-04 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208724) — ARTEX AI 추적 분석 결과 14개 국가·지역에서 359개 고유 IP 식별, 오아시스시큐리티 AGATHA 플랫폼 분석
- 2026-10-04 [금융보안원](https://news.google.com/rss/articles/CBMilgFBVV95cUxONjdPODZJWUFYU0NzWEZRRzVBTTM0dmQ4V0ZBQ3h1czluaW5LR052SDRhaVFlWjFoZS1yYkt0WVd0eXhnX0NPRWRFYmx4Rk82LU5MQlhWODdWcU1EMWtkbU01Um00TnFReG5zS3NDeEwzQVpLeFBIRGpneDczN1JxZlpUUEJMX2dVaDVXM053SFRxdzd1VXc?oc=5) — 금융보안원 '조회 권한' 허점 사전 경고, 규제당국의 감시 강화 권고
- 2026-10-04 [금융위원회](https://news.google.com/rss/articles/CBMigAFBVV95cUxQckdCMS00WGcxN3BDdTRKcERyVzNqMFB5YjBuNlFlc2VhOWRlRGJMSjdCUl9mdWRKazBCOERNbG1TUlpIRHU1aFZFMldoY1ZnaVI4Y0dDcE5sUElaRXcyVHRVQzROdEZvcWRmWF9rRlo4Wm03alJuM0x2NWJRUGNyRw?oc=5) — 금융권 해킹 7곳 확산, AI 자동화 공격 권한 조회 허점 악용 확인
- 2026-10-04 [금융보안원](https://news.google.com/rss/articles/CBMibEFVX3lxTE1jMnpkaHo5Mzk5anRBNDFIR0l6YXV2VVBsT1NOd2UwNzJLRmFxNWtWeFNrM0lqQ3RJaHZrTWpDMVlhQ0hab21HbmdxNWV2VVBnMk03RlI3dTVwRkQ5dzVYSTJFZXVqWGhBcncxTw?oc=5) — 은행 넘어 2금융권까지 인증우회 공격 확산 확인, 금융당국 전 금융권 긴급소집
- 2026-10-05 [매체]() — 금융권 망분리 보안체계 효과성 논쟁, 기술적·정책적 재검토 촉발
- 2026-10-05 [금융보안원]() — 화이트해커 투입에도 불구하고 공격 지속, 위협 고도화 확인
- 2026-10-05 [매체]() — 피해 규모 6만6천명으로 확대, 신용정보 노출로 2차 피해 우려

- 2026-10-06 02:05 [금융감원](https://news.google.com/rss/articles/CBMiZEFVX3lxTFBwQzBRNVhMT2hQY1poVV9vSnJ2Z1lZUkNRYzBIWEcxWEJsQUMzQl9MZE5CMmRjRFVmUFgyWmFpNEhDSTJ5S2hkUEtCZEtrU0dtXzVCVHdHUjJZT1lFcXRFXzBPTTI?oc=5) — 공격 IP 19개 특정, 12개국 IP로 우회 침투 추적
- 2026-10-06 07:36 [금융보안원](https://news.google.com/rss/articles/CBMiS0FVX3lxTFAxX0JyR2ZOQWVIN0xnTDNkVHM2TkZ3c0REMERaeFB6QmVEU2pteWpoeHdZN0hJMUxiekpHaGFWc3FJUUZWcEgzeXNZVQ?oc=5) — 은행권 인증·접근통제 대대적 점검 대응 강화
- 2026-10-06 07:44 [금융보안원](https://news.google.com/rss/articles/CBMic0FVX3lxTFBZUnpKUVBEQ3BuN1p6TmhFdXYyaUM3MTV3VXc0V3ltaWRqT0dENkUzdmRtQjVhSlJLQWRSYkl6aTBNZG56OGN1OF8tOGp0UkRSVUJyMk43S2xpMnhraVRRTGNEX1UwX3o1eXVFVnpkX3hyWjA?oc=5) — 정부 금융보안 '선제대응' 체제로 전환
- 2026-10-06 09:13 [금융보안원](https://news.google.com/rss/articles/CBMiZEFVX3lxTE8xMVJzMXhBTmg0YnVxN0lud1V6b0luQzV6c0NNNjNhUjl3NDRnUFc3XzdfVGQwa19JVE52RTBVU1B3Q2lpd3JfSURUaFhYLXhpSkpValZKalNiYjNGdDFfYWVjSEQ?oc=5) — AI 해킹으로 보안 투자 무색화되는 현실 지적
- 2026-10-06 09:27 [금융보안원](https://news.google.com/rss/articles/CBMiT0FVX3lxTE9rXzIzV2NFekpGLWJTN2RLOURtNFpHWURZaXQ3bE1ON3B1ekxaRW9ZVE1Qbkh1a2NPWjE0Z21LYmRCQ0xBVHAwMDF3RjktVUE?oc=5) — 금융보안원 감시 체계 부실 지적, 해킹 위험 적발 실패
- 2026-10-06 10:13 [금융보안원](https://news.google.com/rss/articles/CBMiZ0FVX3lxTE5fb01Xak0yclc4dDRrZjhmSEI0R3ljbUNhbDJ0ZDZwdldManlQaTFHR0xHR0tRbURTRGcxRGdVWnJUMEVTbWtpd2J0enc1TVpYdENfblFlWDJTV1pNc0pjRjc0WHZrUGs?oc=5) — 금융보안원 보호망 효과성 논쟁, 서비스 받는 은행 피격
- 2026-10-06 10:52 [금융보안원](https://news.google.com/rss/articles/CBMic0FVX3lxTFBPbHpJLTQ4TldUcXpZY1lHRTV1ZG9LZDY5LThyaVNtaUplbjNvQTQ4d0ZDYVZXUXNFaHhTa0pDd3V4VDd6VXJhUzYzcFBRbXpWN1BabVJSSlBKZ1NuX3cxZldlVTZvMmk2SkFXaHVoejliRHM?oc=5) — 해킹 공격 IP 금융사에 전파, 2차 피해 방지책 실천 주문
- 2026-10-06 10:57 [금융보안원](https://news.google.com/rss/articles/CBMibkFVX3lxTE5IMnFBSDhickFmVGFSZUhUYThmUTVsNnBxLVBzNE12QjlVT0l3NU9zdkg3b3JQcnJZVlRWb1Y1ZGdYQXNweHRZM1djY1F3YmFXSi1jR25VRTdhV3ZEdGVpckVWeXhqcktaQXdiZGJB?oc=5) — 해킹 공격 IP 28개 특정, 전 금융사 긴급 점검 지시
- 2026-10-06 15:29 [The Record](https://therecord.media/south-korean-bank-hacks-ai-agents) — 한국 금융당국 중국 사이버보안 도구로 은행 7곳 피격 확인, 6만8천명 개인정보 유출
- 2026-10-06 15:47 [금융보안원](https://news.google.com/rss/articles/CBMijgFBVV95cUxQNi04NVhIeG1sNV9CS3NMZ1ByaEQ0ZEJzNm1YNXRlWDJNcWhhM2VEWHhYMklvNkNnQVV0MzRHNEFPU0FKdEZIX05NSWR4QmJwVVYzSTdwOUFIYmFNallpUV9nTlZmNi1BOVMtUWRpT1Z5SzR1UmJiTy1HLTltUkZvSDVaS1VqTGJSS3h4WFRR?oc=5) — 1월부터 AI 해커 공격 시작, 금융사 공동 보안 경보 미흡 지적
- 2026-10-06 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208754) — 금융권 침해 확산 확인, KB국민·하나·BNK부산·예가람·웰컴저축·현대캐피탈 등 7개 기관 피격, 유출 규모 약 6만8천건
- 2026-10-07 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208767) — 에버스핀 에버세이프 웹으로 ARTEX 탐지 확인, 대출모집인용 시스템·보조 업무서비스 주요 표적, API 직접 호출로 인증 우회 수초 내 완료
- 2026-10-05 [금융보안원](https://news.google.com/rss/articles/CBMiU0FVX3lxTE1rbDJROGg0RGRXYnVuNFY4WTlUTE94RDk5ZmdtUVVaeU5ubFBZVXRoY2puODhPMXRaTlZNNWN0QzN0NkJ2RTBpdDBIOHpCOVFXWFdF0gFYQVVfeXFMTXJTVW4tMzZLaW9ybFE2RkpNMnVpUTJyVDZPTkRWcjNmM0NrbXFoSkpzX0wzc2ZaYjk4dDhPVkh6S0FnWk1Vc1R1OEJacFZwZ2VMT3NNSnFDOA?oc=5) — 과학기술정보통신부 공공기관·민간 정보통신서비스제공자 2만8천 곳 보안점검 권고
- 2026-10-06 [금융감원](https://news.google.com/rss/articles/CBMia0FVX3lxTE82cXBTMGZ2SWRnZ1ZkMXZELVByc25lNjBoUkVmb1dMdVVGOEJJZnFRVlNMNWlWb1Q1bDJkYlBRYjEtbFBGRG4wbWNvVzMyc1E1b18wbUVpUGhMejBfRjdRTzFYWWtqeDB4TUo40gFvQVVfeXFMTnE0THN0MF9ObUpaX3o1Y1hteFc4LVhRZkRZTmRObXEwY29yVlh0UHRhaDNhaE1zNlEzV3RyTUw2TzBDcThHUm15c0lOSU43dmYxcTREbWZHWVRfUWY4U3A2YlpnSHEyYTFoSVJKWFpZ?oc=5) — 금융권 개인정보 유출 관련 소비자경보 발령
- 2026-10-06 [금융위원회](https://news.google.com/rss/articles/CBMibkFVX3lxTE5CQmVWSG9DcUtSa2xwTTFVZWpHOURYMDRveDl0RGo4MklIbjRpY01fUVNIRUJjRGFKcHl0Z24wY19ubTlOWm0yYjdPNnd4MFAwYW8zMWh4N0pLSlJqaThFRnQxUGxsX2lYOTFhLTJB?oc=5) — 사이버위협 종합상황실 24시간 비상 가동, 사이버 대응체계 강화
- 2026-10-08 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208781) — CrowdStrike 보고서로 공격 서버 ARTEX 설정·AI 대화 기록 분석, 국내 유출정보 판매처 검색 시도 확인
- 2026-10-07 [금융보안원](https://news.google.com/rss/articles/CBMigAFBVV95cUxQRjM2WlFNQWNnTEVIN055S0oyOFdTT3poTWZIMXY2MWVKMUNMWHVOd0dMZmRGWnhsOTE2LWNfb09MYkJyak9TeElobXcwV3NGNmg5UWdjRVdOem50Rkpzd0ljSjEtc0YxcTBndEplQ1BRckUzeGx5U21ISTVsZFQ3bA?oc=5) — 1월부터 같은 IP로 금융권 반복 공격, 위험 IP 차단 체계 미흡
- 2026-10-07 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208773) — 엔키화이트햣 분석 보고서, 공격자가 코어뱅킹이 아닌 주변 시스템·인증·인가 허점 악용, API 권한검증 미흡
- 2026-10-07 [금융보안원]() — 보안점검 분석 결과 일부 금융사가 침해 탐지 실패, 점검·감시 체계 강화 권고
- 2026-10-07 [금융보안원](https://news.google.com/rss/articles/CBMibkFVX3lxTE1DQnV1NUhReTg2YzZWNldEdjFkZGtBRUFNaXAwTkp1YVVMa2VQVVY3UEx6MkNWYVN6TEdRTWNYQUlwUERFelFYakc4Q21VejhQemV1bVF5OFVpODJrY21QRXNQQ1d0NnFOX3ZwUkpn?oc=5) — 금융권 겨냥한 사이버 공격 급증, 금감원 8월부터 보안경고·대응 강화
- 2026-10-08 [펜타시큐리티](https://www.dailysecu.com/news/articleView.html?idxno=208791) — 금융권 연쇄 침해 대응 보안 3원칙(가시성·다층인증·권한최소화) 배포
- 2026-10-08 [SK쉴더스](https://www.dailysecu.com/news/articleView.html?idxno=208786) — AI 자동화 공격 시대 섀도우 IT·API 보안이 핵심, 기존 공격기법 AI로 자동화
- 2026-10-08 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208784) — 유출 개인정보를 악용한 보이스피싱·스미싱 2차 금융사기 우려, 금융감독원·금융위원회 소비자경보 발령
- 2026-10-09 [Security Affairs](https://securityaffairs.com/200661/hacking/ai-driven-tool-artex-used-in-attacks-against-south-korean-banks.html) — CrowdStrike ARTEX 분석 보고서 공개, 공격자 설정·AI 대화 기록 노출, 국내 유출정보 판매처 검색 시도 확인
- 2026-10-08 [금융보안원](https://news.google.com/rss/articles/CBMiXEFVX3lxTE9rVUJTbmxXeFk0M0hSV3NGT2ZDZHpkVkxJSWxmU1UzWFI5VzVrYW5RZWNjZzFqSUpTVC14WkF4ZmVWREduNjR3a3ZJM1RMNUQyYWpXbFc2cHNveUhh?oc=5) — 중국산 무료 AI 도구를 악용한 금융권 공격, 보안 투자 효과성 논쟁
- 2026-10-06 [금융위원회](https://news.google.com/rss/articles/CBMiT0FVX3lxTE9INVEwbURYT1dCMVd0TUlsMkJ3ZXc1dW93ZVlYYjBGdmJpZG1GSzVIcXlfNzVpZHVld1VBVm5lcEdhVHUxblNZTGJhcFZJTmPSAV9BVV95cUxPWWNGRnYzOElvZUo0bXdKSUp2SlJxamJGZWdJYXF4cEtoSGdIWHFsXzdVbDl5b0JjTUdvUDg2Zm1SbGtrdXhLZkZKWVVWdDE4Wk5OMzQyMTl0OGQ1Mjdmbw?oc=5) — 금융위 전 금융권 비상점검 지시, 보안체계 원점 재검토 명령
- 2026-10-08 [금융보안원](https://news.google.com/rss/articles/CBMie0FVX3lxTE0yS0RfcV9JUk5jNjdodGFUUXg1TGdSZE9wVmw5RF9EOHNJck1jTEhUdHNEcWJCRlFzMXNSbDg2cXUxVVVxbjRYVEdtUGxtUFFpTlRuNWhBdGY1Z0hWQno3ZklROGxrVG41RVpTb1BYd0ZISEdNT0dtS3g3Z9IBgAFBVV95cUxQaXptVGNEQkFzaURQdEw5MTBaU0dkNTZkZy1VOEJ0LTYxeC1wa1pjSTlPNjhzTTBRSDIwcFg0WVZlR255d25fdVhvck9FY21DYWpxb3pzbDBlRUhRQ2JOSEludmt3YkZYWlVVdXRKT0I0QnY2WklKNENadmFhTTVUNQ?oc=5) — 국감에서 이억원 금융위원장 '관리 공백' 인정, 감독 강화 시사
- 2026-10-09 [데일리시큐](https://www.dailysecu.com/news/articleView.html?idxno=208810) — 금융감독원의 긴급 자체점검 기준 허점 지적, 최근 3개월만 확인하는 금융사 다수, 1년치 기록 조사한 인터넷전문은행에서는 과거 해킹 의심 IP 접속 흔적 발견
- 2026-10-08 [금융보안원](https://news.google.com/rss/articles/CBMia0FVX3lxTE9GUXRtNUl4QkEzUm5WR25lZHhsTWRKZVdVRFNtRnhIY0xSbTVXdUNkb2dqVmZsdVlmMmJvR0RveDBSN3o0bEVOTThDV1B3RFZZWEYwQmlTam1tbUhtWE9JOUplUy1QcXFQWVRJ?oc=5) — 국감 지적 '해킹 인지까지 5일 걸려' 감시체계 허술 확인

## 관련

[[financial-ai-agent-attack-real]]
