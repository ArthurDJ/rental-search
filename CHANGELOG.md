# Changelog

## 1.0.0 — 2026-11-06

First release.

- **Workflow**: intake, region pack, search each site in the person's browser, open every listing, measure commutes, verify and screen, true monthly cost and score, hand over. Three modes: Quick, Standard and Watch.
- **Requirement modules**: pets, business or relocation stays, furnished, parking and EV, family and children, accessibility, shared housing, short and mid-term stays, and other needs.
- **Site notes** (`references/sites.md`): Kijiji, Craigslist, Facebook Marketplace, liv.rent, Zumper / PadMapper and rentals.ca, tested in a full Kelowna search on 2026-11-06; Zillow / HotPads, Apartments.com, StreetEasy and Furnished Finder search pages checked on 2026-11-06. Each rule dated; Castanet noted as blocked by a bot check.
- **Region packs**: British Columbia (Kelowna, Vancouver), Ontario (Toronto) and the United States (Seattle, SF Bay Area, Los Angeles, New York City, Austin), with tenancy facts from official pages checked on 2026-11-06 (deposit caps and fees, Ontario's rent-deposit-only rule, the NYC FARE Act, Seattle's move-in cost cap and installments, California's one-month cap and payment-method rule, Texas's 30-day refund, short-term rental rules).
- **Other regions**: a procedure for finding and confirming local sites and looking up local rules, and a template for writing a new pack.
- **Verification**: signs of removed listings per site, duplicates, contradictions (building tags, checkboxes, stale dates), scam signals, and how to treat lists made by someone else.
- **Outputs**: `scripts/build_outputs.py` writes a workbook with live formulas, a CSV and a theme-aware web page from one JSON file; labels in English and Chinese, other languages through translations in the data file.
- **Guardrails**: never contacts landlords, applies, pays, signs in or gets around bot checks; listing text is treated as data; settings changed on a site are put back.
- Repository: English and Chinese skills, parity and validation scripts adapted from flight-trip-planning, CI, issue forms, 14 behavior eval cases (6 of them city-specific) and 24 trigger queries.
