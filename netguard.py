"""외부 URL 안전 처리. 링크 검증과 기사 본문 fetch.

링크 검증(is_safe_link_url): Discord 링크 줄은 [라벨](<url>) 형식이다.
url 속 '<', '>', 공백, 제어 문자는 <> 감싸기를 끊어 가짜 링크를 만든다.
http/https이고 이런 문자가 없을 때만 통과한다. cardgen.build_link_lines와
notify의 링크 줄이 같은 함수를 쓴다.

기사 fetch(fetch_html): 피드의 기사 URL은 신뢰할 수 없는 입력이다.
- hop마다 호스트를 직접 해석해 공인 주소가 아니면 연결하지 않는다.
  사설, 루프백, 링크로컬(클라우드 메타데이터 169.254.169.254 포함),
  CGNAT, 예약, 멀티캐스트 주소가 대상이다.
- 해석한 그 주소로 연결한다. 연결 시점에 다시 해석하지 않으므로 DNS
  rebinding으로 검사를 우회할 수 없다. HTTPS는 원래 호스트명으로 SNI와
  인증서 검증을 한다.
- 리다이렉트는 자동으로 따라가지 않고 직접 최대 5회 따라간다.
- 기사당 전체 마감(기본 15초)을 감시 타이머로 강제한다. 마감이 지나면
  소켓을 끊는다. 소켓 연산마다 개별 시간 상한도 둔다.
- 본문은 크기 상한까지만 읽는다. gzip 해제 결과에도 같은 상한을 건다.
- 헤더에 charset이 없으면 meta charset, UTF-8, 추정 순으로 디코딩한다.
  requests는 charset 없는 text/html을 ISO-8859-1로 보아 한국어가 깨졌다.
"""
import codecs
import http.client
import ipaddress
import re
import socket
import ssl
import threading
import time
import unicodedata
import zlib
from urllib.parse import urljoin, urlsplit

MAX_REDIRECTS = 5
DEFAULT_DEADLINE = 15.0
DEFAULT_OP_TIMEOUT = 10.0
DEFAULT_MAX_BYTES = 3_000_000
_READ_CHUNK = 65536
_REDIRECT_CODES = {301, 302, 303, 307, 308}

_CT_CHARSET_RE = re.compile(r"charset\s*=\s*[\"']?\s*([A-Za-z0-9_\-:.]+)", re.I)
_META_CHARSET_RE = re.compile(rb"<meta[^>]+charset\s*=\s*[\"']?\s*([A-Za-z0-9_\-:.]+)", re.I)
# 브라우저(WHATWG Encoding) 기준 대체. EUC-KR 라벨은 실제로 cp949로 읽어야
# 확장 한글이 깨지지 않는다
_ENCODING_OVERRIDES = {"euc_kr": "cp949", "iso8859-1": "cp1252", "ascii": "cp1252"}


class BlockedAddress(Exception):
    """공인 주소가 아닌 곳으로 가는 요청."""


class TooManyRedirects(Exception):
    """리다이렉트 상한 초과."""


class DeadlineExceeded(TimeoutError):
    """기사당 전체 마감 초과."""


# ------------------------------------------------------------ 링크 검증

def is_safe_link_url(url) -> bool:
    """Discord 마크다운 링크에 넣어도 되는 URL인지."""
    if not isinstance(url, str) or not url.startswith(("http://", "https://")):
        return False
    for ch in url:
        if ch in "<>" or ch.isspace() or unicodedata.category(ch) in ("Cc", "Cf"):
            return False
    try:
        return bool(urlsplit(url).hostname)
    except ValueError:
        return False


# ------------------------------------------------------------ 주소 검사

def ip_blocked(ip_text: str) -> bool:
    """공인 유니캐스트 주소가 아니면 True."""
    try:
        ip = ipaddress.ip_address(ip_text.split("%", 1)[0])
    except ValueError:
        return True
    if ip.version == 6 and ip.ipv4_mapped is not None:
        ip = ip.ipv4_mapped
    return (not ip.is_global) or ip.is_multicast


