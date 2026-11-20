"""보안 강화 테스트 (QA 2026-11-20 F1 F2 F3 F5 F6 F7 F8 C7 C9).

- claude 호출: 호출 지점마다 글 전용 플래그, 사서만 위키 도구, stdin 전달,
  환경변수 축소, 타임아웃 시 프로세스그룹 종료. subprocess는 전부 가짜다.
- 사서 격리 작업 폴더: wiki/topics/*.md 변경분만 저장소로 반영.
- 기사 fetch: 127.0.0.1 로컬 서버로 내부 주소 차단, 리다이렉트 상한,
  기사당 마감, 크기 상한, 인코딩 추정을 확인한다.
- 링크 URL 검증과 preflight 비밀값 검사.
"""
import gzip
import json
import os
import signal
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import card_editor  # noqa: E402
import cardgen  # noqa: E402
import judge  # noqa: E402
import librarian  # noqa: E402
import netguard  # noqa: E402
import notify  # noqa: E402
import preflight  # noqa: E402
import published_ledger  # noqa: E402
import trend_enrich  # noqa: E402


# ============================================================ claude 호출

@pytest.fixture
def fake_claude(monkeypatch):
    rec = SimpleNamespace(calls=[], stdout=json.dumps({"result": "{}"}), hook=None)

    class FakePopen:
        def __init__(self, cmd, **kw):
            self.args = cmd
            self.kw = kw
            self.pid = 4242
            self.returncode = 0
            self.input = None
            rec.calls.append(self)

        def communicate(self, input=None, timeout=None):
            self.input = input
            if rec.hook:
                rec.hook(self)
            return rec.stdout, ""

        def wait(self):
            return 0

        def kill(self):
            pass

    monkeypatch.setattr(librarian.subprocess, "Popen", FakePopen)
    monkeypatch.setenv("CLAUDE_CODE_OAUTH_TOKEN", "test-oauth-token-value")
    return rec


def _result(obj) -> str:
    return json.dumps({"result": json.dumps(obj, ensure_ascii=False)})


def _flag(cmd, name):
    return cmd[cmd.index(name) + 1]


def _assert_text_only(call, marker):
    cmd = call.args
    assert cmd[:2] == ["claude", "-p"]
    assert _flag(cmd, "--tools") == ""
    assert _flag(cmd, "--permission-mode") == "dontAsk"
    assert "--strict-mcp-config" in cmd
    deny = set(_flag(cmd, "--disallowedTools").split(","))
    assert {"Agent", "Task", "Bash", "Read", "Write", "Edit", "WebFetch", "mcp__*"} <= deny
    assert "--allowedTools" not in cmd
    # 프롬프트는 stdin으로만 간다
    assert call.kw["stdin"] == subprocess.PIPE
    assert marker in call.input
    assert not any(marker in arg for arg in cmd)
    assert call.kw["cwd"] == librarian.BASE_DIR


def test_summarize_is_text_only(fake_claude):
    fake_claude.stdout = _result({"briefing": "총평이다.", "keywords": ["키워드"]})
    out = librarian.summarize([{"title_ko": "요약표식가나다", "summary_ko": "요약이다."}])
    assert out["briefing"] == "총평이다."
    _assert_text_only(fake_claude.calls[-1], "요약표식가나다")


def test_fix_styles_is_text_only(fake_claude):
    verdicts = {"a": {"summary_ko": "문체표식 개조식 요약"}}
    librarian._fix_styles(verdicts, librarian.MODEL, 5)
    _assert_text_only(fake_claude.calls[-1], "문체표식 개조식 요약")


def test_dedup_gate_is_text_only(fake_claude):
    fake_claude.stdout = _result({"groups": []})
    items = [{"title_ko": "중복표식 하나"}, {"title_ko": "중복표식 둘"}]
    assert librarian.dedup_gate(items) == []
    _assert_text_only(fake_claude.calls[-1], "중복표식 하나")


