#!/usr/bin/env python3
"""Builds the hand-drawn SVGs used by the profile README.

    python scripts/build_assets.py --user AliTaqi-d8

hero.svg and stack.svg are drawn locally. stats.svg is drawn from the public
GitHub API, so the daily workflow keeps it current.
"""
import argparse, collections, datetime, json, math, os, pathlib, random, sys
import urllib.request
from xml.sax.saxutils import escape

ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"

INK, GRID, LINE, CHIP = "#1B1230", "#2D2150", "#3A2B66", "#241A40"
PAPER, MUTED = "#F3EEFF", "#B9AEE0"
AMBER, ROSE = "#FFB547", "#FF6F91"
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, monospace"

# Edit these to match what you really use.
STACK = ["Python", "Django", "FastAPI", "PyTorch", "TensorFlow", "scikit-learn",
         "TypeScript", "React", "Next.js", "PostgreSQL", "Docker", "Git", "Linux"]


def smooth(pts):
    """Catmull-Rom spline through pts, as an SVG cubic Bezier path."""
    d = f"M{pts[0][0]:.1f},{pts[0][1]:.1f}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d


def hero():
    rnd = random.Random(7)
    n, x0, x1, base, scale = 48, 56, 844, 300, 105
    train, val = [], []
    for i in range(n):
        t = i / (n - 1)
        loss = 0.14 + 0.86 * math.exp(-4.6 * t)
        lt = loss + rnd.uniform(-1, 1) * 0.045 * (1 - 0.6 * t)
        lv = loss + 0.05 + 0.11 * t ** 1.3 + rnd.uniform(-1, 1) * 0.04
        x = x0 + (x1 - x0) * t
        train.append((x, base - lt * scale))
        val.append((x, base - lv * scale))
    ex, ey = train[-1]
    grid = "".join(
        f'<line x1="56" x2="844" y1="{base - g * scale:.1f}" y2="{base - g * scale:.1f}" stroke="{GRID}" stroke-width="1"/>'
        for g in (0.25, 0.5, 0.75, 1.0))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 340" width="900" height="340" role="img" aria-labelledby="t d">
