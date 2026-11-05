"""Hero banner (CRT boot screen), section prompts and the footer.

The X_CRPTY7 logo is the owner's own 3D block design from the old README, converted
from box-drawing characters into vector shapes so it no longer depends on the font.
"""
import random

from donut import svg_frames

from svg_kit import (BG, BLINK, BORDER, DIM, MONO, MUTED, STATIC, TEXT, WHITE, appear, esc, mono_width,
                     prompt, row, smil, svg, text, typing, write)

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
    for r, line in enumerate(LOGO):
        y = oy + r * CELL_H
        col = 0
        while col < len(line):
            if line[col] == "█":
                start = col
                while col < len(line) and line[col] == "█":
                    col += 1
                blocks.append(f'<rect x="{ox + start * CELL_W:.1f}" y="{y:.1f}" '
                              f'width="{(col - start) * CELL_W:.1f}" height="{CELL_H}"/>')
                continue
            for seg in _line_segments(line[col], ox + col * CELL_W, y):
                pts = " ".join(f"{px:.1f},{py:.1f}" for px, py in seg)
                lines.append(f'<polyline points="{pts}"/>')
            col += 1
    return "".join(blocks), "".join(lines)


def rotating(phrases: list, cx: float, y: float) -> str:
    """Phrases that take turns under the logo, each with its own blinking cursor."""
    out = []
    for i, s in enumerate(phrases):
        w = mono_width(s, 15)
        x = cx - w / 2
        hidden = ' opacity="0"' if STATIC and i else ""
        out.append(f'<g class="ph ph{i}" style="animation-delay:{3.5 * i}s"{hidden}>'
                   f'{text(x, y, s, 15, MUTED)}'
                   f'<rect class="cur" x="{x + w + 8:.1f}" y="{y - 13}" width="9" height="17" fill="{WHITE}"/></g>')
    return "".join(out)


BOOT = [
    [("XCRPTY7 BIOS 2026.11", WHITE, "700"), ("  ·  tashkent node  ·  41.31N 69.24E", DIM)],
    [("[ ", DIM), ("OK", WHITE, "700"), (" ] ", DIM), ("mounted /home/xcrpty7", MUTED)],
    [("[ ", DIM), ("OK", WHITE, "700"), (" ] ", DIM), ("started claude-code.service", MUTED)],
    [("[ ", DIM), ("OK", WHITE, "700"), (" ] ", DIM), ("started telegram-agents.target", MUTED)],
    [("[ ", DIM), ("OK", WHITE, "700"), (" ] ", DIM), ("reached target ship-products", MUTED)],
]
PHRASES = [
    "Tashkent, UZ  ·  AI agents · Telegram bots · MCP  ·  shipping since 14",
    "NASA Space Apps  ·  Moon & Mars on Earth  ·  30 sites, 6 criteria",
    "the model talks, the code decides  ·  nothing sent without a yes",
]
# horizontal bands of the logo (logo-local y) and how far each one jumps during a glitch
SLICES = [(0, 22, (-14, 6, 0)), (22, 50, (10, -4, 3)), (50, 70, (0, -18, 8)),
          (70, 98, (6, 0, -10)), (98, 120, (-8, 12, 0)), (120, 150, (16, -6, 0))]


