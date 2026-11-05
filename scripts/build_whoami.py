"""Who am I: `neofetch` with a spinning 1-bit Earth, and the `man xcrpty7` page.

The globe is ordered-dithered pixel art. Each latitude row is its own strip of the
land mask (scripts/data/land.txt) and steps one pixel at a time, so the planet turns
at one angular speed and the pixels stay on the grid. Tashkent carries a beacon.
"""
import math

from svg_kit import (BG, BORDER, DATA, DIM, GREYS, MONO, MUTED, STATIC, TEXT, WHITE, BLINK, appear,
                     dither, mono_width, row, smil, svg, text, window, write)

R, PX, SPIN = 30, 4, 36          # globe radius in pixels-cells, cell size, seconds per turn
TAS_LAT, TAS_LON = 41.31, 69.24
LIGHT = (-0.78, -0.42, 0.5)      # low sun from the upper left: a visible terminator

LAND = [line for line in (DATA / "land.txt").read_text(encoding="utf-8").splitlines() if line]


def land_at(lat: float, lon: float) -> bool:
    r = min(max(int((90 - lat) / 2), 0), len(LAND) - 1)
    c = int(((lon + 180) % 360) / 2) % len(LAND[0])
    return LAND[r][c] == "#"


def runs(cells: list, y: float) -> str:
    d, k = [], 0
    while k < len(cells):
        if not cells[k]:
            k += 1
            continue
        start = k
        while k < len(cells) and cells[k]:
            k += 1
        d.append(f"M{start * PX} {y}h{(k - start) * PX}v{PX}h{-(k - start) * PX}z")
    return "".join(d)


