English | [简体中文](README.zh-CN.md)

> **Note:** This repository contains a skill for Claude. For information about the Agent Skills standard, see [agentskills.io](https://agentskills.io).

# rental-search

A skill that helps Claude find a rental home to live in, and decide **which listings to contact first**. It searches the listing sites in your own browser, opens every listing, measures the real commute at rush hour, works out the true monthly cost, checks that each listing is still available and not a scam, and hands over a ranked table, a spreadsheet and a web page in your language. It drafts messages to landlords but never sends them, applies or pays.

The repository ships the same skill in two languages: `skills/rental-search` (English instructions) and `skills/rental-search-zh` (Chinese instructions). Install one of them. Either one answers in the language you write in.

## What the skill does

| Problem | What the skill does |
|---|---|
| The same unit is on several sites at different prices, mixed with rooms, offices and other towns | Opens every candidate, merges duplicates, keeps one row with every link |
| Listings go stale; last week's shortlist is half gone | Re-checks every listing before each report and lists what is gone, with the evidence |
| "Furnished", "utilities included" and "parking" mean different things in different places on the page | Reads the unit's own page, flags contradictions, and marks anything unstated as "not stated" |
| Listing pages guess the commute | Measures each listing in Google Maps at your departure time and compares the slow end of the range with your limit |
| Rent alone misleads | Adds utilities, parking, pet fees and one-time fees into a true monthly cost |
| Scams look like the best deal | Screens with a checklist (price far below market, off-platform contact, money before a viewing, landlord abroad) |

Three modes: **Quick** (rank listings you paste), **Standard** (search a city) and **Watch** (report what changed since the last check).

## What it will not do

- Contact landlords, book viewings, submit applications or pay. It drafts; you send.
- Sign in or create accounts for you. Sites that need a sign-in (Facebook Marketplace) use the session already open in your browser.
- Get around CAPTCHAs or bot checks, or bulk-download listing data. It browses at a person's pace and skips sites that block automated browsing.
- Buying property, commercial or office leases, nightly vacation stays, tenancy disputes.

## Regions

| Region | Status |
|---|---|
| British Columbia, Canada (Kelowna, Vancouver) | Full search in Kelowna on 2026-11-06: Kijiji, Craigslist, Facebook Marketplace, liv.rent, Zumper / PadMapper, rentals.ca, each rule dated. Vancouver search pages checked on 2026-11-06. |
| Ontario, Canada (Toronto) | Search pages checked on 2026-11-06. Ontario tenancy rules (rent deposit only, no damage or pet deposits, standard lease) from official pages. |
| United States (Seattle, SF Bay Area, Los Angeles, New York City, Austin) | Zillow, HotPads, Apartments.com, StreetEasy, Furnished Finder, Zumper and Craigslist search pages checked on 2026-11-06. State and city rules (deposit caps, fees, the NYC FARE Act, Seattle move-in limits, short-term rental rules) from official pages. |
| Everywhere else | No pack. The skill finds the local sites, asks you to confirm the list, looks up the local rules on official pages, labels the results, and offers to write a new pack afterwards. |

Packs other than Kelowna were checked lightly (search pages load, rules from official sources) rather than in a full search.

## Requirement modules

Besides the base questions (city, commute, budget, move-in, lease, household, unit type), the skill turns on modules when your request needs them:

| Module | Adds |
|---|---|
| Pets | Pet policy per listing, weight and breed limits, pet deposits and fees |
| Business or relocation | Receipts or invoices for reimbursement, company payment, minimum stay, internet and a desk |
| Furnished | What the furniture really is (kitchenware, bedding) |
| Parking and EV | Stalls included or extra, EV charging |
| Family and children | Bedrooms, school catchment, parks |
| Accessibility | Elevator, ground floor, step-free entry |
| Shared housing | Private bathroom, who else lives there, sublets |
| Short and mid-term | Exact dates, sublet permission, original lease end |

## Outputs

`scripts/build_outputs.py` turns the listing records into:

- an `.xlsx` workbook with one sheet per group (in budget, over budget, gone and excluded) and a settings sheet whose budget and commute limit drive the formulas;
- a `.csv` of every listing;
- a web page that follows light or dark mode, works at phone width, and can be published as a Claude artifact or opened locally.

Labels come in English and Chinese; other languages work by passing translations in the data file. Try it on the invented sample:

```
python skills/rental-search/scripts/build_outputs.py examples/sample-listings.json --out examples/out
```

## Install

- **Claude Code**: `/plugin marketplace add ArthurDJ/rental-search`, then `/plugin install rental-search@rental-search` (or `rental-search-zh@rental-search`).
- **Claude.ai**: download one skill folder as a zip and upload it under Settings → Capabilities → Skills.
- **Other agents** that read Agent Skills: copy one folder from `skills/`.

The skill works best with a browser tool (Claude in Chrome or a similar browser extension) and Python with `openpyxl` for the workbook. Without a browser it works from listings you paste and labels them as not re-checked.

## Repository layout

```
skills/rental-search/          English skill (SKILL.md, references/, scripts/, assets/)
skills/rental-search-zh/       Chinese skill, same structure
evals/                         14 behavior cases and 24 trigger queries
examples/sample-listings.json  Invented sample data for the output script
scripts/                       Repository checks (parity, validation)
```

## Contributing

- Site rules go out of date. If a rule in a region pack no longer works, open a "Rule out of date" issue with the site, the rule and the date you checked.
- New region packs are welcome. Follow `references/regions-other.md` → Writing a new pack, leave out anyone's personal details, and change the English and Chinese skills together.
- Before a pull request, run `python scripts/check_parity.py` and `python scripts/validate_skills.py`.

## License

MIT. See [LICENSE](LICENSE).
