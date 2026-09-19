# Security policy

shopify-catalog-auditor reads a store's public `/products.json` catalog and
writes a report plus an optional CSV. This file defines what counts as a
security issue in that specific process, not in Shopify or in a store you
audit.

## Reporting

Use GitHub's private vulnerability reporting on this repository: **Security →
Report a vulnerability**. It opens a private thread; nothing becomes public
until there is a fix.

If that is not available to you, email **hello@dkautomation.dev** with
`shopify-catalog-auditor` in the subject line.

Include the commit or version you ran, the exact command, and what happened.
A proof of concept is welcome; a scanner's raw output usually is not.

**Do not open a public issue for a vulnerability.**

## Supported versions

No tagged releases yet — the `main` branch is the supported version. Report
against the commit you actually ran.

## What to expect

| | |
|---|---|
| First reply | within 3 working days |
| Assessment | within 7 working days of the first reply |
| Fix or a stated decision not to fix | within 30 days for anything reproducible |

Single-person commitments, not a company SLA.

## Scope

The catalog a store serves back is not trusted input — you choose the domain,
but the store's own owner controls what `/products.json` actually returns.

In scope:

- A product title, description, or any other catalog field that, when it
  reaches the terminal report or the `--csv` file, does more than display as
  text — a leading `=`, `+`, `-`, or `@` that a spreadsheet would execute as a
  formula when the CSV is opened, or terminal control sequences printed
  verbatim into the report.
- A crafted `/products.json` response that makes the tool write outside the
  file named in `--csv`, or crash in a way that is not a clean, reported
  error.

Out of scope:

- The store domain you point the tool at — that is your own choice, not
  something an attacker hands you.
- A store that is slow, unreachable, or returns malformed JSON — handled as
  an error, not a vulnerability.
- Image alt text or variant barcodes/GTINs not being checked — the public
  catalog does not expose them; see "Honest limits" in the README.
- Disagreement with the severity weighting — it is a documented ranking, not
  a revenue model.

## Credit

Named in the fix's release notes if you want that; say so if you would rather
not be.

There is no bug bounty.
