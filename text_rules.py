"""카드 문안 공용 규칙. card_editor, tagger, trend_enrich가 함께 쓴다.

2026-11-20 QA(docs/qa/2026-11-20-qa-results.md C1 C3 C4 C5 C6 C10 C11 C12)
에서 실측한 규칙이다.
- 영어 누출: 한글이 끊는 라틴 단어 연속 구간을 본다(한글 비율 대신)
- 원문 복사: 원문과 60자 이상 같은 구간
- 용어 실체명: 라틴 토큰 허용 목록, 한글 기관 접미사와 고유명, 설명 끝 실체 명사
- 키워드 매처: 태그 규칙과 태그 근거 검사가 같은 매처를 쓴다
- 태그 근거: 원문 문자열 또는 한영 동의어 표
"""
import html
import re
from functools import lru_cache

HANGUL_RE = re.compile(r"[가-힣]")


def hangul_count(text) -> int:
    return len(HANGUL_RE.findall(text)) if isinstance(text, str) else 0


# ------------------------------------------------------------ 보안 약어

# 소문자 비교. 용어 이름의 라틴 토큰 허용 목록이자 영어 누출 판정의 예외
SEC_ACRONYMS = frozenset("""
rce edr xdr mdr ndr siem soar soc xss csrf ssrf sqli sql xxe lfi rfi idor sbom kev cvss
cve cwe epss mfa 2fa otp ddos dos c2 cnc apt ioc ttp ttps api ai llm sso saml oauth oidc
jwt imsi imei sim usim esim vpn ztna sase waf ids ips dlp pki tls ssl dns bgp rdp smb isms
isms-p csap gdpr iot ics ot scada plc uefi bios tpm mitm aitm bec raas iab poc cti dmarc
spf dkim fido fido2 nac casb cspm cnapp devsecops byod mdm hsm kms rbac abac pam iam lotl
uaf ssti rag mcp nfc rfid gps ota usb id url ip http https html pdf qr sms os dbms db cpu
gpu ssh ftp smtp ldap ad ntlm yara osint
tcp udp mptcp quic ipsec ike wpa wpa2 wpa3 wifi ble lte 5g ss7 sip voip imap snmp ntp dhcp
arp icmp vlan nat cdn ca crl ocsp hsts csp cors aslr cfi rop tee sgx vm ueba mssp grc
isac cert csirt psirt itsm rat vdp
""".split())


# ------------------------------------------------------------ 영어 누출

# 소문자로 시작해도 고유명사인 표기(제품, 명령)
LOWER_ALLOW = frozenset("""
iOS iPadOS macOS watchOS tvOS visionOS iPhone iPad iCloud npm pip curl sudo vCenter vSphere
eSIM eBPF iframe kubectl cgroup glibc openssh openssl systemd wget x86 arm64 jQuery pdf exe
dll js py
""".split())

# 영어 산문 표지어(기능어와 보안 뉴스 상투어). 대소문자 무시
EN_PROSE = frozenset("""
a an the of in on at to for from with by as is are was were be been being has have had
it its this that these those and or but not no via after before over under into about against
than then which who whom whose what when where why how will would can could may might should must
do does did new says said warns warn urges patch patches patched fixes fixed exploit exploits exploited
exploiting hackers hacker attackers attacker attack attacks breach breaches breached flaw flaws
vulnerability vulnerabilities critical actively users million billion data leak leaked stolen steal
steals targets targeting targeted campaign campaigns linked behind claims claim discloses disclosed
release released launches launched report reports reported researchers found finds discover discovered
uncover uncovered abuse abused abusing spread spreads spreading deploy deploys deployed allows allow
enable enables lets let gain gains bypass bypasses remote code execution security update updates
""".split())

# 고유명사 사이를 잇는 기능어
GLUE = frozenset("for of and on the by to in with over at a an or via".split())

_STRIP = "*`'\"“”‘’()[]{}<>,.:;!?…—–-/|"
_LATIN_WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9.+'’&_/-]*")
_LOWER_WORD_RE = re.compile(r"[a-z][a-z'’-]*[a-z]")


def _tokens(text: str) -> list[str]:
    out = []
    for raw in (text or "").replace("**", " ").split():
        tok = raw.strip(_STRIP)
        if tok:
            out.append(tok)
    return out