def test_ledger_judge_is_text_only(fake_claude):
    fake_claude.stdout = _result({"results": []})
    entries = [{"date": "2026-11-14", "lane": "news", "url": "https://a.com/1",
                "title": "t", "title_ko": "원장 제목", "summary_ko": "", "cves": []}]
    cand = [{"id": "c", "title": "x", "title_ko": "원장표식 후보", "summary": "",
             "url": "https://b.com/2"}]
    published_ledger._llm_judge(cand, entries)
    _assert_text_only(fake_claude.calls[-1], "원장표식 후보")


def test_card_editor_rewrite_is_text_only(fake_claude):
    fake_claude.stdout = _result({"items": {}})
    assert card_editor._call("재작성표식 프롬프트") == {}
    _assert_text_only(fake_claude.calls[-1], "재작성표식 프롬프트")


def test_trend_pick_is_text_only(fake_claude):
    fake_claude.stdout = json.dumps({"result": "트렌드 결과"})
    assert trend_enrich._call_llm("트렌드표식 프롬프트") == "트렌드 결과"
    _assert_text_only(fake_claude.calls[-1], "트렌드표식 프롬프트")


def test_judge_is_text_only(fake_claude):
    fake_claude.stdout = _result({"urgent": []})
    items = [{"id": "x", "title": "판정표식 대형 통신사 해킹 유출", "summary": ""}]
    assert judge.select_urgent(items, {}, allow_llm=True) == []
    _assert_text_only(fake_claude.calls[-1], "판정표식 대형 통신사 해킹 유출")


def test_librarian_chunk_gets_wiki_tools_in_workspace(fake_claude, tmp_path):
    seen = {}

    def hook(call):
        path = os.path.join(call.kw["cwd"], "state", "librarian_input.json")
        with open(path, encoding="utf-8") as f:
            seen["input"] = json.load(f)

    fake_claude.hook = hook
    fake_claude.stdout = _result({"verdicts": {"a": {"action": "new"}}})
    ws = str(tmp_path)
    out = librarian._run_chunk([{"id": "a", "title": "t"}], "사서표식 프롬프트", ws)
    assert out == {"a": {"action": "new"}}
    call = fake_claude.calls[-1]
    cmd = call.args
    assert call.kw["cwd"] == ws
    assert _flag(cmd, "--tools") == "Read,Glob,Grep,Write,Edit"
    assert _flag(cmd, "--allowedTools") == "Edit(wiki/topics/**)"
    assert _flag(cmd, "--permission-mode") == "dontAsk"
    assert "--strict-mcp-config" in cmd
    deny = set(_flag(cmd, "--disallowedTools").split(","))
    assert {"Bash", "Agent", "Task", "WebFetch", "mcp__*", "Read(.git/**)"} <= deny
    assert "사서표식 프롬프트" == call.input
    assert seen["input"][0]["id"] == "a"


def test_tool_flags_only_from_central_function():
    with pytest.raises(ValueError):
        librarian._run_claude_json(["--model", "m", "--allowedTools", "Bash"], "p", 1)
    with pytest.raises(ValueError):
        librarian._claude_cmd(["--tools", "Bash"], None)


def test_claude_env_drops_other_secrets(fake_claude, monkeypatch):
    for name in ("DISCORD_WEBHOOK_URL", "DISCORD_TREND_WEBHOOK_URL", "NVD_API_KEY",
                 "REDDIT_CLIENT_SECRET", "IG_ACCESS_TOKEN", "GITHUB_TOKEN"):
        monkeypatch.setenv(name, "secret-" + name)
    fake_claude.stdout = _result({"groups": []})
    librarian.dedup_gate([{"title_ko": "가"}, {"title_ko": "나"}])
    env = fake_claude.calls[-1].kw["env"]
    assert not any(v.startswith("secret-") for v in env.values())
    assert env["CLAUDE_CODE_OAUTH_TOKEN"] == "test-oauth-token-value"
    assert env["CLAUDE_CODE_SUBPROCESS_ENV_SCRUB"] == "1"
    assert "PATH" in env


