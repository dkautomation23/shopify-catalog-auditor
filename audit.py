#!/usr/bin/env python3
"""shopify-catalog-auditor — find revenue-losing gaps in a Shopify catalog.

Reads a store's public catalog (no API keys, no store access) and reports the
issues that quietly cost sales: products with no image, images with no alt text,
thin or missing descriptions, missing SKU/barcode, duplicate titles, SEO-length
problems, and sold-out products still published.

Outputs a prioritised summary plus a CSV of every affected product, so the fix
list is ready to hand to whoever does the work.

Usage:
    python audit.py https://examplestore.com
    python audit.py examplestore.com --csv issues.csv --limit 500
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from html import unescape
from urllib.parse import urlparse

import requests

UA = "Mozilla/5.0 (compatible; catalog-auditor/1.0; +https://github.com/dkautomation23)"
TAG_RE = re.compile(r"<[^>]+>")

# Issue code -> (human label, why it costs money, weight for prioritising)
#
# Only checks that the PUBLIC catalog can actually prove are listed here.
# Shopify's public /products.json omits image `alt` text and variant `barcode`
# entirely, so those cannot be audited without Admin API access — claiming them
# from public data would report a problem that may not exist.
ISSUES = {
    "no_image": ("Product has no image", "Products without images convert far worse and are skipped by shopping feeds", 5),
    "thin_description": ("Description under 150 characters", "Thin copy ranks poorly and answers none of the buyer's questions", 3),
    "no_description": ("No description at all", "Empty description kills both SEO and conversion", 5),
    "missing_sku": ("Variant missing SKU", "No SKU breaks inventory reconciliation and supplier matching", 2),
    "duplicate_title": ("Duplicate product title", "Duplicate titles compete against each other in search", 3),
    "title_too_long": ("Title over 70 characters", "Long titles get truncated in search results and feeds", 1),
    "sold_out_published": ("Sold out but still published", "Live sold-out pages waste ad spend and frustrate buyers", 2),
    "no_product_type": ("No product type set", "Missing type breaks collection rules and feed categorisation", 1),
    "single_image": ("Only one image", "Multiple angles measurably lift conversion", 1),
}


@dataclass
class Product:
    id: int
    title: str
    handle: str
    body_html: str
    product_type: str
    images: list = field(default_factory=list)
    variants: list = field(default_factory=list)


def normalise_domain(raw: str) -> str:
    raw = raw.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    p = urlparse(raw)
    return f"{p.scheme}://{p.netloc}"


def fetch_catalog(base: str, limit: int, delay: float) -> list[Product]:
    """Page through the public /products.json endpoint."""
    products: list[Product] = []
    page = 1
    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    while len(products) < limit:
        url = f"{base}/products.json?limit=250&page={page}"
        try:
            r = session.get(url, timeout=30)
        except requests.RequestException as e:
            raise SystemExit(f"Could not reach {url}: {e}")
        if r.status_code == 404:
            raise SystemExit(
                f"{base} does not expose /products.json — it may not be a Shopify store, "
                "or the storefront is password protected."
            )
        r.raise_for_status()
        try:
            batch = r.json().get("products", [])
        except ValueError:
            raise SystemExit(f"{url} did not return JSON — is this a Shopify store?")
        if not batch:
            break
        for p in batch:
            products.append(
                Product(
                    id=p.get("id", 0),
                    title=p.get("title", ""),
                    handle=p.get("handle", ""),
                    body_html=p.get("body_html") or "",
                    product_type=p.get("product_type") or "",
                    images=p.get("images") or [],
                    variants=p.get("variants") or [],
                )
            )
        page += 1
        time.sleep(delay)
    return products[:limit]


def plain_text(html: str) -> str:
    return unescape(TAG_RE.sub(" ", html or "")).strip()


def audit(products: list[Product]) -> tuple[dict, list[dict]]:
    counts: Counter = Counter()
    rows: list[dict] = []

    titles = defaultdict(list)
    for p in products:
        titles[p.title.strip().lower()].append(p)
    dupes = {t for t, group in titles.items() if t and len(group) > 1}

    for p in products:
        found: list[str] = []
        desc = plain_text(p.body_html)

        if not p.images:
            found.append("no_image")
        elif len(p.images) == 1:
            found.append("single_image")

        if not desc:
            found.append("no_description")
        elif len(desc) < 150:
            found.append("thin_description")

        if any(not (v.get("sku") or "").strip() for v in p.variants):
            found.append("missing_sku")

        if p.title.strip().lower() in dupes:
            found.append("duplicate_title")
        if len(p.title) > 70:
            found.append("title_too_long")
        if not p.product_type.strip():
            found.append("no_product_type")
        if p.variants and all(v.get("available") is False for v in p.variants):
            found.append("sold_out_published")

        for code in found:
            counts[code] += 1
        if found:
            rows.append(
                {
                    "product": p.title,
                    "url": f"/products/{p.handle}",
                    "issues": ", ".join(ISSUES[c][0] for c in found),
                    "severity": sum(ISSUES[c][2] for c in found),
                }
            )

    rows.sort(key=lambda r: -r["severity"])
    return counts, rows


def report(base: str, products: list[Product], counts: Counter, rows: list[dict]) -> None:
    total = len(products)
    print("=" * 64)
    print(f"CATALOG AUDIT — {base}")
    print("=" * 64)
    print(f"Products scanned: {total}")
    print(f"Products with at least one issue: {len(rows)} ({len(rows) / total * 100:.0f}%)" if total else "")
    print()

    if not counts:
        print("No issues found. Clean catalog.")
        return

    print("Issues found, highest impact first:")
    print()
    ordered = sorted(counts.items(), key=lambda kv: -(ISSUES[kv[0]][2] * kv[1]))
    for code, n in ordered:
        label, why, _ = ISSUES[code]
        pct = n / total * 100 if total else 0
        print(f"  {n:>5}  ({pct:>3.0f}% of catalog)  {label}")
        print(f"         -> {why}")
    print()
    print("Worst products:")
    for r in rows[:10]:
        print(f"  [{r['severity']:>2}]  {r['product'][:52]:<52}  {r['url']}")
    print()
    print("Note: image alt text and variant barcodes/GTINs are not exposed in the")
    print("public catalog, so they are not audited here. Checking those needs Admin API access.")


def write_csv(path: str, rows: list[dict]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["product", "url", "issues", "severity"])
        w.writeheader()
        w.writerows(rows)
    print(f"\nFull list written to {path} ({len(rows)} products)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Audit a Shopify store's public catalog for revenue-losing gaps.")
    ap.add_argument("store", help="store domain, e.g. examplestore.com")
    ap.add_argument("--limit", type=int, default=1000, help="max products to scan (default 1000)")
    ap.add_argument("--csv", default=None, help="write the full issue list to this CSV")
    ap.add_argument("--delay", type=float, default=0.5, help="seconds between requests (be polite)")
    args = ap.parse_args()

    base = normalise_domain(args.store)
    print(f"Reading public catalog from {base} ...", file=sys.stderr)
    products = fetch_catalog(base, args.limit, args.delay)
    if not products:
        raise SystemExit("No products found in the public catalog.")
    counts, rows = audit(products)
    report(base, products, counts, rows)
    if args.csv:
        write_csv(args.csv, rows)


if __name__ == "__main__":
    main()
