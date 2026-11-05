"""Agent pipeline (packets flow through it) and the journey as a `git log --graph` (real dates only)."""
from svg_kit import (BG, BLINK, BORDER, DIM, MONO, MUTED, STATIC, TEXT, WHITE, appear, bitmap, icon_path,
                     mono_width, short_hash, smil, svg, text, window, write)

PX_ICONS = {
    "router": ["##........##", "##........##", ".##......##.", "..##....##..", "...##..##...", "....####....",
               ".....##.....", ".....##.....", ".....##.....", ".....##.....", "....####....", "....####...."],
    "guard": ["############", "#..........#", "#....##....#", "#....##....#", "#..######..#", "#..######..#",
              "#....##....#", ".#...##...#.", ".#........#.", "..#......#..", "...#....#...", "....####...."],
    "yes": ["............", "..........##", ".........###", "........###.", ".......###..", "##....###...",
            "###..###....", ".######.....", "..####......", "...##.......", "............", "............"],
}

PIPELINE = [
    ("telegram", "Telegram", "you write"),
    ("px:router", "Router", "decision tree"),
    ("claude", "LLM brain", "proposes, no tools"),
    ("px:guard", "Code guard", "checks & limits"),
    ("modelcontextprotocol", "MCP tools", "chats · DB · APIs"),
    ("px:yes", "Your yes", "sends need an OK"),
]

# (lane, date, title, subtitle, decoration); "merge" rows have no date
JOURNEY = [
    ("main", "2026-10", "Jarvis 0.8", "Claude Code agents in Telegram", "HEAD -> main"),
    ("main", "2026-10", "NASA Space Apps", "Moon & Mars on Earth", "tag: nasa"),
    ("main", "2026-09", "AI coding setup", "router · RAG · error memory", ""),
    ("main", "2026-08", "AI Tutor", "injection-resistant, live demo", "tag: live"),
    ("main", "2026-07", "MafTravel", "travel planner SPA", ""),
    ("main", "2026-06", "TOPEX Texnikumi", "school platform, 187 commits", ""),
    ("merge", "", "merge branch 'team'", "", ""),
    ("team", "2026-03", "Savdo-E", "sales platform, team of 5", "team"),
    ("team", "2025-07", "Team React apps", "crew of 8, Redux", "team"),
    ("root", "2025-03", "Joined GitHub", "first repos", ""),
]


def glyph(kind: str, cx: float, top: float) -> str:
    if kind.startswith("px:"):
        return bitmap(PX_ICONS[kind[3:]], cx - 15, top + 18, 2.5, WHITE, ' shape-rendering="crispEdges"')
    return f'<path transform="translate({cx - 14:.1f} {top + 17}) scale(1.1667)" d="{icon_path(kind)}" fill="{WHITE}"/>'


