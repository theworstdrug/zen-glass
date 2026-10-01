# zen-glass

A frosted-glass version of [sameerasw/my-internet](https://github.com/sameerasw/my-internet)'s `styles.json` for the [Zen Internet](https://github.com/sameerasw/zeninternet) extension.

The upstream styles make most of each page fully transparent, so text sits directly on whatever Zen paints behind the window. This version keeps every upstream rule unchanged and adds:

- **A tinted base layer:** one translucent tint under all page content, following light/dark mode, so contrast no longer depends on the wallpaper.
- **A `… transparency glass` feature:** headers, navs, sidebars, footers and menus become blurred glass panels. You can switch it off per site in the extension popup if a site's popups misbehave.
- **Accessibility:** near-opaque layers when the system asks for reduced transparency or more contrast.

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
