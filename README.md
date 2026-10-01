# zen-glass

A frosted-glass version of [sameerasw/my-internet](https://github.com/sameerasw/my-internet)'s `styles.json` for the [Zen Internet](https://github.com/sameerasw/zeninternet) extension.

The upstream styles make most of each page fully transparent, so text sits directly on whatever Zen paints behind the window. This version keeps every upstream rule unchanged and adds:

- **A tinted base layer:** one translucent tint under all page content, following light/dark mode, so contrast no longer depends on the wallpaper.
- **A `… transparency glass` feature:** headers, navs, sidebars, footers and menus become blurred glass panels. You can switch it off per site in the extension popup if a site's popups misbehave.
- **Accessibility:** near-opaque layers when the system asks for reduced transparency or more contrast.

## Look

The tuning matches the Blur my Shell "Default" pipeline: blur radius 30, brightness 0.6 (a 40% black dim in dark mode) and noise 0.4 at lightness 0.8 (a faint grain). For the desktop behind pages to actually blur, Zen (`app.zen_browser.zen`) must **not** be on Blur my Shell's *Applications → blacklist*, and `zen.widget.linux.transparency` must be on.

## Use

In Zen Internet's settings, set the styles repository URL to:

```
https://theworstdrug.github.io/zen-glass/styles.json
```

Then refresh the styles.

## Regenerate

```
pip install tinycss2
curl -sLO https://sameerasw.github.io/my-internet/styles.json && mv styles.json styles.original.json
python3 make_glass.py styles.original.json styles.json
```

Tune the look with the `--zg-*` variables in the `TOKENS` block of `make_glass.py`.

## License

The site styles are derived from sameerasw/my-internet (MIT); see `LICENSE.upstream`.
