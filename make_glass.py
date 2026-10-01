#!/usr/bin/env python3
"""Convert my-internet styles.json from clear transparency to frosted glass.

For every feature whose name contains "transparency" (the extension's global
transparency toggle keys off that substring) we:
  1. append a token block + a single tinted base layer on the page root, so
     text never sits directly on the raw browser background;
  2. add a sibling "<name> glass" feature that turns bar-like surfaces
     (nav/header/sidebar/footer/menus) into blurred glass panels. It is a
     separate feature so it can be switched off per site if a site's
     fixed-position popups get trapped by backdrop-filter's containing block.

Usage: make_glass.py [in.json] [out.json]
"""
import json, re, sys

import tinycss2  # pip install tinycss2

SRC = sys.argv[1] if len(sys.argv) > 1 else "styles.json"
DST = sys.argv[2] if len(sys.argv) > 2 else "styles.glass.json"

# Tuned to match the Blur my Shell "Default" pipeline on this desktop:
#   gaussian blur radius 30, brightness 0.6  -> 40% black dim, blur(30px)
#   noise 0.4 @ lightness 0.8                -> faint grain overlay
# The desktop behind Zen is blurred by BMS itself (Zen must not be on its app
# blacklist); in-page blur only applies to bars over scrolling page content.
NOISE = ("url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E"
         "%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3' stitchTiles='stitch'/%3E"
         "%3CfeColorMatrix values='0 0 0 0 .8 0 0 0 0 .8 0 0 0 0 .8 0 0 0 .14 0'/%3E%3C/filter%3E"
         "%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E\")")
LIGHT = ("--zg-base:rgba(255,255,255,.42);--zg-panel:rgba(255,255,255,.28);"
         "--zg-hi:rgba(255,255,255,.5);--zg-edge:rgba(0,0,0,.08);")
DARK = ("--zg-base:rgba(0,0,0,.4);--zg-panel:rgba(0,0,0,.18);"
        "--zg-hi:rgba(255,255,255,.1);--zg-edge:rgba(255,255,255,.06);")
DARK_SITE = (':root:is(.dark,.theme-dark,.dark-mode,[data-theme="dark"],[data-color-mode="dark"],'
             '[data-darkreader-scheme="dark"]),:root:has(>body:is(.dark,.dark_mode,.dark-mode,'
             '.theme-dark,[data-theme="dark"]))')
LIGHT_SITE = (':root:is(.light,.theme-light,[data-theme="light"],[data-color-mode="light"]),'
              ':root:has(>body:is(.light,.light_mode,.theme-light,[data-theme="light"]))')
TOKENS = (
    f":root{{{LIGHT}--zg-blur:30px;--zg-sat:150%;--zg-noise:{NOISE}}}"
    f"@media (prefers-color-scheme:dark){{:root{{{DARK}}}}}"
    f"{DARK_SITE}{{{DARK}}}{LIGHT_SITE}{{{LIGHT}}}"
    # accessibility: near-opaque when the user asks for less transparency / more contrast
    "@media (prefers-reduced-transparency:reduce),(prefers-contrast:more){"
    ":root{--zg-base:rgba(246,246,248,.94);--zg-panel:rgba(255,255,255,.9)}}"
    "@media (prefers-color-scheme:dark) and ((prefers-reduced-transparency:reduce) or (prefers-contrast:more)){"
    ":root{--zg-base:rgba(22,22,26,.94);--zg-panel:rgba(44,44,50,.9)}}"
)

BAR = re.compile(r"(?<![\w])(nav|navbar|navigation|header|masthead|topbar|top-bar|appbar|app-bar|"
                 r"toolbar|sidebar|side-bar|sidenav|side-nav|aside|footer|banner|drawer|dropdown|"
                 r"popover|popup|modal|dialog|tooltip|menu)(?![\w])", re.I)
NOT_BAR = re.compile(r"item|link|btn|button|icon|toggle|label|text|title|logo|backdrop|overlay|"
                     r"wrapper-inner|container::", re.I)
