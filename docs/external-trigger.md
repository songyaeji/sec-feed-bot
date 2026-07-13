# 외부 트리거 설정 — cron-job.org → workflow_dispatch

## 왜 필요한가

GitHub Actions 예약 cron(`*/20`)은 지연·스킵이 구조적이다(공식 문서상
실행 시각 무보장 — https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).
실측 런 간격 49분~3시간 17분(2026-07-08). 긴급 알림의 실시간성을 위해
외부 스케줄러가 10분마다 `workflow_dispatch` REST API를 호출한다.
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
   - **Schedule**: Every 10 minutes
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

## 2-1. digest 잡 등록 (아침 카드뉴스 — 사용자 직접)

GitHub schedule cron만으로는 digest 발화가 21:50 UTC 예약에서 실측
50분+ 밀린다(2026-07-10: 52분 지연 → 07:00 KST 발행 실패). realtime과
동일하게 cron-job.org를 주 경로로, GitHub cron(`50 21 * * *`)을 안전망으로
쓴다. main.py의 `last_digest_date` 가드(state/seen.json, KST 날짜)가 같은
날 두 번째 digest를 realtime으로 강등해 이중 발행을 막는다 — 그래서 두
경로가 겹쳐도 안전하다.

1. cron-job.org → Create cronjob (두 번째 잡, 기존 PAT 재사용)
2. 설정 — URL·method·헤더는 realtime 잡과 동일, 차이는 둘뿐:
   - **Schedule**: 매일 21:50 UTC (= 06:50 KST. cron-job.org 잡 시간대를
     UTC로 두었는지 확인)
   - **Request body**:
     ```json
     {"ref": "main", "inputs": {"mode": "digest"}}
     ```
3. Test run 1회 → Actions 탭에 workflow_dispatch 런 생성 확인. 단, 실제
   digest 발행까지 확인하려면 그날 `last_digest_date`가 오늘이 아니어야
   한다(이미 발행된 날의 테스트 런은 realtime으로 강등되는 게 정상).

주의: main.py에 digest 허용 시간창 가드가 있다 — KST 06~12시 밖에 도착한
digest는 realtime으로 강등된다(2026-07-12 사고: realtime 잡 payload가
`mode=digest`로 잘못 등록돼 자정 직후 00:23에 발행됨). 시간창 밖 수동
테스트가 필요하면 워크플로 env에 `ALLOW_OFFHOUR_DIGEST=1`을 임시로 준다.
같은 날 digest 재발행(검증·사고 복구)은 state의 `last_digest_date`를
손으로 되감지 말 것 — merge_state의 max() union이 동시 realtime 커밋에서
오늘 날짜를 부활시켜 레이스로 무산된다(2026-07-13 실측). 대신
workflow_dispatch 입력 `force_digest=true`(이중발행·시간창 가드 동시
우회)를 쓴다: `gh workflow run collect.yml -f mode=digest -f force_digest=true`.

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
- [ ] 이후 10분 간격으로 런이 쌓이는지 1시간 관찰
- [ ] 긴급 판정 0건인 런은 Discord에 아무것도 안 보내는 게 정상