def latin_runs(text: str) -> list[list[str]]:
    """한글 토큰이 끊는 라틴 단어 연속 구간들. 숫자만인 토큰은 끊지도 세지도 않는다."""
    runs, cur = [], []
    for tok in _tokens(text):
        if HANGUL_RE.search(tok):
            if cur:
                runs.append(cur)
            cur = []
        elif _LATIN_WORD_RE.fullmatch(tok):
            cur.append(tok)
    if cur:
        runs.append(cur)
    return runs


def _plain_lower(tok: str) -> bool:
    """허용 목록 밖 소문자 단어(영어 산문의 내용어)."""
    return (tok.isalpha() and tok.islower() and len(tok) >= 2
            and tok not in LOWER_ALLOW and tok not in SEC_ACRONYMS)


def _is_prose(tok: str) -> bool:
    return tok.lower() in EN_PROSE or _plain_lower(tok)


def english_leak_title(text: str) -> bool:
    """제목용. 라틴 3단어 이상 연속 구간에 기능어, 상투어, 허용 밖 소문자 단어가
    하나라도 있으면 영어 원제 누출."""
    return any(len(run) >= 3 and any(_is_prose(t) for t in run)
               for run in latin_runs(text))


def english_leak_prose(text: str) -> bool:
    """요약, why, CVE 설명, 트렌드 설명용. 라틴 3단어 이상 구간에 허용 밖
    소문자 내용어가 있거나 소문자 기능어 2개 이상이거나 대문자 상투어 3개 이상,
    또는 라틴 2단어 이상 구간에 소문자 내용어 2개 이상이면 영어 구 삽입."""
    for run in latin_runs(text):
        if len(run) >= 3:
            content = [t for t in run if _plain_lower(t) and t not in GLUE]
            glue = [t for t in run if t in GLUE]
            cliche = [t for t in run if not t.islower() and t.lower() in EN_PROSE
                      and t.lower() not in GLUE]
            if content or len(glue) >= 2 or len(cliche) >= 3:
                return True
        if len(run) >= 2:
            lower = [t for t in run if _LOWER_WORD_RE.fullmatch(t) and t not in GLUE
                     and t not in LOWER_ALLOW and t.lower() not in SEC_ACRONYMS]
            if len(lower) >= 2:
                return True
    return False


# ------------------------------------------------------------ 원문 복사

COPY_MIN_CHARS = 60
_TAG_RE = re.compile(r"<[^>]+>")


def _norm_copy(text) -> str:
    if not isinstance(text, str):
        return ""
    t = html.unescape(_TAG_RE.sub(" ", text))
    return " ".join(t.replace("**", "").split())


def copies_source(text, sources, min_len: int = COPY_MIN_CHARS) -> bool:
    """text가 sources 중 하나와 min_len자 이상 같은 구간을 가지면 True."""
    t = _norm_copy(text)
    srcs = [s for s in (_norm_copy(x) for x in sources) if len(s) >= min_len]
    if len(t) < min_len or not srcs:
        return False
    return any(t[i:i + min_len] in s
               for i in range(len(t) - min_len + 1) for s in srcs)


# ------------------------------------------------------------ 용어 실체명