CLEARS = re.compile(r"transparent|background\s*:\s*none", re.I)


def last_compound(sel):
    # drop (...) / [...] groups first so ":not(.a, .b)" isn't split on its inner spaces
    prev = None
    while prev != sel:
        prev, sel = sel, re.sub(r"\([^()]*\)|\[[^\[\]]*\]", "", sel)
    return re.split(r"\s*[>+~]\s*|\s+", sel.strip())[-1]


def split_selectors(prelude):
    """Split a selector list on top-level commas only (not inside :is(a, b) or "a,b")."""
    parts, cur = [], []
    for tok in prelude:
        if tok.type == "literal" and tok.value == ",":
            parts.append(tinycss2.serialize(cur).strip())
            cur = []
        else:
            cur.append(tok)
    parts.append(tinycss2.serialize(cur).strip())
    return parts


def qualified_rules(nodes):
    for r in nodes:
        if r.type == "qualified-rule":
            yield r
        elif r.type == "at-rule" and r.content and r.lower_at_keyword in ("media", "supports", "-moz-document"):
            yield from qualified_rules(tinycss2.parse_rule_list(r.content, skip_comments=True, skip_whitespace=True))


def classify(css):
    roots, bars = [], []
    for rule in qualified_rules(tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True)):
        if not CLEARS.search(tinycss2.serialize(rule.content)):
            continue
        for sel in split_selectors(rule.prelude):
            if not sel or "::" in sel or ":hover" in sel:
                continue
            if sel in ("html", ":root", "body"):
                roots.append(sel)
                continue
            lc = last_compound(sel)
            if BAR.search(lc) and not NOT_BAR.search(lc) and sel not in bars:
                bars.append(sel)
    return roots, bars


def root_layer(roots):
    # Exactly one tinted layer: stacking tints on html AND body would compound.
    target = "html" if "html" in roots else ":root" if ":root" in roots else "body" if roots else None
    if not target:
        return ""
    return (f"\n/* frosted base: one tint layer under all content */\n"
            f"{target}{{background-color:var(--zg-base)!important;background-image:var(--zg-noise)!important;background-attachment:fixed!important}}")


def bar_layer(bars):
    if not bars:
        return ""
    lst = ",".join(bars)
    return (
        "/* frosted glass bars (:is() keeps the list forgiving and wins specificity) */\n"
        f":is({lst}){{background-color:var(--zg-panel,rgba(128,128,128,.3))!important;"
        "backdrop-filter:blur(var(--zg-blur,30px)) saturate(var(--zg-sat,150%))!important;background-image:var(--zg-noise,none)!important;"
        "box-shadow:inset 0 .5px 0 var(--zg-hi,rgba(255,255,255,.2)),0 0 0 .5px var(--zg-edge,rgba(128,128,128,.2))!important}\n"
        "/* a bar nested in a bar stays clear so glass never stacks */\n"
        f":is({lst}) :is({lst}){{background-color:transparent!important;background-image:none!important;"
        "backdrop-filter:none!important;box-shadow:none!important}"
    )


def main():
    data = json.load(open(SRC))
    stats = dict(features=0, roots=0, bars=0)
    out = {}
    for site, feats in data["website"].items():
        nf = {}
        for name, css in feats.items():
            if "transparency" not in name.lower() or "zg-base" in css:
                nf[name] = css
                continue
            stats["features"] += 1
            roots, bars = classify(css)
            rl = root_layer(roots)
            stats["roots"] += bool(rl)
            nf[name] = css.rstrip() + "\n" + TOKENS + rl
            bl = bar_layer(bars)
            if bl:
                stats["bars"] += 1
                nf[name + " glass"] = bl
        out[site] = nf
    data["website"] = out
    json.dump(data, open(DST, "w"), indent=2, ensure_ascii=False)
    print(stats)


if __name__ == "__main__":
    main()
