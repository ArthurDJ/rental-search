#!/usr/bin/env python3
"""Validate the skills, the plugin marketplace and the evals in this repository.

Skills (every folder in skills/ and every path listed in marketplace.json):
  - SKILL.md starts with a YAML frontmatter block that parses;
  - only the fields the Agent Skills specification allows
    (https://agentskills.io/specification): name, description, license,
    compatibility, metadata, allowed-tools;
  - name: 1-64 characters, a-z, 0-9 and hyphens only, no leading, trailing or
    double hyphen, and the same as the folder name;
  - description: a non-empty string of at most 1024 characters, without
    angle brackets (skill-creator's quick_validate rejects them);
  - compatibility, if present: at most 500 characters;
  - metadata, if present: a map of string keys to string values
    (write version: "3.0.0", not version: 3.0);
  - license: present (required by this repository, optional in the spec), and
    any file it names, such as LICENSE.txt, exists in the skill folder;
  - every relative Markdown link, and every references/, scripts/ or assets/
    path mentioned in any .md file of the skill, exists inside the skill folder;
  - every file in references/ is mentioned in SKILL.md, so the agent can find it;
  - SKILL.md under 500 lines (a recommendation in the spec, so only a warning).

Marketplace (.claude-plugin/marketplace.json):
  - valid JSON with name, owner.name and a non-empty plugins list;
  - plugin names are unique and kebab-case; a local source path exists;
  - every skills path exists, stays inside the repository and contains SKILL.md;
  - every folder in skills/ is listed by some plugin.

Versions: metadata.version is the same in every SKILL.md and in
marketplace.json metadata.version, and CHANGELOG.md has a "## <version>" heading.

Evals (evals/):
  - every case folder has a non-empty prompt.md, a case.yaml whose name matches
    the folder and that has an expected_outcome, and at least one graders/*.md;
  - trigger-queries.json is a list of {"query": non-empty string,
    "should_trigger": true|false} with no duplicate queries.

Only the standard library is used. The frontmatter parser understands the
subset of YAML these files use (key: value, quoted strings, | and > block
scalars, one level of nested mapping) and reports anything else as an error
rather than guessing.

Usage: python scripts/validate_skills.py [repo_root]
Exit status: 0 if every check passes, 1 if any fails.
"""
import json
import re
import sys
from pathlib import Path

ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")  # also rules out leading/trailing/double hyphens
MAX_NAME, MAX_DESCRIPTION, MAX_COMPATIBILITY, MAX_LINES = 64, 1024, 500, 500
MD_LINK = re.compile(r"!?\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+[\"'][^)]*[\"'])?\s*\)")
SKILL_PATH = re.compile(r"(?<![\w/.-])((?:references|scripts|assets)/[\w./-]*\w\.\w+)")
URL_SCHEME = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
LICENSE_FILE = re.compile(r"\b(LICEN[CS]E(?:\.[A-Za-z]+)?|[\w-]+\.(?:txt|md))\b")


class YamlError(ValueError):
    pass


# ---------------------------------------------------------------- YAML subset

KEY_LINE = re.compile(r"^([A-Za-z0-9_][A-Za-z0-9_.-]*):(?:[ \t]+(.*?))?[ \t]*$")
INT_RE = re.compile(r"^[-+]?(?:0|[1-9]\d*|0o[0-7]+|0x[0-9a-fA-F]+)$")
FLOAT_RE = re.compile(r"^[-+]?(?:\.\d+|\d+\.\d*|\d+)(?:[eE][-+]?\d+)?$|^[-+]?\.(?:inf|Inf|INF)$|^\.(?:nan|NaN|NAN)$")


def _indent(line):
    return len(line) - len(line.lstrip(" "))