def pipeline() -> str:
    width, height = 1000, 330
    box_w, box_h, gap, top = 130, 112, 26, 92
    x0 = (width - (len(PIPELINE) * box_w + (len(PIPELINE) - 1) * gap)) / 2
    mid = top + box_h / 2
    boxes, arrows = [], []
    for i, (kind, title, sub) in enumerate(PIPELINE):
        x = x0 + i * (box_w + gap)
        cx = x + box_w / 2
        num = f" {i + 1:02d} "
        boxes.append(f'<g class="n" style="animation-delay:{0.12 * i:.2f}s">'
                     f'<rect x="{x:.1f}" y="{top}" width="{box_w}" height="{box_h}" rx="5" fill="{BG}" stroke="{BORDER}"/>'
                     f'<rect x="{x + 10:.1f}" y="{top - 8}" width="{mono_width(num, 11):.1f}" height="16" fill="{BG}"/>'
                     f'{text(x + 10, top + 4, num, 11, DIM)}'
                     f'{glyph(kind, cx, top)}'
                     f'{text(cx, top + 74, title, 13.5, WHITE, "700", anchor="middle")}'
                     f'{text(cx, top + 93, sub, 10.5, MUTED, anchor="middle")}</g>')
        if i < len(PIPELINE) - 1:
            ax = x + box_w
            arrows.append(f'<path d="M{ax + 3:.1f} {mid}H{ax + gap - 5:.1f}" stroke="{DIM}" stroke-width="1.5" stroke-dasharray="3 3"/>'
                          f'<path d="M{ax + gap - 10:.1f} {mid - 4}L{ax + gap - 4:.1f} {mid}L{ax + gap - 10:.1f} {mid + 4}" stroke="{MUTED}" stroke-width="1.5"/>')
    last_cx = x0 + (len(PIPELINE) - 1) * (box_w + gap) + box_w / 2
    track = f"M{x0 + box_w / 2:.1f} {mid}H{last_cx:.1f}"
    hidden = "0" if STATIC else "1"
    packets = "".join(
        f'<rect x="-3.5" y="-3.5" width="7" height="7" fill="{WHITE}" opacity="{0 if STATIC else 1}">'
        + smil(f'<animateMotion dur="5s" begin="{delay}s" repeatCount="indefinite" path="{track}"/>') + "</rect>"
        for delay in (0, 1.7, 3.4))
    llm_x = x0 + 2 * (box_w + gap) + box_w / 2
    guard_x = x0 + 3 * (box_w + gap) + box_w / 2
    loop_y = top + box_h + 34
    reject_path = (f"M{llm_x:.1f} {mid}H{guard_x:.1f}C{guard_x:.1f} {loop_y + 22} {llm_x:.1f} {loop_y + 22} "
                   f"{llm_x:.1f} {mid}")
    reject = (f'<rect x="-4" y="-4" width="8" height="8" stroke="{WHITE}" stroke-width="1.5" fill="{BG}" opacity="{hidden}">'
              + smil(f'<animateMotion dur="7s" repeatCount="indefinite" path="{reject_path}"/>') + "</rect>")
    loop = (f'<path d="M{guard_x:.1f} {top + box_h}C{guard_x:.1f} {loop_y + 22} {llm_x:.1f} {loop_y + 22} {llm_x:.1f} {top + box_h}" '
            f'stroke="{BORDER}" stroke-dasharray="2 4"/>'
            + text((llm_x + guard_x) / 2, loop_y + 30, "denied → back to the model", 10.5, DIM, anchor="middle"))
    caption = "prompt prefix 21k → 2k tokens  ·  cost per call $0.17 → $0.02"
    back, front = window(width, height, "cat ~/agents/pipeline.txt", "jarvis")
    body = f"""{back}
<g font-family="{MONO}">
{text(28, 66, "# the model talks · the code decides", 13, MUTED)}
{text(width - 28, 66, "nothing is sent without your yes", 12, DIM, anchor="end")}
{loop}{''.join(arrows)}{reject}{packets}{''.join(boxes)}
{text(width - 28, height - 22, caption, 12, MUTED, anchor="end")}
{text(28, height - 22, "$ ", 12, WHITE, "700")}<rect class="cur" x="{28 + 2 * 7.2:.1f}" y="{height - 33}" width="7.2" height="13" fill="{WHITE}"/>
</g>
{front}"""
    css = BLINK + """.n{animation:pop .5s ease-out both}
@keyframes pop{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}"""
    return svg(width, height, body, css, "How my agents work: the model proposes, the code decides")


