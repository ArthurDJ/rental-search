## What changed

<!-- What the skill now does differently, and why. Link the issue if there is one. -->

## Checklist

Tick what applies; strike through or delete lines that do not, and say why.

- [ ] The English (`skills/rental-search`) and Chinese (`skills/rental-search-zh`) skills are changed together, and so are `README.md` and `README.zh-CN.md`
- [ ] `scripts/build_outputs.py` and `assets/page_template.html` are identical in both skill folders
- [ ] `python scripts/check_parity.py` passes
- [ ] `python scripts/validate_skills.py` passes
- [ ] Every site rule has a "Last checked" date, and every tenancy fact cites an official source
- [ ] No personal details (names, addresses, workplaces, budgets, specific people's listings) are added
- [ ] `CHANGELOG.md` has an entry
- [ ] If behavior changes (the same input can get a different answer): version bumped in `metadata.version` of both SKILL.md files and in `.claude-plugin/marketplace.json`
- [ ] A relevant eval case in `evals/` is added or updated (or `evals/trigger-queries.json`, for description changes)
