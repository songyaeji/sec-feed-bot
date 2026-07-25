# CLI 터미널 프레임 + 픽셀 캐릭터 아바타 2종 생성.
# 디스코드 웹훅 아바타는 128px로 축소 표시되므로 픽셀아트가 또렷하게
# 보이도록 512px 캔버스에 큰 픽셀 단위로 그린다.
from PIL import Image, ImageDraw

SIZE = 512
BG = (13, 17, 23)        # 터미널 다크(#0D1117)
BAR = (33, 38, 45)       # 타이틀바
DOTS = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]  # 신호등 버튼

GREEN = (63, 185, 80)    # 보안 봇 액센트
GREEN_HI = (126, 231, 135)
ORANGE = (243, 156, 18)  # 트렌드 봇 액센트(TREND_COLOR와 동일 계열)
ORANGE_HI = (255, 204, 92)
DARK = (13, 17, 23)      # 캐릭터 얼굴(눈·입)

SHIELD = [
    ".XXXXXXXXX.",
    "XXXXXXXXXXX",
    "XXXXXXXXXXX",
    "XXXXXXXXXXX",
    "XXXeXXXeXXX",
    "XXXXXXXXXXX",
    "XXXmXXXmXXX",
    "XXXXmmmXXXX",
    ".XXXXXXXXX.",
    ".XXXXXXXXX.",
    "..XXXXXXX..",
    "...XXXXX...",
    "....XXX....",
]

FLAME = [
    "....h....",
    "....hh...",
    "...hhh...",
    "...XXXX..",
    "..XXXXX..",
    ".XXhhXXX.",
    ".XhhhhXX.",
    "XXhhhhXXX",
    "XXeXhXeXX",
    "XXXhhhXXX",
    ".XmXXXmX.",
    ".XXmmmXX.",
    "..XXXXX..",
]


def draw_frame(d: ImageDraw.ImageDraw, accent):
    d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=72, fill=BG)
    # 타이틀바 — 위쪽 모서리만 둥글게: 둥근 사각형 위에 아래 절반을 덧칠
    d.rounded_rectangle([0, 0, SIZE - 1, 96], radius=72, fill=BAR)
    d.rectangle([0, 56, SIZE - 1, 96], fill=BAR)
    for i, c in enumerate(DOTS):
        cx = 52 + i * 56
        d.ellipse([cx - 16, 32, cx + 16, 64], fill=c)
    # 프롬프트 '>' 셰브론 + '_' 커서 (블록으로 그려 CLI 감성)
    t = 18  # 획 두께
    x0, y0 = 48, 140
    for i in range(3):
        d.rectangle([x0 + i * t, y0 + i * t, x0 + (i + 1) * t, y0 + (i + 1) * t], fill=accent)
    for i in range(3):
        d.rectangle([x0 + i * t, y0 + (5 - i) * t, x0 + (i + 1) * t, y0 + (6 - i) * t], fill=accent)
    d.rectangle([x0 + 4 * t, y0 + 5 * t, x0 + 7 * t, y0 + 6 * t], fill=accent)


def draw_pixels(d, grid, palette, px, ox, oy):
    for r, row in enumerate(grid):
        for c, ch in enumerate(row):
            if ch == ".":
                continue
            color = palette[ch]
            d.rectangle([ox + c * px, oy + r * px,
                         ox + (c + 1) * px - 1, oy + (r + 1) * px - 1], fill=color)


def build(grid, accent, hi, path):
    img = Image.new("RGB", (SIZE, SIZE), BG)
    d = ImageDraw.Draw(img)
    draw_frame(d, accent)
    px = 26
    w = len(grid[0]) * px
    h = len(grid) * px
    ox = (SIZE - w) // 2 + 40   # 프롬프트와 겹치지 않게 살짝 오른쪽·아래
    oy = SIZE - h - 56
    palette = {"X": accent, "h": hi, "e": DARK, "m": DARK}
    draw_pixels(d, grid, palette, px, ox, oy)
    img.save(path)
    print("saved", path)


build(SHIELD, GREEN, GREEN_HI, "avatar_sec.png")
build(FLAME, ORANGE, ORANGE_HI, "avatar_trend.png")
