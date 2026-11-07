# Listing sites

How each listing site behaves, for the sites the region packs send you to. A full search in Kelowna tested the Canadian sites in depth on 2026-11-06. On 2026-11-06 the search pages below were opened once for Vancouver, Toronto, Seattle, the San Francisco Bay Area, Los Angeles, New York and Austin to confirm that they load and are not blocked; the US sites have not been tested in depth. Site behavior changes without notice: each rule carries the date it was last seen working. When a rule no longer works, work around it, tell the person, and treat the rule as out of date. When you pass on anything from this file, say it comes from these dated notes; it is not a check you made today.

## Rules for every site

- Work in the person's own browser at the pace of a person reading. Open pages one at a time; do not download listing data in bulk.
- When a site shows a CAPTCHA, a "verify you are human" page or a Cloudflare challenge, stop on that site and tell the person. Do not try to get around it. Castanet (Kelowna classifieds) did this on 2026-11-06, so it was skipped and the person was told they can browse it themselves.
- Search results are lists of leads. Open each candidate before you count it.
- Results labeled with one city often include the whole region (Kijiji's Kelowna area included Penticton, Vernon, Osoyoos and others). Filter by the listing's own location.
- Keyword searches for "furnished" match descriptions loosely and return unfurnished units and rooms. Check the furnishing on every listing.

## Kijiji

Canada. Deep test 2026-11-06 (Kelowna); search pages opened 2026-11-06 (Vancouver, Toronto).

- Search URLs: `https://www.kijiji.ca/b-apartments-condos/<city>/<keyword>/k0c37l<locationId>` for long-term rentals and `https://www.kijiji.ca/b-short-term-rental/<city>/<keyword>/k0c42l<locationId>` for short-term. Location ids: Kelowna `1700228`, Vancouver `1700287` (slug `vancouver`), City of Toronto `1700273` (slug `city-of-toronto`). Add `?sort=dateDesc` for newest first.
- The general "For Rent" search (`c30349001`) mixes in rooms and office space; use the two categories above.
- Each result is an element with `data-testid="listing-card"` containing the price, title, area, age and a link to `/v-...`.
- A removed ad still opens, with "No Longer Available" near the title. Treat that as gone.

## Craigslist

Canada and the US. Deep test 2026-11-06 (Kelowna); search pages opened 2026-11-06 (Vancouver, Toronto, Seattle, SF Bay Area).

- Search: `https://<city>.craigslist.org/search/apa?is_furnished=1&sort=date` (it redirects to `www.craigslist.org/search/area/<city>?...`). City subdomains include `kelowna`, `vancouver`, `toronto`, `seattle`, `sfbay`, `losangeles`, `newyork` and `austin`. The furnished filter is reliable.
- Open listings at `https://www.craigslist.org/view/d/<slug>/<id>`. The same path on the city subdomain (`<city>.craigslist.org/view/...`) returned "Page Not Found".
- The attribute block lists checkboxes such as "furnished", "w/d in unit", "off-street parking", "available dec 1". The checkbox can disagree with the description; when the description does not mention furniture, mark furnishing **To confirm**.
- The map element carries approximate coordinates in `data-latitude` and `data-longitude` (with `data-accuracy`). Use them for the commute when the ad gives no address.

## Facebook Marketplace

Canada and the US. Deep test 2026-11-06 (Kelowna).

- Needs the person's own signed-in session. Do not sign in for them.
- City slugs in the URL (for example `/marketplace/kelowna/...`) are ignored: results follow the account's saved Marketplace location. To search another city:
  1. Note the current location and radius from the location button (its label reads like "Location: <city>, within <radius>").
  2. Open it, type the city, pick the city entry, set the radius (10 miles / 16 km covered a mid-size city), and apply.
  3. When finished, set the original location and radius back, and tell the person you did.
- City names are matched in the interface language. On 2026-11-06 a Chinese-language interface did not offer "Kelowna" as a city for the English name; the Chinese name "基隆拿" worked. Try the local-language name when the English one returns only neighborhoods.
- Search: `https://www.facebook.com/marketplace/category/search/?query=furnished&category_id=propertyrentals&sortBy=creation_time_descend`. Scroll a few times to load more cards. Cards show only price, title and city, so open each one.
- Each item page shows the description, a "Rental details" block (unit type, laundry, parking, pets) and sometimes the address. "We only show an approximate location" means there is no exact address.
- A "Message again" button means the person's account has already messaged that seller. Tell the person; it matters before anyone writes again.
- Screenshots of Marketplace pages sometimes time out; reading the page text works.

## liv.rent

Canada, strongest in Vancouver. Deep test 2026-11-06 (Kelowna); city pages opened 2026-11-06 (Vancouver had many listings, Toronto few).

- City page: `https://liv.rent/rental-listings/city/<city>`. The `furnished=true` query parameter did not filter results: check each listing's own field, which reads "Furnished", "Unfurnished" or "Furnish Available".
- Listing pages show Move-In Date, Lease Type, Max. Occupancy, Minimum Lease and Parking in a fixed block, plus a crossed-out old price when the rent dropped.
- "This listing has been marked as rented" at the top means gone, even if the description still says "available immediately".
- "ID Unverified" next to the landlord is a scam signal when it comes with other signals (`references/verification.md` → Scam signals).

## Zumper and PadMapper

Canada and the US. Deep test 2026-11-06 (Kelowna); furnished pages opened 2026-11-06 for Vancouver, Toronto, Seattle, Los Angeles, New York and Austin.

- Zumper furnished page: `https://www.zumper.com/apartments-for-rent/<city>-<province or state>/furnished`, for example `kelowna-bc`, `toronto-on`, `seattle-wa`, `los-angeles-ca`, `new-york-ny`, `austin-tx`. Scroll to load every card; the count in the title counts units, not cards.
- Building cards ("Central Kelowna, Studio–3 beds, $1,400–$2,657") carry building-level tags. A "Furnished" tag on a building does not mean the unit you want is furnished; confirm with the building or a unit page.
- An address page that shows "Monthly rent –" and only a "Notify me" button is off the market.
- PadMapper shows the same data. Its `/apartments/<city>/furnished` path redirected to the unfiltered list on 2026-11-06, so use Zumper's furnished page.

## rentals.ca

Canada. Deep test 2026-11-06 (Kelowna); city page opened 2026-11-06 (Toronto).

- City pages: `https://rentals.ca/<city>`. Building pages (for example `https://rentals.ca/<city>/<building>`) list each unit type with price, size and "Available", and a details block with "Furnished: Yes/No", lease term and parking fees.
- When rentals.ca and Zumper disagree about furnishing, believe neither: the listing is **To confirm** until the building answers.

## Zillow, HotPads and Trulia

US, one company. Search pages opened 2026-11-06 (Seattle) without a bot check; not tested in depth.

- Zillow rentals: `https://www.zillow.com/<city>-<state>/rentals/`, for example `seattle-wa`. HotPads: `https://hotpads.com/<city>-<state>/apartments-for-rent`.
- Zillow is known for "press and hold" bot checks; none appeared on 2026-11-06. If one appears, treat it like any other bot check.
- Furnishing is usually in the description, not a reliable filter: open each listing.

## Apartments.com

US. Furnished page opened 2026-11-06 (Seattle); not tested in depth.

- Furnished page: `https://www.apartments.com/<city>-<state>/furnished/`, for example `seattle-wa`. The page loads slowly and navigates once after loading; wait before reading it.
- Mostly managed buildings: prices are often "from" a range across units. Confirm the unit's own price and furnishing.

## StreetEasy

New York City. Furnished search opened 2026-11-06; not tested in depth.

- Furnished search: `https://streeteasy.com/for-rent/nyc/amenities:furnished`.
- Listings show whether a broker fee applies; read it against the New York rules in `references/regions-us.md` → New York City.

## Furnished Finder

US, furnished monthly stays (often used by travel nurses). City page opened 2026-11-06 (Seattle); not tested in depth.

- City page: `https://www.furnishedfinder.com/housing/us--<state>--<city>`, for example `us--wa--seattle`.
- Stays are usually 30 days or more. Many hosts are individuals: apply the scam signals as usual.