<title id="t">Ali Taqi</title>
<desc id="d">A training loss curve falling over time. Ali Taqi, Python developer, learning machine learning and deep learning.</desc>
<defs>
<clipPath id="reveal"><rect x="0" y="0" width="900" height="340"><animate attributeName="width" from="0" to="900" dur="3.6s" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1" fill="freeze"/></rect></clipPath>
</defs>
<rect width="900" height="340" rx="18" fill="{INK}"/>
{grid}
<line x1="56" x2="844" y1="{base}" y2="{base}" stroke="{LINE}" stroke-width="1.5"/>
<text x="56" y="88" font-family="{SERIF}" font-size="62" fill="{PAPER}" letter-spacing="-1">Ali Taqi</text>
<text x="58" y="124" font-family="{SANS}" font-size="17" fill="{MUTED}">Python developer. Currently training on machine learning,</text>
<text x="58" y="147" font-family="{SANS}" font-size="17" fill="{MUTED}">deep learning and my own research projects.</text>
<g clip-path="url(#reveal)" fill="none" stroke-linecap="round" stroke-linejoin="round">
<path d="{smooth(val)}" stroke="{ROSE}" stroke-width="2.5" stroke-dasharray="7 6"/>
<path d="{smooth(train)}" stroke="{AMBER}" stroke-width="3.5"/>
</g>
<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5.5" fill="{AMBER}"/>
<circle cx="{ex:.1f}" cy="{ey:.1f}" r="5.5" fill="none" stroke="{AMBER}" stroke-width="2" opacity="0">
<animate attributeName="r" values="5.5;18" dur="2.2s" begin="3.6s" repeatCount="indefinite"/>
<animate attributeName="opacity" values="0.9;0" dur="2.2s" begin="3.6s" repeatCount="indefinite"/>
</circle>
<text x="{ex - 20:.1f}" y="{ey - 40:.1f}" text-anchor="end" font-family="{MONO}" font-size="12.5" fill="{AMBER}">still training</text>
<g font-family="{MONO}" font-size="12.5">
<line x1="640" x2="670" y1="60" y2="60" stroke="{AMBER}" stroke-width="3.5" stroke-linecap="round"/>
<text x="680" y="64" fill="{MUTED}">training loss</text>
<line x1="640" x2="670" y1="82" y2="82" stroke="{ROSE}" stroke-width="2.5" stroke-dasharray="7 6"/>
<text x="680" y="86" fill="{MUTED}">validation loss</text>
<text x="56" y="322" fill="{MUTED}">then</text>
<text x="844" y="322" text-anchor="end" fill="{MUTED}">now</text>
</g>
</svg>
'''


def stack():
    cw, pad, gap, h, maxw = 8.6, 16, 12, 36, 788
    rows, row, w = [], [], 0
    for name in STACK:
        cwid = len(name) * cw + pad * 2
        if row and w + gap + cwid > maxw:
            rows.append(row); row, w = [], 0
        row.append((name, cwid)); w += cwid + (gap if len(row) > 1 else 0)
    rows.append(row)
    height = 56 + len(rows) * (h + gap) - gap
    out = []
    for r, items in enumerate(rows):
        x, y = 56, 28 + r * (h + gap)
        for name, cwid in items:
            out.append(f'<rect x="{x:.1f}" y="{y}" width="{cwid:.1f}" height="{h}" rx="{h // 2}" fill="{CHIP}" stroke="{LINE}"/>'
                       f'<text x="{x + cwid / 2:.1f}" y="{y + 23}" text-anchor="middle" font-family="{MONO}" font-size="14" fill="{PAPER}">{escape(name)}</text>')
            x += cwid + gap
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 {height}" width="900" height="{height}" role="img" aria-label="Tools I use: {escape(", ".join(STACK))}">'
            f'<rect width="900" height="{height}" rx="18" fill="{INK}"/>{"".join(out)}</svg>\n')


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "profile-readme", "Accept": "application/vnd.github+json"})
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        req.add_header("Authorization", f"Bearer {tok}")
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def stats(user):
    u = get(f"https://api.github.com/users/{user}")
    repos = [r for r in get(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner") if not r["fork"]]
    stars = sum(r["stargazers_count"] for r in repos)
    langs = collections.Counter(r["language"] for r in repos if r["language"])
    total = sum(langs.values()) or 1
    top = langs.most_common(5)
    nums = [(u["public_repos"], "public repositories"), (stars, "stars received"), (u["followers"], "followers")]
    blocks = "".join(
        f'<text x="{56 + i * 178}" y="112" font-family="{SERIF}" font-size="54" fill="{PAPER}">{v}</text>'
        f'<text x="{58 + i * 178}" y="140" font-family="{SANS}" font-size="14" fill="{MUTED}">{escape(lbl)}</text>'
        for i, (v, lbl) in enumerate(nums))
    bars = "".join(
        f'<text x="568" y="{78 + i * 28}" font-family="{MONO}" font-size="13" fill="{PAPER}">{escape(name)}</text>'
        f'<rect x="716" y="{67 + i * 28}" width="128" height="10" rx="5" fill="{GRID}"/>'
        f'<rect x="716" y="{67 + i * 28}" width="{max(8, 128 * c / total):.0f}" height="10" rx="5" fill="url(#bar)"/>'
        for i, (name, c) in enumerate(top))
    today = datetime.date.today().isoformat()
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 220" width="900" height="220" role="img" aria-label="GitHub activity for {escape(user)}">
<defs><linearGradient id="bar" x1="0" x2="1"><stop offset="0" stop-color="{AMBER}"/><stop offset="1" stop-color="{ROSE}"/></linearGradient></defs>
<rect width="900" height="220" rx="18" fill="{INK}"/>
<text x="56" y="52" font-family="{SERIF}" font-size="22" font-style="italic" fill="{MUTED}">Run log</text>
{blocks}
<line x1="540" x2="540" y1="40" y2="180" stroke="{LINE}"/>
{bars}
<text x="56" y="196" font-family="{MONO}" font-size="12" fill="{MUTED}">updated {today}</text>
</svg>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default=os.environ.get("GITHUB_REPOSITORY_OWNER", "AliTaqi-d8"))
    ap.add_argument("--skip-stats", action="store_true")
    a = ap.parse_args()
    ASSETS.mkdir(exist_ok=True)
    (ASSETS / "hero.svg").write_text(hero(), encoding="utf-8")
    (ASSETS / "stack.svg").write_text(stack(), encoding="utf-8")
    if not a.skip_stats:
        try:
            (ASSETS / "stats.svg").write_text(stats(a.user), encoding="utf-8")
        except Exception as e:
            print(f"stats.svg not updated: {e}", file=sys.stderr)
            sys.exit(1)
    print("assets written to", ASSETS)


if __name__ == "__main__":
    main()
