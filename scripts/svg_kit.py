"""Shared monochrome palette and helpers for the profile SVGs.

The whole profile is one black-and-white terminal session. Every asset is
self-contained (no external fonts or images), so it renders the same inside
GitHub's <img> sandbox. Animations are CSS keyframes or SMIL only. With STATIC=1
the CSS and SMIL are dropped and the final frame is drawn: that is what
scripts/preview.sh renders through QuickLook, and what reduced-motion viewers see.
"""
import hashlib
import os
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path(os.environ.get("ASSETS_DIR", ROOT / "assets"))
ICONS = Path(__file__).resolve().parent / "icons"
DATA = Path(__file__).resolve().parent / "data"
STATIC = os.environ.get("STATIC") == "1"

BG = "#000000"
BAR = "#0d0d0d"
LINE = "#1c1c1c"
BORDER = "#2e2e2e"
DIM = "#5f5f5f"
MUTED = "#9d9d9d"
TEXT = "#e6e6e6"
WHITE = "#ffffff"
GREYS = ["#000000", "#242424", "#494949", "#6d6d6d", "#929292", "#b6b6b6", "#dbdbdb", "#ffffff"]

MONO = ("ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'DejaVu Sans Mono',"
        "'Liberation Mono',monospace")
CW = 0.6  # advance width of one monospace glyph, in em
HOST = "xcrpty7@tashkent"
PROMPT = f"{HOST}:~$ "

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
BLINK = ".cur{animation:blink 1.06s steps(1) infinite}@keyframes blink{50%{opacity:0}}"


def esc(text: str) -> str:
    return escape(text, {'"': "&quot;"})


def svg(width: int, height: int, body: str, css: str = "", title: str = "") -> str:
    """Wrap body into a root <svg>; css is dropped in STATIC mode (final frame only)."""
    style = "" if STATIC or not css else f"<style>{css}{REDUCED_MOTION}</style>"
    label = f"<title>{esc(title)}</title>" if title else ""
    # QuickLook crops non-square thumbnails, so STATIC previews are letterboxed into a square.
    box_w = box_h = max(width, height) if STATIC else None
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{box_w or width}" height="{box_h or height}" '
        f'viewBox="0 0 {width} {height}" role="img" fill="none">{label}{style}{body}</svg>\n'
    )


def smil(markup: str) -> str:
    """SMIL animation elements, omitted in STATIC mode."""
    return "" if STATIC else markup


def typing(attr: str, start: float, end: float, steps: int, begin: float, dur: float) -> str:
    """Discrete SMIL animation from start to end in `steps` jumps (typewriter effect)."""
    steps = max(steps, 1)
    values = ";".join(f"{start + (end - start) * i / steps:.1f}" for i in range(steps + 1))
    return smil(f'<animate attributeName="{attr}" values="{values}" calcMode="discrete" '
                f'begin="{begin:.2f}s" dur="{dur:.2f}s" fill="freeze"/>')


def appear(begin: float) -> tuple:
    """(opacity, <set>) pair: hidden until `begin`, always visible in STATIC mode."""
    if STATIC:
        return "1", ""
    return "0", f'<set attributeName="opacity" to="1" begin="{begin:.2f}s" fill="freeze"/>'


def write(rel_path: str, content: str) -> Path:
    path = ASSETS / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def icon_path(slug: str) -> str:
    """Path data of a simple-icons glyph (24x24 viewBox), CC0."""
    raw = (ICONS / f"{slug}.svg").read_text(encoding="utf-8")
    match = re.search(r'<path d="([^"]+)"', raw)
    if not match:
        raise ValueError(f"no path in icon {slug}")
    return match.group(1)


def mono_width(text: str, size: float) -> float:
    """Advance width of monospace text; pair with textLength so every font lands on the grid."""
    return len(text) * size * CW


def text(x: float, y: float, s: str, size: float = 15, fill: str = TEXT, weight: str = "",
         anchor: str = "", extra: str = "") -> str:
    """One monospace run pinned to the character grid with textLength."""
    if not s:
        return ""
    w = f' font-weight="{weight}"' if weight else ""
    a = f' text-anchor="{anchor}"' if anchor else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}"{w}{a} '
            f'textLength="{mono_width(s, size):.1f}" lengthAdjust="spacing" xml:space="preserve"{extra}>'
            f'{esc(s)}</text>')


