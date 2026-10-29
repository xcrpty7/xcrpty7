"""Project cards: one SVG per project with a light streak running around the border."""
from svg_kit import (BG, BORDER, CYAN, EMOJI, GREEN, MONO, MUTED, PANEL, PURPLE, SANS, TEXT, esc,
                     mono_width, svg, wrap, write)

W, H = 480, 228

TAGS = {
    "demo": ("LIVE DEMO", GREEN),
    "oss": ("OPEN SOURCE", CYAN),
    "private": ("PRIVATE", PURPLE),
}

CARDS = {
    "ai-tutor": dict(
        emoji="🎓", title="AI Tutor", tag="demo", metric="uz · ru · en",
        desc="School AI tutor that leads students to the answer instead of doing their homework. "
             "Sticks to school subjects and resists prompt injection. Web, Telegram bot and Mini App.",
        chips=["TypeScript", "LLM", "Telegram", "Mini App"]),
    "jarvis": dict(
        emoji="🤵", title="Jarvis", tag="private", metric="$0.17 → $0.02 / call",
        desc="Personal Telegram assistant that runs Claude Code agents. The model proposes, the code "
             "decides, and nothing is sent without an explicit yes.",
        chips=["Python", "Agent SDK", "MCP", "Telethon"]),
    "claude-kit-uz": dict(
        emoji="🧰", title="claude-kit-uz", tag="private", metric="1-click install",
        desc="Claude Code booster for Uzbek-speaking devs on Windows: task router, BM25 RAG with "
             "Uzbek/Russian stemming, error memory on hooks.",
        chips=["Python", "PowerShell", "Hooks", "RAG"]),
    "kuch-3d": dict(
        emoji="🥫", title="KUCH · 3D ad", tag="private", metric="$0 budget",
        desc="Energy-drink commercial for a fictional brand, built entirely from Python scripts in "
             "Blender: can, condensation drops, lights, camera moves.",
        chips=["Blender bpy", "Cycles", "Geometry Nodes"]),
    "savdo-e": dict(
        emoji="🛒", title="Savdo-E", tag="private", metric="team of 5 · JWT + OAuth",
        desc="Sales management platform for small and mid-size businesses: products, sales, reports "
             "and an admin panel.",
        chips=["Node/Express", "React", "MongoDB", "Docker"]),
    "topex": dict(
        emoji="🏫", title="TOPEX Texnikumi", tag="oss", metric="frontend + backend",
        desc="Education platform for a private technical school in Tashkent, grades 10–11: site, "
             "backend and deploy scripts.",
        chips=["JavaScript", "HTML/CSS", "Render"]),
    "maftravel": dict(
        emoji="✈️", title="MafTravel", tag="oss", metric="SPA + /api",
        desc="Travel planner single-page app with serverless-style API handlers, deployed on Render.",
        chips=["React", "Vite", "JavaScript"]),
    "osint": dict(
        emoji="🕵️", title="OSINT portfolio", tag="oss", metric="pure HTML/CSS/JS",
        desc="OSINT / offensive-security portfolio: fog aura, particle network and an Obsidian-style "
             "OSINT chain graph.",
        chips=["HTML", "CSS", "JavaScript"]),
}


def chips(items: list, y: float) -> str:
    out, x = [], 24
    for label in items:
        w = mono_width(label, 12) + 20
        out.append(f'<rect x="{x:.0f}" y="{y}" width="{w:.0f}" height="24" rx="12" fill="{BG}" stroke="{BORDER}"/>'
                   f'<text x="{x + w / 2:.0f}" y="{y + 16.5}" text-anchor="middle" font-family="{MONO}" '
                   f'font-size="12" fill="{MUTED}">{esc(label)}</text>')
        x += w + 8
    return "".join(out)


def card(key: str, data: dict) -> str:
    tag_text, accent = TAGS[data["tag"]]
    tag_w = mono_width(tag_text, 11) + 22
    lines = wrap(data["desc"], 58)[:4]
    desc = "".join(f'<text x="24" y="{104 + i * 21}">{esc(line)}</text>' for i, line in enumerate(lines))
    perimeter = 2 * (W + H)
    body = f"""<defs>
<linearGradient id="bg-{key}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#121a26"/><stop offset="1" stop-color="{PANEL}"/></linearGradient>
<linearGradient id="streak-{key}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="{CYAN}"/></linearGradient>
<radialGradient id="halo-{key}" cx="1" cy="0" r="0.8"><stop offset="0" stop-color="{accent}" stop-opacity="0.16"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
</defs>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="url(#bg-{key})" stroke="{BORDER}" stroke-width="1.5"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" fill="url(#halo-{key})"/>
<rect class="streak" x="1" y="1" width="{W - 2}" height="{H - 2}" rx="16" stroke="url(#streak-{key})" stroke-width="2.5"
 stroke-dasharray="140 {perimeter}" stroke-linecap="round" opacity="0"/>
<rect x="24" y="24" width="46" height="46" rx="12" fill="{BG}" stroke="{BORDER}"/>
<text x="47" y="56" text-anchor="middle" font-family="{EMOJI}" font-size="24" fill="#fff">{data["emoji"]}</text>
<text x="84" y="47" font-family="{SANS}" font-size="21" font-weight="700" fill="{TEXT}">{esc(data["title"])}</text>
<text x="84" y="68" font-family="{MONO}" font-size="12.5" fill="{accent}">{esc(data["metric"])}</text>
<rect x="{W - 24 - tag_w:.0f}" y="28" width="{tag_w:.0f}" height="22" rx="11" fill="{accent}" fill-opacity="0.12" stroke="{accent}" stroke-opacity="0.55"/>
<text x="{W - 24 - tag_w / 2:.0f}" y="43" text-anchor="middle" font-family="{MONO}" font-size="11" font-weight="700" letter-spacing="1" fill="{accent}">{tag_text}</text>
<g font-family="{SANS}" font-size="14.5" fill="#c9d1d9">{desc}</g>
{chips(data["chips"], H - 44)}"""
    css = f""".streak{{opacity:1;animation:run 7s linear infinite}}
@keyframes run{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-{perimeter}}}}}"""
    return svg(W, H, body, css, f"{data['title']}: {data['desc']}")


if __name__ == "__main__":
    for name, info in CARDS.items():
        write(f"cards/{name}.svg", card(name, info))
    print(f"cards: {len(CARDS)} ok")
