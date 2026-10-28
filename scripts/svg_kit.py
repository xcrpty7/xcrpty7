"""Shared palette and helpers for the profile SVGs.

Every asset is self-contained (no external fonts or images), so it renders the same
inside GitHub's <img> sandbox. Animations start from CSS keyframes only: with
STATIC=1 the <style> animations are dropped and the final frame is drawn, which is
what scripts/preview.sh renders through QuickLook for a visual check.
"""
import os
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
ASSETS = Path(os.environ.get("ASSETS_DIR", ROOT / "assets"))
ICONS = Path(__file__).resolve().parent / "icons"
STATIC = os.environ.get("STATIC") == "1"

BG = "#0d1117"
PANEL = "#0f1620"
PANEL_HI = "#141c28"
BORDER = "#253041"
TEXT = "#e6edf3"
MUTED = "#8b949e"
DIM = "#4b5563"
GREEN = "#3fb950"
GREEN_DEEP = "#1f6f3a"
CYAN = "#39d0d8"
PURPLE = "#a371f7"
ORANGE = "#f0883e"
PINK = "#f778ba"
BLUE = "#58a6ff"
RED = "#ff4d6d"

MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"
EMOJI = "'Apple Color Emoji','Segoe UI Emoji','Noto Color Emoji',sans-serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"

REDUCED_MOTION = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def esc(text: str) -> str:
    return escape(text, {'"': "&quot;"})


def svg(width: int, height: int, body: str, css: str = "", title: str = "") -> str:
    """Wrap body into a root <svg>; css is dropped in STATIC mode (final frame only)."""
    style = "" if STATIC or not css else f"<style>{css}{REDUCED_MOTION}</style>"
    label = f"<title>{esc(title)}</title>" if title else ""
    # QuickLook crops non-square thumbnails, so STATIC previews are letterboxed into a square.
    box_w = box_h = max(width, height) if STATIC else None
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{box_w or width}" height="{box_h or height}" '
        f'viewBox="0 0 {width} {height}" role="img" fill="none">{label}{style}{body}</svg>\n'
    )


def smil(markup: str) -> str:
    """SMIL animation elements, omitted in STATIC mode."""
    return "" if STATIC else markup


def typing(attr: str, start: float, end: float, steps: int, begin: float, dur: float) -> str:
    """Discrete SMIL animation from start to end in `steps` jumps (typewriter effect)."""
    values = ";".join(f"{start + (end - start) * i / steps:.1f}" for i in range(steps + 1))
    return smil(f'<animate attributeName="{attr}" values="{values}" calcMode="discrete" '
                f'begin="{begin}s" dur="{dur}s" fill="freeze"/>')


def write(rel_path: str, content: str) -> Path:
    path = ASSETS / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def icon_path(slug: str) -> str:
    """Path data of a simple-icons glyph (24x24 viewBox), CC0."""
    raw = (ICONS / f"{slug}.svg").read_text(encoding="utf-8")
    match = re.search(r'<path d="([^"]+)"', raw)
    if not match:
        raise ValueError(f"no path in icon {slug}")
    return match.group(1)


def luminance(hex_color: str) -> float:
    r, g, b = (int(hex_color.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def readable(hex_color: str) -> str:
    """Brand colours too dark for the dark panels fall back to near-white."""
    return TEXT if luminance(hex_color) < 0.28 else hex_color


def mono_width(text: str, size: float) -> float:
    """Advance width of monospace text (Menlo, SF Mono, DejaVu ~0.6em); pair with textLength."""
    return len(text) * size * 0.6


def wrap(text: str, max_chars: int) -> list[str]:
    lines, line = [], ""
    for word in text.split():
        candidate = f"{line} {word}".strip()
        if len(candidate) > max_chars and line:
            lines.append(line)
            line = word
        else:
            line = candidate
    if line:
        lines.append(line)
    return lines