def _resolve(host: str, port: int, timeout: float) -> list[str]:
    """호스트를 해석해 연결할 주소 목록을 돌려준다. 해석된 주소 중 하나라도
    차단 대상이면 거부한다. getaddrinfo에는 시간 상한이 없어 데몬 스레드로
    돌리고 timeout만 기다린다."""
    box: dict = {}

    def work():
        try:
            box["infos"] = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        except OSError as exc:
            box["error"] = exc

    worker = threading.Thread(target=work, daemon=True)
    worker.start()
    worker.join(timeout)
    if worker.is_alive():
        raise DeadlineExceeded("DNS 해석 시간 초과")
    if "error" in box:
        raise box["error"]
    addrs = list(dict.fromkeys(info[4][0] for info in box.get("infos", [])))
    if not addrs:
        raise BlockedAddress("해석 결과 없음")
    if any(ip_blocked(a) for a in addrs):
        raise BlockedAddress("공인 주소가 아님")
    return addrs


# ------------------------------------------------------------ 연결

class _Deadline:
    """전체 마감 감시. 마감 시각에 현재 소켓을 끊어 막힌 읽기를 풀어 준다."""

    def __init__(self, seconds: float):
        self.end = time.monotonic() + seconds
        self.sock = None
        self._timer = threading.Timer(max(0.0, seconds), self._fire)
        self._timer.daemon = True
        self._timer.start()

    def remaining(self) -> float:
        left = self.end - time.monotonic()
        if left <= 0:
            raise DeadlineExceeded("기사당 마감 초과")
        return left

    def _fire(self):
        sock = self.sock
        if sock is not None:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass

    def cancel(self):
        self._timer.cancel()


class _PinnedConnection(http.client.HTTPConnection):
    """검사를 통과한 IP로만 연결한다. 주소가 여럿이면 차례로 시도한다
    (IPv6 경로가 없는 러너 대비). TLS는 원래 호스트명으로 검증한다."""

    def __init__(self, ips, port, timeout, deadline, tls_context=None, server_hostname=None):
        super().__init__(ips[0], port, timeout=timeout)
        self._ips = ips
        self._deadline = deadline
        self._tls_context = tls_context
        self._server_hostname = server_hostname

    def _connect_any(self):
        last = None
        for ip in self._ips:
            try:
                return socket.create_connection(
                    (ip, self.port), min(self.timeout, self._deadline.remaining()))
            except OSError as exc:
                last = exc
        raise last

    def connect(self):
        raw = self._connect_any()
        self._deadline.sock = raw
        sock = raw
        if self._tls_context is not None:
            try:
                sock = self._tls_context.wrap_socket(raw, server_hostname=self._server_hostname)
            except Exception:
                raw.close()
                raise
            self._deadline.sock = sock
        self.sock = sock


_TLS_CONTEXT = None


def _tls_context() -> ssl.SSLContext:
    global _TLS_CONTEXT
    if _TLS_CONTEXT is None:
        try:
            import certifi
            _TLS_CONTEXT = ssl.create_default_context(cafile=certifi.where())
        except ImportError:
            _TLS_CONTEXT = ssl.create_default_context()
    return _TLS_CONTEXT


def _request_target(parts) -> str:
    from requests.utils import requote_uri  # requests와 같은 퍼센트 인코딩
    target = parts.path or "/"
    if parts.query:
        target += "?" + parts.query
    return requote_uri(target)


def _open(url: str, deadline: _Deadline, op_timeout: float, user_agent: str):
    """한 hop 요청. (conn, resp)를 돌려준다. 본문은 읽지 않는다."""
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    if scheme not in ("http", "https") or not parts.hostname:
        raise BlockedAddress("http/https 아님")
    host = parts.hostname.encode("idna").decode("ascii")
    port = parts.port or (443 if scheme == "https" else 80)
    ips = _resolve(host, port, min(op_timeout, deadline.remaining()))

    host_header = f"[{host}]" if ":" in host else host
    if port != (443 if scheme == "https" else 80):
        host_header += f":{port}"
    conn = _PinnedConnection(
        ips, port, timeout=min(op_timeout, deadline.remaining()), deadline=deadline,
        tls_context=_tls_context() if scheme == "https" else None,
        server_hostname=host if scheme == "https" else None,
    )
    try:
        conn.request("GET", _request_target(parts), headers={
            "Host": host_header,
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
        })
        conn.sock.settimeout(min(op_timeout, deadline.remaining()))
        resp = conn.getresponse()
    except Exception:
        conn.close()
        raise
    return conn, resp


