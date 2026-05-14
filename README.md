# Knowledge Pages

Generated HTML knowledge pages and slide decks.

Live site: <https://knowledge.11tech.xyz/>

Production content is built from `content/public/` and deployed with GitHub
Pages. Unlisted content can live under `content/unlisted/` and be published
under hash-like URLs without appearing in the gallery.

## Layout

```txt
content/
  artifacts.json
  public/decks/<slug>/index.html
  unlisted/<token>/index.html
scripts/build_site.py
site/                 # generated, not committed
```

Run locally:

```sh
python3 scripts/build_site.py
```