def journey() -> str:
    width, size = 1000, 14.5
    lane = {0: 44, 1: 70}
    top, step, conn = 78, 32, 18
    rows_, nodes, t = [], [], 0.25
    ys = []
    y = top
    for i, (kind, *_rest) in enumerate(JOURNEY):
        ys.append(y)
        y += step
        if kind == "merge" or (kind == "team" and JOURNEY[i + 1][0] == "root"):
            y += conn
    height = y + 34
    end_y = ys[-1] + 44
    merge_i = next(i for i, e in enumerate(JOURNEY) if e[0] == "merge")
    root_i = len(JOURNEY) - 1
    graph = (f'<path class="g0" d="M{lane[0]} {ys[0] - 5}V{ys[root_i] - 5}" stroke="{MUTED}" stroke-width="2" '
             f'stroke-dasharray="{ys[root_i] - ys[0]}"/>'
             f'<path d="M{lane[0]} {ys[merge_i] - 5}C{lane[0]} {ys[merge_i] + 12} {lane[1]} {ys[merge_i] + 12} {lane[1]} {ys[merge_i] + 26}'
             f'V{ys[root_i - 1] + 4}C{lane[1]} {ys[root_i - 1] + 26} {lane[0]} {ys[root_i - 1] + 26} {lane[0]} {ys[root_i] - 14}" '
             f'stroke="{DIM}" stroke-width="2"/>')
    for i, (kind, date, title, sub, deco) in enumerate(JOURNEY):
        y = ys[i]
        x = lane[1] if kind == "team" else lane[0]
        t += 0.14
        op, show = appear(t)
        if kind == "merge":
            nodes.append(f'<circle cx="{x}" cy="{y - 5}" r="6" fill="{BG}" stroke="{WHITE}" stroke-width="2"/>')
        elif i == 0:
            nodes.append(f'<circle class="head" cx="{x}" cy="{y - 5}" r="11" stroke="{WHITE}" stroke-width="1.5"/>'
                         f'<circle cx="{x}" cy="{y - 5}" r="6" fill="{WHITE}"/>')
        else:
            nodes.append(f'<rect x="{x - 5}" y="{y - 10}" width="10" height="10" fill="{WHITE if kind != "team" else TEXT}"/>')
        parts = text(100, y, short_hash(title), size, DIM)
        if kind == "merge":
            parts += text(176, y, title, size, MUTED)
        else:
            parts += text(176, y, date, size, MUTED)
            parts += text(266, y, title, size, WHITE, "700")
            parts += text(266 + mono_width(title, size), y, f"  {sub}", size, MUTED)
        if deco:
            dw = mono_width(deco, 12) + 14
            reverse = deco.startswith("HEAD")
            fill, ink = (TEXT, BG) if reverse else (BG, MUTED)
            stroke = "" if reverse else f' stroke="{BORDER}"'
            parts += (f'<rect x="{width - 28 - dw:.1f}" y="{y - 15}" width="{dw:.1f}" height="20" rx="2" fill="{fill}"{stroke}/>'
                      + text(width - 28 - dw + 7, y, deco, 12, ink, "700"))
        rows_.append(f'<g opacity="{op}">{show}{parts}</g>')
    op, show = appear(t + 0.3)
    end = (f'<g opacity="{op}">{show}<rect x="28" y="{end_y - 15}" width="{mono_width("(END)", 13) + 10:.1f}" height="20" fill="{TEXT}"/>'
           f'{text(33, end_y, "(END)", 13, BG, "700")}'
           f'<rect class="cur" x="{28 + mono_width("(END)", 13) + 16:.1f}" y="{end_y - 14}" width="8" height="17" fill="{WHITE}"/></g>')
    back, front = window(width, height, "git log --graph --oneline", "~/life")
    body = f"""{back}
<g font-family="{MONO}">{graph}{''.join(nodes)}{''.join(rows_)}{end}</g>
{front}"""
    css = BLINK + f""".g0{{animation:draw 1.8s ease-out both}}
@keyframes draw{{from{{stroke-dashoffset:{ys[root_i] - ys[0]}}}to{{stroke-dashoffset:0}}}}
.head{{transform-box:fill-box;transform-origin:center;animation:beat 1.6s ease-in-out infinite}}
@keyframes beat{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.5);opacity:.2}}}}"""
    return svg(width, height, body, css, "Journey: from first repos in 2025 to AI agents in 2026")


if __name__ == "__main__":
    write("pipeline.svg", pipeline())
    write("journey.svg", journey())
    print("pipeline, journey: ok")