def _scalar(raw, where):
    """Turn an inline YAML scalar into a Python value (YAML 1.2 core schema)."""
    if raw.startswith('"'):
        if not raw.endswith('"') or len(raw) < 2:
            raise YamlError(f"{where}: unterminated double-quoted string")
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            raise YamlError(f"{where}: bad double-quoted string ({e.msg})")
    if raw.startswith("'"):
        body = raw[1:-1] if len(raw) >= 2 and raw.endswith("'") else None
        if body is None or re.search(r"(?<!')'(?!')", body.replace("''", "")):
            raise YamlError(f"{where}: bad single-quoted string")
        return body.replace("''", "'")
    if raw[0] in "[{&*!%@`|>":
        raise YamlError(f"{where}: unsupported YAML ({raw[0]!r} at the start of a value); quote the value")
    if " #" in raw or "\t#" in raw:
        raw = re.split(r"[ \t]#", raw, 1)[0].rstrip()
    if ": " in raw or raw.endswith(":"):
        raise YamlError(f"{where}: plain value contains ': ', which YAML reads as a mapping; quote the value")
    if raw in ("true", "True", "TRUE"):
        return True
    if raw in ("false", "False", "FALSE"):
        return False
    if raw in ("null", "Null", "NULL", "~"):
        return None
    if INT_RE.match(raw):
        return int(raw, 0)
    if FLOAT_RE.match(raw):
        return float(raw.replace("inf", "Infinity").replace("Inf", "Infinity").replace("INF", "Infinity"))
    return raw


def _block(lines, i, style, parent_indent):
    """Read a | or > block scalar starting at lines[i]. Returns (text, next_i)."""
    body = []
    while i < len(lines) and (not lines[i].strip() or _indent(lines[i]) > parent_indent):
        body.append(lines[i])
        i += 1
    while body and not body[-1].strip():
        body.pop()
    if not body:
        return "", i
    cut = min(_indent(l) for l in body if l.strip())
    body = [l[cut:] for l in body]
    if style.startswith("|"):
        text = "\n".join(body)
    else:
        paras, cur = [], []
        for l in body:
            if l.strip():
                cur.append(l.strip())
            else:
                paras.append(" ".join(cur))
                cur = []
        paras.append(" ".join(cur))
        text = "\n".join(paras)
    return (text if style.endswith("-") else text + "\n"), i


def parse_yaml(text, where):
    """Parse the YAML subset used by SKILL.md frontmatter and case.yaml."""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    data, i = {}, 0

    def mapping(indent, target, i):
        while i < len(lines):
            line = lines[i]
            if not line.strip() or line.lstrip().startswith("#"):
                i += 1
                continue
            ind = _indent(line)
            if ind < indent:
                return i
            if ind > indent or "\t" in line[:ind + 1]:
                raise YamlError(f"{where} line {i + 1}: unexpected indentation")
            m = KEY_LINE.match(line[ind:])
            if not m:
                raise YamlError(f"{where} line {i + 1}: expected 'key: value', got {line.strip()!r}")
            key, raw = m.group(1), (m.group(2) or "")
            if key in target:
                raise YamlError(f"{where} line {i + 1}: duplicate key {key!r}")
            i += 1
            if raw in ("|", "|-", "|+", ">", ">-", ">+"):
                target[key], i = _block(lines, i, raw.rstrip("+"), ind)
            elif raw == "" or raw.startswith("#"):
                j = i
                while j < len(lines) and (not lines[j].strip() or lines[j].lstrip().startswith("#")):
                    j += 1
                if j < len(lines) and _indent(lines[j]) > ind:
                    if indent > 0:
                        raise YamlError(f"{where} line {j + 1}: nesting deeper than one level is not supported")
                    target[key] = {}
                    i = mapping(_indent(lines[j]), target[key], j)
                else:
                    target[key] = None
            else:
                target[key] = _scalar(raw, f"{where} line {i}")
        return i

    mapping(0, data, i)
    return data


def split_frontmatter(text, where):
    """Return (frontmatter_text, body_text) of a Markdown file with --- frontmatter."""
    text = text.replace("\r\n", "\n").lstrip("﻿")
    if not text.startswith("---\n"):
        raise YamlError(f"{where}: must start with a '---' frontmatter line")
    end = re.search(r"^---[ \t]*$", text[4:], re.M)
    if not end:
        raise YamlError(f"{where}: frontmatter is not closed with '---'")
    return text[4:4 + end.start()], text[4 + end.end():]


# ---------------------------------------------------------------- checks

class Report:
    def __init__(self, root):
        self.root, self.errors, self.warnings, self.notes = root, [], [], []

    def rel(self, path):
        try:
            return Path(path).resolve().relative_to(self.root.resolve()).as_posix()
        except ValueError:
            return Path(path).as_posix()

    def error(self, msg):
        self.errors.append(msg)

    def warn(self, msg):
        self.warnings.append(msg)


