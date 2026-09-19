# Contributing

Real commands for this repository. `.github/workflows/ci.yml` is the source of
truth if this page and CI ever disagree.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
```

One dependency: `requests`.

## Before you write code

The README's "Honest limits" section names what this tool deliberately does
not check — image alt text and variant barcodes/GTINs, because Shopify's
public `/products.json` does not expose them. Adding those needs Shopify
Admin API access, which this tool intentionally does not use; a pull request
adding it will be declined. Open an issue first for anything beyond a fix.

## The one rule that is not negotiable

A new check starts as a failing test. Add a `check("label", condition)` call
inside `selftest()` in `audit.py` that fails against the current behaviour,
confirm it fails for the right reason, then implement the check and register
it in the `ISSUES` table.

## Running the tests

```bash
python -m compileall -q .
python audit.py --selftest
```

Same two steps CI runs, in that order.

## Commit messages

Match `git log --oneline` in this repository: a short, imperative summary, no
ticket prefixes, no emoji. Recent examples:

```
Add --selftest, and run it in CI
shopify-catalog-auditor: audit any Shopify catalog for revenue-losing gaps, no API keys needed
```

## License

Contributions are published under this repository's MIT license.
