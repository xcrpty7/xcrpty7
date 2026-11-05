"""Project cards: TUI panes with a 1-bit pixel icon and a light streak running around the frame."""
from svg_kit import BG, BORDER, DIM, MONO, MUTED, TEXT, WHITE, bitmap, mono_width, row, svg, text, wrap, write

CARD_W, H = 480, 236

# (label, reverse video?, ls -l permissions)
TAGS = {
    "demo": ("LIVE DEMO", True, "drwxr-xr-x"),
    "private": ("PRIVATE", False, "drwx------"),
    "nasa": ("NASA SPACE APPS", True, "drwx------"),
}

ICONS = {
    "moon-mars": [
        "....####....",
        "..###.......",
        ".###........",
        ".##......##.",
        "###.....####",
        "###.....####",
        "###......##.",
        "###.........",
        ".##.........",
        ".###........",
        "..###.......",
        "....####....",
    ],
    "ai-tutor": [
        "............",
        ".####..####.",
        "#....##....#",
        "#.##.##.##.#",
        "#....##....#",
        "#.##.##.##.#",
        "#....##....#",
        "#.##.##.##.#",
        "#....##....#",
        "#####..#####",
        ".....##.....",
        "............",
    ],
    "jarvis": [
        ".....##.....",
        ".....##.....",
        "..########..",
        ".#........#.",
        ".#.##..##.#.",
        ".#.##..##.#.",
        ".#........#.",
        ".#..####..#.",
        ".#........#.",
        "..########..",
        "...#....#...",
        "..###..###..",
    ],
    "claude-kit-uz": [
        "............",
        "....####....",
        "...#....#...",
        "############",
        "#..........#",
        "#..........#",
        "#####..#####",
        "#....##....#",
        "#..........#",
        "#..........#",
        "############",
        "............",
    ],
    "kuch-3d": [
        "...######...",
        "..#......#..",
        "..########..",
        "..#......#..",
        "..#...##.#..",
        "..#..##..#..",
        "..#.####.#..",
        "..#..##..#..",
        "..#.##...#..",
        "..#......#..",
        "..########..",
        "...######...",
    ],
    "savdo-e": [
        "............",
        "###.........",
        "..#.........",
        "..#########.",
        "..#.#.#.#.#.",
        "..#########.",
        "...#.#.#.#..",
        "...#######..",
        "...#........",
        "...########.",
        "...##...##..",
        "...##...##..",
    ],
    "topex": [
        ".....#......",
        ".....###....",
        ".....#......",
        "....####....",
        "..########..",
        "############",
        ".#........#.",
        ".#.##..##.#.",
        ".#.##..##.#.",
        ".#........#.",
        ".#...##...#.",
        "############",
    ],
    "maftravel": [
        ".....##.....",
        ".....##.....",
        ".....##.....",
        "....####....",
        "..########..",
        "############",
        "##...##...##",
        ".....##.....",
        ".....##.....",
        "....####....",
        "...######...",
        "............",
    ],
    "osint": [
        "............",
        "............",
        "....####....",
        "..##....##..",
        ".#...##...#.",
        "#...####...#",
        "#...####...#",
        ".#...##...#.",
        "..##....##..",
        "....####....",
        "............",
        "............",
    ],
}

# second frames: the icon flips to it for a moment (blink, wave, flicker); (frame, period s, shown %)
ICON_ALT = {
    "jarvis": ([".....##.....", ".....##.....", "..########..", ".#........#.", ".#........#.", ".#.##..##.#.",
                ".#........#.", ".#..####..#.", ".#........#.", "..########..", "...#....#...", "..###..###.."], 4.2, 4),
    "osint": (["............", "............", "............", "............", "............", ".##########.",
               "..#.#..#.#..", "............", "............", "............", "............", "............"], 5.1, 4),
    "kuch-3d": (["...######...", "..#......#..", "..########..", "..#......#..", "..#......#..", "..#......#..",
                 "..#......#..", "..#......#..", "..#......#..", "..#......#..", "..########..", "...######..."], 3.3, 6),
    "topex": ([".....##.....", ".....#.##...", ".....#......", "....####....", "..########..", "############",
               ".#........#.", ".#.##..##.#.", ".#.##..##.#.", ".#........#.", ".#...##...#.", "############"], 1.4, 50),
    "maftravel": ([".....##.....", ".....##.....", ".....##.....", "....####....", "..########..", "############",
                   "#....##....#", ".....##.....", ".....##.....", "....####....", "...######...", "............"], 1.8, 50),
    "moon-mars": (["....####....", "..###.......", ".###........", ".##.........", "###......##.", "###......##.",
                   "###.........", "###.........", ".##.........", ".###........", "..###.......", "....####...."], 2.6, 50),
}