def check_skill(skill_dir, rep):
    """Validate one skill folder. Returns metadata.version or None."""
    label = rep.rel(skill_dir)
    errors_before = len(rep.errors)
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        rep.error(f"{label}: SKILL.md not found")
        return None
    text = skill_md.read_text(encoding="utf-8")
    try:
        fm_text, body = split_frontmatter(text, f"{label}/SKILL.md")
        fm = parse_yaml(fm_text, f"{label}/SKILL.md frontmatter")
    except YamlError as e:
        rep.error(str(e))
        return None

    extra = sorted(set(fm) - ALLOWED_FIELDS)
    if extra:
        rep.error(f"{label}/SKILL.md: fields not in the Agent Skills spec: {', '.join(extra)}")

    name = fm.get("name")
    if not isinstance(name, str) or not name.strip():
        rep.error(f"{label}/SKILL.md: 'name' is missing or not a string")
    else:
        if len(name) > MAX_NAME:
            rep.error(f"{label}/SKILL.md: name is {len(name)} characters (max {MAX_NAME})")
        if not NAME_RE.match(name):
            rep.error(f"{label}/SKILL.md: name {name!r} must use a-z, 0-9 and single hyphens, "
                      "not starting or ending with a hyphen")
        if name != skill_dir.name:
            rep.error(f"{label}/SKILL.md: name {name!r} does not match the folder name {skill_dir.name!r}")

    desc = fm.get("description")
    if not isinstance(desc, str) or not desc.strip():
        rep.error(f"{label}/SKILL.md: 'description' is missing, empty or not a string")
    else:
        if len(desc) > MAX_DESCRIPTION:
            rep.error(f"{label}/SKILL.md: description is {len(desc)} characters (max {MAX_DESCRIPTION})")
        if "<" in desc or ">" in desc:
            rep.error(f"{label}/SKILL.md: description contains '<' or '>'")

    if "compatibility" in fm:
        comp = fm["compatibility"]
        if not isinstance(comp, str) or not comp.strip():
            rep.error(f"{label}/SKILL.md: 'compatibility' must be a non-empty string")
        elif len(comp) > MAX_COMPATIBILITY:
            rep.error(f"{label}/SKILL.md: compatibility is {len(comp)} characters (max {MAX_COMPATIBILITY})")

    if "allowed-tools" in fm and not isinstance(fm["allowed-tools"], str):
        rep.error(f"{label}/SKILL.md: 'allowed-tools' must be a space-separated string")

    version = None
    if "metadata" in fm:
        meta = fm["metadata"]
        if not isinstance(meta, dict):
            rep.error(f"{label}/SKILL.md: 'metadata' must be a mapping")
        else:
            for k, v in meta.items():
                if not isinstance(v, str):
                    rep.error(f"{label}/SKILL.md: metadata.{k} must be a string; quote it (got {v!r})")
            version = meta.get("version") if isinstance(meta.get("version"), str) else None

    lic = fm.get("license")
    if not isinstance(lic, str) or not lic.strip():
        rep.error(f"{label}/SKILL.md: 'license' is missing (this repository requires it)")
    else:
        for fname in LICENSE_FILE.findall(lic):
            if not (skill_dir / fname).is_file():
                rep.error(f"{label}/SKILL.md: license names {fname}, which is not in the skill folder")

    n_lines = len(text.splitlines())
    if n_lines > MAX_LINES:
        rep.warn(f"{label}/SKILL.md: {n_lines} lines; the spec recommends under {MAX_LINES}")

    # Links and paths, in SKILL.md and every other Markdown file of the skill.
    skill_root = skill_dir.resolve()
    n_paths = 0
    for md in sorted(skill_dir.rglob("*.md")):
        md_text = body if md == skill_md else md.read_text(encoding="utf-8")
        md_label = rep.rel(md)
        targets = []
        for link in MD_LINK.findall(md_text):
            if URL_SCHEME.match(link) or link.startswith("#"):
                continue
            path = link.split("#", 1)[0].split("?", 1)[0]
            if path:
                targets.append((link, (md.parent / path).resolve()))
        for p in SKILL_PATH.findall(md_text):  # written relative to the skill root, as the spec says
            targets.append((p, (skill_dir / p).resolve()))
        reported = set()
        for shown, target in targets:
            n_paths += 1
            if target in reported:  # one message per missing file, however often it is mentioned
                continue
            reported.add(target)
            if skill_root != target and skill_root not in target.parents:
                rep.error(f"{md_label}: '{shown}' points outside the skill folder "
                          "(it will not exist once the skill is installed)")
            elif not target.exists():
                rep.error(f"{md_label}: '{shown}' does not exist")

    refs = skill_dir / "references"
    if refs.is_dir():
        for f in sorted(p for p in refs.rglob("*") if p.is_file()):
            relpath = f.relative_to(skill_dir).as_posix()
            if relpath not in body:
                rep.error(f"{label}/SKILL.md: never mentions {relpath}, so the agent will not know to read it")

    if len(rep.errors) == errors_before:
        rep.notes.append(f"{label}: frontmatter OK (name, description {len(desc)} chars, license, "
                         f"metadata), {n_paths} file references resolve")
    return version


