# 외부 트리거 설정 — cron-job.org → workflow_dispatch

## 왜 필요한가

GitHub Actions 예약 cron(`*/20`)은 지연·스킵이 구조적이다(공식 문서상
실행 시각 무보장 — https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
실측 런 간격 49분~3시간 17분(2026-07-08). 긴급 알림의 실시간성을 위해
외부 스케줄러가 15분마다 `workflow_dispatch` REST API를 호출한다.
기존 `*/20` cron은 외부 서비스 장애 대비 안전망으로 유지한다.

## 1. Fine-grained PAT 발급 (사용자 직접, 브라우저)

1. GitHub → Settings → Developer settings → Personal access tokens →
   **Fine-grained tokens** → Generate new token
2. 설정:
   - **Repository access**: Only select repositories → `songyaeji/sec-feed-bot` 만
   - **Permissions**: Repository permissions → **Actions: Read and write** 만.
     (workflow_dispatch API 호출에 필요한 최소 권한 — 다른 권한 전부 No access)
   - **Expiration**: 90일 (만료 시 재발급 후 cron-job.org 헤더만 교체)
3. 생성된 `github_pat_...` 토큰을 복사 — **이 화면을 벗어나면 다시 못 본다.**

## 2. cron-job.org 잡 등록 (사용자 직접)

1. https://cron-job.org 가입 → Create cronjob
2. 설정:
   - **URL**: `https://api.github.com/repos/songyaeji/sec-feed-bot/actions/workflows/collect.yml/dispatches`
   - **Schedule**: Every 15 minutes
   - **Request method**: POST
   - **Headers**:
     - `Authorization: Bearer <PAT>`
     - `Accept: application/vnd.github+json`
   - **Request body**:
     ```json
     {"ref": "main", "inputs": {"mode": "realtime"}}
     ```
3. 저장 후 Test run 1회 → GitHub repo Actions 탭에 workflow_dispatch 런이
   생기는지 확인. **성공 응답은 204 No Content(본문 없음)** — 200이 아니어도 정상.

## 3. 보안 유의사항

> **Warning:** PAT는 이 저장소의 Actions 실행 권한을 가진 자격증명이다.
> 코드·커밋·이슈·위키 어디에도 절대 붙여넣지 않는다.

- PAT는 cron-job.org 잡 설정(헤더)에만 저장한다. 다른 곳에 기록 금지.
- fine-grained + repo 한정 + Actions read/write 한정이라 유출돼도 피해
  범위는 "이 repo의 워크플로 실행"에 그친다 — 그래도 유출 의심 시 즉시
  GitHub에서 revoke하고 재발급한다.
- 만료(90일) 임박 알림이 GitHub 메일로 온다 — 재발급 후 cron-job.org
  헤더의 토큰만 교체하면 된다.

## 동작 확인 체크리스트

- [ ] cron-job.org Test run → Actions 탭에 `workflow_dispatch` 이벤트 런 생성
- [ ] 이후 15분 간격으로 런이 쌓이는지 1시간 관찰
- [ ] 긴급 판정 0건인 런은 Discord에 아무것도 안 보내는 게 정상
