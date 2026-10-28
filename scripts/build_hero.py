"""Hero banner, section headers and footer.

The X_CRPTY7 logo is the owner's own 3D block design from the old README, converted
from box-drawing characters into vector shapes so it no longer depends on the font.
"""
import random

from svg_kit import (BG, CYAN, DIM, GREEN, MONO, MUTED, PURPLE, RED, STATIC, TEXT, esc,
                     mono_width, svg, typing, write)

LOGO = [
    "██╗  ██╗           ██████╗ ██████╗  ██████╗  ████████╗ ██╗   ██╗ ███████╗",
    "╚██╗██╔╝          ██╔════╝ ██╔══██╗ ██╔══██╗ ╚══██╔══╝ ╚██╗ ██╔╝ ╚════██║",
    " ╚███╔╝           ██║      ██████╔╝ ██████╔╝    ██║     ╚████╔╝      ██╔╝",
    " ██╔██╗           ██║      ██╔══██╗ ██╔═══╝     ██║      ╚██╔╝      ██╔╝ ",
    "██╔╝ ██╗ ███████╗ ╚██████╗ ██║  ██║ ██║         ██║       ██║       ██║  ",
    "╚═╝  ╚═╝ ╚══════╝  ╚═════╝ ╚═╝  ╚═╝ ╚═╝         ╚═╝       ╚═╝       ╚═╝  ",
]
CELL_W, CELL_H, GAP = 13, 24, 2.4


def _line_segments(ch: str, x: float, y: float) -> list:
    """Double-line box characters as polylines inside one cell."""
    w, h, d = CELL_W, CELL_H, GAP
    cx, cy = x + w / 2, y + h / 2
    shapes = {
        "═": [[(x, cy - d), (x + w, cy - d)], [(x, cy + d), (x + w, cy + d)]],
        "║": [[(cx - d, y), (cx - d, y + h)], [(cx + d, y), (cx + d, y + h)]],
        "╗": [[(x, cy - d), (cx + d, cy - d), (cx + d, y + h)], [(x, cy + d), (cx - d, cy + d), (cx - d, y + h)]],
        "╔": [[(x + w, cy - d), (cx - d, cy - d), (cx - d, y + h)], [(x + w, cy + d), (cx + d, cy + d), (cx + d, y + h)]],
        "╝": [[(x, cy + d), (cx + d, cy + d), (cx + d, y)], [(x, cy - d), (cx - d, cy - d), (cx - d, y)]],
        "╚": [[(x + w, cy + d), (cx - d, cy + d), (cx - d, y)], [(x + w, cy - d), (cx + d, cy - d), (cx + d, y)]],
    }
    return shapes.get(ch, [])


def logo_shapes(ox: float, oy: float) -> tuple:
    """Return (blocks, lines): merged rects for █ runs and polylines for the 3D edges."""
    blocks, lines = [], []
    for row, text in enumerate(LOGO):
        y = oy + row * CELL_H
        col = 0
        while col < len(text):
            if text[col] == "█":
                start = col
                while col < len(text) and text[col] == "█":
                    col += 1
                blocks.append(f'<rect x="{ox + start * CELL_W:.1f}" y="{y:.1f}" '
                              f'width="{(col - start) * CELL_W:.1f}" height="{CELL_H}"/>')
                continue
            for seg in _line_segments(text[col], ox + col * CELL_W, y):
                pts = " ".join(f"{px:.1f},{py:.1f}" for px, py in seg)
                lines.append(f'<polyline points="{pts}"/>')
            col += 1
    return "".join(blocks), "".join(lines)


