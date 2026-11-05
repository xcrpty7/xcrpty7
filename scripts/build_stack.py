"""Tech stack as `ls /usr/local/bin`: monochrome simple-icons glyphs and a selection that walks the grid."""
from svg_kit import BG, BORDER, DIM, MONO, MUTED, TEXT, WHITE, icon_path, svg, text, window, write

STACK = [
    ("ai/", [("claude", "Claude Code"), ("anthropic", "Agent SDK"), ("modelcontextprotocol", "MCP"),
             ("telegram", "aiogram 3"), ("obsidian", "RAG · BM25")]),
    ("backend/", [("python", "Python"), ("fastapi", "FastAPI"), ("nodedotjs", "Node.js"), ("express", "Express"),
                  ("nestjs", "NestJS"), ("fastify", "Fastify")]),
    ("frontend/", [("react", "React"), ("nextdotjs", "Next.js"), ("typescript", "TypeScript"),
                   ("tailwindcss", "Tailwind"), ("vite", "Vite"), ("redux", "Redux")]),
    ("data/", [("postgresql", "PostgreSQL"), ("supabase", "Supabase"), ("mongodb", "MongoDB"), ("sqlite", "SQLite"),
               ("prisma", "Prisma"), ("redis", "Redis")]),
    ("devops/", [("docker", "Docker"), ("linux", "Linux"), ("git", "Git"), ("githubactions", "Actions"),
                 ("vercel", "Vercel"), ("render", "Render"), ("cloudflare", "Cloudflare")]),
    ("mobile+3d/", [("flutter", "Flutter"), ("dart", "Dart"), ("kotlin", "Kotlin"), ("godotengine", "Godot"),
                    ("blender", "Blender"), ("openjdk", "JavaFX"), ("ffmpeg", "FFmpeg")]),
]

ROW_H, LABEL_W, PITCH, TILE, TOP = 92, 210, 104, 52, 62
STEP = 0.55  # seconds the selection rests on one tool


def tool_count() -> int:
    return sum(len(items) for _, items in STACK)


def stack() -> str:
    width = 1000
    height = TOP + ROW_H * len(STACK) + 40
    total = tool_count()
    period = total * STEP
    slot = 100 / total
    rows, k = [], 0
    for r, (label, items) in enumerate(STACK):
        y = TOP + r * ROW_H
        rows.append(text(28, y + 25, label, 14, WHITE, "700")
                    + text(28, y + 45, f"{len(items):02d} tools", 11.5, DIM))
        if r:
            rows.append(f'<path d="M28 {y - 10}H{width - 28}" stroke="{BORDER}" stroke-dasharray="2 6"/>')
        for i, (slug, name) in enumerate(items):
            x = LABEL_W + i * PITCH
            delay = k * STEP
            rows.append(
                f'<g class="t" style="animation-delay:{0.05 + 0.035 * k:.2f}s">'
                f'<rect x="{x}" y="{y}" width="{TILE}" height="{TILE}" rx="4" fill="{BG}" stroke="{BORDER}"/>'
                f'<rect class="sel" style="animation-delay:{delay:.2f}s" x="{x}" y="{y}" width="{TILE}" height="{TILE}" '
                f'rx="4" fill="{TEXT}" opacity="0"/>'
                f'<use href="#i-{slug}" transform="translate({x + 13} {y + 13}) scale(1.0833)" fill="{TEXT}"/>'
                f'<use class="sel" style="animation-delay:{delay:.2f}s" href="#i-{slug}" '
                f'transform="translate({x + 13} {y + 13}) scale(1.0833)" fill="{BG}" opacity="0"/>'
                f'{text(x + TILE / 2, y + TILE + 19, name, 11.5, MUTED, anchor="middle")}'
                f'<g class="sel" style="animation-delay:{delay:.2f}s" opacity="0">'
                f'{text(x + TILE / 2, y + TILE + 19, name, 11.5, WHITE, "700", anchor="middle")}</g></g>')
            k += 1
    back, front = window(width, height, "ls /usr/local/bin", f"{total} tools")
    footer = text(28, height - 18, f"total {total}  ·  {len(STACK)} dirs  ·  glyphs: simple-icons (CC0), inlined, no external requests",
                  11.5, DIM)
    glyphs = "".join(f'<path id="i-{slug}" d="{icon_path(slug)}"/>' for _, items in STACK for slug, _ in items)
    body = f"""<defs>{glyphs}</defs>
{back}
<g font-family="{MONO}">{''.join(rows)}{footer}</g>
{front}"""
    css = f""".t{{animation:up .5s ease-out both}}
@keyframes up{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:translateY(0)}}}}
.sel{{animation:sel {period:.2f}s steps(1) infinite}}
@keyframes sel{{0%{{opacity:1}}{slot:.3f}%,100%{{opacity:0}}}}"""
    return svg(width, height, body, css, "Tech stack")


if __name__ == "__main__":
    write("stack.svg", stack())
    print("stack: ok")
