# shopify-catalog-auditor

Audit any Shopify store's catalog for the gaps that quietly cost sales —
**no API keys, no store access, no app install.** Point it at a domain and get a
prioritised report plus a CSV fix-list in under a minute.

```bash
python audit.py examplestore.com --csv issues.csv
```

## Why

Merchants describe the same complaints over and over: exporting products just to
spot what's broken, hunting missing data across spreadsheets, sold-out pages
still taking ad clicks. This finds those problems in one pass and ranks them by
what they actually cost.

## What it checks

| Check | Why it costs money |
|---|---|
| Product has no image | Converts far worse; skipped by shopping feeds |
| Only one image | Multiple angles measurably lift conversion |
| No description at all | Kills both SEO and conversion |
| Description under 150 chars | Thin copy ranks poorly, answers no buyer questions |
| Variant missing SKU | Breaks inventory reconciliation and supplier matching |
| Duplicate product title | Duplicates compete against each other in search |
| Title over 70 chars | Truncated in search results and feeds |
| Sold out but still published | Live sold-out pages waste ad spend |
| No product type set | Breaks collection rules and feed categorisation |

## Sample output

```
================================================================
CATALOG AUDIT — https://examplestore.com
================================================================
Products scanned: 150
Products with at least one issue: 120 (80%)

Issues found, highest impact first:

    114  ( 76% of catalog)  Sold out but still published
         -> Live sold-out pages waste ad spend and frustrate buyers
     16  ( 11% of catalog)  Description under 150 characters
         -> Thin copy ranks poorly and answers none of the buyer's questions
     11  (  7% of catalog)  Title over 70 characters
         -> Long titles get truncated in search results and feeds

Worst products:
  [ 6]  Men's Tree Runner Go - Utility            /products/mens-tree-runner-go-utility
```

The CSV lists every affected product with its issues and a severity score, so
the fix list is ready to work through.

## Install

```bash
pip install requests
python audit.py yourstore.com
```

Options: `--limit N` (products to scan, default 1000), `--csv FILE`, `--delay S`
(seconds between requests, default 0.5 — keep it polite).

## Honest limits

- Reads only the **public** `/products.json` catalog that every Shopify
  storefront serves. Password-protected stores return nothing.
- **Image alt text and variant barcodes/GTINs are not audited.** Shopify's public
  catalog omits those fields entirely — reporting them from public data would
  flag problems that may not exist. Checking them requires Admin API access.
- Severity weights are a practical ranking, not a revenue model. Use them to
  order the work, not to forecast income.

## License

MIT — see [LICENSE](LICENSE).