def hero() -> str:
    width, height = 1200, 460
    logo_w, logo_h = len(LOGO[0]) * CELL_W, CELL_H * len(LOGO)
    ox, oy = (width - logo_w) / 2, 132
    blocks, lines = logo_shapes(ox, oy)
    rng = random.Random(7)

    boot = []
    for i, parts in enumerate(BOOT):
        op, show = appear(0.1 + 0.22 * i)
        boot.append(f'<g opacity="{op}">{show}{row(34, 44 + 17 * i, parts, 11.5)}</g>')
    hud = (text(width - 34, 44, "[ SYS://XCRPTY7 ]", 11.5, DIM, anchor="end")
           + text(width - 34, 61, "ONLINE", 11.5, WHITE, "700", anchor="end")
           + f'<rect class="pulse" x="{width - 34 - mono_width("ONLINE", 11.5) - 16:.1f}" y="52" width="8" height="8" fill="{WHITE}"/>'
           + text(width - 34, 78, "uz_UZ · ru_RU · en_US", 11.5, DIM, anchor="end"))

    reveal_h = logo_h + 20
    clip_h = reveal_h if STATIC else 0
    slice_defs = "".join(f'<clipPath id="s{i}"><rect x="0" y="{oy + a - (6 if i == 0 else 0)}" width="{width}" '
                         f'height="{b - a + (6 if i == 0 else 0)}"/></clipPath>' for i, (a, b, _) in enumerate(SLICES))
    slices = "".join(f'<g clip-path="url(#s{i})"><use href="#L" class="sl s{i}"/></g>' for i in range(len(SLICES)))
    glitch_css = "".join(
        f".s{i}{{animation:g{i} 7s steps(1) infinite}}"
        f"@keyframes g{i}{{0%,90%,94%,97%,100%{{transform:none}}91%{{transform:translateX({d1}px)}}"
        f"92.5%{{transform:translateX({d2}px)}}96%{{transform:translateX({d3}px)}}}}"
        for i, (_, _, (d1, d2, d3)) in enumerate(SLICES))
    grain = (f'<filter id="grain" x="0" y="0" width="100%" height="100%"><feTurbulence type="fractalNoise" '
             f'baseFrequency="0.85" numOctaves="1" seed="4"/><feColorMatrix type="saturate" values="0"/>'
             f'<feComponentTransfer><feFuncA type="table" tableValues="0 0.09"/></feComponentTransfer></filter>')
    stars = "".join(f'<rect x="{rng.randint(20, width - 20)}" y="{rng.randint(100, height - 60)}" width="2" height="2" '
                    f'class="tw" style="animation-delay:-{rng.uniform(0, 5):.1f}s" fill="{MUTED}"/>' for _ in range(22))

    bar_y, bar_h, size = height - 30, 30, 12.5
    cw = size * 0.6
    left = [("[xcrpty7] ", BG, "700"), ("0:zsh  1:agents  2:bots  ", BG)]
    left_w = sum(len(p[0]) for p in left)
    cur_tab = " 3:ship* "
    right_s = "tashkent  41.31N 69.24E  ·  uz ru en "
    spin_x = width - 16 - mono_width(right_s, size) - 4 * cw
    hidden = ' opacity="0"'
    spinner = "".join(f'<text class="sp sp{i}" x="{spin_x + cw:.1f}" y="{bar_y + 20}" font-size="{size}" '
                      f'font-weight="700" fill="{BG}"{hidden if i else ""}>{esc(ch)}</text>'
                      for i, ch in enumerate("|/-\\"))
    tmux = f"""<g clip-path="url(#frame)">
<rect x="0" y="{bar_y}" width="{width}" height="{bar_h}" fill="#d6d6d6"/>
{row(16, bar_y + 20, left, size)}
<rect x="{16 + left_w * cw:.1f}" y="{bar_y}" width="{len(cur_tab) * cw:.1f}" height="{bar_h}" fill="{BG}"/>
{text(16 + left_w * cw, bar_y + 20, cur_tab, size, WHITE, "700")}
{text(spin_x, bar_y + 20, "[ ]", size, BG, "700")}{spinner}
{text(width - 16, bar_y + 20, right_s, size, BG, anchor="end")}
</g>"""

    defs = f"""<defs>
  <clipPath id="frame"><rect width="{width}" height="{height}" rx="16"/></clipPath>
  <clipPath id="reveal"><rect x="0" y="{oy - 10}" width="{width}" height="{clip_h}">{typing("height", 0, reveal_h, 12, 1.25, 0.55)}</rect></clipPath>
  {slice_defs}
  <pattern id="raster" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="3" fill="#f2f2f2"/><rect y="3" width="4" height="1" fill="#7d7d7d"/></pattern>
  <pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" fill-opacity="0.035"/></pattern>
  <radialGradient id="glow" cx="0.5" cy="0.45" r="0.6"><stop offset="0" stop-color="#fff" stop-opacity="0.09"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
  <radialGradient id="vig" cx="0.5" cy="0.5" r="0.75"><stop offset="0.6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="0.75"/></radialGradient>
  <linearGradient id="shine" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="roll" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="0.5" stop-color="#fff" stop-opacity="0.05"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <mask id="logoMask"><g fill="#fff">{blocks}</g></mask>
  <filter id="blur" x="-10%" y="-40%" width="120%" height="180%"><feGaussianBlur stdDeviation="8"/></filter>
  {grain}
  <g id="L"><g fill="none" stroke="#5c5c5c" stroke-width="1.5">{lines}</g><g fill="url(#raster)">{blocks}</g></g>
</defs>"""

    flash = smil('<animate attributeName="opacity" values="0;0.85;0" begin="1.75s" dur="0.7s" fill="freeze"/>')
    body = f"""{defs}
<g clip-path="url(#frame)">
<rect width="{width}" height="{height}" fill="{BG}"/>
<rect width="{width}" height="{height}" fill="url(#glow)"/>
<g>{stars}</g>
<g clip-path="url(#reveal)">
  <g class="halo" fill="#fff" filter="url(#blur)" opacity="0.2">{blocks}</g>
  <g class="ghost" fill="#8c8c8c" opacity="0">{blocks}</g>
  {slices}
  <g mask="url(#logoMask)"><rect class="shine" x="-300" y="{oy}" width="240" height="{logo_h}" fill="url(#shine)" opacity="0"/></g>
  <g fill="#fff" filter="url(#blur)" opacity="0">{blocks}{flash}</g>
</g>
<text x="{width / 2}" y="{oy + logo_h + 52}" text-anchor="middle" font-family="{MONO}" font-size="20" font-weight="700" letter-spacing="7" fill="{WHITE}">FULL-STACK  ·  AI-AGENT DEVELOPER</text>
<g font-family="{MONO}">
{rotating(PHRASES, width / 2, oy + logo_h + 88)}
{''.join(boot)}
{hud}
{tmux}
</g>
<g stroke="{DIM}" stroke-width="2"><path d="M18 {height - 66}V{height - 50}H34M{width - 34} {height - 50}H{width - 18}V{height - 66}"/></g>
<rect class="roll" x="0" y="-140" width="{width}" height="140" fill="url(#roll)"/>
<rect width="{width}" height="{height}" fill="url(#scan)"/>
<rect width="{width}" height="{height}" filter="url(#grain)"/>
<rect width="{width}" height="{height}" fill="url(#vig)"/>
</g>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="16" stroke="{BORDER}"/>"""

    css = f"""{BLINK}
.halo{{animation:halo 4s ease-in-out infinite}}
@keyframes halo{{0%,100%{{opacity:.14}}50%{{opacity:.3}}}}
{glitch_css}
.ghost{{animation:ghost 7s steps(1) infinite}}
@keyframes ghost{{0%,90%,94%,100%{{opacity:0;transform:none}}91%{{opacity:.6;transform:translate(7px,-2px)}}92.5%{{opacity:.45;transform:translate(-6px,1px)}}}}
.shine{{opacity:1;animation:shine 5s ease-in-out 2.4s infinite both}}
@keyframes shine{{0%{{transform:translateX(0)}}55%,100%{{transform:translateX({width + 600}px)}}}}
.roll{{animation:roll 7s linear infinite}}
@keyframes roll{{from{{transform:translateY(0)}}to{{transform:translateY({height + 140}px)}}}}
.tw{{animation:tw 5s ease-in-out infinite}}
@keyframes tw{{0%,100%{{opacity:.15}}50%{{opacity:.8}}}}
.ph{{opacity:0;animation:phrase 10.5s linear infinite}}
@keyframes phrase{{0%{{opacity:0}}3%,30%{{opacity:1}}33%,100%{{opacity:0}}}}
@media (prefers-reduced-motion: reduce){{.ph0{{opacity:1}}}}
.pulse{{animation:blink 1.4s steps(1) infinite}}
.sp{{animation:sp .8s steps(1) infinite}}
.sp1{{animation-delay:.2s}}.sp2{{animation-delay:.4s}}.sp3{{animation-delay:.6s}}
@keyframes sp{{0%{{opacity:1}}25%,100%{{opacity:0}}}}
"""
    return svg(width, height, body, css, "xcrpty7: full-stack and AI-agent developer from Tashkent, Uzbekistan")