# 한글 이름이 이것으로 끝나면 기관, 기업. 두 글자 이상만(한 글자는 '서비스거부' 같은 용어를 자른다)
KO_ORG_SUFFIXES = (
    "위원회", "공사", "공단", "재단", "협회", "은행", "연구원", "보안원", "진흥원", "감독원",
    "정보원", "주식회사", "공제", "경찰청", "검찰청", "사업청", "수사국", "안보국", "정보국",
    "보안청", "정통부", "안전부", "국방부", "법무부", "통신부", "산업부", "벤처부", "전자",
    "텔레콤", "유플러스", "카드사", "생명", "증권", "거래소", "그룹", "센터", "본부", "방통위",
    "국정원", "과기부", "개보위", "금감원", "금보원", "경찰", "검찰", "정부",
)
# 접미사로 안 잡히는 한글 고유명사. 이름이 이것으로 시작해도 거부
KO_PROPER_NOUNS = frozenset((
    "쿠팡", "네이버", "카카오", "토스", "배민", "당근", "야놀자", "인터파크", "예스24",
    "알리익스프레스", "테무", "라자루스", "김수키", "안다리엘", "블루노로프", "코니", "록빗",
    "클롭", "아키라", "노란우산",
))
# 설명 끝 명사가 이것이면 실체(기관, 기업, 조직, 제품)를 설명한 것
DESC_ENTITY_HEADS = (
    "기관", "기구", "부처", "기업", "회사", "업체", "제조사", "개발사", "운영사", "통신사",
    "사업자", "카드사", "은행", "그룹", "조직", "단체", "집단", "위원회", "정보원", "진흥원",
    "보안원", "감독원", "연구원", "연구소", "포털", "브랜드", "제품", "서비스", "플랫폼",
    "운영체제", "브라우저", "라이브러리", "서점", "수사국", "안보국", "보안청", "경찰", "정부",
    "센터", "비서", "핀테크",
)
_TERM_LATIN_RE = re.compile(r"[A-Za-z0-9]+(?:-[A-Za-z0-9]+)*")


def _desc_head(desc: str) -> str:
    d = re.sub(r"[.\s]+$", "", desc)
    d = re.sub(r"(이다|입니다|이에요|다)$", "", d)
    d = re.split(r"[,，]", d)[-1].strip()
    toks = d.split()
    return toks[-1] if toks else ""


def _latin_token_ok(tok: str) -> bool:
    low = tok.lower()
    if low.isdigit() or low in SEC_ACRONYMS:
        return True
    return all(p.isdigit() or p in SEC_ACRONYMS for p in low.split("-"))


def term_entity_reason(name: str, desc: str) -> str | None:
    """용어 이름과 설명이 기관, 기업, 그룹, 제품 같은 실체면 거부 사유. 보안 용어면 None.
    term_type 없이 내용만으로 판정한다."""
    bare = re.sub(r"\(.*?\)", "", name).strip()
    for tok in _TERM_LATIN_RE.findall(bare):
        if not _latin_token_ok(tok):
            return f"라틴 고유명사 {tok}"
    ko = re.sub(r"[^가-힣0-9]", "", bare)
    if ko in KO_PROPER_NOUNS or any(ko.startswith(e) for e in KO_PROPER_NOUNS):
        return "한글 고유명사"
    if any(ko.endswith(s) for s in KO_ORG_SUFFIXES):
        return "기관 접미사"
    head = _desc_head(desc)
    if head == "청" or any(head.endswith(h) for h in DESC_ENTITY_HEADS):
        return f"설명이 실체 {head}"
    return None


# ------------------------------------------------------------ 키워드 매처

# 뒤에 번호가 붙어도 같은 말인 접두(APT29, UNC3886, CVE-2026)
_DIGIT_TAIL_PREFIXES = frozenset(("apt", "unc", "ta", "fin", "storm", "cve", "cwe", "ms", "kb"))
# 한글 키워드가 다른 낱말 안에 들어 있는 경우(페이지, 인터페이스, 딥페이크)
_KO_COLLISIONS = {"페이": ("페이지", "페이스", "페이크", "페이로드", "페이퍼")}


@lru_cache(maxsize=None)
def keyword_matcher(keyword: str):
    """키워드 → text를 받아 bool을 돌려주는 함수. 태그 규칙과 태그 근거 검사 공용.

    영문: 단어 경계, 하이픈과 공백 동치, 복수형 s/es, 숫자 꼬리는 그룹 번호
    접두만. 전부 대문자로 쓴 키워드(APT, RCE, LLM, C2, ATM)는 대소문자를
    구분한다. 소문자 apt는 패키지 관리자, atm은 함수명이다.
    한글: 부분 문자열. 키워드의 공백만 있어도 없어도 되고('원격 코드'가
    원격코드실행에 맞는다) 본문 공백은 메우지 않는다('제로 데이터'는 제로데이가
    아니다). 충돌어 안의 일치는 버린다."""
    kw = " ".join(keyword.split())
    if not kw:
        return lambda text: False
    parts = [re.escape(p) for p in re.split(r"[-\s]+", kw) if p]
    if kw.isascii():
        tail = r"(?:e?s)?"
        if kw.lower() in _DIGIT_TAIL_PREFIXES:
            tail += r"(?:-?\d+)?"
        pattern = re.compile(
            rf"(?<![A-Za-z0-9_]){r'[-\s]?'.join(parts)}{tail}(?![A-Za-z0-9_])",
            0 if kw.isupper() else re.I)
        return lambda text: bool(pattern.search(text or ""))
    pattern = re.compile(r"\s?".join(parts), re.I)
    bad = _KO_COLLISIONS.get(kw.replace(" ", "").lower(), ())

    def match(text) -> bool:
        hay = text or ""
        return any(not any(hay.startswith(b, m.start()) for b in bad)
                   for m in pattern.finditer(hay))
    return match