def globe(cx: float, cy: float) -> tuple:
    """Returns (defs, markup, css) of the spinning globe centred on (cx, cy)."""
    ox, oy = cx - R * PX, cy - R * PX
    norm = math.sqrt(sum(c * c for c in LIGHT))
    lx, ly, lz = (c / norm for c in LIGHT)
    disk, strips, shade, ocean, css = [], [], [], [], []
    beacon = ""
    tas_row = min(range(2 * R), key=lambda j: abs(math.degrees(math.asin(-(j + 0.5 - R) / R)) - TAS_LAT))
    for j in range(2 * R):
        yc = (j + 0.5 - R) / R
        half = round(R * math.sqrt(max(0.0, 1 - yc * yc)))
        if half == 0:
            continue
        chord, lat = 2 * half, math.degrees(math.asin(-yc))
        width = 2 * chord                       # texture cells for 360 degrees of longitude
        left = R - half
        y = oy + j * PX
        disk.append(f"M{ox + left * PX:g} {y:g}h{chord * PX}v{PX}h{-chord * PX}z")
        cells = [land_at(lat, -180 + 360 * (k + 0.5) / width) for k in range(width)]
        u0 = round((TAS_LON + 90) / 360 * width)  # Tashkent faces the viewer at t=0
        start, end = -(u0 + width) * PX, -u0 * PX
        strips.append(f'<g transform="translate({ox + left * PX:g} {y:g})"><path class="r{j}" '
                      f'transform="translate({start} 0)" d="{runs(cells + cells, 0)}"/></g>')
        css.append(f".r{j}{{animation:r{j} {SPIN}s steps({width}) infinite}}"
                   f"@keyframes r{j}{{from{{transform:translateX({start}px)}}to{{transform:translateX({end}px)}}}}")
        for i in range(left, left + chord):
            xc = (i + 0.5 - R) / R
            z = math.sqrt(max(0.0, 1 - xc * xc - yc * yc))
            light = max(0.0, xc * lx + yc * ly + z * lz)
            if not dither(0.04 + 1.25 * light, i, j):
                shade.append((i, j))
            elif i % 2 == 0 and j % 2 == 0:
                ocean.append((i, j))
        if j == tas_row:
            k = int((TAS_LON + 180) / 360 * width)
            ping = "" if STATIC else f'<circle class="ping" cx="{k * PX + 2}" cy="2" r="4" stroke="{WHITE}" stroke-width="1.5"/>'
            mark = (f'<rect x="{k * PX - 4}" y="-4" width="12" height="12" fill="{BG}"/>'
                    f'<rect class="bk" x="{k * PX}" y="0" width="4" height="4" fill="{WHITE}"/>{ping}')
            moved = mark + mark.replace(f'x="{k * PX - 4}"', f'x="{(k + width) * PX - 4}"') \
                .replace(f'x="{k * PX}"', f'x="{(k + width) * PX}"').replace(f'cx="{k * PX + 2}"', f'cx="{(k + width) * PX + 2}"')
            beacon = (f'<g transform="translate({ox + left * PX:g} {y:g})"><g class="r{j}" '
                      f'transform="translate({start} 0)">{moved}</g></g>')

    def cells_path(points: list) -> str:
        by_row = {}
        for i, j in points:
            by_row.setdefault(j, []).append(i)
        d = []
        for j, cols in by_row.items():
            cols.sort()
            k = 0
            while k < len(cols):
                start = cols[k]
                while k + 1 < len(cols) and cols[k + 1] == cols[k] + 1:
                    k += 1
                n = cols[k] - start + 1
                d.append(f"M{ox + start * PX:g} {oy + j * PX:g}h{n * PX}v{PX}h{-n * PX}z")
                k += 1
        return "".join(d)

    rx, ry, tilt = R * PX + 52, 30, -17
    orbit = f"M{-rx} 0A{rx} {ry} 0 0 0 {rx} 0A{rx} {ry} 0 0 0 {-rx} 0"
    sat = '<rect x="-3" y="-3" width="6" height="6" fill="{fill}">{motion}{vis}</rect>'
    motion = smil(f'<animateMotion dur="9s" repeatCount="indefinite" path="{orbit}"/>')
    front_vis = smil('<animate attributeName="opacity" values="1;0" keyTimes="0;0.5" calcMode="discrete" dur="9s" repeatCount="indefinite"/>')
    back_vis = smil('<animate attributeName="opacity" values="0;1" keyTimes="0;0.5" calcMode="discrete" dur="9s" repeatCount="indefinite"/>')
    orbit_g = f'<g transform="translate({cx} {cy}) rotate({tilt})">'
    back = (f'{orbit_g}<path d="M{rx} 0A{rx} {ry} 0 0 0 {-rx} 0" stroke="{DIM}" stroke-dasharray="2 5"/>'
            + ("" if STATIC else sat.format(fill=MUTED, motion=motion, vis=back_vis)) + "</g>")
    front = (f'{orbit_g}<path d="M{-rx} 0A{rx} {ry} 0 0 0 {rx} 0" stroke="{MUTED}" stroke-dasharray="2 5"/>'
             + (f'<rect x="{-rx - 3}" y="-3" width="6" height="6" fill="{WHITE}"/>' if STATIC
                else sat.format(fill=WHITE, motion=motion, vis=front_vis)) + "</g>")

    # stepped silhouette: down the left edges, back up the right edges
    left_pts, right_pts = [], []
    for j in range(2 * R):
        yc = (j + 0.5 - R) / R
        half = round(R * math.sqrt(max(0.0, 1 - yc * yc)))
        if half:
            y = oy + j * PX
            left_pts += [(ox + (R - half) * PX, y), (ox + (R - half) * PX, y + PX)]
            right_pts += [(ox + (R + half) * PX, y), (ox + (R + half) * PX, y + PX)]
    outline = "M" + "L".join(f"{x:g} {y:g}" for x, y in left_pts + right_pts[::-1]) + "Z"
    defs = f'<clipPath id="disk"><path d="{"".join(disk)}"/></clipPath>'
    markup = f"""{back}
<circle class="ring" cx="{cx}" cy="{cy}" r="{R * PX + 16}" stroke="{BORDER}" stroke-dasharray="1 7"/>
<g clip-path="url(#disk)" shape-rendering="crispEdges">
<path d="{"".join(disk)}" fill="{BG}"/>
<path d="{''.join(f'M{ox + i * PX + 1:g} {oy + j * PX + 1:g}h2v2h-2z' for i, j in ocean)}" fill="#5a5a5a"/>
<g fill="{WHITE}">{"".join(strips)}</g>
<path d="{cells_path(shade)}" fill="{BG}"/>
{beacon}
</g>
<path d="{outline}" stroke="#3a3a3a" stroke-width="1.5" shape-rendering="crispEdges"/>
{front}"""
    css.append(f""".ring{{transform-origin:{cx}px {cy}px;animation:spin 60s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.bk{{animation:blink 1.06s steps(1) infinite}}
.ping{{transform-box:fill-box;transform-origin:center;animation:ping 2s ease-out infinite}}
@keyframes ping{{from{{transform:scale(1);opacity:1}}to{{transform:scale(5);opacity:0}}}}""")
    return defs, markup, "".join(css)