def section(number: str, cmd: str, comment: str) -> str:
    """Prompt bar of a section. The transparent strip on top keeps it clear of GitHub's sticky
    header when a nav key jumps here, and gives sections some air."""
    width, bar, pad = 1000, 58, 44
    defs, line, _ = prompt(80, 36, cmd, 16, begin=0.35, char_time=0.055, uid="c")
    body = f"""<defs>{defs}</defs>
<g transform="translate(0 {pad})">
<rect x="0.5" y="0.5" width="{width - 1}" height="{bar - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>
<rect x="14" y="14" width="50" height="30" rx="3" fill="{TEXT}"/>
<g font-family="{MONO}">
{text(39, 35, number, 15, BG, "700", anchor="middle")}
{line}
{text(width - 22, 35, f"# {comment}", 13, DIM, anchor="end")}
</g></g>"""
    return svg(width, bar + pad, body, BLINK, f"$ {cmd}  # {comment}")


def footer() -> str:
    """`exit`, then the donut screensaver spins until the CRT powers off and on again."""
    width, height = 1200, 350
    dx, dy = 50, 74                       # donut origin
    x0 = 430                              # text column
    donut, donut_css = svg_frames(dx, dy, 12, 12.4, 0.1, STATIC)
    defs, exit_line, t = prompt(x0, 64, "exit", 15, begin=0.4, char_time=0.12, uid="x")
    rows_ = []
    for i, s in enumerate(("logout", "Connection to xcrpty7 closed.")):
        op, show = appear(t + 0.3 + 0.25 * i)
        rows_.append(f'<g opacity="{op}">{show}{text(x0, 90 + 24 * i, s, 15, MUTED)}</g>')
    quote = "\"I don't write code. I ship products.\""
    size = 28
    q_w = mono_width(quote, size)
    qy = 202
    begin = t + 1.0
    steps = len(quote)
    clip_w = q_w + 4 if STATIC else 0
    links = [("$ ", WHITE, "700"), ("open t.me/xcrpty7", TEXT), ("  ·  ", DIM), ("open github.com/xcrpty7", TEXT)]
    body = f"""<defs>{defs}
<clipPath id="type"><rect x="{x0 - 2:.0f}" y="{qy - 34}" width="{clip_w:.0f}" height="48">{typing("width", 0, q_w + 4, steps, begin, 2.4)}</rect></clipPath>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#fff" fill-opacity="0.035"/></pattern>
<radialGradient id="glow" cx="0.18" cy="0.55" r="0.5"><stop offset="0" stop-color="#fff" stop-opacity="0.07"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>
</defs>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="16" fill="{BG}" stroke="{BORDER}"/>
<g class="crt" font-family="{MONO}">
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="15" fill="url(#glow)"/>
{row(dx, 44, [("$ ", WHITE, "700"), ("./donut", TEXT), ("   # screensaver", DIM)], 12)}
<g fill="{TEXT}">{donut}</g>
<path d="M{x0 - 40} 34V{height - 34}" stroke="{BORDER}" stroke-dasharray="2 6"/>
{exit_line}{''.join(rows_)}
<g clip-path="url(#type)">{text(x0, qy, quote, size, WHITE, "700")}</g>
<rect class="cur" x="{x0 + (q_w + 6 if STATIC else 0):.0f}" y="{qy - 24}" width="15" height="28" fill="{WHITE}">{typing("x", x0, x0 + q_w + 6, steps, begin, 2.4)}</rect>
{row(x0, 254, links, 15)}
{text(x0, 292, "BUILT WITH CLAUDE CODE · PURE SVG · NO JAVASCRIPT", 11.5, DIM)}
<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="15" fill="url(#scan)"/>
</g>
<rect class="flat" x="40" y="{height / 2 - 1}" width="{width - 80}" height="2" fill="{WHITE}" opacity="0"/>"""
    css = f"""{BLINK}{donut_css}
.crt{{transform-origin:{width / 2}px {height / 2}px;animation:crt 16s ease-in-out infinite}}
@keyframes crt{{0%,80%{{transform:scale(1,1);opacity:1}}83%{{transform:scale(1.03,.004);opacity:1}}84%,96%{{transform:scale(1,.004);opacity:0}}98%{{transform:scale(1.02,1.05);opacity:1}}100%{{transform:scale(1,1)}}}}
.flat{{transform-origin:{width / 2}px {height / 2}px;animation:flat 16s ease-in infinite}}
@keyframes flat{{0%,82.5%{{opacity:0;transform:scaleX(1)}}83.5%{{opacity:1;transform:scaleX(1)}}87%{{opacity:1;transform:scaleX(.002)}}89%,95%{{opacity:0;transform:scaleX(.002)}}96%{{opacity:1;transform:scaleX(.002)}}97.5%{{opacity:.9;transform:scaleX(1)}}98.5%,100%{{opacity:0;transform:scaleX(1)}}}}
"""
    return svg(width, height, body, css, "$ exit. A spinning ASCII donut. I don't write code. I ship products.")