def any_keyword(keywords, text: str) -> bool:
    return any(keyword_matcher(k)(text) for k in keywords)


# ------------------------------------------------------------ 태그 근거

# 영문 태그 조각 → 원문 근거 키워드(대문자 키)
LATIN_TAG_EVIDENCE = {
    "RCE": ("RCE", "remote code execution", "remote code", "원격 코드"),
    "APT": ("APT", "advanced persistent", "state-sponsored", "nation-state", "state-backed",
            "government-backed", "state-linked", "China-nexus", "Lazarus", "Kimsuky", "Andariel",
            "BlueNoroff", "Chollima", "Typhoon", "Fancy Bear", "Cozy Bear", "국가배후", "국가 배후"),
    "LLM": ("LLM", "language model", "언어 모델"),
    "AI": ("AI", "artificial intelligence", "LLM", "GenAI", "generative", "machine learning",
           "인공지능", "생성형"),
    "RAAS": ("RaaS", "ransomware-as-a-service", "서비스형 랜섬웨어"),
    "C2": ("C2", "C&C", "command and control", "command-and-control", "명령제어"),
    "MFA": ("MFA", "2FA", "multi-factor", "multifactor", "two-factor", "다중 인증",
            "2단계 인증"),
    "XSS": ("XSS", "cross-site scripting", "크로스사이트"),
    "CSRF": ("CSRF", "cross-site request forgery"),
    "SSRF": ("SSRF", "server-side request forgery"),
    "DDOS": ("DDoS", "denial of service", "denial-of-service", "디도스", "서비스 거부"),
    "ICS": ("ICS", "industrial control", "SCADA", "PLC", "OT", "산업제어", "제어시스템"),
    "OT": ("OT", "operational technology", "ICS", "SCADA", "PLC", "산업제어"),
    "VPN": ("VPN", "SSL-VPN", "가상사설망"),
    "SQL": ("SQL", "SQLi"),
    "BEC": ("BEC", "business email compromise"),
    "CA": ("CA", "certificate authority", "certification authority"),
    "CI": ("CI", "continuous integration"),
    "CD": ("CD", "continuous delivery", "continuous deployment"),
}