def hero() -> str:
    width, height = 1200, 380
    logo_w = len(LOGO[0]) * CELL_W
    ox, oy = (width - logo_w) / 2, 64
    blocks, lines = logo_shapes(ox, oy)
    rng = random.Random(7)

    floor = "".join(f'<line x1="{600 + (i - 12) * 18}" y1="300" x2="{600 + (i - 12) * 140}" y2="{height}"/>'
                    for i in range(25))
    rows = "".join(f'<line x1="0" y1="{300 + k * 16}" x2="{width}" y2="{300 + k * 16}"/>' for k in range(6))
    particles = "".join(
        f'<circle class="p" cx="{rng.randint(40, width - 40)}" cy="{rng.randint(40, height - 20)}" '
        f'r="{rng.choice((1, 1.2, 1.6, 2))}" style="animation-delay:-{rng.uniform(0, 9):.1f}s;'
        f'animation-duration:{rng.uniform(7, 13):.1f}s"/>' for _ in range(26))
    sub1 = "FULL-STACK  ·  AI-AGENT DEVELOPER"
    sub2 = "Tashkent, UZ  ·  AI agents · Telegram bots · MCP  ·  shipping since 14"
    cursor_x = width / 2 + mono_width(sub2, 15) / 2 + 6

    defs = f"""<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0a0f16"/><stop offset="1" stop-color="#07130d"/></linearGradient>
  <radialGradient id="glow" cx="0.5" cy="0.42" r="0.55"><stop offset="0" stop-color="{GREEN}" stop-opacity="0.22"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
  <linearGradient id="logoFill" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{GREEN}"/><stop offset="0.55" stop-color="#5ee08a"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.75"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="floorFade" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000"/><stop offset="1" stop-color="#fff"/></linearGradient>
  <mask id="floorMask"><rect x="0" y="300" width="{width}" height="{height - 300}" fill="url(#floorFade)"/></mask>
  <mask id="logoMask"><g fill="#fff">{blocks}</g></mask>
  <filter id="blur" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="7"/></filter>
</defs>"""

    hud = f"""<g font-family="{MONO}" font-size="12" letter-spacing="2" fill="{DIM}">
  <text x="34" y="38">[ SYS://XCRPTY7 ]</text>
  <text x="{width - 34}" y="38" text-anchor="end" fill="{GREEN}">ONLINE</text>
  <text x="34" y="{height - 26}">LAT 41.31 · LON 69.24</text>
  <text x="{width - 34}" y="{height - 26}" text-anchor="end">BUILD 2026.10</text>
</g>
<circle class="pulse" cx="{width - 104}" cy="34" r="4" fill="{GREEN}"/>
<g stroke="{GREEN}" stroke-width="2" opacity="0.6">
  <path d="M18 34V18H34M{width - 34} 18H{width - 18}V34M18 {height - 34}V{height - 18}H34M{width - 34} {height - 18}H{width - 18}V{height - 34}"/>
</g>"""

    body = f"""{defs}
<rect width="{width}" height="{height}" rx="18" fill="url(#bg)"/>
<rect width="{width}" height="{height}" rx="18" fill="url(#glow)"/>
<g stroke="{GREEN}" stroke-opacity="0.35" mask="url(#floorMask)">{floor}<g class="rows">{rows}</g></g>
<g fill="{GREEN}" opacity="0.55">{particles}</g>
<g class="halo" fill="{GREEN}" filter="url(#blur)" opacity="0.45">{blocks}</g>
<g class="glitch r" fill="{RED}" opacity="0">{blocks}</g>
<g class="glitch c" fill="{CYAN}" opacity="0">{blocks}</g>
<g fill="none" stroke="#2f9e57" stroke-width="1.5" stroke-linejoin="miter">{lines}</g>
<g fill="url(#logoFill)">{blocks}</g>
<g mask="url(#logoMask)"><rect class="shine" x="-300" y="{oy}" width="260" height="{CELL_H * 6}" fill="url(#shine)" opacity="0"/></g>
<rect class="scan" x="0" y="0" width="{width}" height="3" fill="{GREEN}" opacity="0"/>
<text x="{width / 2}" y="{oy + CELL_H * 6 + 52}" text-anchor="middle" font-family="{MONO}" font-size="21" font-weight="700" letter-spacing="7" fill="{TEXT}">{esc(sub1)}</text>
<text x="{width / 2 - mono_width(sub2, 15) / 2:.1f}" y="{oy + CELL_H * 6 + 84}" font-family="{MONO}" font-size="15" fill="{MUTED}" textLength="{mono_width(sub2, 15):.0f}" lengthAdjust="spacing" xml:space="preserve">{esc(sub2)}</text>
<rect class="cursor" x="{cursor_x:.1f}" y="{oy + CELL_H * 6 + 71}" width="9" height="17" fill="{GREEN}"/>
{hud}"""

    css = f"""
.p{{animation:drift linear infinite}}
@keyframes drift{{0%{{transform:translateY(0);opacity:0}}15%{{opacity:.9}}100%{{transform:translateY(-120px);opacity:0}}}}
.rows{{animation:rows 1.6s linear infinite}}
@keyframes rows{{from{{transform:translateY(0)}}to{{transform:translateY(16px)}}}}
.halo{{animation:halo 4s ease-in-out infinite}}
@keyframes halo{{0%,100%{{opacity:.28}}50%{{opacity:.6}}}}
.glitch{{animation:glitch 5s steps(1) infinite}}
.glitch.c{{animation-delay:.06s}}
@keyframes glitch{{0%,88%,100%{{opacity:0;transform:translate(0,0)}}89%{{opacity:.75;transform:translate(-5px,1px)}}90.5%{{opacity:.6;transform:translate(4px,-1px)}}92%{{opacity:0}}95%{{opacity:.5;transform:translate(-3px,0)}}96%{{opacity:0}}}}
.shine{{opacity:1;animation:shine 4.5s ease-in-out infinite}}
@keyframes shine{{0%{{transform:translateX(0)}}60%,100%{{transform:translateX({width + 600}px)}}}}
.scan{{animation:scan 6s linear infinite}}
@keyframes scan{{0%{{transform:translateY(0);opacity:0}}5%{{opacity:.35}}95%{{opacity:.35}}100%{{transform:translateY({height}px);opacity:0}}}}
.cursor{{animation:blink 1s steps(1) infinite}}
@keyframes blink{{50%{{opacity:0}}}}
.pulse{{transform-origin:{width - 104}px 34px;animation:pulse 1.6s ease-out infinite}}
@keyframes pulse{{0%{{opacity:1}}70%{{opacity:.2}}100%{{opacity:1}}}}
"""
    return svg(width, height, body, css, "xcrpty7 — Full-Stack & AI-Agent Developer")


