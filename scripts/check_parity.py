#!/usr/bin/env python3
"""Check that the English and Chinese versions of the skill, and the three
READMEs, say the same thing structurally.

For every pair of files it compares:
  1. the sequence of heading levels (headings inside code fences are ignored);
  2. every number in each section (amounts, percentages, durations, times,
     dates, rule numbers), as a multiset per section, so word order may differ
     between languages but no number may be added, dropped or changed;
  3. in the skill files, cross-references written as
     `references/<file>.md` -> <Section name> (or `SKILL.md` -> <Section name>):
     each must name a heading that exists in the target file of the same
     language, and both languages must have the same number of them.

Pairs checked:
  skills/rental-search/**.md  <->  skills/rental-search-zh/**.md
  README.md  <->  README.zh-CN.md

Write dates as YYYY-MM-DD and numbers as digits in every language, so that
"6 zones" and "6 个时区" compare equal.

Usage: python scripts/check_parity.py [repo_root]
Exit status: 0 if everything matches, 1 if anything differs.
"""
import re
import sys
from collections import Counter
from pathlib import Path

EN_SKILL = Path("skills/rental-search")
ZH_SKILL = Path("skills/rental-search-zh")
READMES = ["README.md", "README.zh-CN.md"]

HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")
NUMBER = re.compile(r"\d+(?:[.:]\d+)*")
THOUSANDS = re.compile(r"(?<=\d),(?=\d{3}\b)")
XREF = re.compile(
    r"`((?:references/)?[\w.-]+\.md)`\s*→\s*"
    r"([^,.;:|()\[\]\n，。；：、（）「」“”\"]+)"
)


def sections(text):
    """Split into sections at headings outside code fences.

    Returns (levels, sections) where sections[0] is the text before the first
    heading and sections[i] (i >= 1) belongs to the i-th heading.
    """
    levels, titles, chunks = [], [], [[]]
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
        m = None if in_fence else HEADING.match(line)
        if m:
            levels.append(len(m.group(1)))
            titles.append(m.group(2))
            chunks.append([line])
        else:
            chunks[-1].append(line)
    return levels, titles, ["\n".join(c) for c in chunks]


def numbers(text):
    return Counter(NUMBER.findall(THOUSANDS.sub("", text)))


def heading_names(path):
    _, titles, _ = sections(path.read_text(encoding="utf-8"))
    names = []
    for t in titles:
        t = re.sub(r"^\d+\.\s*", "", t)  # drop "3. " numbering
        names.append(t.strip().lower())
    return names


def fmt(counter):
    return ", ".join(f"{k}×{v}" if v > 1 else k for k, v in sorted(counter.items()))


def compare(a_path, b_path, problems):
    a_text = a_path.read_text(encoding="utf-8")
    b_text = b_path.read_text(encoding="utf-8")
    a_lv, a_ti, a_sec = sections(a_text)
    b_lv, b_ti, b_sec = sections(b_text)
    label = f"{a_path.as_posix()} <-> {b_path.as_posix()}"
    if a_lv != b_lv:
        problems.append(f"{label}: heading structure differs\n"
                        f"    {len(a_lv)} headings {a_lv}\n"
                        f"    {len(b_lv)} headings {b_lv}")
        return
    for i, (sa, sb) in enumerate(zip(a_sec, b_sec)):
        na, nb = numbers(sa), numbers(sb)
        if na != nb:
            where = "preamble" if i == 0 else f"section '{a_ti[i - 1]}' / '{b_ti[i - 1]}'"
            only_a, only_b = na - nb, nb - na
            problems.append(f"{label}: numbers differ in {where}\n"
                            f"    only in {a_path.as_posix()}: {fmt(only_a) or '-'}\n"
                            f"    only in {b_path.as_posix()}: {fmt(only_b) or '-'}")


def check_xrefs(skill_dir, path, problems):
    text = path.read_text(encoding="utf-8")
    refs = XREF.findall(text)
    for target, name in refs:
        name = name.strip()
        tpath = skill_dir / target
        if not tpath.exists():
            problems.append(f"{path.as_posix()}: cross-reference to missing file {target}")
            continue
        names = heading_names(tpath)
        if not any(h.startswith(name.lower()) for h in names):
            problems.append(f"{path.as_posix()}: '{target} → {name}' names no heading in {target}")
    return len(refs)


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    root =Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
    problems, pairs = [], 0
    en_files = sorted(p.relative_to(root / EN_SKILL) for p in (root / EN_SKILL).rglob("*.md"))
    zh_files = sorted(p.relative_to(root / ZH_SKILL) for p in (root / ZH_SKILL).rglob("*.md"))
    for missing in sorted(set(en_files) ^ set(zh_files)):
        side = "Chinese" if missing in en_files else "English"
        problems.append(f"{missing.as_posix()}: missing in the {side} skill")
    for rel in sorted(set(en_files) & set(zh_files)):
        a, b = root / EN_SKILL / rel, root / ZH_SKILL / rel
        compare(a, b, problems)
        pairs += 1
        na = check_xrefs(root / EN_SKILL, a, problems)
        nb = check_xrefs(root / ZH_SKILL, b, problems)
        if na != nb:
            problems.append(f"{rel.as_posix()}: {na} cross-references in English, {nb} in Chinese")
    base = root / READMES[0]
    for other in READMES[1:]:
        o = root / other
        if not o.exists():
            problems.append(f"{other}: missing")
            continue
        compare(base, o, problems)
        pairs += 1

    # Show paths relative to the repo root.
    prefix = root.as_posix().rstrip("/") + "/"
    problems = [p.replace(prefix, "") for p in problems]
    if problems:
        print(f"PARITY CHECK FAILED: {len(problems)} problem(s) in {pairs} file pair(s)")
        for p in problems:
            print(" - " + p)
        return 1
    print(f"Parity OK: {pairs} file pairs (skill en/zh, README en/zh-CN): "
          "heading structure, numbers per section and cross-references match.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