# 한글 태그 조각 → 원문 근거 키워드. 조각 자신도 근거로 친다(국문 기사)
KO_TAG_EVIDENCE = {
    "랜섬웨어": ("ransomware", "RaaS"),
    "서비스형랜섬웨어": ("ransomware-as-a-service", "RaaS"),
    "악성코드": ("malware", "malicious", "trojan", "backdoor", "loader", "stealer", "RAT",
                 "worm", "virus", "멀웨어"),
    "멀웨어": ("malware", "악성코드"),
    "트로이목마": ("trojan",),
    "백도어": ("backdoor",),
    "루트킷": ("rootkit",),
    "봇넷": ("botnet",),
    "인포스틸러": ("infostealer", "info-stealer", "stealer", "information stealer"),
    "스틸러": ("stealer", "infostealer"),
    "스파이웨어": ("spyware",),
    "와이퍼": ("wiper",),
    "로더": ("loader",),
    "웹셸": ("web shell", "webshell", "웹쉘"),
    "웹쉘": ("web shell", "webshell", "웹셸"),
    "키로거": ("keylogger",),
    "크립토재킹": ("cryptojacking", "cryptominer", "miner"),
    "피싱": ("phishing", "phish", "lure"),
    "스미싱": ("smishing", "SMS"),
    "보이스피싱": ("vishing", "voice phishing"),
    "큐싱": ("quishing", "QR"),
    "스피어피싱": ("spear-phishing", "spear phishing"),
    "사회공학": ("social engineering",),
    "사칭": ("impersonation", "impersonating", "impersonate", "impersonated", "spoof",
             "spoofing", "spoofed", "fake", "posing", "masquerading", "위장"),
    "위장": ("disguised", "masquerading", "masquerade", "fake", "posing", "impersonating",
             "사칭"),
    "가짜": ("fake", "bogus", "counterfeit", "rogue"),
    "딥페이크": ("deepfake",),
    "제로데이": ("zero-day", "0-day"),
    "공급망": ("supply chain", "supply-chain", "third-party", "dependency", "dependencies"),
    "오픈소스": ("open source", "open-source", "GitHub", "npm", "PyPI"),
    "패키지": ("package", "npm", "PyPI"),
    "크리덴셜": ("credential", "password", "login"),
    "스터핑": ("stuffing",),
    "자격증명": ("credential", "password", "login", "크리덴셜"),
    "계정정보": ("credential", "password", "login", "account"),
    "비밀번호": ("password", "passphrase", "패스워드"),
    "패스워드": ("password", "비밀번호"),
    "계정": ("account", "login", "credential"),
    "탈취": ("steal", "stole", "stolen", "stealing", "theft", "hijack", "hijacked",
             "hijacking", "exfiltration", "exfiltrated", "takeover", "take over", "harvest",
             "harvesting"),
    "유출": ("leak", "leaked", "leaking", "breach", "breached", "exposed", "exposure",
             "stolen", "exfiltration", "exfiltrated", "dump", "dumped"),
    "침해": ("breach", "breached", "compromise", "compromised", "intrusion", "hacked",
             "break in", "broke into", "broken into", "infiltrated"),
    "해킹": ("hack", "hacked", "hacker", "hacking", "breach", "breached", "compromise",
             "compromised", "intrusion", "break in", "broke into"),
    "해커": ("hacker", "threat actor", "attacker", "cybercriminal"),
    "개인정보": ("personal information", "personal data", "personal details", "PII",
                 "customer data", "customer information", "customer records", "user data",
                 "data breach", "고객정보"),
    "고객정보": ("customer data", "customer information", "customer records", "개인정보"),
    "고객": ("customer", "client", "subscriber"),
    "가입자": ("subscriber", "member", "customer", "user"),
    "인증": ("authentication", "authenticate", "auth", "login", "credential"),
    "우회": ("bypass", "bypassed", "bypassing", "circumvent", "evade", "evasion"),
    "권한상승": ("privilege escalation", "elevation of privilege", "escalate privileges",
                 "권한 상승"),
    "권한": ("privilege", "permission", "admin", "administrator", "root"),
    "원격코드실행": ("remote code execution", "RCE", "원격 코드"),
    "원격": ("remote",),
    "코드실행": ("code execution", "execute arbitrary code", "RCE"),
    "명령삽입": ("command injection", "OS command"),
    "명령어삽입": ("command injection", "OS command"),
    "인젝션": ("injection", "삽입"),
    "삽입": ("injection", "inject", "injected", "인젝션"),
    "프롬프트": ("prompt",),
    "탈옥": ("jailbreak",),
    "에이전트": ("agent", "agentic"),
    "인공지능": ("AI", "artificial intelligence", "LLM", "machine learning"),
    "생성형": ("generative", "GenAI", "LLM"),
    "언어모델": ("language model", "LLM"),
    "모델": ("model", "LLM"),
    "챗봇": ("chatbot", "ChatGPT", "assistant"),
    "클라우드": ("cloud", "AWS", "Azure", "GCP", "SaaS"),
    "컨테이너": ("container", "Docker", "Kubernetes"),
    "쿠버네티스": ("Kubernetes", "K8s"),
    "브라우저": ("browser", "Chrome", "Firefox", "Edge", "Safari", "Chromium"),
    "확장프로그램": ("extension", "add-on"),
    "확장": ("extension", "add-on"),
    "플러그인": ("plugin", "plug-in", "extension", "add-on"),
    "워드프레스": ("WordPress",),
    "라우터": ("router",),
    "방화벽": ("firewall",),
    "이메일": ("email", "e-mail", "mail", "Outlook", "Gmail", "메일"),
    "메일": ("email", "e-mail", "mail", "Outlook", "Gmail", "이메일"),
    "메신저": ("messenger", "WhatsApp", "Telegram", "Signal", "KakaoTalk", "카카오톡"),
    "모바일": ("mobile", "smartphone", "phone", "Android", "iOS", "iPhone"),
    "스마트폰": ("smartphone", "phone", "mobile", "Android", "iPhone"),
    "안드로이드": ("Android",),
    "아이폰": ("iPhone", "iOS"),
    "윈도": ("Windows",),
    "윈도우": ("Windows",),
    "리눅스": ("Linux",),
    "커널": ("kernel",),
    "서버": ("server",),
    "데이터베이스": ("database", "DB", "SQL"),
    "인프라": ("infrastructure",),
    "기반시설": ("infrastructure", "utility", "utilities", "critical infrastructure"),
    "산업제어": ("industrial control", "ICS", "SCADA", "PLC", "OT"),
    "제어시스템": ("control system", "ICS", "SCADA", "PLC"),
    "의료": ("health", "healthcare", "hospital", "medical", "patient", "병원"),
    "병원": ("hospital", "healthcare", "medical", "clinic", "의료"),
    "금융": ("bank", "banking", "financial", "finance", "fintech", "은행"),
    "금융권": ("bank", "banking", "financial", "finance", "은행", "금융"),
    "은행": ("bank", "banking"),
    "가상자산": ("crypto", "cryptocurrency", "bitcoin", "Ethereum", "wallet", "blockchain",
                 "암호화폐", "코인"),
    "암호화폐": ("crypto", "cryptocurrency", "bitcoin", "Ethereum", "wallet", "가상자산", "코인"),
    "블록체인": ("blockchain", "smart contract"),
    "거래소": ("exchange",),
    "결제": ("payment", "checkout", "card", "pay"),
    "통신사": ("telecom", "telecommunications", "carrier", "mobile operator", "telco"),
    "통신": ("telecom", "telecommunications", "carrier", "telco"),
    "유심": ("SIM", "USIM", "eSIM"),
    "정부": ("government", "federal", "ministry", "agency"),
    "기관": ("agency", "agencies", "institution", "government", "ministry", "authority"),
    "공공": ("public sector", "government", "agency", "municipal", "정부"),
    "국방": ("military", "defense", "defence", "army", "navy"),
    "외교": ("diplomatic", "diplomat", "embassy", "foreign ministry"),
    "선거": ("election", "voting", "voter"),
    "교육": ("education", "school", "university", "student"),
    "대학": ("university", "college", "academic"),
    "국내": ("Korea", "Korean", "한국"),
    "한국": ("Korea", "Korean", "국내"),
    "북한": ("North Korea", "North Korean", "DPRK", "Lazarus", "Kimsuky", "Andariel"),
    "중국": ("China", "Chinese", "PRC"),
    "러시아": ("Russia", "Russian"),
    "이란": ("Iran", "Iranian"),
    "미국": ("US", "U.S.", "United States", "America", "American"),
    "일본": ("Japan", "Japanese"),
    "유럽": ("Europe", "European", "EU"),
    "국가배후": ("state-sponsored", "nation-state", "state-backed", "APT"),
    "국가행위자": ("nation-state", "state-sponsored", "state-backed", "state actor",
                   "government-backed"),
    "행위자": ("actor", "threat actor"),
    "국가지원": ("state-sponsored", "nation-state", "state-backed"),
    "사이버범죄": ("cybercrime", "cybercriminal", "criminal"),
    "범죄": ("crime", "criminal", "cybercrime", "fraud"),
    "사기": ("fraud", "scam", "scammer"),
    "협박": ("extortion", "extort", "ransom", "threaten"),
    "갈취": ("extortion", "extort", "ransom"),
    "체포": ("arrest", "arrested", "detained"),
    "검거": ("arrest", "arrested", "detained"),
    "기소": ("charged", "indicted", "indictment", "prosecuted"),
    "수사": ("investigation", "investigating", "police", "law enforcement", "FBI"),
    "제재": ("sanction", "sanctioned", "penalty", "fine", "fined"),
    "해체": ("takedown", "dismantle", "dismantled", "disrupt", "disrupted", "seized"),
    "법": ("law", "act", "bill", "legislation"),
    "법안": ("bill", "legislation", "act"),
    "규제": ("regulation", "regulator", "regulatory", "rule", "compliance"),
    "개정": ("amendment", "amended", "revision", "revised"),
    "시행": ("take effect", "takes effect", "effective", "enforcement", "implement"),
    "제도": ("regulation", "scheme", "program", "policy", "framework"),
    "정책": ("policy", "policies"),
    "가이드라인": ("guideline", "guidance"),
    "지침": ("guideline", "guidance", "directive"),
    "과징금": ("fine", "fined", "penalty"),
    "벌금": ("fine", "fined", "penalty"),
    "패치": ("patch", "patched", "fix", "fixed", "update", "updated"),
    "업데이트": ("update", "updated", "patch"),
    "버그바운티": ("bug bounty",),
    "실악용": ("actively exploited", "exploited in the wild", "in the wild",
               "active exploitation", "under active attack"),
    "실제악용": ("actively exploited", "exploited in the wild", "in the wild",
                 "active exploitation", "under active attack"),
    "워터홀": ("watering hole", "watering-hole", "waterhole"),
    "워터링홀": ("watering hole", "watering-hole", "waterhole"),
    "손상": ("compromise", "compromised", "damage", "damaged", "corrupted"),
    "위조": ("forged", "forgery", "forge", "spoofed", "counterfeit", "fake"),
    "펜테스팅": ("penetration testing", "pentest", "pentesting", "pen test", "red team"),
    "모의해킹": ("penetration testing", "pentest", "pentesting", "red team"),
    "자동화": ("automated", "automation", "automate", "autonomous"),
    "가상화": ("virtualization", "virtual machine", "VM", "hypervisor"),
    "하이퍼바이저": ("hypervisor", "Xen", "ESXi", "Hyper-V", "KVM"),
    "메모리": ("memory",),
    "접근": ("access", "accessed"),
    "네트워크": ("network", "networking"),
    "기기": ("device", "devices", "appliance", "equipment", "hardware"),
    "장비": ("device", "appliance", "equipment", "hardware"),
    "광고": ("ad", "advertising", "advertisement", "adware", "malvertising"),
    "손실": ("loss", "losses", "cost", "costs"),
    "디도스": ("DDoS", "denial of service", "denial-of-service"),
    "서비스거부": ("denial of service", "denial-of-service", "DoS", "DDoS"),
    "무차별대입": ("brute force", "brute-force", "password spraying"),
    "인증서": ("certificate", "CA"),
    "암호화": ("encryption", "encrypt", "encrypted", "cryptographic", "cipher"),
    "양자내성": ("post-quantum", "quantum-resistant", "PQC"),
    "양자": ("quantum",),
    "제로트러스트": ("zero trust",),
    "다중인증": ("MFA", "multi-factor", "2FA", "two-factor"),
    "패스키": ("passkey",),
    "생체인증": ("biometric",),
    "위치정보": ("location", "geolocation", "GPS"),
    "추적": ("tracking", "track", "tracked", "tracker"),
    "감시": ("surveillance", "monitoring", "spy"),
    "스파이": ("spy", "spying", "espionage", "spyware"),
    "첩보": ("espionage", "spying", "cyberespionage"),
    "내부자": ("insider",),
    "취약점공개": ("disclosed", "disclosure", "advisory"),
    "무패치": ("unpatched", "no patch"),
    "미패치": ("unpatched", "no patch"),
    "대규모": ("mass", "massive", "large-scale", "widespread", "thousands", "millions",
               "million"),
}

