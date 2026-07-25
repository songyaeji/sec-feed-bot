"""공유 최하층 — 경로 상수·웹훅 토큰 마스킹. 로컬 모듈 import 금지(순환 방지)."""
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.yaml")
STATE_DIR = os.path.join(BASE_DIR, "state")
STATE_PATH = os.path.join(STATE_DIR, "seen.json")
PENDING_PATH = os.path.join(STATE_DIR, "pending.json")
# 포트폴리오(songyaeji.github.io) Trend 탭 게시 산출물 — collect.yml의
# 후속 스텝이 이 디렉터리를 포트폴리오 repo로 push한다
TREND_DIR = os.path.join(BASE_DIR, "out", "trend")

SEEN_TTL_DAYS = 90

# requests exceptions can embed the request URL (e.g. connection/timeout
# errors), and webhook URLs carry a bearer token in their path, so any
# exception text we print must have that token pattern masked first
WEBHOOK_TOKEN_RE = re.compile(r"webhooks/\d+/[\w-]+")


def _safe_exc_str(exc: Exception) -> str:
    return f"{type(exc).__name__}: {WEBHOOK_TOKEN_RE.sub('webhooks/***', str(exc))}"