def _read_body(conn, resp, deadline: _Deadline, op_timeout: float, max_bytes: int) -> bytes:
    encoding = (resp.getheader("Content-Encoding") or "").strip().lower()
    if encoding in ("", "identity"):
        inflater = None
    elif encoding in ("gzip", "x-gzip", "deflate"):
        # gzip과 zlib 머리를 자동 판별
        inflater = zlib.decompressobj(zlib.MAX_WBITS | 32)
    else:
        raise ValueError(f"지원하지 않는 Content-Encoding: {encoding}")

    sock = conn.sock or deadline.sock
    out = bytearray()
    # 본문을 다 읽으면 http.client가 소켓을 닫는다. 닫힌 뒤에는 멈춘다
    while len(out) < max_bytes and not resp.isclosed():
        if sock is not None:
            sock.settimeout(min(op_timeout, deadline.remaining()))
        chunk = resp.read1(_READ_CHUNK)
        if not chunk:
            break
        if inflater is not None:
            chunk = inflater.decompress(chunk, max_bytes - len(out))
        out += chunk
    # 감시 타이머가 소켓을 끊으면 읽기는 EOF처럼 끝난다. 시각으로 다시 가린다
    deadline.remaining()
    return bytes(out[:max_bytes])


# ------------------------------------------------------------ 디코딩

def _normalize_encoding(name):
    if not name:
        return None
    try:
        norm = codecs.lookup(name.strip().strip("\"'")).name
    except LookupError:
        return None
    return _ENCODING_OVERRIDES.get(norm, norm)


def _guess_encoding(body: bytes):
    try:
        from charset_normalizer import from_bytes
    except ImportError:
        return None
    best = from_bytes(body[:200_000]).best()
    return _normalize_encoding(best.encoding) if best else None


def _decode(body: bytes, encoding: str, errors: str = "replace") -> str:
    # final=False: 크기 상한에서 잘린 마지막 멀티바이트 조각은 버린다
    return codecs.getincrementaldecoder(encoding)(errors).decode(body, final=False)


def decode_html(body: bytes, content_type: str = "") -> str:
    """BOM, 헤더 charset, meta charset, UTF-8, 추정 순으로 디코딩."""
    if body.startswith(codecs.BOM_UTF8):
        return _decode(body[len(codecs.BOM_UTF8):], "utf-8")
    header = _CT_CHARSET_RE.search(content_type or "")
    meta = _META_CHARSET_RE.search(body[:4096])
    for label in (header.group(1) if header else None,
                  meta.group(1).decode("ascii", "ignore") if meta else None):
        enc = _normalize_encoding(label)
        if enc:
            return _decode(body, enc)
    try:
        return _decode(body, "utf-8", "strict")
    except UnicodeDecodeError:
        pass
    return _decode(body, _guess_encoding(body) or "cp949")


# ------------------------------------------------------------ fetch

def fetch_html(url: str, *, user_agent: str, deadline: float = DEFAULT_DEADLINE,
               op_timeout: float = DEFAULT_OP_TIMEOUT, max_bytes: int = DEFAULT_MAX_BYTES,
               max_redirects: int = MAX_REDIRECTS) -> str:
    """HTML 본문 텍스트. 200이 아니거나 HTML이 아니면 빈 문자열.
    차단, 마감 초과, 리다이렉트 초과, 네트워크 오류는 예외로 올린다."""
    clock = _Deadline(deadline)
    try:
        current = url
        for _ in range(max_redirects + 1):
            conn, resp = _open(current, clock, op_timeout, user_agent)
            try:
                if resp.status in _REDIRECT_CODES:
                    location = resp.getheader("Location")
                    if not location:
                        return ""
                    current = urljoin(current, location.strip())
                    continue
                content_type = resp.getheader("Content-Type") or ""
                if resp.status != 200 or "html" not in content_type.lower():
                    return ""
                body = _read_body(conn, resp, clock, op_timeout, max_bytes)
                return decode_html(body, content_type)
            finally:
                resp.close()
                conn.close()
        raise TooManyRedirects(f"리다이렉트 {max_redirects}회 초과")
    except (DeadlineExceeded, BlockedAddress, TooManyRedirects):
        raise
    except Exception as exc:
        # 감시 타이머가 소켓을 끊으면 읽기 쪽 예외 종류가 제각각이다
        if time.monotonic() >= clock.end:
            raise DeadlineExceeded("기사당 마감 초과") from exc
        raise
    finally:
        clock.cancel()