INFO = [
    ("role", "full-stack & ai-agent developer"),
    ("host", "tashkent, uzbekistan · 41.31N 69.24E"),
    ("uptime", "shipping since 14"),
    ("kernel", "python · typescript · node · react"),
    ("shell", "zsh + claude code + mcp"),
    ("agents", "telegram bots that do real work"),
    ("langs", "uz_UZ · ru_RU · en_US"),
    ("memory", "obsidian rag · each bug fixed once"),
    ("motto", "the model talks, the code decides"),
]


def neofetch() -> str:
    width, height = 1000, 440
    gx, gy = 190, 236
    g_defs, g_markup, g_css = globe(gx, gy)
    x0, size, lh = 376, 16, 28
    lines, t = [], 0.35
    op, show = appear(t)
    lines.append(f'<g opacity="{op}">{show}{row(x0, 90, [("xcrpty7", WHITE, "700"), ("@", MUTED), ("tashkent", WHITE, "700")], 18)}'
                 f'<path d="M{x0} 104H{x0 + mono_width("xcrpty7@tashkent", 18):.0f}" stroke="{DIM}" stroke-dasharray="6 3"/></g>')
    for i, (key, value) in enumerate(INFO):
        t += 0.09
        op, show = appear(t)
        lines.append(f'<g opacity="{op}">{show}'
                     f'{row(x0, 138 + i * lh, [(key.ljust(8), WHITE, "700"), (value, TEXT)], size)}</g>')
    blocks = []
    for i, grey in enumerate(GREYS):
        t += 0.06
        op, show = appear(t)
        blocks.append(f'<rect x="{x0 + i * 34}" y="{138 + len(INFO) * lh - 6}" width="30" height="16" fill="{grey}" '
                      f'stroke="{BORDER}" opacity="{op}">{show}</rect>')
    label = f"[ tashkent · 41.31N 69.24E ]"
    back, front = window(width, height, "neofetch", "tty1")
    body = f"""<defs>{g_defs}</defs>
{back}
<g font-family="{MONO}">
{g_markup}
{text(gx, gy + R * PX + 44, label, 12, DIM, anchor="middle")}
{''.join(lines)}{''.join(blocks)}
</g>
{front}"""
    css = g_css + BLINK
    return svg(width, height, body, css, "neofetch: xcrpty7, full-stack and AI-agent developer from Tashkent, Uzbekistan")


def h(name: str) -> list:
    return [(name, WHITE, "700")]


def p(s: str, indent: int = 7) -> list:
    return [(" " * indent, TEXT), (s, TEXT)]


def opt(flag: str, desc: str) -> list:
    return [(" " * 7, TEXT), (flag.ljust(16), WHITE, "700"), (desc, TEXT)]