def section(number: str, label: str, accent: str) -> str:
    width, height = 1000, 64
    text_w = mono_width(f"{number}  {label}", 21) + 74
    body = f"""<defs><linearGradient id="fade" x1="0" y1="0" x2="1" y2="0">
<stop offset="0" stop-color="{accent}" stop-opacity="0.9"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="12" fill="{BG}" stroke="#253041"/>
<rect x="14" y="16" width="5" height="32" rx="2.5" fill="{accent}"/>
<text x="34" y="41" font-family="{MONO}" font-size="21" font-weight="700" letter-spacing="1">
<tspan fill="{accent}">{number}</tspan><tspan fill="{TEXT}" dx="14">{esc(label)}</tspan></text>
<rect x="{text_w:.0f}" y="31" width="{width - text_w - 24:.0f}" height="2" fill="url(#fade)"/>
<circle class="dot" cx="{text_w:.0f}" cy="32" r="3.5" fill="{accent}"/>"""
    css = f""".dot{{animation:run 3.2s ease-in-out infinite}}
@keyframes run{{0%{{transform:translateX(0);opacity:0}}10%{{opacity:1}}80%{{opacity:.8}}100%{{transform:translateX({width - text_w - 60:.0f}px);opacity:0}}}}"""
    return svg(width, height, body, css, f"{number} {label}")


def footer() -> str:
    width, height = 1200, 210
    quote = '"I don\'t write code. I ship products."'
    q_w = mono_width(quote, 26)
    x0 = (width - q_w) / 2
    full = q_w + 8
    steps = len(quote)
    clip_w = 0 if not STATIC else full
    body = f"""<defs><radialGradient id="g" cx="0.5" cy="0.5" r="0.6"><stop offset="0" stop-color="{PURPLE}" stop-opacity="0.18"/><stop offset="1" stop-color="{PURPLE}" stop-opacity="0"/></radialGradient>
<clipPath id="type"><rect x="{x0 - 4:.0f}" y="40" width="{clip_w:.0f}" height="60">{typing("width", 0, full, steps, 0.4, 2.6)}</rect></clipPath></defs>
<rect width="{width}" height="{height}" rx="18" fill="{BG}"/>
<rect width="{width}" height="{height}" rx="18" fill="url(#g)"/>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="18" stroke="#253041"/>
<text x="{x0:.0f}" y="84" font-family="{MONO}" font-size="26" font-weight="700" fill="{TEXT}" clip-path="url(#type)" xml:space="preserve" textLength="{q_w:.0f}" lengthAdjust="spacing">{esc(quote)}</text>
<rect class="cursor" x="{x0 + q_w + 6:.0f}" y="62" width="13" height="26" fill="{GREEN}">{typing("x", x0, x0 + q_w + 6, steps, 0.4, 2.6)}</rect>
<text x="{width / 2}" y="138" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{MUTED}" letter-spacing="1">
<tspan fill="{GREEN}">$</tspan> open t.me/xcrpty7 <tspan fill="{DIM}">·</tspan> open github.com/xcrpty7</text>
<text x="{width / 2}" y="172" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{DIM}" letter-spacing="3">BUILT WITH CLAUDE CODE · RENDERED AS PURE SVG</text>"""
    css = """.cursor{animation:blink 1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}"""
    return svg(width, height, body, css, "I don't write code. I ship products.")


SECTIONS = {
    "01-agents": ("01", "AI & AGENTS", PURPLE),
    "02-products": ("02", "PRODUCTS SHIPPED", GREEN),
    "03-stack": ("03", "TECH STACK", CYAN),
    "04-rules": ("04", "HOW I WORK", "#f0883e"),
    "05-stats": ("05", "LIVE STATS", "#58a6ff"),
}

if __name__ == "__main__":
    write("hero.svg", hero())
    write("footer.svg", footer())
    for name, (num, label, accent) in SECTIONS.items():
        write(f"sections/{name}.svg", section(num, label, accent))
    print("hero, footer, sections: ok")
