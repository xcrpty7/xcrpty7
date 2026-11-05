"""Spinning ASCII torus (the classic donut.c math) rendered into SVG text frames.

Frames are precomputed: z-buffered points of a torus, lit by a fixed light, each
cell drawn with a character from a luminance ramp. One loop = one full turn on
both axes, so the animation repeats without a jump.
"""
import math

RAMP = ".,-~:;=!*#$@"


def frames(cols: int = 44, rows: int = 22, count: int = 48) -> list:
    r1, r2, k2 = 1.0, 2.0, 5.0
    kx = cols * k2 * 3 / (8 * (r1 + r2))
    ky = kx / 2  # terminal cells are about twice as tall as they are wide
    out = []
    thetas = [i * 0.07 for i in range(int(2 * math.pi / 0.07) + 1)]
    phis = [i * 0.02 for i in range(int(2 * math.pi / 0.02) + 1)]
    trig_t = [(math.cos(t), math.sin(t)) for t in thetas]
    trig_p = [(math.cos(p), math.sin(p)) for p in phis]
    for f in range(count):
        a = 2 * math.pi * f / count + 1.0
        b = 2 * math.pi * f / count + 0.3
        ca, sa, cb, sb = math.cos(a), math.sin(a), math.cos(b), math.sin(b)
        grid = [[" "] * cols for _ in range(rows)]
        zbuf = [[0.0] * cols for _ in range(rows)]
        for ct, st in trig_t:
            cx, cy = r2 + r1 * ct, r1 * st
            for cp, sp in trig_p:
                x = cx * (cb * cp + sa * sb * sp) - cy * ca * sb
                y = cx * (sb * cp - sa * cb * sp) + cy * ca * cb
                ooz = 1 / (k2 + ca * cx * sp + cy * sa)
                xp = int(cols / 2 + kx * ooz * x)
                yp = int(rows / 2 - ky * ooz * y)
                if not (0 <= xp < cols and 0 <= yp < rows) or ooz <= zbuf[yp][xp]:
                    continue
                lum = cp * ct * sb - ca * ct * sp - sa * st + cb * (ca * st - ct * sa * sp)
                if lum > 0:
                    zbuf[yp][xp] = ooz
                    grid[yp][xp] = RAMP[min(int(lum * 8), len(RAMP) - 1)]
        out.append(["".join(line).rstrip() for line in grid])
    return out


def svg_frames(x: float, y: float, size: float, line_h: float, step: float, static: bool) -> tuple:
    """(markup, css): one <text> per frame, shown one after another with CSS steps."""
    seq = frames()
    period = step * len(seq)
    slot = 100 / len(seq)
    parts = []
    for i, lines in enumerate(seq):
        if static and i:
            break
        spans = "".join(f'<tspan x="{x:g}" y="{y + r * line_h:g}">{line}</tspan>'
                        for r, line in enumerate(lines) if line.strip())
        op = "1" if i == 0 else "0"
        parts.append(f'<text class="fr" style="animation-delay:{i * step:.2f}s" opacity="{op}" '
                     f'xml:space="preserve">{spans}</text>')
    markup = f'<g font-size="{size}">{"".join(parts)}</g>'
    css = (f".fr{{animation:fr {period:.2f}s steps(1) infinite}}"
           f"@keyframes fr{{0%{{opacity:1}}{slot:.3f}%,100%{{opacity:0}}}}")
    return markup, css
