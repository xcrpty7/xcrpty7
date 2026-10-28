"""Live stats card from the GitHub GraphQL API (run daily by .github/workflows/profile.yml).

Usage: GITHUB_TOKEN=... python3 scripts/stats.py <login>
Writes stats.svg into ASSETS_DIR (the workflow publishes it to the `output` branch).
"""
import json
import os
import sys
import urllib.request

from svg_kit import (BG, BLUE, BORDER, CYAN, DIM, GREEN, MONO, MUTED, ORANGE, PANEL, PINK, PURPLE,
                     SANS, TEXT, esc, mono_width, svg, write)

QUERY = """query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, privacy: PUBLIC, isFork: false, first: 100) {
      totalCount
      nodes { languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
        edges { size node { name color } } } }
    }
    createdAt
  }
}"""
SKIP_LANGS = {"Batchfile", "Dockerfile", "Makefile", "Procfile"}


def fetch(login: str, token: str) -> dict:
    payload = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", data=payload, headers={
        "Authorization": f"bearer {token}", "Content-Type": "application/json", "User-Agent": "xcrpty7-profile"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.load(resp)
    if body.get("errors"):
        raise RuntimeError(f"GraphQL errors: {body['errors']}")
    return body["data"]["user"]


def languages(repos: list, top: int = 6) -> list:
    sizes, colors = {}, {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            if name in SKIP_LANGS:
                continue
            sizes[name] = sizes.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"] or MUTED
    total = sum(sizes.values()) or 1
    ranked = sorted(sizes.items(), key=lambda kv: kv[1], reverse=True)[:top]
    return [(name, size / total, colors[name]) for name, size in ranked]


def code_size(repos: list) -> str:
    total = sum(e["size"] for r in repos for e in r["languages"]["edges"] if e["node"]["name"] not in SKIP_LANGS)
    return f"{total / 1_000_000:.1f} MB" if total >= 1_000_000 else f"{total / 1000:.0f} KB"


def card(user: dict) -> str:
    width, height = 1000, 236
    repos = user["repositories"]
    langs = languages(repos["nodes"])
    used = {e["node"]["name"] for r in repos["nodes"] for e in r["languages"]["edges"]} - SKIP_LANGS
    # Contribution totals are deliberately not shown: this account's calendar is inflated by
    # auto-generated commits, so only metrics that reflect real work go on the card.
    metrics = [
        (str(repos["totalCount"]), "PUBLIC REPOS", CYAN),
        (str(len(used)), "LANGUAGES USED", GREEN),
        (langs[0][0] if langs else "-", "TOP LANGUAGE", ORANGE),
        (code_size(repos["nodes"]), "CODE IN PUBLIC REPOS", "#e3b341"),
        (str(user["followers"]["totalCount"]), "FOLLOWERS", PURPLE),
        (user["createdAt"][:4], "ON GITHUB SINCE", PINK),
    ]
    tiles = []
    for i, (value, label, accent) in enumerate(metrics):
        x, y = 24 + (i % 3) * 168, 24 + (i // 3) * 94
        size = min(27.0, 124 / max(mono_width(value, 1), 0.1))  # long values ("JavaScript") shrink to fit
        tiles.append(f'<g class="m" style="animation-delay:{0.08 * i:.2f}s">'
                     f'<rect x="{x}" y="{y}" width="156" height="82" rx="12" fill="{BG}" stroke="{BORDER}"/>'
                     f'<text x="{x + 16}" y="{y + 42}" font-family="{MONO}" font-size="{size:.1f}" font-weight="700" fill="{accent}">{esc(value)}</text>'
                     f'<text x="{x + 16}" y="{y + 64}" font-family="{MONO}" font-size="10.5" letter-spacing="1" fill="{MUTED}">{label}</text></g>')

    bar_x, bar_w, bar = 560, 412, []
    x = bar_x
    for name, share, color in langs:
        w = max(share * bar_w, 3)
        bar.append(f'<rect class="b" x="{x:.1f}" y="62" width="{w:.1f}" height="12" fill="{color}"/>')
        x += w
    legend = []
    for i, (name, share, color) in enumerate(langs):
        lx, ly = bar_x + (i % 2) * 210, 104 + (i // 2) * 30
        legend.append(f'<circle cx="{lx + 6}" cy="{ly - 4}" r="5" fill="{color}"/>'
                      f'<text x="{lx + 18}" y="{ly}" font-family="{SANS}" font-size="13.5" fill="{TEXT}">{esc(name)}'
                      f'<tspan fill="{MUTED}" font-family="{MONO}" font-size="12"> {share * 100:.1f}%</tspan></text>')
    body = f"""<defs><clipPath id="bar"><rect x="{bar_x}" y="62" width="{bar_w}" height="12" rx="6"/></clipPath></defs>
<rect x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="16" fill="{PANEL}" stroke="{BORDER}"/>
{''.join(tiles)}
<text x="{bar_x}" y="44" font-family="{MONO}" font-size="12" font-weight="700" letter-spacing="1.5" fill="{BLUE}">TOP LANGUAGES · PUBLIC REPOS</text>
<g clip-path="url(#bar)">{''.join(bar)}</g>
{''.join(legend)}
<text x="{width - 24}" y="{height - 16}" text-anchor="end" font-family="{MONO}" font-size="10.5" fill="{DIM}">live data · GitHub GraphQL API</text>"""
    css = """.m{animation:up .5s ease-out both}
@keyframes up{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.b{transform-box:fill-box;transform-origin:left;animation:grow 1.2s cubic-bezier(.2,.8,.2,1) both}
@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}"""
    return svg(width, height, body, css, "GitHub stats")


def main() -> int:
    login = sys.argv[1] if len(sys.argv) > 1 else "xcrpty7"
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("stats: GITHUB_TOKEN is not set", file=sys.stderr)
        return 1
    try:
        user = fetch(login, token)
    except Exception as exc:  # network or API failure: keep the previous card, fail the job loudly
        print(f"stats: GitHub API request failed: {exc}", file=sys.stderr)
        return 1
    path = write("stats.svg", card(user))
    print(f"stats: wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
