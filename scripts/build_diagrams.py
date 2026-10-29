"""Agent pipeline diagram (packets flow through it) and the journey timeline (real dates only)."""
from svg_kit import (BG, BORDER, CYAN, DIM, EMOJI, GREEN, MONO, MUTED, ORANGE, PANEL, PINK, PURPLE,
                     SANS, STATIC, TEXT, esc, icon_path, smil, svg, write)

PIPELINE = [
    ("telegram", None, "Telegram", "you write", CYAN),
    (None, "🧭", "Router", "decision tree", ORANGE),
    ("claude", None, "LLM brain", "proposes, no tools", "#D97757"),
    (None, "🛡️", "Code guard", "checks & limits", GREEN),
    ("modelcontextprotocol", None, "MCP tools", "chats · DB · APIs", PURPLE),
    (None, "✅", "Your yes", "sends need your OK", PINK),
]

JOURNEY = [
    ("2025-03", "Joined GitHub", "first repos", DIM),
    ("2025-07", "Team React apps", "crew of 8, Redux", CYAN),
    ("2026-03", "Savdo-E", "sales platform, team of 5", GREEN),
    ("2026-06", "TOPEX Texnikumi", "school platform, 187 commits", GREEN),
    ("2026-07", "MafTravel", "travel planner SPA", GREEN),
    ("2026-08", "AI Tutor", "injection-resistant, live demo", PURPLE),
    ("2026-09", "AI coding setup", "router · RAG · error memory", PURPLE),
    ("2026-10", "NASA Space Apps", "Moon & Mars on Earth", ORANGE),
    ("2026-10", "Jarvis 0.8", "Claude Code agents in Telegram", PINK),
]


def pipeline() -> str:
    width, height = 1000, 250
    box_w, box_h, gap, top = 128, 112, 30, 54
    x0 = (width - (len(PIPELINE) * box_w + (len(PIPELINE) - 1) * gap)) / 2
    mid = top + box_h / 2
    boxes, arrows = [], []
    for i, (slug, emoji, title, sub, accent) in enumerate(PIPELINE):
        x = x0 + i * (box_w + gap)
        cx = x + box_w / 2
        if slug:
            glyph = (f'<path transform="translate({cx - 13:.1f} {top + 18}) scale(1.0833)" '
                     f'd="{icon_path(slug)}" fill="{accent}"/>')
        else:
            glyph = (f'<text x="{cx:.1f}" y="{top + 40}" text-anchor="middle" font-family="{EMOJI}" '
                     f'font-size="24" fill="#fff">{emoji}</text>')
        boxes.append(f'<g class="n" style="animation-delay:{0.12 * i:.2f}s">'
                     f'<rect x="{x:.1f}" y="{top}" width="{box_w}" height="{box_h}" rx="14" fill="{BG}" '
                     f'stroke="{accent}" stroke-opacity="0.55"/>{glyph}'
                     f'<text x="{cx:.1f}" y="{top + 72}" text-anchor="middle" font-family="{SANS}" font-size="15" '
                     f'font-weight="700" fill="{TEXT}">{esc(title)}</text>'
                     f'<text x="{cx:.1f}" y="{top + 92}" text-anchor="middle" font-family="{MONO}" font-size="10.5" '
                     f'fill="{MUTED}">{esc(sub)}</text></g>')
        if i < len(PIPELINE) - 1:
            ax = x + box_w
            arrows.append(f'<path d="M{ax + 4:.1f} {mid}H{ax + gap - 6:.1f}" stroke="{DIM}" stroke-width="2"/>'
                          f'<path d="M{ax + gap - 11:.1f} {mid - 5}L{ax + gap - 5:.1f} {mid}L{ax + gap - 11:.1f} {mid + 5}" '
                          f'stroke="{DIM}" stroke-width="2"/>')
    # packets travel the whole chain; the guard bounces a red one back now and then
    last_cx = x0 + (len(PIPELINE) - 1) * (box_w + gap) + box_w / 2
    track = f"M{x0 + box_w / 2:.1f} {mid}H{last_cx:.1f}"
    packets = "".join(
        f'<circle r="5" fill="{color}" filter="url(#glow)" opacity="{0 if STATIC else 1}">'
        + smil(f'<animateMotion dur="5s" begin="{delay}s" repeatCount="indefinite" path="{track}" '
               f'keyPoints="0;1" keyTimes="0;1" calcMode="linear"/>')
        + "</circle>"
        for color, delay in ((GREEN, 0), (CYAN, 1.7), (PURPLE, 3.4)))
    guard_x = x0 + 3 * (box_w + gap) + box_w / 2
    llm_x = x0 + 2 * (box_w + gap) + box_w / 2
    reject = (f'<circle r="5" fill="#ff4d6d" filter="url(#glow)" opacity="{0 if STATIC else 1}">'
              + smil(f'<animateMotion dur="7s" repeatCount="indefinite" '
                     f'path="M{llm_x:.1f} {mid}H{guard_x:.1f}C{guard_x:.1f} {mid + 70} {llm_x:.1f} {mid + 70} {llm_x:.1f} {mid}"/>')
              + "</circle>")
    caption = ("prompt prefix 21k → 2k tokens  ·  cost per call $0.17 → $0.02  ·  "
               "risky actions bounce back to the model")
    body = f"""<defs><filter id="glow" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.5" result="b"/>
<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="16" fill="{PANEL}" stroke="{BORDER}"/>
<text x="24" y="34" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1.5" fill="{GREEN}">THE MODEL TALKS · THE CODE DECIDES</text>
<text x="{width - 24}" y="34" text-anchor="end" font-family="{MONO}" font-size="11" fill="{DIM}">jarvis · claude code agents</text>
{''.join(arrows)}{reject}{packets}{''.join(boxes)}
<text x="{width / 2}" y="{height - 26}" text-anchor="middle" font-family="{MONO}" font-size="12" fill="{MUTED}">{esc(caption)}</text>"""
    css = """.n{animation:pop .5s ease-out both}
@keyframes pop{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}"""
    return svg(width, height, body, css, "How my agents work: the model proposes, the code decides")


