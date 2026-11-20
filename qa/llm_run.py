"""QA 전용 실제 LLM digest 실행 — 발송 없음, 커밋 없음.

.github/workflows/qa-llm.yml에서만 실행한다. 운영 digest와 같은 코드 경로
(수집, 사서, 원장 판정, 중복 게이트, 문안 재작성, 총평, 트렌드 선정, 카드
렌더)를 실제 claude CLI로 돌리고, 단계별 입출력과 카드 PNG를 산출물 폴더에
남긴다. Discord 전송 함수는 전부 막고, 네트워크 전송 경로가 호출되면 즉시
예외로 멈춘다. QA가 끝나면 이 파일과 workflow는 지운다.

사용: python qa/llm_run.py <산출물 폴더>
"""
import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else "out/qa")
sys.path.insert(0, ROOT)
os.chdir(ROOT)
os.makedirs(OUT, exist_ok=True)

for key in ("DISCORD_WEBHOOK_URL", "DISCORD_TREND_WEBHOOK_URL", "DRY_RUN", "FORCE_DIGEST"):
    os.environ.pop(key, None)
os.environ["RUN_MODE"] = "digest"
os.environ["ALLOW_OFFHOUR_DIGEST"] = "1"

# 같은 날 이미 발행된 운영 상태에서도 digest 경로를 타게 가드 날짜만 지운다
seen_path = os.path.join(ROOT, "state", "seen.json")
with open(seen_path, encoding="utf-8") as f:
    seen = json.load(f)
seen.pop("last_digest_date", None)
seen.pop("last_trend_date", None)
with open(seen_path, "w", encoding="utf-8") as f:
    json.dump(seen, f)


def dump(name, obj):
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, default=str)


import cardgen  # noqa: E402
import card_editor  # noqa: E402
import judge  # noqa: E402
import librarian  # noqa: E402
import main  # noqa: E402
import notify  # noqa: E402
import published_ledger  # noqa: E402
import trend_enrich  # noqa: E402

timing: dict[str, float] = {}


def timed(mod, name, label, save_input=False):
    fn = getattr(mod, name)

    def wrapper(*args, **kwargs):
        start = time.time()
        result = fn(*args, **kwargs)
        timing[label] = round(time.time() - start, 1)
        if save_input:
            dump(f"{label}_in.json", args[0] if args else None)
        dump(f"{label}_out.json", result)
        return result

    setattr(mod, name, wrapper)


timed(main, "collect_all", "collect")
timed(judge, "select_urgent", "judge")
timed(librarian, "run_librarian", "librarian", save_input=True)
timed(published_ledger, "filter_news", "ledger", save_input=True)
timed(librarian, "dedup_gate", "dedup_gate", save_input=True)
timed(card_editor, "rewrite", "rewrite", save_input=True)
timed(librarian, "summarize", "summarize")
timed(trend_enrich, "pick", "trend", save_input=True)

sent: dict = {}


def _blocked(*args, **kwargs):
    raise RuntimeError("QA run: 네트워크 전송 차단")


notify._post_with_retry = _blocked
notify.send_card_news = lambda pngs, lines: sent.update(card_lines=lines, cards=len(pngs))
notify.send_digest = lambda items, *a, **k: sent.update(
    text_fallback=[it.get("title_ko") for it in items])
notify.send_cards = lambda items, *a, **k: sent.update(
    urgent=[it.get("title") for it in items])
notify.send_trend = lambda items, *a, **k: sent.update(trend=items)

_build = cardgen.build_cards


def build_and_save(items, **kwargs):
    dump("to_send.json", items)
    pngs = _build(items, **kwargs)
    for i, png in enumerate(pngs, start=1):
        with open(os.path.join(OUT, f"card_{i:02d}.png"), "wb") as f:
            f.write(png)
    return pngs


cardgen.build_cards = build_and_save

started = time.time()
error = None
try:
    main.main()
except BaseException as exc:  # noqa: BLE001 — QA 산출물은 실패해도 남긴다
    error = repr(exc)
finally:
    timing["total"] = round(time.time() - started, 1)
    dump("sent.json", sent)
    dump("timing.json", timing)
    dump("error.json", error)
    diff = subprocess.run(["git", "status", "--porcelain", "wiki/", "state/"],
                          capture_output=True, text=True).stdout
    with open(os.path.join(OUT, "changed_files.txt"), "w", encoding="utf-8") as f:
        f.write(diff)
    wiki_out = os.path.join(OUT, "wiki_changed")
    for line in diff.splitlines():
        path = line[3:].strip()
        if path.startswith("wiki/") and path.endswith(".md") and os.path.isfile(path):
            dest = os.path.join(wiki_out, path)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy(path, dest)
    print("QA DONE", json.dumps(timing), "error:", error)