def check_marketplace(root, rep):
    """Validate .claude-plugin/marketplace.json. Returns (skill dirs listed, metadata.version)."""
    path = root / ".claude-plugin" / "marketplace.json"
    label = rep.rel(path)
    if not path.is_file():
        rep.error(f"{label}: not found")
        return [], None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        rep.error(f"{label}: invalid JSON at line {e.lineno} column {e.colno}: {e.msg}")
        return [], None
    if not isinstance(data, dict):
        rep.error(f"{label}: top level must be an object")
        return [], None
    if not isinstance(data.get("name"), str) or not data["name"]:
        rep.error(f"{label}: 'name' is missing")
    if not isinstance(data.get("owner"), dict) or not data["owner"].get("name"):
        rep.error(f"{label}: 'owner.name' is missing")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or not plugins:
        rep.error(f"{label}: 'plugins' must be a non-empty list")
        plugins = []

    seen, listed, repo = set(), [], root.resolve()
    for idx, plugin in enumerate(plugins):
        where = f"{label}: plugins[{idx}]"
        if not isinstance(plugin, dict):
            rep.error(f"{where} is not an object")
            continue
        pname = plugin.get("name")
        if not isinstance(pname, str) or not NAME_RE.match(pname):
            rep.error(f"{where}: name {pname!r} must be kebab-case")
        elif pname in seen:
            rep.error(f"{where}: duplicate plugin name {pname!r}")
        else:
            seen.add(pname)
            where = f"{label}: plugin {pname!r}"
        source = plugin.get("source")
        base = None
        if isinstance(source, str):
            base = (root / source).resolve()
            if not base.is_dir():
                rep.error(f"{where}: source {source!r} is not a folder in the repository")
                base = None
        elif source is None:
            rep.error(f"{where}: 'source' is missing")
        # A non-string source (github, url, ...) is fetched elsewhere; nothing local to check.
        skills = plugin.get("skills", [])
        if not isinstance(skills, list) or not all(isinstance(s, str) for s in skills):
            rep.error(f"{where}: 'skills' must be a list of paths")
            continue
        for s in skills:
            if base is None:
                continue
            target = (base / s).resolve()
            if repo != target and repo not in target.parents:
                rep.error(f"{where}: skills path {s!r} is outside the repository")
            elif not target.is_dir():
                rep.error(f"{where}: skills path {s!r} does not exist")
            elif not (target / "SKILL.md").is_file():
                rep.error(f"{where}: skills path {s!r} has no SKILL.md")
            else:
                listed.append(target)

    skills_dir = root / "skills"
    if skills_dir.is_dir():
        for d in sorted(p for p in skills_dir.iterdir() if (p / "SKILL.md").is_file()):
            if d.resolve() not in listed:
                rep.error(f"{label}: {rep.rel(d)} is not listed by any plugin, so it cannot be installed")

    meta = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}
    rep.notes.append(f"{label}: {len(plugins)} plugins, {len(listed)} skill paths OK")
    return listed, meta.get("version")


def check_versions(root, skill_versions, market_version, rep):
    found = {rep.rel(d): v for d, v in skill_versions.items() if v is not None}
    if market_version is not None:
        found[".claude-plugin/marketplace.json"] = market_version
    if not found:
        return
    if len(set(found.values())) > 1:
        rep.error("versions differ: " + ", ".join(f"{k} = {v}" for k, v in sorted(found.items())))
        return
    version = next(iter(found.values()))
    changelog = root / "CHANGELOG.md"
    if changelog.is_file():
        text = changelog.read_text(encoding="utf-8")
        if not re.search(rf"^##\s+v?{re.escape(version)}\b", text, re.M):
            rep.error(f"CHANGELOG.md: no '## {version}' heading for the current version")
    rep.notes.append(f"version {version}: same in {len(found)} places and in CHANGELOG.md")


