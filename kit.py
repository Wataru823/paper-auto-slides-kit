#!/usr/bin/env python3
"""Render a JSON slide spec into a self-contained HTML deck.

    python3 kit.py examples/spec.json examples/index.html

The spec is just data; this file turns it into markup. No dependencies, no
build step. Design rules live in DESIGN.md.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

SECTIONS = {
    "problem": "The Problem",
    "idea": "Key Idea",
    "method": "Method",
    "results": "Results",
    "limits": "Limitations",
    "takeaway": "Why It Matters",
    "detail": "Detail",
}


def esc(value) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def clip(text, limit: int) -> str:
    s = " ".join(str(text or "").split())
    return s if len(s) <= limit else s[: limit - 1] + "…"


def rich(text) -> str:
    """Escape, then honour **bold** for emphasis."""
    import re

    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(clip(text, 240)))


def bullets(items, cards: bool = False) -> str:
    if not items:
        return ""
    cls = "bullets bullets--cards" if cards else "bullets"
    return f'<ul class="{cls}">' + "".join(f"<li>{rich(i)}</li>" for i in items) + "</ul>"


def table_html(table: dict) -> str:
    headers = (table or {}).get("headers") or []
    rows = (table or {}).get("rows") or []
    if not headers and not rows:
        return ""
    head = "".join(f"<th>{esc(h)}</th>" for h in headers[:5])
    body = "".join(
        "<tr>" + "".join(f"<td>{esc(c)}</td>" for c in (r or [])[:5]) + "</tr>"
        for r in rows[:6]
    )
    return (
        "<table class=\"tbl\">"
        + (f"<thead><tr>{head}</tr></thead>" if head else "")
        + f"<tbody>{body}</tbody></table>"
    )


def figure_html(media: dict | None, caption: str = "", band: bool = False) -> str:
    if not media:
        return ""
    src = media.get("src") or ""
    if not src:
        return ""
    if media.get("kind") == "video":
        poster = media.get("poster") or ""
        attr = f' poster="{esc(poster)}"' if poster else ""
        return (
            '<figure class="fig fig--video">'
            f'<video src="{esc(src)}"{attr} autoplay muted loop playsinline></video>'
            + (f"<figcaption>{esc(caption)}</figcaption>" if caption and not band else "")
            + "</figure>"
        )
    cls = "fig fig--band" if band else "fig"
    cap = f"<figcaption>{esc(caption)}</figcaption>" if caption and not band else ""
    return f'<figure class="{cls}"><img src="{esc(src)}" alt="">{cap}</figure>'


def pager(number: int, total: int) -> str:
    w = max(2, len(str(total)))
    return f"{number:0{w}d} / {total:0{w}d}"


def cover_slide(spec: dict, total: int) -> str:
    cover = spec.get("cover") or {}
    meta = "".join(
        f'<span class="chip">{esc(c)}</span>' for c in (cover.get("chips") or [])
    )
    art = cover.get("image")
    figure = (
        f'<div class="cover__figure"><img src="{esc(art)}" alt=""></div>'
        if art else '<div class="cover__figure"></div>'
    )
    return f"""
<section class="slide slide--cover is-active" aria-hidden="false">
  <div class="slide__inner">
    <div class="cover">
      <div class="cover__text">
        <div class="cover__kicker">{esc(cover.get("kicker") or "")}</div>
        <h1 class="cover__catch">{rich(cover.get("title"))}</h1>
        <p class="cover__one">{rich(cover.get("lead"))}</p>
        <p class="cover__title-en">{esc(clip(cover.get("subtitle"), 110))}</p>
        <div class="cover__meta">{meta}</div>
      </div>
      {figure}
    </div>
  </div>
  <span class="brand">{esc(spec.get("brand") or "")}</span>
  <span class="pager">{pager(1, total)}</span>
