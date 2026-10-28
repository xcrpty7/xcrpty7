"""Animated `whoami` terminal: commands type themselves, output appears line by line."""
from svg_kit import (BORDER, CYAN, DIM, GREEN, MONO, MUTED, PANEL, PURPLE, STATIC, TEXT, esc,
                     mono_width, svg, typing, write)

FONT, LINE_H = 17, 28
CHAR_TIME, AFTER_CMD, AFTER_OUT = 0.045, 0.25, 0.35

SESSION = [
    ("whoami", [[("xcrpty7", GREEN), (" · Full-Stack & AI-Agent Developer · Tashkent, Uzbekistan", TEXT)]]),
    ("cat focus.txt", [
        [("▸ ", PURPLE), ("AI agents in Telegram: the model talks, the code decides", TEXT)],
        [("▸ ", PURPLE), ("my Claude Code setup: task router · RAG over Obsidian · error memory", TEXT)],
        [("▸ ", PURPLE), ("products with auth, payments and admin panels, used by real businesses", TEXT)],
    ]),
    ("ls ~/stack", [[("python  typescript  node  react  next  postgres  mongo  docker  claude  mcp", CYAN)]]),
    ("echo $LANG", [[("uz_UZ", TEXT), (" · ", DIM), ("ru_RU", TEXT), (" · ", DIM), ("en_US", TEXT)]]),
    ("uptime", [[("shipping since 14", GREEN), (" · MVP in 3–7 days · each mistake only once", MUTED)]]),
]


def appear(begin: float) -> tuple:
    """(opacity attribute, <set>) pair: hidden until `begin`, visible in STATIC mode."""
    if STATIC:
        return "1", ""
    return "0", f'<set attributeName="opacity" to="1" begin="{begin:.2f}s" fill="freeze"/>'


def spans(parts: list) -> str:
    return "".join(f'<tspan fill="{color}">{esc(text)}</tspan>' for text, color in parts)


def terminal() -> str:
    width, x0, y = 1000, 34, 92
    rows, clips, t = [], [], 0.6
    for i, (cmd, outputs) in enumerate(SESSION):
        cmd_w = mono_width(cmd, FONT)
        type_dur = max(len(cmd) * CHAR_TIME, 0.2)
        op, show = appear(t)
        clip_w = cmd_w + 6 if STATIC else 0
        clips.append(f'<clipPath id="c{i}"><rect x="{x0 + 22}" y="{y - FONT}" width="{clip_w:.0f}" height="{LINE_H}">'
                     f'{typing("width", 0, cmd_w + 6, len(cmd), t, type_dur)}</rect></clipPath>')
        rows.append(f'<g opacity="{op}">{show}<text x="{x0}" y="{y}" fill="{GREEN}">$</text>'
                    f'<text x="{x0 + 22}" y="{y}" fill="{TEXT}" clip-path="url(#c{i})" '
                    f'textLength="{cmd_w:.0f}" lengthAdjust="spacing">{esc(cmd)}</text></g>')
        t += type_dur + AFTER_CMD
        y += LINE_H
        for parts in outputs:
            line = "".join(text for text, _ in parts)
            op, show = appear(t)
            rows.append(f'<g opacity="{op}">{show}<text x="{x0}" y="{y}" textLength="{mono_width(line, FONT):.0f}" '
                        f'lengthAdjust="spacing" xml:space="preserve">{spans(parts)}</text></g>')
            t += 0.12
            y += LINE_H
        t += AFTER_OUT
    op, show = appear(t)
    rows.append(f'<g opacity="{op}">{show}<text x="{x0}" y="{y}" fill="{GREEN}">$</text>'
                f'<rect class="cursor" x="{x0 + 22}" y="{y - FONT + 2}" width="10" height="{FONT + 2}" fill="{GREEN}"/></g>')
    height = y + 34

    body = f"""<defs>
<radialGradient id="glow" cx="0.85" cy="0" r="0.9"><stop offset="0" stop-color="{GREEN}" stop-opacity="0.12"/><stop offset="1" stop-color="{GREEN}" stop-opacity="0"/></radialGradient>
{''.join(clips)}
</defs>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" fill="{PANEL}" stroke="{BORDER}"/>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="14" fill="url(#glow)"/>
<path d="M1 46H{width - 1}" stroke="{BORDER}"/>
<circle cx="26" cy="23" r="6.5" fill="#ff5f56"/><circle cx="48" cy="23" r="6.5" fill="#ffbd2e"/><circle cx="70" cy="23" r="6.5" fill="#27c93f"/>
<text x="{width / 2}" y="28" text-anchor="middle" font-family="{MONO}" font-size="13" fill="{MUTED}">xcrpty7@mac — zsh — 100×30</text>
<g font-family="{MONO}" font-size="{FONT}">{''.join(rows)}</g>"""
    css = ".cursor{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}"
    return svg(width, height, body, css, "whoami: xcrpty7, Full-Stack & AI-Agent Developer")


if __name__ == "__main__":
    write("terminal.svg", terminal())
    print("terminal: ok")
