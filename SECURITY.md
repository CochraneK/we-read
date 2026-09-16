# Security Policy

## Sensitive data boundary

`we-read` processes personal reading data. Treat the following as sensitive by default:

- `WEREAD_API_KEY` and other credentials;
- full raw WeRead exports;
- full highlights and user-authored reviews/thoughts;
- local search indexes and Private Reading Lab artifacts;
- private synthesis or semantic-review outputs.

Public GitHub Pages content is governed by [docs/publication-policy.md](docs/publication-policy.md) and must pass `scripts/validate_pages_output.py` before deployment.

## Reporting a security or privacy issue

Please open a private GitHub security advisory when available, or contact the repository owner privately. Do not include credentials, private reading text, or other sensitive evidence in a public issue.

## Credential exposure

If an API key or credential is exposed, revoke/rotate it first. Removing the current file or adding it to `.gitignore` does not invalidate a leaked credential or erase Git history.

## Repository history

Tracked personal data and history cleanup are handled separately from the Page publication policy. Destructive history rewriting must not be performed automatically and requires an explicit owner decision.
