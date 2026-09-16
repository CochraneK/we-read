# WeRead Public Publication Policy

> Canonical publication policy. Updated 2026-09-16. This file is the source of truth for what may enter the public GitHub Pages artifact.

## Policy authority

`README.md`, `AGENTS.md`, `docs/pages.md`, workflow configuration and validators must stay consistent with this document. If older documentation conflicts with this file, this policy wins and the stale documentation should be updated.

This policy governs **published Page artifacts**. It does not authorize destructive cleanup of repository history. Historical tracked personal exports are a separate maintenance concern tracked in Issue #2 and must not be rewritten or removed automatically.

## Current public scope

GitHub Pages is allowed to publish:

- books marked `secret=1` when `WEREAD_PAGES_INCLUDE_PRIVATE=1`;
- bounded highlight excerpts when `WEREAD_PAGES_INCLUDE_PUBLIC_QUOTES=1`;
- book title, author, chapter and WeRead deep link for each public excerpt;
- existing aggregate reading facts, metadata and deterministic analysis.

## What the authorization does not mean

The authorization to publish highlights changes the privacy decision. It does not remove the independent copyright/distribution boundary.

The Page therefore does **not** publish the full raw notes export.

Public quote policy:

```text
source                marks/highlights only
reviews               never published by this module
max characters        90 per excerpt
max per book          1
max total             48
long highlight        truncated
private-book marks    eligible only when Pages private-book scope is enabled
full raw body         remains private
```

Implementation:

```text
scripts/pages_public_quotes.py
```

Deployment opt-in:

```text
WEREAD_PAGES_INCLUDE_PUBLIC_QUOTES=1
```

This switch is intentionally independent from:

```text
WEREAD_PAGES_INCLUDE_PRIVATE=1
```

so book privacy scope and quote publication scope can be changed separately.

## Public artifact contract

`site/report-data.json` may contain a `publicQuotes` object with:

- an explicit `userAuthorized=true` policy;
- `source=marks_only`;
- `reviewsPublished=false`;
- `fullRawPublished=false`;
- the configured excerpt/per-book/total caps;
- the selected bounded excerpts.

The final Page also contains a `#public-quotes` section titled:

```text
我的划线 · 公开摘录
```

## Validation

`scripts/validate_pages_output.py` rejects deployment if:

- the public quote contract is not explicitly authorized;
- any public quote comes from `review` rather than `mark`;
- a quote exceeds the hard character cap;
- more than one quote from the same book is exposed;
- the total exceeds the hard cap;
- `text/content/markText/reviewText` raw-body fields appear in public quote items;
- any sampled raw mark/review body leaks outside the explicit bounded-excerpt contract.

The existing `insights.scope.rawTextPublished=false` flag continues to mean **full/raw evidence payloads are not published**. Authorized bounded excerpts are governed separately by `publicQuotes`.

## Private Reading Lab

Nothing changes for the Private Reading Lab. It remains the place for:

- full marks;
- full user reviews/thoughts;
- Search index;
- Recall evidence;
- Deep Notes;
- Alchemy;
- private synthesis and semantic review.

A future decision to publish user-authored reviews should be treated as a separate authorization and implementation change, not inferred from the current highlight authorization.