def check_evals(root, rep):
    evals = root / "evals"
    if not evals.is_dir():
        rep.notes.append("evals/: not present, skipped")
        return
    cases = sorted(p for p in evals.iterdir() if p.is_dir() and not p.name.startswith("."))
    for case in cases:
        label = rep.rel(case)
        prompt = case / "prompt.md"
        if not prompt.is_file():
            rep.error(f"{label}: prompt.md missing")
        elif not prompt.read_text(encoding="utf-8").strip():
            rep.error(f"{label}: prompt.md is empty")
        cy = case / "case.yaml"
        if not cy.is_file():
            rep.error(f"{label}: case.yaml missing")
        else:
            try:
                data = parse_yaml(cy.read_text(encoding="utf-8"), f"{label}/case.yaml")
            except YamlError as e:
                rep.error(str(e))
                data = None
            if data is not None:
                if data.get("name") != case.name:
                    rep.error(f"{label}/case.yaml: name {data.get('name')!r} does not match the folder name")
                if not isinstance(data.get("expected_outcome"), str) or not data["expected_outcome"].strip():
                    rep.error(f"{label}/case.yaml: expected_outcome is missing or empty")
        graders = case / "graders"
        if not graders.is_dir() or not any(graders.glob("*.md")):
            rep.error(f"{label}: graders/ has no .md files")

    tq = evals / "trigger-queries.json"
    counts = None
    if not tq.is_file():
        rep.error("evals/trigger-queries.json: missing")
    else:
        try:
            queries = json.loads(tq.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            rep.error(f"evals/trigger-queries.json: invalid JSON at line {e.lineno} column {e.colno}: {e.msg}")
            queries = None
        if queries is not None:
            if not isinstance(queries, list) or not queries:
                rep.error("evals/trigger-queries.json: must be a non-empty list")
            else:
                seen, counts = set(), {True: 0, False: 0}
                for i, q in enumerate(queries):
                    where = f"evals/trigger-queries.json: item {i}"
                    if not isinstance(q, dict):
                        rep.error(f"{where} is not an object")
                        continue
                    if not isinstance(q.get("query"), str) or not q["query"].strip():
                        rep.error(f"{where}: 'query' must be a non-empty string")
                    elif q["query"] in seen:
                        rep.error(f"{where}: duplicate query")
                    else:
                        seen.add(q["query"])
                    if not isinstance(q.get("should_trigger"), bool):
                        rep.error(f"{where}: 'should_trigger' must be true or false, got {q.get('should_trigger')!r}")
                    else:
                        counts[q["should_trigger"]] += 1
    summary = f"evals/: {len(cases)} cases"
    if counts:
        summary += f", {counts[True] + counts[False]} trigger queries ({counts[True]} should, {counts[False]} should not)"
    rep.notes.append(summary)


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if len(argv) > 2 or (len(argv) == 2 and argv[1] in ("-h", "--help")):
        print("Usage: python scripts/validate_skills.py [repo_root]")
        return 0 if len(argv) == 2 else 2
    root = Path(argv[1]) if len(argv) == 2 else Path(__file__).resolve().parent.parent
    if not root.is_dir():
        print(f"Usage: python scripts/validate_skills.py [repo_root]\n{root}: not a folder")
        return 2
    rep = Report(root)

    listed, market_version = check_marketplace(root, rep)
    skills_dir = root / "skills"
    skill_dirs = {p.resolve() for p in skills_dir.iterdir() if p.is_dir()} if skills_dir.is_dir() else set()
    skill_dirs |= set(listed)
    versions = {d: check_skill(d, rep) for d in sorted(skill_dirs)}
    if not skill_dirs:
        rep.error("no skills found in skills/")
    check_versions(root, versions, market_version, rep)
    check_evals(root, rep)

    for w in rep.warnings:
        print("warning: " + w)
    if rep.errors:
        print(f"VALIDATION FAILED: {len(rep.errors)} problem(s)")
        for e in rep.errors:
            print(" - " + e)
        return 1
    print("Validation OK")
    for n in rep.notes:
        print(" - " + n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