def test_timeout_kills_process_group(monkeypatch):
    killed = {}

    class SlowPopen:
        def __init__(self, cmd, **kw):
            self.pid = 777

        def communicate(self, input=None, timeout=None):
            raise subprocess.TimeoutExpired("claude", timeout)

        def wait(self):
            killed["waited"] = True

        def kill(self):
            killed["kill"] = True

    monkeypatch.setattr(librarian.subprocess, "Popen", SlowPopen)
    monkeypatch.setattr(os, "getpgid", lambda pid: pid + 1, raising=False)
    monkeypatch.setattr(os, "killpg", lambda pgid, sig: killed.update(pg=pgid), raising=False)
    monkeypatch.setattr(signal, "SIGKILL", 9, raising=False)
    assert librarian._run_claude_json(["--model", "m"], "p", 1) is None
    assert killed["pg"] == 778 and killed["waited"]


def test_long_prompt_goes_through_stdin(monkeypatch):
    # argv 한 인자 상한(131072바이트)을 넘는 한국어 프롬프트가 실제 하위
    # 프로세스에 손실 없이 도착한다
    child = ("import sys, json; data = sys.stdin.buffer.read().decode('utf-8'); "
             "print(json.dumps({'result': str(len(data)) + ':' + data[-3:]}))")
    monkeypatch.setattr(librarian, "_claude_cmd",
                        lambda extra, ws: [sys.executable, "-c", child])
    prompt = "가" * 200_000 + "끝표식"
    proc = librarian._run_claude_json(["--model", "m"], prompt, 60)
    assert proc is not None and proc.returncode == 0
    assert json.loads(proc.stdout)["result"] == f"{len(prompt)}:끝표식"


# ============================================================ 사서 작업 폴더

@pytest.fixture
def fake_wiki(tmp_path, monkeypatch):
    wiki = tmp_path / "repo" / "wiki"
    (wiki / "topics").mkdir(parents=True)
    (wiki / "CLAUDE.md").write_text("규약", encoding="utf-8")
    (wiki / "INDEX.md").write_text("목차", encoding="utf-8")
    (wiki / "topics" / "a.md").write_text("에이", encoding="utf-8")
    (wiki / "topics" / "b.md").write_text("비", encoding="utf-8")
    monkeypatch.setattr(librarian, "WIKI_DIR", str(wiki))
    monkeypatch.setattr(librarian, "TOPICS_DIR", str(wiki / "topics"))
    return wiki


def test_workspace_syncs_only_topic_pages(fake_wiki):
    ws = librarian._make_workspace()
    try:
        assert os.path.commonpath([ws, librarian.BASE_DIR]) != librarian.BASE_DIR
        wt = os.path.join(ws, "wiki")
        with open(os.path.join(wt, "topics", "a.md"), "w", encoding="utf-8") as f:
            f.write("에이 수정")
        with open(os.path.join(wt, "topics", "new.md"), "w", encoding="utf-8") as f:
            f.write("새 페이지")
        with open(os.path.join(wt, "CLAUDE.md"), "w", encoding="utf-8") as f:
            f.write("덮어씀")
        with open(os.path.join(wt, "INDEX.md"), "w", encoding="utf-8") as f:
            f.write("덮어씀")
        with open(os.path.join(wt, "topics", "note.txt"), "w", encoding="utf-8") as f:
            f.write("x")
        os.makedirs(os.path.join(wt, "topics", "sub"))
        with open(os.path.join(wt, "topics", "sub", "x.md"), "w", encoding="utf-8") as f:
            f.write("x")
        assert librarian._sync_topics(ws) == 2
    finally:
        import shutil
        shutil.rmtree(ws, ignore_errors=True)
    assert (fake_wiki / "topics" / "a.md").read_text(encoding="utf-8") == "에이 수정"
    assert (fake_wiki / "topics" / "new.md").read_text(encoding="utf-8") == "새 페이지"
    assert (fake_wiki / "topics" / "b.md").read_text(encoding="utf-8") == "비"
    assert (fake_wiki / "CLAUDE.md").read_text(encoding="utf-8") == "규약"
    assert (fake_wiki / "INDEX.md").read_text(encoding="utf-8") == "목차"
    assert not (fake_wiki / "topics" / "note.txt").exists()
    assert not (fake_wiki / "topics" / "sub").exists()


