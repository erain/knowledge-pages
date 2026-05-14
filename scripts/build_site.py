#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
PUBLIC = CONTENT / "public"
UNLISTED = CONTENT / "unlisted"
SITE = ROOT / "site"
ARTIFACTS = CONTENT / "artifacts.json"


def copytree(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    shutil.copytree(src, dst, dirs_exist_ok=True)


def load_artifacts() -> list[dict[str, object]]:
    if not ARTIFACTS.exists():
        return []
    with ARTIFACTS.open(encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, list):
        raise ValueError("content/artifacts.json must contain a list")
    return data


def artifact_url(item: dict[str, object]) -> str:
    kind = str(item.get("kind", "page"))
    slug = str(item["slug"])
    visibility = str(item.get("visibility", "public"))
    if visibility == "unlisted":
        return f"u/{slug}/"
    if kind == "deck":
        return f"decks/{slug}/"
    return f"pages/{slug}/"


def build_index(public_items: list[dict[str, object]]) -> str:
    cards: list[str] = []
    for item in public_items:
        title = html.escape(str(item.get("title", item.get("slug", "Untitled"))))
        summary = html.escape(str(item.get("summary", "")))
        updated = html.escape(str(item.get("updated", "")))
        tags = item.get("tags", [])
        tag_html = ""
        if isinstance(tags, list):
            tag_html = "".join(f"<span>{html.escape(str(tag))}</span>" for tag in tags[:6])
        cards.append(
            f"""
        <a class="card" href="{html.escape(artifact_url(item))}">
          <div class="meta">{updated}</div>
          <h2>{title}</h2>
          <p>{summary}</p>
          <div class="tags">{tag_html}</div>
        </a>"""
        )

    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    body = "\n".join(cards) if cards else "<p>No public artifacts yet.</p>"
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Knowledge Pages</title>
  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='10' fill='%23071014'/%3E%3Cpath d='M15 34h34M15 22h34M15 46h22' stroke='%2300add8' stroke-width='6' stroke-linecap='round'/%3E%3C/svg%3E">
  <style>
    :root {{
      color-scheme: dark;
      --bg: #071014;
      --panel: #0f1c22;
      --text: #e8f1f2;
      --muted: #97a9b0;
      --line: #24414a;
      --cyan: #00add8;
      --green: #7fdbb6;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      min-height: 100vh;
      font: 16px/1.55 Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: var(--text);
      background:
        linear-gradient(rgba(0, 173, 216, 0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0, 173, 216, 0.06) 1px, transparent 1px),
        radial-gradient(circle at top right, rgba(127, 219, 182, 0.16), transparent 32rem),
        var(--bg);
      background-size: 32px 32px, 32px 32px, auto, auto;
    }}
    main {{ width: min(1120px, calc(100% - 40px)); margin: 0 auto; padding: 72px 0; }}
    header {{ margin-bottom: 34px; }}
    .eyebrow {{ color: var(--green); font: 700 13px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace; text-transform: uppercase; }}
    h1 {{ margin: 10px 0 10px; font-size: clamp(42px, 8vw, 92px); line-height: 0.92; letter-spacing: 0; }}
    .lede {{ max-width: 760px; color: var(--muted); font-size: 18px; }}
    .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px; }}
    .card {{
      min-height: 240px;
      display: flex;
      flex-direction: column;
      gap: 14px;
      padding: 24px;
      color: inherit;
      text-decoration: none;
      background: color-mix(in srgb, var(--panel), transparent 6%);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .card:hover {{ border-color: var(--cyan); transform: translateY(-2px); transition: 150ms ease; }}
    .meta {{ color: var(--green); font: 700 12px/1.2 ui-monospace, SFMono-Regular, Menlo, monospace; }}
    h2 {{ margin: 0; font-size: 24px; line-height: 1.1; letter-spacing: 0; }}
    p {{ margin: 0; color: var(--muted); }}
    .tags {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: auto; }}
    .tags span {{ border: 1px solid var(--line); border-radius: 999px; padding: 4px 9px; color: var(--muted); font-size: 12px; }}
    footer {{ margin-top: 36px; color: var(--muted); font: 13px/1.4 ui-monospace, SFMono-Regular, Menlo, monospace; }}
  </style>
</head>
<body>
  <main>
    <header>
      <div class="eyebrow">erain / generated knowledge</div>
      <h1>Knowledge Pages</h1>
      <p class="lede">Self-contained HTML decks and notes generated from engineering work, then published as static artifacts.</p>
    </header>
    <section class="grid" aria-label="Published artifacts">
{body}
    </section>
    <footer>Generated {generated}</footer>
  </main>
</body>
</html>
"""


def main() -> int:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)
    (SITE / ".nojekyll").write_text("", encoding="utf-8")

    artifacts = load_artifacts()
    public_items: list[dict[str, object]] = []
    manifest: list[dict[str, object]] = []

    for item in artifacts:
        visibility = str(item.get("visibility", "public"))
        kind = str(item.get("kind", "page"))
        slug = str(item["slug"])
        if visibility == "unlisted":
            src = UNLISTED / slug
            dst = SITE / "u" / slug
        elif kind == "deck":
            src = PUBLIC / "decks" / slug
            dst = SITE / "decks" / slug
            public_items.append(item)
        else:
            src = PUBLIC / "pages" / slug
            dst = SITE / "pages" / slug
            public_items.append(item)

        if not (src / "index.html").exists():
            raise FileNotFoundError(f"missing artifact index.html: {src}")
        copytree(src, dst)
        published = dict(item)
        published["url"] = artifact_url(item)
        manifest.append(published)

    (SITE / "index.html").write_text(build_index(public_items), encoding="utf-8")
    (SITE / "artifacts.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