KEYS = [("F1", "whoami"), ("F2", "man"), ("F3", "projects"), ("F4", "agents"), ("F5", "git log"),
        ("F6", "stack"), ("F7", "htop")]


def keycap(index: int, key: str, label: str) -> str:
    """A keyboard key for the nav row; the row presses itself in a wave every few seconds."""
    width, height = 132, 46
    body = f"""<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" fill="#1b1b1b" stroke="{BORDER}"/>
<g class="face">
<rect x="3" y="2.5" width="{width - 6}" height="{height - 10}" rx="6" fill="#0b0b0b" stroke="#3c3c3c"/>
<rect class="lit" x="3" y="2.5" width="{width - 6}" height="{height - 10}" rx="6" fill="{TEXT}" opacity="0"/>
<g font-family="{MONO}">
{text(11, 15, key, 10, DIM, "700")}
{text(width / 2, 29, label, 13.5, WHITE, "700", anchor="middle")}
<g class="lit" opacity="0">{text(11, 15, key, 10, "#555555", "700")}{text(width / 2, 29, label, 13.5, BG, "700", anchor="middle")}</g>
</g></g>"""
    delay = 1.2 + 0.18 * index
    css = f""".face{{animation:press 9s ease-out {delay:.2f}s infinite}}
@keyframes press{{0%,6%,100%{{transform:translateY(0)}}2%{{transform:translateY(3px)}}}}
.lit{{animation:lit 9s steps(1) {delay:.2f}s infinite}}
@keyframes lit{{0%{{opacity:1}}4%,100%{{opacity:0}}}}"""
    return svg(width, height, body, css, f"{key} {label}")


SECTIONS = {
    "01-whoami": ("01", "neofetch", "who am i"),
    "02-man": ("02", "man xcrpty7", "what i do"),
    "03-projects": ("03", "ls -l ~/projects", "what i built"),
    "04-pipeline": ("04", "cat ~/agents/pipeline.txt", "how my agents work"),
    "05-journey": ("05", "git log --graph --oneline", "journey"),
    "06-stack": ("06", "ls /usr/local/bin", "tech stack"),
    "07-stats": ("07", "htop", "live stats"),
}

if __name__ == "__main__":
    write("hero.svg", hero())
    write("footer.svg", footer())
    for name, (num, cmd, comment) in SECTIONS.items():
        write(f"sections/{name}.svg", section(num, cmd, comment))
    for i, (key, label) in enumerate(KEYS):
        write(f"keys/{key.lower()}.svg", keycap(i, key, label))
    print("hero, footer, sections: ok")