</section>"""


def content_slide(slide: dict, spec: dict, number: int, total: int) -> str:
    kind = slide.get("type") or "detail"
    label = slide.get("section") or SECTIONS.get(kind, "Detail")
    has_table = bool(slide.get("table"))
    media = slide.get("media")
    band = bool(media and media.get("band") and not has_table)

    parts: list[str] = []
    if slide.get("statement"):
        parts.append(f'<p class="statement">{rich(slide["statement"])}</p>')
    if slide.get("steps"):
        compact = bool(media) or has_table
        count = min(len(slide["steps"]), 4)
        cls = "steps"
        if compact:
            cls += f" steps--compact steps--n{count}"
        rows = "".join(
            f'<div class="step"><span class="step__num">{i + 1}</span>'
            f'<span class="step__label">{esc(st.get("label"))}</span>'
            f'<span class="step__text">{esc(st.get("text"))}</span></div>'
            for i, st in enumerate(slide["steps"])
        )
        parts.append(f'<div class="{cls}">{rows}</div>')
    if slide.get("stats"):
        cards = "".join(
            f'<div class="stat"><div class="stat__value">{esc(st.get("value"))}</div>'
            f'<div class="stat__label">{esc(st.get("label"))}</div></div>'
            for st in slide["stats"]
        )
        parts.append(f'<div class="stats">{cards}</div>')
    show_bullets = not (kind == "results" and (media or has_table))
    if slide.get("bullets") and show_bullets:
        as_cards = (
            not media
            and kind in ("problem", "limits", "takeaway", "detail")
            and len(slide["bullets"]) <= 3
        )
        parts.append(bullets(slide["bullets"], cards=as_cards))
    if slide.get("note") and kind != "results":
        parts.append(f'<div class="note">{esc(slide["note"])}</div>')

    text_col = f'<div class="col col--text">{"".join(parts)}</div>'
    tbl = table_html(slide.get("table") or {})
    caption = (spec.get("brand") or "") and "" or ""
    fig = figure_html(media, caption, band=band)

    if tbl:
        body = f'<div class="stack">{text_col}{tbl}</div>'
        layout = "center"
    elif fig and band:
        body = f'<div class="stack stack--band">{text_col}{fig}</div>'
        layout = "top"
    elif fig:
        order = "split--steps" if kind == "method" else (
            "split--figure-first" if number % 2 == 0 else "split--text-first"
        )
        body = f'<div class="split {order}">{text_col}<div class="col col--figure">{fig}</div></div>'
        layout = "center"
    else:
        body = f'<div class="stack">{text_col}</div>'
        layout = "top"

    claim = slide.get("claim") or ""
    claim_html = f'<p class="claim">{rich(claim)}</p>' if claim else ""
    cite = slide.get("cite") or ""

    return f"""
<section class="slide" aria-hidden="true">
  <div class="band">
    <span class="band__num">{number:02d}</span>
    <span class="band__label">{esc(label)}</span>
  </div>
  <div class="slide__inner">
    <div class="slide__head">
      <h2>{esc(slide.get("title") or "")}{f'<span class="cite">[{esc(cite)}]</span>' if cite else ''}</h2>
      {claim_html}
    </div>
    <div class="slide__body" data-layout="{layout}">{body}</div>
  </div>
  <span class="brand">{esc(spec.get("brand") or "")}</span>
  <span class="pager">{pager(number, total)}</span>
</section>"""


def links_slide(spec: dict, number: int, total: int) -> str:
    links = spec.get("links") or []
    if not links:
        return ""
    cards = "".join(
        f'<a class="linkcard" href="{esc(l.get("url"))}" target="_blank" rel="noopener">'
        f'<div class="linkcard__label">{esc(l.get("label"))}</div>'
        f'<div class="linkcard__value">{esc(l.get("text"))}</div></a>'
        for l in links
    )
    return f"""
<section class="slide" aria-hidden="true">
  <div class="band">
    <span class="band__num">{number:02d}</span>
    <span class="band__label">Read More</span>
  </div>
  <div class="slide__inner">
    <div class="slide__head">
      <h2>{esc(spec.get("links_title") or "リンク")}</h2>
      <p class="claim">{esc(spec.get("links_claim") or "")}</p>
    </div>
    <div class="slide__body" data-layout="top"><div class="stack"><div class="linkgrid">{cards}</div></div></div>
  </div>
  <span class="brand">{esc(spec.get("brand") or "")}</span>
  <span class="pager">{pager(number, total)}</span>
</section>"""


def render(spec: dict, css: str = "css/deck.css", js: str = "js/deck.js") -> str:
    slides = spec.get("slides") or []
    total = len(slides) + 1 + (1 if spec.get("links") else 0)
    sections = [cover_slide(spec, total)]
    for i, slide in enumerate(slides):
        sections.append(content_slide(slide, spec, i + 2, total))
    if spec.get("links"):
        sections.append(links_slide(spec, total, total))
    title = spec.get("page_title") or (spec.get("cover") or {}).get("title") or "Slides"
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{esc(title)}</title>
<link rel="stylesheet" href="{css}">
</head>
<body>
<div class="deck-viewport">
  <div class="deck-stage">
{''.join(sections)}
  </div>
</div>
<div class="hud">
  <div class="hud__bar"><div class="hud__fill"></div></div>
  <span class="hud__hint">← → 移動 / F 全画面 / P 印刷</span>
</div>
<script src="{js}"></script>
</body>
</html>
"""


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    src = Path(argv[1])
    out = Path(argv[2]) if len(argv) > 2 else src.with_suffix(".html")
    spec = json.loads(src.read_text(encoding="utf-8"))
    depth = len(out.parent.relative_to(out.parents[len(out.parents) - 1]).parts) if False else 0
    # relative asset paths: assume css/ and js/ sit at the project root
    css = "../css/deck.css" if out.parent.name == "examples" else "css/deck.css"
    js = "../js/deck.js" if out.parent.name == "examples" else "js/deck.js"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(spec, css, js), encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