def test_run_librarian_uses_and_removes_workspace(fake_claude, fake_wiki):
    used = {}

    def hook(call):
        used["cwd"] = call.kw["cwd"]
        with open(os.path.join(call.kw["cwd"], "wiki", "topics", "c.md"), "w",
                  encoding="utf-8") as f:
            f.write("사서가 쓴 페이지")

    fake_claude.hook = hook
    fake_claude.stdout = _result({"verdicts": {"a": {"action": "new", "topic": "c"}}})
    out = librarian.run_librarian([{"id": "a", "title": "t"}])
    assert out == {"verdicts": {"a": {"action": "new", "topic": "c"}}}
    assert used["cwd"] != librarian.BASE_DIR
    assert not os.path.exists(used["cwd"])
    assert (fake_wiki / "topics" / "c.md").read_text(encoding="utf-8") == "사서가 쓴 페이지"


# ============================================================ 기사 fetch

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.server.hits.append(self.path)
        route = self.server.routes.get(self.path.split("?", 1)[0])
        if route is None:
            self.send_response(404)
            self.end_headers()
            return
        try:
            route(self)
        except OSError:
            pass

    def log_message(self, *args):
        pass


def _send(handler, body: bytes, ctype="text/html", status=200, headers=None):
    handler.send_response(status)
    handler.send_header("Content-Type", ctype)
    for k, v in (headers or {}).items():
        handler.send_header(k, v)
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


@pytest.fixture
def server():
    srv = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    srv.daemon_threads = True
    srv.routes = {}
    srv.hits = []
    srv.base = f"http://127.0.0.1:{srv.server_address[1]}"
    thread = threading.Thread(target=srv.serve_forever, daemon=True)
    thread.start()
    yield srv
    srv.shutdown()
    srv.server_close()


@pytest.fixture
def allow_loopback(monkeypatch):
    # 테스트 서버(127.0.0.1)만 열어 준다. 그 밖의 비공인 주소는 그대로 차단
    real = netguard.ip_blocked
    monkeypatch.setattr(netguard, "ip_blocked",
                        lambda ip: False if ip.startswith("127.") else real(ip))


ARTICLE_KO = ("<html><body><article><p>국내 대형 통신사에서 가입자 개인정보가 대량으로 "
              "유출되는 사고가 발생했다. 회사는 침해 사실을 당국에 신고했다.</p>"
              "</article></body></html>")


def test_loopback_blocked_by_default(server):
    server.routes["/ok"] = lambda h: _send(h, ARTICLE_KO.encode("utf-8"))
    with pytest.raises(netguard.BlockedAddress):
        netguard.fetch_html(server.base + "/ok", user_agent="t")
    with pytest.raises(netguard.BlockedAddress):
        netguard.fetch_html(f"http://localhost:{server.server_address[1]}/ok", user_agent="t")
    assert server.hits == []
    # card_editor 경로도 같은 차단을 거쳐 빈 본문
    assert card_editor.fetch_article(server.base + "/ok") == ""
    assert server.hits == []


def test_fetch_article_reads_local_page(server, allow_loopback):
    server.routes["/ok"] = lambda h: _send(h, ARTICLE_KO.encode("utf-8"),
                                           "text/html; charset=utf-8")
    assert "개인정보가 대량으로" in card_editor.fetch_article(server.base + "/ok")


def test_euc_kr_without_charset(server, allow_loopback):
    server.routes["/kr"] = lambda h: _send(h, ARTICLE_KO.encode("euc-kr"), "text/html")
    assert "개인정보가 대량으로 유출" in netguard.fetch_html(server.base + "/kr", user_agent="t")


def test_meta_charset_used(server, allow_loopback):
    body = ('<meta charset="euc-kr">' + ARTICLE_KO).encode("euc-kr")
    server.routes["/meta"] = lambda h: _send(h, body, "text/html")
    assert "침해 사실" in netguard.fetch_html(server.base + "/meta", user_agent="t")


def _redirect_chain(server, n):
    for i in range(1, n + 1):
        server.routes[f"/r{i}"] = (lambda nxt: lambda h: _send(
            h, b"", status=302, headers={"Location": nxt}))(f"/r{i - 1}")
    server.routes["/r0"] = lambda h: _send(h, ARTICLE_KO.encode("utf-8"))


