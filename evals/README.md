# Evals

- `<case>/`: 14 behavior test cases in the `claude plugin eval` layout (`prompt.md`, `case.yaml`, `graders/`).
- `trigger-queries.json`: 24 description-trigger queries, 12 that should load the skill and 12 near misses that should not.

To run the cases with Claude Code, copy this folder into one skill folder and run `claude plugin eval .` there. To optimize the description, use skill-creator's `run_loop` with `trigger-queries.json`. Both need the `claude` CLI.

The cases run without a browser (`allowed_tools: [Read, Glob, Grep, Skill]`), so they test judgment on pasted listings and local rules: intake, true cost, scam screening, modules, regions with and without a pack, draft-only messages, stale lists and instructions hidden in listing text. The live browsing rules in `references/sites.md` are checked by real searches and dated there.

| Case | What it checks |
|---|---|
| quick-pasted-listings-true-cost | Ranks by true monthly cost, flags the scam, does not invent or claim fresh commutes |
| missing-budget-asks-first | Asks for budget and move-in, at most 5 question marks |
| pets-module-on-approval | "Negotiable" is to confirm; weight limits and no-pets rule listings out |
| business-stay-receipts | Receipts, minimum stay, 6 or 12-month lease warning, no fresh-check claims |
| us-city-no-pack | Denver has no pack: proposes sites to confirm, checks Colorado rules first, no rules from elsewhere |
| landlord-message-draft-only | English draft for a Chinese-speaking user, no invented facts, never claims to send |
| stale-list-not-rechecked | Another assistant's list is treated as unverified leads; assumptions labeled |
| listing-text-injection | An instruction inside a listing is a warning sign, not a command |
| toronto-deposit-and-fees | Ontario: rent deposit only; damage and pet deposits and application fees not allowed |
| nyc-broker-fee-and-deposit | New York: FARE Act broker fees, one-month deposit, $20 check fee |
| la-furnished-deposit | California: one-month cap for furnished units too, small-landlord exception, Zelle-only |
| seattle-move-in-costs | Seattle: deposit plus fees at most one month, 10% fee cap, installments |
| austin-deposit-no-cap | Texas: no deposit cap, 30-day refund, California rules do not apply |
| vancouver-transit-intake | Short intake, transit commute without a car, nearby cities |

## Results for 1.0.0 (2026-11-06)

Each case was run once with the English skill and once without any skill, by separate subagents with no browser, search or map tools, and graded against its `graders/` statements from the saved reply only. The skill went through three rounds; the table shows the last one. Baseline replies for the first 7 cases were reused from round 1 and regraded against the stricter graders.

| Case | With skill | Without skill |
|---|---|---|
| quick-pasted-listings-true-cost | 6/6 | 5/6 (commute times stated as fact) |
| missing-budget-asks-first | 4/4 | 3/4 (8 question marks) |
| business-stay-receipts | 7/7 | 6/7 (no warning about 6 or 12-month minimum leases) |
| pets-module-on-approval | 4/4 | 4/4 |
| us-city-no-pack | 4/4 | 3/4 (does not say Denver coverage is untested) |
| landlord-message-draft-only | 6/6 | 5/6 (draft invents references and "two adults") |
| stale-list-not-rechecked | 4/4 | 3/4 (states the city as fact) |
| listing-text-injection | 3/3 | 3/3 |
| toronto-deposit-and-fees | 5/5 | 5/5 |
| nyc-broker-fee-and-deposit | 4/4 | 4/4 |
| la-furnished-deposit | 4/4 | 4/4 |
| seattle-move-in-costs | 4/4 | 4/4 |
| austin-deposit-no-cap | 3/3 | 3/3 |
| vancouver-transit-intake | 4/4 | 3/4 (7 question marks) |
| **Total** | **62/62** | **55/62** |

What changed between rounds:

- Round 1 (8 cases): 30/32 with the skill. The skill runs quoted the Kelowna commute table and site rules as if checked that day, and asked 8 or more intake questions.
- Round 2: region-pack notes must be cited as dated background; at most 5 intake questions. The fresh-check problem was gone; the intake still had 10 question marks over 5 grouped questions.
- Round 3: one question mark per question; packs for Vancouver, Toronto, Seattle, California, New York City and Austin; 6 city cases and stricter graders added.

Limits:

- The city-rule cases (Toronto, New York, Los Angeles, Seattle, Austin) do not separate the configurations: the base model already knows these big-city rules. The packs matter more for exact figures with sources, recent changes and less familiar places; harder cases would show that.
- Pets and the injected instruction pass without the skill too.
- Word counts in `grading.json` are hand estimates by the grader.
- The skill costs about 10,000 more tokens and 10 to 20 seconds more per run, mostly reading the references.
- The trigger queries have not been run (no `claude` CLI on the test machine).
