"""Tech-stack panel (simple-icons glyphs, no external requests) and the "how I work" strip."""
from svg_kit import (BG, BLUE, BORDER, CYAN, DIM, EMOJI, GREEN, MONO, MUTED, ORANGE, PANEL, PINK, PURPLE,
                     SANS, TEXT, esc, icon_path, readable, svg, wrap, write)

STACK = [
    ("AI & AGENTS", PURPLE, [("claude", "Claude Code", "D97757"), ("anthropic", "Agent SDK", "191919"),
                             ("modelcontextprotocol", "MCP", "000000"), ("telegram", "aiogram 3", "26A5E4"),
                             ("obsidian", "RAG · BM25", "7C3AED")]),
    ("BACKEND", GREEN, [("python", "Python", "3776AB"), ("fastapi", "FastAPI", "009688"),
                        ("nodedotjs", "Node.js", "5FA04E"), ("express", "Express", "000000"),
                        ("nestjs", "NestJS", "E0234E"), ("fastify", "Fastify", "000000")]),
    ("FRONTEND", CYAN, [("react", "React", "61DAFB"), ("nextdotjs", "Next.js", "000000"),
                        ("typescript", "TypeScript", "3178C6"), ("tailwindcss", "Tailwind", "06B6D4"),
                        ("vite", "Vite", "646CFF"), ("redux", "Redux", "764ABC")]),
    ("DATA", BLUE, [("postgresql", "PostgreSQL", "4169E1"), ("supabase", "Supabase", "3FCF8E"),
                    ("mongodb", "MongoDB", "47A248"), ("sqlite", "SQLite", "003B57"),
                    ("prisma", "Prisma", "2D3748"), ("redis", "Redis", "FF4438")]),
    ("DEVOPS", ORANGE, [("docker", "Docker", "2496ED"), ("linux", "Linux", "FCC624"), ("git", "Git", "F05032"),
                        ("githubactions", "Actions", "2088FF"), ("vercel", "Vercel", "000000"),
                        ("render", "Render", "000000"), ("cloudflare", "Cloudflare", "F38020")]),
    ("MOBILE & 3D", PINK, [("flutter", "Flutter", "02569B"), ("dart", "Dart", "0175C2"),
                                   ("kotlin", "Kotlin", "7F52FF"), ("godotengine", "Godot", "478CBF"),
                                   ("blender", "Blender", "E87D0D"), ("openjdk", "JavaFX", "000000"),
                                   ("ffmpeg", "FFmpeg", "007808")]),
]

RULES = [
    ("🚀", "MVP in 3–7 days", "ship first, polish once real users touch it", GREEN),
    ("🛡️", "Security first", "validated input, parameterized SQL, secrets only in .env", "#ff6b81"),
    ("⚖️", "Code decides", "the LLM proposes, the code checks and executes", PURPLE),
    ("📏", "Measured", "no test or number behind it, no claim", CYAN),
    ("🧠", "Each mistake once", "every solved bug goes into memory", ORANGE),
]

ROW_H, LABEL_W, PITCH, TILE = 88, 200, 104, 52


def tile(x: float, y: float, slug: str, name: str, color: str, delay: float, glow: bool) -> str:
    fill = readable(f"#{color}")
    scale = 26 / 24
    cls = "t g" if glow else "t"
    return (f'<g class="{cls}" style="animation-delay:{delay:.2f}s">'
            f'<rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="13" fill="{BG}" stroke="{fill}" stroke-opacity="0.35"/>'
            f'<path transform="translate({x + 13} {y + 13}) scale({scale:.4f})" d="{icon_path(slug)}" fill="{fill}"/>'
            f'<text x="{x + TILE / 2}" y="{y + TILE + 18}" text-anchor="middle" font-family="{SANS}" '
            f'font-size="12.5" fill="{MUTED}">{esc(name)}</text></g>')


def stack() -> str:
    width = 1000
    height = 24 + ROW_H * len(STACK) + 8
    rows, delay = [], 0.1
    for r, (label, accent, items) in enumerate(STACK):
        y = 24 + r * ROW_H
        rows.append(f'<rect x="24" y="{y + 8}" width="4" height="36" rx="2" fill="{accent}"/>'
                    f'<text x="40" y="{y + 25}" font-family="{MONO}" font-size="13" font-weight="700" '
                    f'letter-spacing="1.5" fill="{accent}">{esc(label)}</text>'
                    f'<text x="40" y="{y + 44}" font-family="{MONO}" font-size="11.5" fill="{DIM}">{len(items):02d} tools</text>')
        if r:
            rows.append(f'<path d="M24 {y - 8}H{width - 24}" stroke="{BORDER}" stroke-dasharray="3 6"/>')
        for i, (slug, name, color) in enumerate(items):
            rows.append(tile(LABEL_W + i * PITCH, y, slug, name, color, delay, r == 0))
            delay += 0.04
    body = (f'<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="16" fill="{PANEL}" stroke="{BORDER}"/>'
            + "".join(rows))
    css = """.t{animation:up .55s ease-out both}
@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.g rect{animation:glow 3s ease-in-out infinite}
@keyframes glow{0%,100%{stroke-opacity:.35}50%{stroke-opacity:.95}}"""
    return svg(width, height, body, css, "Tech stack")


def rules() -> str:
    width, height, gap, pad = 1000, 196, 12, 0
    tile_w = (width - gap * (len(RULES) - 1)) / len(RULES)
    parts = []
    for i, (emoji, title, sub, accent) in enumerate(RULES):
        x = pad + i * (tile_w + gap)
        lines = "".join(f'<text x="{x + 18:.0f}" y="{124 + k * 18}">{esc(line)}</text>'
                        for k, line in enumerate(wrap(sub, 25)[:3]))
        parts.append(f"""<g class="r" style="animation-delay:{0.15 * i:.2f}s">
<rect x="{x + 0.5:.1f}" y="0.5" width="{tile_w - 1:.1f}" height="{height - 1}" rx="14" fill="{PANEL}" stroke="{BORDER}"/>
<rect x="{x + 18:.1f}" y="0.5" width="{tile_w - 36:.1f}" height="3" rx="1.5" fill="{accent}"/>
<text x="{x + 18:.0f}" y="38" font-family="{MONO}" font-size="13" font-weight="700" fill="{accent}">0{i + 1}</text>
<text x="{x + tile_w - 18:.0f}" y="42" text-anchor="end" font-family="{EMOJI}" font-size="24" fill="#fff">{emoji}</text>
<text x="{x + 18:.0f}" y="92" font-family="{SANS}" font-size="17" font-weight="700" fill="{TEXT}">{esc(title)}</text>
<g font-family="{SANS}" font-size="13" fill="{MUTED}">{lines}</g></g>""")
    css = """.r{animation:up .6s ease-out both}
@keyframes up{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}"""
    return svg(width, height, "".join(parts), css, "How I work")


if __name__ == "__main__":
    write("stack.svg", stack())
    write("rules.svg", rules())
    print("stack, rules: ok")
