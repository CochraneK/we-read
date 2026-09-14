#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a reproducible WeRead archive without touching the canonical Page.

This entrypoint reuses the exact production Pages render chain, but makes the
input data directory and output site directory explicit.  It deliberately
refuses to write to ``site/`` so template experiments cannot overwrite the
owner's deployed archive.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
CANONICAL_SITE = (ROOT / "site").resolve()
REQUIRED_DATA_FILES = (
    "weread_shelf.json",
    "weread_notebooks.json",
    "weread_notes_export.json",
    "weread_readdata.json",
)

if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


def _same_path(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return False


def validate_inputs(data_dir: Path, output_dir: Path) -> None:
    data_dir = data_dir.expanduser()
    output_dir = output_dir.expanduser()
    if not data_dir.is_dir():
        raise SystemExit(f"ERROR: data directory does not exist: {data_dir}")
    missing = [name for name in REQUIRED_DATA_FILES if not (data_dir / name).is_file()]
    if missing:
        raise SystemExit("ERROR: missing required WeRead exports: " + ", ".join(missing))
    if _same_path(output_dir, CANONICAL_SITE):
        raise SystemExit(
            "ERROR: template builder refuses to overwrite ./site. "
            "Choose another --output directory; the production Page remains owned by pages_runtime.py."
        )
    if _same_path(output_dir, data_dir):
        raise SystemExit("ERROR: --output must not be the same directory as --data")


def _set_private_env(enabled: bool) -> str | None:
    previous = os.environ.get("WEREAD_PAGES_INCLUDE_PRIVATE")
    os.environ["WEREAD_PAGES_INCLUDE_PRIVATE"] = "1" if enabled else "0"
    return previous


def _restore_private_env(previous: str | None) -> None:
    if previous is None:
        os.environ.pop("WEREAD_PAGES_INCLUDE_PRIVATE", None)
    else:
        os.environ["WEREAD_PAGES_INCLUDE_PRIVATE"] = previous


def build_template_site(
    data_dir: Path,
    output_dir: Path,
    *,
    include_private: bool = False,
    publish_marks: bool = False,
) -> dict:
    """Assemble the production visual system into an isolated output directory."""
    data_dir = data_dir.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()
    validate_inputs(data_dir, output_dir)

    previous_private = _set_private_env(include_private)
    try:
        # Import only after the privacy mode is set. pages_insights_full installs
        # the production enrichment UI at import time when full mode is enabled.
        import build_pages_report as report
        import pages_polish_site
        import pages_public_quotes
        import pages_runtime

        if output_dir.exists():
            shutil.rmtree(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # Match scripts/pages_runtime.py exactly, except the data/output paths are
        # explicit and the canonical ./site directory is never mutated.
        report.daily_read_times = pages_runtime.daily_read_times
        template = report.TEMPLATE
        if 'id="shift"' not in template:
            template = pages_runtime.enhance_template(template)

        page_report = pages_runtime.build_report(data_dir, include_private=include_private)
        payload = json.dumps(page_report, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        (output_dir / "index.html").write_text(
            template.replace("__REPORT_JSON__", payload), encoding="utf-8"
        )
        (output_dir / "report-data.json").write_text(
            json.dumps(page_report, ensure_ascii=False, indent=2), encoding="utf-8"
        )

        quote_result = pages_public_quotes.augment_site(
            output_dir,
            data_dir,
            enabled=publish_marks,
        )
        pages_polish_site.polish(output_dir)
        (output_dir / ".nojekyll").write_text("", encoding="utf-8")

        build_meta = {
            "builder": "weread-template",
            "renderChain": [
                "pages_runtime",
                "pages_public_quotes" if publish_marks else "pages_public_quotes:disabled",
                "pages_polish_site",
            ],
            "includePrivate": bool(include_private),
            "publishMarks": bool(publish_marks),
            "output": str(output_dir),
            "summary": page_report.get("summary") or {},
            "quotes": quote_result,
        }
        (output_dir / "template-build.json").write_text(
            json.dumps(build_meta, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return build_meta
    finally:
        _restore_private_env(previous_private)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        required=True,
        help="Directory containing the exported weread_*.json files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Isolated static-site output directory. ./site is intentionally forbidden.",
    )
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Include secret=1 book metadata. Raw review text is still not placed in report-data.json.",
    )
    parser.add_argument(
        "--publish-marks",
        action="store_true",
        help=(
            "Publish the authorized marks-only browser search index and rotating excerpts. "
            "This writes mark text into the static output, so it is opt-in."
        ),
    )
    args = parser.parse_args()
    result = build_template_site(
        args.data,
        args.output,
        include_private=args.include_private,
        publish_marks=args.publish_marks,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