def test_redirect_limit(server, allow_loopback):
    _redirect_chain(server, 6)
    assert "개인정보" in netguard.fetch_html(server.base + "/r5", user_agent="t")
    with pytest.raises(netguard.TooManyRedirects):
        netguard.fetch_html(server.base + "/r6", user_agent="t")


def test_redirect_to_metadata_blocked(server, allow_loopback):
    server.routes["/meta-hop"] = lambda h: _send(
        h, b"", status=302,
        headers={"Location": "http://169.254.169.254/latest/meta-data/"})
    start = time.monotonic()
    with pytest.raises(netguard.BlockedAddress):
        netguard.fetch_html(server.base + "/meta-hop", user_agent="t")
    assert time.monotonic() - start < 2


def test_slow_drip_hits_deadline(server, allow_loopback):
    def drip(h):
        h.send_response(200)
        h.send_header("Content-Type", "text/html")
        h.end_headers()
        for _ in range(60):
            h.wfile.write(b"a")
            h.wfile.flush()
            time.sleep(0.2)

    server.routes["/drip"] = drip
    start = time.monotonic()
    with pytest.raises(TimeoutError):
        netguard.fetch_html(server.base + "/drip", user_agent="t", deadline=1.5, op_timeout=5)
    assert time.monotonic() - start < 3.5


def test_stalled_server_hits_deadline(server, allow_loopback):
    server.routes["/stall"] = lambda h: time.sleep(6)
    start = time.monotonic()
    with pytest.raises(TimeoutError):
        netguard.fetch_html(server.base + "/stall", user_agent="t", deadline=1.0, op_timeout=5)
    assert time.monotonic() - start < 3


def test_size_cap(server, allow_loopback):
    body = ("<p>" + "가" * 700_000 + "</p>").encode("utf-8")
    server.routes["/big"] = lambda h: _send(h, body, "text/html; charset=utf-8")
    text = netguard.fetch_html(server.base + "/big", user_agent="t", max_bytes=50_000)
    assert 0 < len(text.encode("utf-8")) <= 50_000


def test_gzip_body_capped_and_decoded(server, allow_loopback):
    body = gzip.compress(("<p>" + "나" * 400_000 + "</p>").encode("utf-8"))
    server.routes["/gz"] = lambda h: _send(h, body, "text/html; charset=utf-8",
                                           headers={"Content-Encoding": "gzip"})
    text = netguard.fetch_html(server.base + "/gz", user_agent="t", max_bytes=30_000)
    assert text.startswith("<p>나나") and len(text.encode("utf-8")) <= 30_000


def test_falls_back_to_next_vetted_address(server, allow_loopback, monkeypatch):
    # 첫 주소 연결이 실패하면(IPv6 경로 없는 러너 등) 검사를 통과한 다음 주소로
    import socket
    port = server.server_address[1]
    monkeypatch.setattr(netguard.socket, "getaddrinfo", lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.2", port + 1)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("127.0.0.1", port)),
    ])
    server.routes["/ok"] = lambda h: _send(h, ARTICLE_KO.encode("utf-8"))
    assert "개인정보" in netguard.fetch_html(f"http://multi.test:{port}/ok", user_agent="t")
    assert server.hits == ["/ok"]


def test_any_blocked_address_rejects_host(monkeypatch):
    import socket
    monkeypatch.setattr(netguard.socket, "getaddrinfo", lambda *a, **k: [
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 80)),
        (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", 80)),
    ])
    with pytest.raises(netguard.BlockedAddress):
        netguard.fetch_html("http://rebind.test/", user_agent="t")


def test_non_html_is_empty(server, allow_loopback):
    server.routes["/json"] = lambda h: _send(h, b"{}", "application/json")
    assert netguard.fetch_html(server.base + "/json", user_agent="t") == ""


@pytest.mark.parametrize("ip", ["127.0.0.1", "10.1.2.3", "172.16.0.1", "192.168.1.1",
                                "169.254.169.254", "100.64.0.1", "0.0.0.0", "224.0.0.1",
                                "::1", "fe80::1", "fd00::1", "::ffff:10.0.0.1"])
def test_non_public_ips_blocked(ip):
    assert netguard.ip_blocked(ip)