# 뜻이 넓어 근거로 치지도 거부하지도 않는 말(공격, 그룹 같은 꼬리)
GENERIC_TAG_WORDS = frozenset((
    "공격", "공격자", "취약점", "사고", "피해", "그룹", "조직", "위협", "보안", "경고", "주의",
    "권고", "대응", "확산", "발견", "공개", "발표", "캠페인", "기법", "수법", "사례", "분석",
    "확인", "시스템", "정보", "서비스", "기업", "사용자", "대량", "긴급", "신규", "실제",
    "악용", "노출", "위험", "악성", "도구", "프레임워크", "작전", "연계", "표적", "배후",
    "기반",
))
_STEM_MAX = max(len(k) for k in KO_TAG_EVIDENCE)
_TAG_PART_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9.&+-]*|[가-힣]+")


def _latin_supported(part: str, evidence: str) -> bool:
    keys = LATIN_TAG_EVIDENCE.get(part.upper(), (part,))
    return any_keyword(keys, evidence)


def _korean_supported(seg: str, evidence: str) -> tuple[bool, bool]:
    """(근거 있음, 구체 근거 포함). 조각을 아는 말로 쪼개 하나하나 근거를 본다.
    모르는 두 글자 이상 덩어리는 원문에 글자 그대로 있어야 한다."""
    if seg in evidence:
        return True, True
    pieces, unknown, i = [], "", 0
    while i < len(seg):
        for size in range(min(_STEM_MAX, len(seg) - i), 1, -1):
            word = seg[i:i + size]
            if word in KO_TAG_EVIDENCE or word in GENERIC_TAG_WORDS:
                break
        else:
            unknown += seg[i]
            i += 1
            continue
        pieces += [unknown, word]
        unknown = ""
        i += size
    pieces.append(unknown)
    specific = False
    for piece in pieces:
        if piece in KO_TAG_EVIDENCE:
            if not any_keyword((piece,) + KO_TAG_EVIDENCE[piece], evidence):
                return False, False
            specific = True
        elif len(piece) >= 2 and piece not in GENERIC_TAG_WORDS:
            if piece not in evidence:
                return False, False
            specific = True
    return True, specific