CARDS = {
    "moon-mars": dict(
        title="Moon & Mars on Earth", tag="nasa", width=980,
        metric="30 Earth sites · 18 Moon/Mars targets · 6 criteria",
        desc="Interactive atlas of places on Earth that stand in for lunar and Martian conditions. "
             "Similarity is computed, not claimed: a six-criteria index from open data with a source behind "
             "every score. 3D globe, reverse search from a Mars target, side-by-side Earth/Mars maps, offline mode.",
        chips=["React", "three.js / globe.gl", "MapLibre", "Express", "MongoDB", "Zod", "12 unit tests"]),
    "ai-tutor": dict(
        title="AI Tutor", tag="demo", metric="uz · ru · en",
        desc="School AI tutor that leads students to the answer instead of doing their homework. "
             "Sticks to school subjects and resists prompt injection. Web, Telegram bot and Mini App.",
        chips=["TypeScript", "LLM", "Telegram", "Mini App"]),
    "jarvis": dict(
        title="Jarvis", tag="private", metric="$0.17 → $0.02 per call",
        desc="Personal Telegram assistant that runs Claude Code agents. The model proposes, the code "
             "decides, and nothing is sent without an explicit yes.",
        chips=["Python", "Agent SDK", "MCP", "Telethon"]),
    "claude-kit-uz": dict(
        title="claude-kit-uz", tag="private", metric="1-click install",
        desc="Claude Code booster for Uzbek-speaking devs on Windows: task router, BM25 RAG with "
             "Uzbek/Russian stemming, error memory on hooks.",
        chips=["Python", "PowerShell", "Hooks", "RAG"]),
    "kuch-3d": dict(
        title="KUCH · 3D ad", tag="private", metric="$0 budget",
        desc="Energy-drink commercial for a fictional brand, built entirely from Python scripts in "
             "Blender: can, condensation drops, lights, camera moves.",
        chips=["Blender bpy", "Cycles", "Geometry Nodes"]),
    "savdo-e": dict(
        title="Savdo-E", tag="private", metric="team of 5 · JWT + OAuth",
        desc="Sales management platform for small and mid-size businesses: products, sales, reports "
             "and an admin panel.",
        chips=["Node/Express", "React", "MongoDB", "Docker"]),
    "topex": dict(
        title="TOPEX Texnikumi", tag="private", metric="frontend + backend",
        desc="Education platform for a private technical school in Tashkent, grades 10-11: site, "
             "backend and deploy scripts.",
        chips=["JavaScript", "HTML/CSS", "Render"]),
    "maftravel": dict(
        title="MafTravel", tag="private", metric="SPA + /api",
        desc="Travel planner single-page app with serverless-style API handlers, deployed on Render.",
        chips=["React", "Vite", "JavaScript"]),
    "osint": dict(
        title="OSINT portfolio", tag="private", metric="pure HTML/CSS/JS",
        desc="OSINT / offensive-security portfolio: fog aura, particle network and an Obsidian-style "
             "OSINT chain graph.",
        chips=["HTML", "CSS", "JavaScript"]),
}


def chips(items: list, y: float, x0: float = 26) -> str:
    parts = []
    for label in items:
        parts += [("[", DIM), (label, MUTED), ("]", DIM), ("  ", DIM)]
    return row(x0, y, parts, 12.5)


def label_on_frame(x: float, y: float, s: str, size: float, reverse: bool, anchor_end: bool = False) -> str:
    """A label that sits on the frame line, cutting it like a TUI pane title."""
    w = mono_width(s, size) + 14
    left = x - w if anchor_end else x
    fill, ink = (TEXT, BG) if reverse else (BG, MUTED)
    stroke = "" if reverse else f' stroke="{BORDER}"'
    return (f'<rect x="{left:.1f}" y="{y - 10}" width="{w:.1f}" height="20" rx="2" fill="{fill}"{stroke}/>'
            + text(left + 7, y + 4.5, s, size, ink, "700"))


def card(key: str, data: dict) -> str:
    W = data.get("width", CARD_W)
    tag_text, reverse, perms = TAGS[data["tag"]]
    inset = 10
    fx, fy, fw, fh = inset, inset, W - 2 * inset, H - 2 * inset
    per_line = int((W - 52) / (13 * 0.6))
    lines = wrap(data["desc"], per_line)[:4]
    desc = "".join(text(26, 116 + i * 20, line, 13, "#cfcfcf") for i, line in enumerate(lines))
    perimeter = 2 * (fw + fh)
    path_label = f" ~/projects/{key} "
    crisp = ' shape-rendering="crispEdges"'
    icon, icon_css = bitmap(ICONS[key], 33, 41, 3, WHITE, crisp), ""
    if key in ICON_ALT:
        frame, period, shown = ICON_ALT[key]
        icon = (bitmap(ICONS[key], 33, 41, 3, WHITE, crisp + ' class="ia"')
                + bitmap(frame, 33, 41, 3, WHITE, crisp + ' class="ib" opacity="0"'))
        cut = 100 - shown
        icon_css = (f".ia{{animation:ia {period}s steps(1) infinite}}.ib{{animation:ib {period}s steps(1) infinite}}"
                    f"@keyframes ia{{0%{{opacity:1}}{cut}%,100%{{opacity:0}}}}"
                    f"@keyframes ib{{0%{{opacity:0}}{cut}%,100%{{opacity:1}}}}")
    body = f"""<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{BG}" stroke="{BORDER}"/>
<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="6" stroke="{BORDER}"/>
<rect class="streak" x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="6" stroke="{WHITE}" stroke-width="2"
 stroke-dasharray="120 {perimeter}" stroke-linecap="round" opacity="0"/>
<g font-family="{MONO}">
<rect x="26" y="{fy - 9}" width="{mono_width(path_label, 11.5):.1f}" height="18" fill="{BG}"/>
{text(26, fy + 4, path_label, 11.5, DIM)}
{label_on_frame(W - 26, fy, tag_text, 11, reverse, anchor_end=True)}
<rect x="26" y="34" width="50" height="50" rx="4" stroke="{BORDER}"/>
{icon}
{text(92, 56, data["title"], 20, WHITE, "700")}
{text(92, 78, data["metric"], 12.5, MUTED)}
{text(W - 26, 78, perms, 12, DIM, anchor="end")}
{desc}
{chips(data["chips"], H - 34)}
</g>"""
    css = f""".streak{{opacity:1;animation:run 8s linear infinite}}
@keyframes run{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-{perimeter}}}}}{icon_css}"""
    return svg(W, H, body, css, f"{data['title']}: {data['desc']}")


if __name__ == "__main__":
    for name, info in CARDS.items():
        write(f"cards/{name}.svg", card(name, info))
    print(f"cards: {len(CARDS)} ok")