def journey() -> str:
    width, height = 1000, 270
    left, right, axis = 110, 880, 132
    step = (right - left) / (len(JOURNEY) - 1)
    parts = []
    for i, (date, title, sub, accent) in enumerate(JOURNEY):
        x = left + i * step
        up = i % 2 == 0
        ty = axis - 74 if up else axis + 52
        stem = f"M{x:.1f} {axis - 12 if up else axis + 12}V{axis - 46 if up else axis + 26}"
        parts.append(f'<g class="j" style="animation-delay:{0.6 + 0.18 * i:.2f}s">'
                     f'<path d="{stem}" stroke="{accent}" stroke-opacity="0.6" stroke-dasharray="2 3"/>'
                     f'<circle cx="{x:.1f}" cy="{axis}" r="8" fill="{BG}" stroke="{accent}" stroke-width="2.5"/>'
                     f'<circle cx="{x:.1f}" cy="{axis}" r="3" fill="{accent}"/>'
                     f'<text x="{x:.1f}" y="{ty}" text-anchor="middle" font-family="{MONO}" font-size="11" '
                     f'fill="{accent}">{date}</text>'
                     f'<text x="{x:.1f}" y="{ty + 19}" text-anchor="middle" font-family="{SANS}" font-size="13.5" '
                     f'font-weight="700" fill="{TEXT}">{esc(title)}</text>'
                     f'<text x="{x:.1f}" y="{ty + 36}" text-anchor="middle" font-family="{SANS}" font-size="11" '
                     f'fill="{MUTED}">{esc(sub)}</text></g>')
    now_x = right + 44
    body = f"""<defs><linearGradient id="axis" gradientUnits="userSpaceOnUse" x1="{left - 30}" y1="0" x2="{now_x}" y2="0"><stop offset="0" stop-color="{DIM}"/>
<stop offset="0.5" stop-color="{GREEN}"/><stop offset="1" stop-color="{PINK}"/></linearGradient></defs>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="16" fill="{PANEL}" stroke="{BORDER}"/>
<path class="axis" d="M{left - 30} {axis}H{now_x - 10}" stroke="url(#axis)" stroke-width="3" stroke-linecap="round"
 stroke-dasharray="{now_x - left + 20}" stroke-dashoffset="0"/>
{''.join(parts)}
<circle class="now" cx="{now_x}" cy="{axis}" r="7" fill="{GREEN}"/>
<text x="{now_x}" y="{axis + 30}" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" fill="{GREEN}">NOW</text>"""
    css = f""".axis{{animation:draw 1.6s ease-out both}}
@keyframes draw{{from{{stroke-dashoffset:{now_x - left + 20}}}to{{stroke-dashoffset:0}}}}
.j{{animation:in .5s ease-out both}}
@keyframes in{{from{{opacity:0}}to{{opacity:1}}}}
.now{{transform-box:fill-box;transform-origin:center;animation:beat 1.4s ease-in-out infinite}}
@keyframes beat{{0%,100%{{transform:scale(1);opacity:1}}50%{{transform:scale(1.6);opacity:.5}}}}"""
    return svg(width, height, body, css, "Journey: from first repos in 2025 to AI agents in 2026")


if __name__ == "__main__":
    write("pipeline.svg", pipeline())
    write("journey.svg", journey())
    print("pipeline, journey: ok")
