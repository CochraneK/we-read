# weread-template

`weread-template` is the reproducible, user-facing build path for the current WeRead Pages experience.

Its core invariant is simple:

> **Reuse the production render chain, but never write to the owner's canonical `site/` directory.**

The template does **not** maintain a copied HTML fork. It calls the same `pages_runtime → pages_public_quotes → pages_polish_site` layers used by the live Page, with explicit `--data` and `--output` directories. This keeps the template visually aligned as the main Page evolves and prevents template experiments from breaking the deployed archive.

## 1. Zero-secret demo

Generate a synthetic dataset and build the full current-page profile:

```bash
python template/demo_data.py --output .tmp/weread-demo-data

python scripts/build_template_site.py \
  --data .tmp/weread-demo-data \
  --output .tmp/weread-demo-site \
  --include-private \
  --publish-marks
```

Validate it with the same production contract used before GitHub Pages deploys:

```bash
python scripts/validate_pages_output.py \
  --site .tmp/weread-demo-site \
  --data .tmp/weread-demo-data \
  --js-out .tmp/weread-demo-inline.js

node --check .tmp/weread-demo-inline.js
```

Then serve locally:

```bash
python -m http.server 8000 -d .tmp/weread-demo-site
```

Open `http://localhost:8000`.

Everything in `template/demo_data.py` is synthetic. No real reading history, title, highlight, review, account identifier, or API key is required.

## 2. Build from your own exported WeRead data

The template builder expects these four files in one directory:

```text
weread_shelf.json
weread_notebooks.json
weread_notes_export.json
weread_readdata.json
```

The current enrichment layer also uses these when present:

```text
weread_progress.json
weread_bookinfo.json
```

If you use this repository's normal export path, a typical local flow is:

```bash
export WEREAD_API_KEY="wrk-..."
export WEREAD_DATA_DIR="$HOME/.local/share/we-read"

python scripts/export_notes.py
python scripts/fetch_enrich.py

python scripts/build_template_site.py \
  --data "$WEREAD_DATA_DIR" \
  --output dist
```

The default is deliberately conservative:

- `secret=1` books are excluded;
- raw review text is not published;
- mark text is not published;
- the result is written only to the directory you passed with `--output`.

## 3. Match the current owner's full public Page profile

The owner's current Page explicitly opts into both private-book metadata and the marks-only public search/quote layer. To reproduce that profile with **your own** data:

```bash
python scripts/build_template_site.py \
  --data "$WEREAD_DATA_DIR" \
  --output dist \
  --include-private \
  --publish-marks
```

`--include-private` means metadata for `secret=1` books can appear in the output.

`--publish-marks` is more sensitive: it writes a browser-local `public-marks-index.js` containing the full text of eligible marks and also enables rotating excerpts. Use it only when you intentionally want those marks in a public static site. Reviews remain excluded from that marks index.

## 4. Why the template cannot break the existing Page

`scripts/build_template_site.py` refuses to use the repository's canonical `site/` directory as its output. If you try this:

```bash
python scripts/build_template_site.py --data /path/to/data --output site
```

it exits with an error before writing anything.

The production Page remains owned by the existing deployment path:

```text
.github/workflows/pages.yml
  → scripts/pages_runtime.py
  → scripts/pages_public_quotes.py
  → scripts/pages_polish_site.py
  → site/
```

The template path is separate:

```text
scripts/build_template_site.py
  → same production render modules
  → your explicit output directory
```

The regression test `tests/test_template_site.py` additionally snapshots `site/index.html`, builds and validates a full synthetic template in a temporary directory, and asserts that the canonical Page is byte-for-byte unchanged.

## 5. Deploy in your own fork/repository

`template/github-pages.example.yml` is an **inactive example workflow**. It is intentionally not placed under `.github/workflows/`, so it cannot compete with or alter this repository's current Pages deployment.

Copy it into your own repository as `.github/workflows/pages.yml`, add `WEREAD_API_KEY` as a GitHub Actions secret, and keep the default filtered/no-marks profile unless you explicitly want broader publication.

## 6. Design rule going forward

When the main Page gains a new stable visual module, prefer adding that module to the shared production render chain. Do not paste a second implementation into `template/`.

That gives the project one renderer and two safe entrypoints:

```text
owner production Page  ─┐
                        ├─ shared render chain
reproducible template ──┘
```