UL = ' text-decoration="underline"'
MAN = [
    None,
    [],
    h("NAME"),
    [(" " * 7, TEXT), ("xcrpty7", WHITE, "700"), (" - full-stack & AI-agent developer from Tashkent, Uzbekistan", TEXT)],
    [],
    h("SYNOPSIS"),
    [(" " * 7, TEXT), ("xcrpty7", WHITE, "700"), (" [", MUTED), ("--idea", WHITE, "700"), (" ", TEXT), ("text", TEXT, "", UL),
     ("] [", MUTED), ("--deadline", WHITE, "700"), (" ", TEXT), ("3-7d", TEXT, "", UL), ("] [", MUTED),
     ("--lang", WHITE, "700"), (" ", TEXT), ("uz|ru|en", TEXT, "", UL), ("] ", MUTED), ("ship", WHITE, "700")],
    [],
    h("DESCRIPTION"),
    p("Builds AI agents that live in Telegram and do real work: chats, databases, APIs, reports."),
    p("The model talks, the code decides, and nothing is sent without your explicit yes."),
    p("Ships web apps with auth, payments and admin panels that real businesses use every day."),
    p("Writes code since 14. Speaks Uzbek, Russian and English."),
    [],
    h("OPTIONS"),
    opt("--mvp", "MVP in 3-7 days; polish once real users touch it"),
    opt("--secure", "validated input, parameterized SQL, secrets only in .env"),
    opt("--code-decides", "the LLM proposes; the code checks, limits and executes"),
    opt("--measured", "no test or number behind it, no claim"),
    [],
    h("BUGS"),
    p("Each mistake happens only once: every solved bug is written to memory."),
    [],
    h("SEE ALSO"),
    [(" " * 7, TEXT), ("telegram", WHITE, "700"), ("(1) t.me/xcrpty7,  ", MUTED), ("ai-tutor", WHITE, "700"),
     ("(7) live demo,  ", MUTED), ("github", WHITE, "700"), ("(1) xcrpty7", MUTED)],
    [],
    "footer",
]


def manpage() -> str:
    width, size, lh, x0 = 1000, 14, 21, 30
    top = 68
    height = top + len(MAN) * lh + 44
    rows_, t = [], 0.25
    right = width - x0
    for i, parts in enumerate(MAN):
        y = top + i * lh
        t += 0.035
        op, show = appear(t)
        if parts is None:
            line = (text(x0, y, "XCRPTY7(1)", size, WHITE, "700") +
                    text(width / 2, y, "General Commands Manual", size, MUTED, anchor="middle") +
                    text(right, y, "XCRPTY7(1)", size, WHITE, "700", anchor="end"))
        elif parts == "footer":
            line = (text(x0, y, "xcrpty7 2026.11", size, MUTED) +
                    text(width / 2, y, "Tashkent, UZ", size, MUTED, anchor="middle") +
                    text(right, y, "XCRPTY7(1)", size, WHITE, "700", anchor="end"))
        elif not parts:
            continue
        else:
            line = row(x0, y, parts, size)
        rows_.append(f'<g opacity="{op}">{show}{line}</g>')
    bar_y = height - 38
    status = f" Manual page xcrpty7(1) line 1/{len(MAN)} (END) (press q to quit)"
    op, show = appear(t + 0.2)
    pager = (f'<g opacity="{op}">{show}<rect x="{x0 - 6}" y="{bar_y}" width="{mono_width(status, size) + 8:.0f}" height="22" fill="{TEXT}"/>'
             f'{text(x0 - 4, bar_y + 16, status, size, BG, "700")}'
             f'<rect class="cur" x="{x0 + mono_width(status, size) + 8:.0f}" y="{bar_y + 2}" width="{size * 0.6:.1f}" '
             f'height="18" fill="{WHITE}"/></g>')
    back, front = window(width, height, "man xcrpty7", "less")
    body = f"""{back}
<g font-family="{MONO}">{''.join(rows_)}{pager}</g>
{front}"""
    return svg(width, height, body, BLINK, "man xcrpty7: full-stack and AI-agent developer from Tashkent, Uzbekistan")


if __name__ == "__main__":
    write("whoami.svg", neofetch())
    write("man.svg", manpage())
    print("whoami, man: ok")