# 태그에서만 보는 회사명 꼬리. 용어 쪽 KO_ORG_SUFFIXES에 넣으면 '스마트카드'
# 같은 용어까지 막혀서 따로 둔다. 앞에 일반어가 오면 회사명이 아니다
_TAG_COMPANY_TAILS = ("카드", "캐피탈", "손해보험", "화재", "건설", "뱅크", "페이")
_TAG_GENERIC_HEADS = ("신용", "체크", "스마트", "교통", "선불", "간편", "모바일", "인터넷")


def tag_entity_reason(tag: str) -> str | None:
    """태그가 기관, 기업, 제품 같은 실체 이름이면 거부 사유. 주제어면 None.
    2026-11-23 QA 실행: NCIC, NSANet, 롯데카드가 태그 pill로 나갔다.
    라틴 조각은 보안 약어 목록에 있어야 한다. 한글은 용어 칸과 같은 고유명
    목록과 기관 접미사, 태그 전용 회사명 꼬리로 본다."""
    t = "".join(tag.split())
    for part in _TERM_LATIN_RE.findall(t):
        if not _latin_token_ok(part):
            return f"라틴 고유명사 {part}"
    ko = re.sub(r"[^가-힣]", "", t)
    if not ko:
        return None
    if any(ko.startswith(e) for e in KO_PROPER_NOUNS):
        return "한글 고유명사"
    if any(ko.endswith(s) for s in KO_ORG_SUFFIXES):
        return "기관 접미사"
    for tail in _TAG_COMPANY_TAILS:
        head = ko[:-len(tail)]
        if ko.endswith(tail) and len(head) >= 2 and not head.endswith(_TAG_GENERIC_HEADS):
            return f"회사명 꼬리 {tail}"
    return None


def tag_has_evidence(tag: str, evidence: str) -> bool:
    """태그가 원문(evidence)에 근거가 있는지. evidence는 원제, 피드 요약,
    기사 본문만이다. LLM이 쓴 한국어 제목과 요약은 근거가 아니다.
    원문 공백은 메우지 않는다. 개인정보유출 같은 합성 태그는 조각별로 본다."""
    t = "".join(tag.split())
    evidence = evidence or ""
    if not t or not evidence.strip():
        return False
    specific = False
    for part in _TAG_PART_RE.findall(t):
        if HANGUL_RE.match(part):
            ok, spec = _korean_supported(part, evidence)
            if not ok:
                return False
            specific = specific or spec
        elif part.isdigit():
            continue
        elif _latin_supported(part, evidence):
            # 라틴 조각은 부분 문자열 금지(resource 안의 rce). 매처로만 본다
            specific = True
        else:
            return False
    return specific