@pytest.mark.parametrize("ip", ["8.8.8.8", "1.1.1.1", "2606:4700:4700::1111"])
def test_public_ips_allowed(ip):
    assert not netguard.ip_blocked(ip)


# ============================================================ 링크 URL 검증

@pytest.mark.parametrize("url", [
    "https://example.com/a?b=1&c=(2)",
    "http://news.example.co.kr/기사/1",
])
def test_safe_link_urls(url):
    assert netguard.is_safe_link_url(url)


@pytest.mark.parametrize("url", [
    "javascript:alert(1)", "ftp://a.com/x", "", None, "https://",
    "https://a.com/x> [가짜](https://evil.example)", "https://a.com/<x", "https://a.com/a b",
    "https://a.com/\tx", "https://a.com/\nx", "https://a.com/‮x", "https://a.com/\x00",
])
def test_unsafe_link_urls(url):
    assert not netguard.is_safe_link_url(url)


def test_link_lines_drop_unsafe_url_but_keep_numbering():
    items = [
        {"title_ko": "정상 제목", "url": "https://a.com/x"},
        {"title_ko": "주입 제목", "url": "https://a.com/x> [가짜](https://evil.example)"},
        {"title_ko": "공백 제목", "url": "https://a.com/a b"},
    ]
    lines = cardgen.build_link_lines(items, [], [])
    assert lines == ["1. [정상 제목](<https://a.com/x>)", "2. 주입 제목", "3. 공백 제목"]
    fatal, _ = preflight.check_card_news([b"png"] * 3, lines, [
        {"id": str(i), "title_ko": it["title_ko"], "summary_ko": "요약이다.", "url": it["url"]}
        for i, it in enumerate(items)], "총평이다.", {})
    assert any("원문 링크 없는 줄" in f for f in fatal)


def test_digest_embed_drops_unsafe_link():
    item = {"title": "제목", "source": "출처", "tags": [],
            "url": "https://a.com/x> [가짜](https://evil.example)"}
    desc = notify._build_digest_embed("news", [item], {})["description"]
    assert "evil.example" not in desc and "**제목**" in desc


# ============================================================ preflight 비밀값

@pytest.mark.parametrize("text,label", [
    ("https://discord.com/api/webhooks/123/abcDEF", "Discord 웹훅"),
    ("https://discordapp.com/api/v10/webhooks/1/x", "Discord 웹훅"),
    ("토큰 ghp_" + "a1B2" * 9, "GitHub 토큰"),
    ("github_pat_" + "A1b2_" * 6, "GitHub 토큰"),
    ("gho_" + "z" * 36, "GitHub 토큰"),
    ("sk-ant-oat01-" + "x" * 40, "Anthropic 토큰"),
    ("sk-ant-api03-" + "Y" * 40, "Anthropic 토큰"),
    ("Authorization: Bearer abcdefghijklmnopqrstuvwxyz012345", "Bearer 토큰"),
    ("AUTHORIZATION: basic eC1hY2Nlc3MtdG9rZW46Z2hzX3h4eA==", "Authorization 헤더"),
])
def test_secret_patterns(text, label):
    assert label in preflight.find_secrets([text])


def test_clean_text_has_no_secret():
    texts = ["국내 통신사 개인정보 유출 사고가 발생했다.", "1. [제목](<https://a.com/x>)",
             "bearer tokens were abused", "GitHub 토큰 유출 사고"]
    assert preflight.find_secrets(texts) == []


def test_env_secret_value_detected(monkeypatch):
    monkeypatch.setenv("NVD_API_KEY", "nvd-secret-value-1234")
    assert preflight.find_secrets(["본문 nvd-secret-value-1234 끝"]) == ["환경변수 비밀값"]


def test_card_text_secret_is_fatal_without_echo():
    token = "ghp_" + "Q" * 36
    items = [{"id": "a", "title_ko": "제목이다", "summary_ko": f"요약 {token} 이다.",
              "url": "https://a.com/x"}]
    fatal, _ = preflight.check_card_news([b"png"] * 3, ["1. [제목](<https://a.com/x>)"],
                                         items, "총평이다.", {})
    msgs = [f for f in fatal if "비밀값" in f]
    assert msgs and token not in msgs[0]
