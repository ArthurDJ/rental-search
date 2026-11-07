# Outputs

## Language

Write everything for the person (the summary, the table, the workbook, the page) in the language they wrote in, unless they ask for another. Keep proper names, addresses and site names as they appear on the listing. Messages to landlords default to the language of the listing (English for most North American listings), whatever language the person uses with you; show the person a translation beside the draft when it helps them check it.

## What to hand over

In this order:

1. **Two lines on what changed**, if this updates an earlier search: listings gone, new ones, price changes, corrections to the earlier list.
2. **Top 3**, each with the rent and true monthly cost, the measured commute, two or three reasons, and the first thing to ask the landlord. If nothing meets every hard filter, say so and show the best **To confirm** listings instead.
3. **The full table** of active listings, grouped by status or by budget, with links.
4. **Gone and excluded**, each with the evidence ("Kijiji: No Longer Available", "commute 18–35 min", "suspected scam: …").
5. **How it was done**, short: the sites searched, the sites skipped and why, how commutes were measured, the date and time checked, and any setting changed and put back.
6. **Files**: the workbook, the CSV and the page, from `scripts/build_outputs.py`.

Keep the chat answer short when there are files: the top 3, the changes, and where the files are.

## Listing records

`scripts/build_outputs.py` reads one JSON file. Write it as you go, one record per listing. Use `null` for anything the page does not state; the outputs show it as "not stated" in the person's language.

```json
{
  "meta": {
    "title": "Furnished rentals, Kelowna",
    "language": "en",
    "currency": "CAD",
    "checked_at": "2026-11-06 21:00",
    "budget_target": 1500,
    "budget_max": null,
    "commute_limit_min": 20,
    "commute_anchor": "Downtown office",
    "commute_basis": "Driving, Monday 08:15, Google Maps typical range",
    "move_in": "around 2026-12-01",
    "household": "2 adults",
    "modules": ["furnished"],
    "extra_columns": [{"key": "pets", "label": "Pets"}],
    "sites": ["Kijiji", "Craigslist", "Facebook Marketplace", "liv.rent", "Zumper", "rentals.ca"],
    "method": ["One line per step of how the search was done"],
    "notes": ["Corrections to an earlier list, caveats"]
  },
  "picks": [
    {"id": "cl-1br-ellis", "reasons": ["5 min to the office", "furnished, in-suite laundry"], "ask": "Exact address, move-in date, utilities"}
  ],
  "listings": [
    {
      "id": "cl-1br-ellis",
      "name": "Downtown 1 bedroom, Ellis St",
      "status": "meets",
      "rent": 1575,
      "rent_note": null,
      "true_cost": 1635,
      "true_cost_note": "electricity est. $60 (not stated)",
      "bedrooms": 1,
      "unit_type": "1 bed, 1 bath",
      "size_sqft": 760,
      "commute_min": 5,
      "commute_max": 5,
      "furnished": "Yes (listing checkbox)",
      "laundry": "In-suite washer and dryer",
      "parking": "Detached garage",
      "utilities": null,
      "move_in": null,
      "lease": null,
      "extra": {"pets": "Cats and dogs OK"},
      "is_new": true,
      "source": "Craigslist",
      "url": "https://www.craigslist.org/view/d/...",
      "note": "Posted 2026-10-23",
      "reason": null
    }
  ]
}
```

- `status`: `meets`, `confirm`, `fails`, `gone` or `excluded`. `reason` is required for `fails`, `gone` and `excluded`.
- `bedrooms`: `0` for a studio, `null` if unknown. The page uses it for the unit-type filter.
- `commute_min` and `commute_max`: minutes, the fastest route's range; equal when Maps gives one number; `null` when not measured, with the reason in `note`.
- `true_cost`: from `references/scoring.md` → True monthly cost; leave `null` rather than guess when too much is unknown.
- `extra`: values for `meta.extra_columns`, which the modules add (pets, receipts, minimum stay and so on).
- `is_new`: new since the last check (or since the list the person brought).

Run:

```
python scripts/build_outputs.py listings.json --out <folder> [--name rentals]
```

It writes `<name>.xlsx` (needs `openpyxl`; skipped with a message if missing), `<name>.csv` and `<name>.html`. The workbook has one sheet per group and a settings sheet whose budget and commute limit drive the "vs budget" and "commute OK" formulas. The page uses `assets/page_template.html` and follows the viewer's light or dark theme. It works at phone width.

## Landlord messages

Only when the person asks, and always as drafts.

- One message per listing, short, in the listing's language.
- Who is asking (without details the person has not agreed to share), the move-in date, the lease length, the household, and the two or three questions that decide whether this listing works (often: is it still available, exact address, what is included, furniture list, pets, parking).
- No promises the person has not made (income, credit, references), no request to hold the unit, no payment talk.
- End with how to reach the person, using a placeholder like `[your phone or email]` unless they gave you what to use.

Example:

> Hi, is the furnished 1-bedroom on [street] still available for a December 1 move-in? We are two working adults, non-smokers, looking for a 12-month lease. Could you tell me the exact address, which utilities are included, and whether a parking stall comes with it? We would like to arrange a viewing. Thanks, [name], [your phone or email]
