"""Stats card from the GitHub GraphQL API, across all of the owner's repos (private included).

Usage: GITHUB_TOKEN=$(gh auth token) python3 scripts/stats.py <login>
Run it locally: the repos are private, so a CI token would only see this profile repo.
Writes stats.svg into ASSETS_DIR (default: assets/).
"""
import json
import os
import sys
import urllib.request

from svg_kit import (BG, BLINK, BORDER, DIM, GREYS, MONO, MUTED, STATIC, TEXT, WHITE, esc, mono_width, row,
                     svg, text, typing, window, write)

QUERY = """query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100) {
      totalCount
      nodes { isPrivate languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
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
    """htop-style card: language meters on the left, totals on the right, F-key bar below."""
    width, height, size = 1000, 300, 14
    cw = size * 0.6
    repos = user["repositories"]
    langs = languages(repos["nodes"])
    used = {e["node"]["name"] for r in repos["nodes"] for e in r["languages"]["edges"]} - SKIP_LANGS
    private = sum(1 for r in repos["nodes"] if r.get("isPrivate"))
    # Contribution totals are deliberately not shown: this account's calendar was inflated by
    # auto-generated commits once, so only metrics that reflect real work go on the card.
    meters, bar_chars = [], 34
    for i, (name, share, _) in enumerate(langs):
        y = 80 + i * 26
        filled = max(1, round(share * bar_chars))
        pct = f"{share * 100:.1f}%"
        bars = "|" * filled
        x_bar = 28 + 12 * cw
        clip_w = mono_width(bars, size) + 1
        start_w = clip_w if STATIC else 0
        meters.append(
            f'<clipPath id="m{i}"><rect x="{x_bar:.1f}" y="{y - 14}" width="{start_w:.1f}" height="20">'
            f'{typing("width", 0, clip_w, filled, 0.5 + 0.1 * i, 0.03 * filled)}</rect></clipPath>'
            + text(28, y, name[:11].ljust(11), size, TEXT)
            + text(28 + 11 * cw, y, "[", size, WHITE, "700")
            + f'<g clip-path="url(#m{i})">{text(x_bar, y, bars, size, GREYS[7 - min(i, 3)], "700")}</g>'
            + text(28 + (12 + bar_chars) * cw, y, pct.rjust(6), size, MUTED)
            + text(28 + (18 + bar_chars) * cw, y, "]", size, WHITE, "700"))
    info = [
        ("Repos", f"{repos['totalCount']} total, {private} private"),
        ("Languages", f"{len(used)} used, top {langs[0][0] if langs else '-'}"),
        ("Code", f"{code_size(repos['nodes'])} written"),
        ("Followers", str(user["followers"]["totalCount"])),
        ("Uptime", f"on GitHub since {user['createdAt'][:4]}"),
        ("Load avg", "ship · ship · ship"),
    ]
    rx = 600
    right = "".join(row(rx, 80 + i * 26, [(f"{k}:".ljust(11), MUTED), (v, WHITE, "700")], size)
                    for i, (k, v) in enumerate(info))
    keys = [("F1", "whoami"), ("F2", "projects"), ("F3", "agents"), ("F4", "stack"), ("F5", "telegram"),
            ("F10", "ship")]
    fkeys, col = [], 0
    bar_y = height - 52
    for key, label in keys:
        kx = 28 + col * cw
        lw = (len(label) + 1) * cw
        fkeys.append(text(kx, bar_y + 15, key, size, WHITE, "700")
                     + f'<rect x="{kx + len(key) * cw:.1f}" y="{bar_y}" width="{lw:.1f}" height="21" fill="#bdbdbd"/>'
                     + text(kx + len(key) * cw, bar_y + 15, label, size, BG, "700"))
        col += len(key) + len(label) + 2
    back, front = window(width, height, "htop", "github.com/xcrpty7")
    body = f"""{back}
<g font-family="{MONO}">
{''.join(meters)}
<path d="M{rx - 28} 62V{62 + 6 * 26}" stroke="{BORDER}" stroke-dasharray="2 5"/>
{right}
{''.join(fkeys)}
{text(width - 28, bar_y + 15, "private repos: numbers only, never code", 11.5, DIM, anchor="end")}
</g>
{front}"""
    return svg(width, height, body, BLINK, "GitHub stats")


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