def row(x: float, y: float, parts: list, size: float = 15) -> str:
    """Runs of (text, fill[, weight[, extra attrs]]) laid out column by column on one line."""
    out, col = [], 0
    for part in parts:
        s, fill = part[0], part[1]
        weight = part[2] if len(part) > 2 else ""
        extra = part[3] if len(part) > 3 else ""
        out.append(text(x + col * size * CW, y, s, size, fill, weight, extra=extra))
        col += len(s)
    return "".join(out)


def bitmap(rows: list, x: float, y: float, px: float, fill: str = TEXT, extra: str = "") -> str:
    """1-bit pixel art ('#' = on) as one path, horizontal runs merged."""
    d = []
    for r, line in enumerate(rows):
        c = 0
        while c < len(line):
            if line[c] != "#":
                c += 1
                continue
            start = c
            while c < len(line) and line[c] == "#":
                c += 1
            d.append(f"M{x + start * px:g} {y + r * px:g}h{(c - start) * px:g}v{px:g}h{-(c - start) * px:g}z")
    return f'<path d="{"".join(d)}" fill="{fill}"{extra}/>'


def window(width: int, height: int, title: str, right: str = "") -> tuple:
    """Black terminal window. Returns (back, front): draw content between the two."""
    bar = 36
    back = f"""<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
<path d="M0.5 12.5A12 12 0 0 1 12.5 0.5H{width - 12.5}A12 12 0 0 1 {width - 0.5} 12.5V{bar}H0.5Z" fill="{BAR}"/>
<path d="M1 {bar}H{width - 1}" stroke="{LINE}"/>
<g stroke="#4a4a4a" stroke-width="1.2"><circle cx="22" cy="18" r="5" fill="#4a4a4a"/><circle cx="40" cy="18" r="5"/><circle cx="58" cy="18" r="5"/></g>
<g font-family="{MONO}">{text(width / 2, 23, title, 12.5, MUTED, anchor="middle")}{text(width - 20, 23, right, 11.5, DIM, anchor="end")}</g>"""
    front = (f'<defs><pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">'
             f'<rect width="4" height="1" fill="#fff" fill-opacity="0.035"/></pattern></defs>'
             f'<rect x="1" y="{bar + 1}" width="{width - 2}" height="{height - bar - 2}" rx="11" fill="url(#scan)"/>')
    return back, front


def prompt(x: float, y: float, cmd: str, size: float, begin: float, char_time: float = 0.05,
           uid: str = "p") -> tuple:
    """Shell prompt whose command types itself. Returns (defs, markup, typing end time)."""
    cw = size * CW
    cmd_x = x + len(PROMPT) * cw
    cmd_w = mono_width(cmd, size)
    dur = max(len(cmd) * char_time, 0.1)
    clip_w = cmd_w + 2 if STATIC else 0
    defs = (f'<clipPath id="{uid}"><rect x="{cmd_x - 1:.1f}" y="{y - size * 1.1:.1f}" width="{clip_w:.1f}" '
            f'height="{size * 1.6:.1f}">{typing("width", 0, cmd_w + 2, len(cmd), begin, dur)}</rect></clipPath>')
    head = row(x, y, [(HOST, WHITE, "700"), (":", MUTED), ("~", MUTED), ("$ ", WHITE, "700")], size)
    body = (head + f'<g clip-path="url(#{uid})">{text(cmd_x, y, cmd, size, TEXT)}</g>'
            f'<rect class="cur" x="{cmd_x + (cmd_w if STATIC else 0):.1f}" y="{y - size * 0.82:.1f}" '
            f'width="{cw:.1f}" height="{size * 1.05:.1f}" fill="{WHITE}">'
            f'{typing("x", cmd_x, cmd_x + cmd_w, len(cmd), begin, dur)}</rect>')
    return defs, body, begin + dur


def wrap(s: str, max_chars: int) -> list:
    lines, line = [], ""
    for word in s.split():
        candidate = f"{line} {word}".strip()
        if len(candidate) > max_chars and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines


def short_hash(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()[:7]


BAYER8 = [
    [0, 32, 8, 40, 2, 34, 10, 42], [48, 16, 56, 24, 50, 18, 58, 26],
    [12, 44, 4, 36, 14, 46, 6, 38], [60, 28, 52, 20, 62, 30, 54, 22],
    [3, 35, 11, 43, 1, 33, 9, 41], [51, 19, 59, 27, 49, 17, 57, 25],
    [15, 47, 7, 39, 13, 45, 5, 37], [63, 31, 55, 23, 61, 29, 53, 21],
]


def dither(value: float, col: int, row_: int) -> bool:
    """Ordered (Bayer 8x8) dithering: True when a pixel of brightness `value` (0..1) is lit."""
    return value > (BAYER8[row_ % 8][col % 8] + 0.5) / 64
