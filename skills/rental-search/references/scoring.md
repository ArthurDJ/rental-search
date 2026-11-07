# Commute, cost and scoring

## Commute

Measure every candidate with a map tool at the hour the person actually travels. Listing pages and straight-line distances are not commute times.

### With Google Maps in a browser

1. Use the next normal weekday (not a holiday), at the person's departure time.
2. A directions link can carry the departure time, which saves clicking through the "Depart at" menu:

   `https://www.google.com/maps/dir/<origin>/<destination>/data=!4m6!4m5!2m3!6e0!7e2!8j<seconds>!3e0`

   - `<origin>` and `<destination>`: an address with city and province, spaces as `+`, or `lat,lng`.
   - `6e0` means "depart at"; `6e1` means "arrive by".
   - `8j<seconds>`: the local clock time written as if it were UTC, in seconds since 1970. For 08:15 on 2026-11-09, that is the UTC timestamp of `2026-11-09T08:15:00Z`, which is 1794212100. In Python: `int(datetime(2026, 11, 9, 8, 15, tzinfo=timezone.utc).timestamp())`.
   - `3e0` driving, `3e1` bicycling, `3e2` walking, `3e3` transit.
3. Read the route list. Driving shows "typically 8–14 min" for a future time. Record the fastest route's range and distance. Transit shows a duration per option; record the fastest that leaves after the departure time.
4. Check that the origin Maps resolved is the right one (it shows the full address in the starting-point box). A business name can appear when you give coordinates; that is fine if the point is right.

The page text can be read with a script instead of screenshots, which is faster when there are many listings: each route block contains "typically", the range, the distance and "via <road>".

### Listings without an exact address

- Use the coordinates the site gives (Craigslist puts them on the map element; see `references/sites.md` → Craigslist), the postal code, or the nearest intersection named in the ad.
- Label the result "approximate location".
- When there is nothing to go on, mark the commute "not measured" and say why.

### Against the limit

Compare the **slow end** of the range with the limit. "12–22 min" against a 20-minute limit is a fail on bad days, so the listing is **To confirm** at best, and the table shows it in the warning color. Say how many days a week the person travels if it changes the call.

### Without a map tool

Estimate: straight-line distance × 1.35 ÷ 40 km/h for city driving, and label it "estimate, not measured". Tell the person which listings most need a real measurement (the ones close to the limit).

## True monthly cost

Rent alone misleads: "$1,450 all utilities included with parking" can cost less than "$1,400 plus utilities, parking $100".

```
true monthly cost = rent
                  + utilities not included (electricity, heat, water, internet; estimate if not stated)
                  + parking or storage fees
                  + pet fees (if the pets module is on)
                  + one-time non-refundable fees ÷ lease months (move-in fee, admin fee)
                  − free rent ÷ lease months (for example "first month free on a 12-month lease")
```

- Deposits are refundable, so they are not a monthly cost. List them separately, since they affect cash needed at move-in.
- Label every estimated part, for example "electricity est. $60 (not stated)". Use local typical figures when known and write the source.
- When the person has not decided on the lease length, use 12 months and say so.

## Scoring

Hard filters first, then a score to order what passes.

### Hard filters

From the intake: city or areas, unit type, must-haves, the commute limit (slow end), the pet policy if pets are on, and the move-in date if the person has a fixed one. A listing that fails a hard filter is **Fails**, with the reason. When the page does not say, the listing is **To confirm**, not Fails.

### Score

Default weights, which the person can change:

| Part | Weight | How |
|---|---|---|
| Price | 40% | True monthly cost against the budget; at or under the target scores best, falling to zero at the stated maximum (or 30% above the target if no maximum) |
| Commute | 20% | Slow end of the range; 0 at the limit |
| Unit fit | 15% | Room count and size for the household |
| Amenities | 15% | Laundry, parking, furnishing and the nice-to-haves from the intake |
| Lease fit | 10% | Matches the wanted length and flexibility, and the move-in date |

When a module is on, give its checks part of the Amenities weight, or ask the person whether it should count more (for example, a company-paid stay may care most about receipts and lease terms).

### Statuses

| Status | Meaning |
|---|---|
| **Meets** | Passes every hard filter on the evidence of the page |
| **To confirm** | Nothing fails, but at least one hard filter depends on something not stated or contradictory |
| **Fails** | Fails at least one hard filter; say which |

Gone listings and suspected scams go to a separate list with the evidence (`references/verification.md`).

### Explaining the order

For each of the top 3, give two or three plain reasons and the first question to ask the landlord. For listings that look good but rank lower, one line on what held them back ("no parking", "studio", "22 minutes on bad days").
