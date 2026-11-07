#!/usr/bin/env python3
"""Build the hand-over files for a rental search from one JSON file of listing records.

Writes, into --out:
  <name>.html  the web page (always; standard library only)
  <name>.csv   every listing, one row each (always)
  <name>.xlsx  the workbook (only if openpyxl is installed)

The record format is described in references/outputs.md -> Listing records.

Labels come in English ("en") and Chinese ("zh"). For any other language, set
meta.language and give translations in meta.labels (same keys as LABELS["en"]);
missing keys fall back to English.

Usage: python scripts/build_outputs.py listings.json --out <folder> [--name rentals]
"""
import argparse
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "page_template.html"

LABELS = {
    "en": {
        "not_stated": "not stated",
        "in_budget": "In budget",
        "over_budget": "Over budget",
        "active": "Active",
        "gone_excluded": "Gone and excluded",
        "picks": "Contact these first",
        "all_listings": "All listings",
        "method": "How the search was done",
        "notes": "Notes and corrections",
        "checked": "Checked",
        "budget": "Budget",
        "move_in": "Move-in",
        "commute": "Commute",
        "commute_basis": "Commute measured",
        "household": "Household",
        "sites": "Sites searched",
        "col_n": "#",
        "col_name": "Listing",
        "col_rent": "Rent",
        "col_true_cost": "True monthly cost",
        "col_type": "Unit",
        "col_commute": "Commute",
        "col_commute_min": "Commute fastest (min)",
        "col_commute_max": "Commute slowest (min)",
        "col_commute_ok": "Slowest within limit",
        "col_vs_budget": "Rent vs budget",
        "col_furnished": "Furnished",
        "col_details": "Move-in and details",
        "col_laundry": "Laundry",
        "col_parking": "Parking",
        "col_utilities": "Utilities",
        "col_lease": "Lease",
        "col_status": "Status",
        "col_new": "New",
        "col_source": "Source",
        "col_link": "Link",
        "col_note": "Note",
        "col_reason": "Reason",
        "col_size": "Size (sq ft)",
        "open": "Open",
        "open_listing": "Open listing",
        "status_meets": "Meets",
        "status_confirm": "To confirm",
        "status_fails": "Fails",
        "status_gone": "Gone",
        "status_excluded": "Excluded",
        "new": "New",
        "yes": "Yes",
        "no": "No",
        "not_measured": "not measured",
        "minutes": "min",
        "vs_budget": "vs budget",
        "f_type": "Unit",
        "f_all": "All",
        "f_studio": "Studio",
        "f_bed": "1 bedroom or more",
        "f_sort": "Sort",
        "s_rank": "Recommended order",
        "s_rent": "Rent, low to high",
        "s_cost": "True cost, low to high",
        "s_commute": "Commute, short to long",
        "f_ok": "Commute within limit",
        "f_new": "New only",
        "f_hide_fails": "Hide fails",
        "legend_range": "Commute range (scale 0–{max} min, dashed line = {limit} min limit)",
        "legend_over": "Slowest time over the limit",
        "empty": "No listings match these filters.",
        "settings": "Settings",
        "settings_budget": "Budget target",
        "settings_limit": "Commute limit (min)",
        "settings_help": "Change the yellow cells; the vs budget and commute columns recalculate.",
        "ask": "Ask",
        "reasons": "Why",
        "footer": "Listings change quickly. Confirm a listing is still available before contacting anyone. Nobody was contacted on your behalf.",
        "per_month": "/ month",
        "sqft": "sq ft",
    },
    "zh": {
        "not_stated": "未写",
        "in_budget": "预算内",
        "over_budget": "超预算",
        "active": "在租",
        "gone_excluded": "已下架和排除",
        "picks": "先联系这几套",
        "all_listings": "全部房源",
        "method": "怎么查的",
        "notes": "说明和更正",
        "checked": "核实时间",
        "budget": "预算",
        "move_in": "入住",
        "commute": "通勤",
        "commute_basis": "车程口径",
        "household": "住几个人",
        "sites": "搜索平台",
        "col_n": "#",
        "col_name": "房源",
        "col_rent": "月租",
        "col_true_cost": "实际月花费",
        "col_type": "房型",
        "col_commute": "车程",
        "col_commute_min": "车程最快（分钟）",
        "col_commute_max": "车程最慢（分钟）",
        "col_commute_ok": "最慢车程是否达标",
        "col_vs_budget": "比预算多/少",
        "col_furnished": "家具",
        "col_details": "入住和配套",
        "col_laundry": "洗衣",
        "col_parking": "车位",
        "col_utilities": "水电网",
        "col_lease": "租期",
        "col_status": "状态",
        "col_new": "新发现",
        "col_source": "来源",
        "col_link": "链接",
        "col_note": "备注",
        "col_reason": "原因",
        "col_size": "面积（尺）",
        "open": "打开",
        "open_listing": "打开原帖",
        "status_meets": "符合",
        "status_confirm": "待核实",
        "status_fails": "不符合",
        "status_gone": "已下架",
        "status_excluded": "已排除",
        "new": "新",
        "yes": "是",
        "no": "否",
        "not_measured": "未测",
        "minutes": "分钟",
        "vs_budget": "vs 预算",
        "f_type": "房型",
        "f_all": "全部",
        "f_studio": "Studio",
        "f_bed": "1 房及以上",
        "f_sort": "排序",
        "s_rank": "推荐顺序",
        "s_rent": "月租 低→高",
        "s_cost": "实际花费 低→高",
        "s_commute": "车程 短→长",
        "f_ok": "只看车程达标",
        "f_new": "只看新发现",
        "f_hide_fails": "隐藏不符合",
        "legend_range": "车程区间（刻度 0–{max} 分钟，虚线 = {limit} 分钟上限）",
        "legend_over": "最慢超过上限",
        "empty": "没有符合这些条件的房源。",
        "settings": "设置",
        "settings_budget": "预算目标",
        "settings_limit": "车程上限（分钟）",
        "settings_help": "改黄色格子，“比预算多/少”和车程两列会自动重算。",
        "ask": "要问",
        "reasons": "理由",
        "footer": "房源变化很快，联系之前先确认还在租。没有替你联系任何人。",
        "per_month": "/ 月",
        "sqft": "尺",
    },
}

ACTIVE = {"meets", "confirm", "fails"}
FIELDS = ["id", "name", "status", "rent", "rent_note", "true_cost", "true_cost_note", "bedrooms", "unit_type",
          "size_sqft", "commute_min", "commute_max", "furnished", "laundry", "parking", "utilities", "move_in",
          "lease", "is_new", "source", "url", "note", "reason"]


def labels_for(meta):
    lang = (meta.get("language") or "en").lower()
    base = dict(LABELS["en"])
    base.update(LABELS.get(lang.split("-")[0], {}))
    base.update(meta.get("labels") or {})
    return base


def load(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    meta = data.setdefault("meta", {})
    data.setdefault("picks", [])
    listings = data.setdefault("listings", [])
    problems = []
    seen = set()
    for i, rec in enumerate(listings):
        for f in FIELDS:
            rec.setdefault(f, None)
        rec.setdefault("extra", {})
        if not rec.get("id"):
            rec["id"] = f"listing-{i + 1}"
        if rec["id"] in seen:
            problems.append(f"duplicate id {rec['id']}")
        seen.add(rec["id"])
        if rec["status"] not in ACTIVE | {"gone", "excluded"}:
            problems.append(f"{rec['id']}: status must be meets, confirm, fails, gone or excluded")
        if rec["status"] in {"fails", "gone", "excluded"} and not rec.get("reason"):
            problems.append(f"{rec['id']}: status {rec['status']} needs a reason")
    ids = {r["id"] for r in listings}
    for p in data["picks"]:
        if p.get("id") not in ids:
            problems.append(f"pick {p.get('id')} is not a listing id")
    if problems:
        sys.exit("Problems in the listing file:\n  " + "\n  ".join(problems))
    meta.setdefault("extra_columns", [])
    return data


def budget_cap(meta):
    if meta.get("budget_max"):
        return meta["budget_max"]
    if meta.get("budget_target"):
        return round(meta["budget_target"] * 1.1)
    return None


def groups(data, L):
    meta, recs = data["meta"], data["listings"]
    active = [r for r in recs if r["status"] in ACTIVE]
    closed = [r for r in recs if r["status"] not in ACTIVE]
    cap = budget_cap(meta)
    out = []
    if cap:
        out.append(("in", L["in_budget"], [r for r in active if r["rent"] is None or r["rent"] <= cap]))
        out.append(("over", L["over_budget"], [r for r in active if r["rent"] is not None and r["rent"] > cap]))
    else:
        out.append(("active", L["active"], active))
    out.append(("closed", L["gone_excluded"], closed))
    return out


def text(v, L):
    if v is None or v == "":
        return L["not_stated"]
    if v is True:
        return L["yes"]
    if v is False:
        return L["no"]
    return str(v)


def write_csv(data, L, path):
    extra = data["meta"]["extra_columns"]
    head = [L["col_status"], L["col_name"], L["col_rent"], L["col_true_cost"], L["col_type"], L["col_size"],
            L["col_commute_min"], L["col_commute_max"], L["col_furnished"], L["col_laundry"], L["col_parking"],
            L["col_utilities"], L["move_in"], L["col_lease"]] + [c["label"] for c in extra] + \
           [L["col_new"], L["col_source"], L["col_link"], L["col_note"], L["col_reason"]]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(head)
        for r in data["listings"]:
            w.writerow([L["status_" + r["status"]], r["name"], r["rent"], r["true_cost"], r["unit_type"], r["size_sqft"],
                        r["commute_min"], r["commute_max"], r["furnished"], r["laundry"], r["parking"], r["utilities"],
                        r["move_in"], r["lease"]] + [r["extra"].get(c["key"]) for c in extra] +
                       [L["new"] if r["is_new"] else "", r["source"], r["url"], r["note"], r["reason"]])


def write_xlsx(data, L, path):
    try:
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
        from openpyxl.utils import get_column_letter
    except ImportError:
        print("openpyxl is not installed: skipped the workbook (pip install openpyxl to get it).")
        return False
    meta = data["meta"]
    font = "Arial"
    thin = Side(style="thin", color="BFBFBF")
    border = Border(left=thin, right=thin, top=thin, bottom=thin)
    head_fill = PatternFill("solid", fgColor="1F4E78")
    wb = Workbook()
    wb.remove(wb.active)
    settings_name = L["settings"][:31]
    sref = "'" + settings_name.replace("'", "''") + "'"
    extra = meta["extra_columns"]

    def header(ws, names):
        for j, h in enumerate(names, 1):
            c = ws.cell(1, j, h)
            c.font = Font(name=font, bold=True, color="FFFFFF")
            c.fill = head_fill
            c.border = border
            c.alignment = Alignment(wrap_text=True, vertical="center", horizontal="center")
        ws.row_dimensions[1].height = 32

    def body(ws, i, j, v, fmt=None):
        c = ws.cell(i, j, v)
        c.font = Font(name=font, size=10)
        c.alignment = Alignment(wrap_text=True, vertical="top")
        c.border = border
        if fmt:
            c.number_format = fmt
        return c

    money = '"$"#,##0'
    for key, title, recs in groups(data, L):
        ws = wb.create_sheet(title[:31])
        if key == "closed":
            header(ws, [L["col_name"], L["col_rent"], L["col_status"], L["col_reason"], L["col_source"], L["col_link"]])
            for i, r in enumerate(recs, 2):
                body(ws, i, 1, r["name"])
                body(ws, i, 2, r["rent"], money)
                body(ws, i, 3, L["status_" + r["status"]])
                body(ws, i, 4, r["reason"])
                body(ws, i, 5, r["source"])
                c = body(ws, i, 6, L["open"] if r["url"] else "")
                if r["url"]:
                    c.hyperlink = r["url"]
                    c.font = Font(name=font, size=10, color="0563C1", underline="single")
            for j, w in enumerate([44, 12, 14, 60, 16, 8], 1):
                ws.column_dimensions[get_column_letter(j)].width = w
            ws.freeze_panes = "B2"
            continue
        names = [L["col_n"], L["col_name"], L["col_status"], L["col_rent"], L["col_true_cost"], L["col_vs_budget"],
                 L["col_type"], L["col_size"], L["col_commute_min"], L["col_commute_max"], L["col_commute_ok"],
                 L["col_furnished"], L["col_laundry"], L["col_parking"], L["col_utilities"], L["move_in"],
                 L["col_lease"]] + [c["label"] for c in extra] + [L["col_new"], L["col_source"], L["col_link"], L["col_note"]]
        header(ws, names)
        for i, r in enumerate(recs, 2):
            row = [i - 1, r["name"], L["status_" + r["status"]], r["rent"], r["true_cost"],
                   f'=IF(OR(D{i}="",{sref}!$B$2=""),"",D{i}-{sref}!$B$2)',
                   text(r["unit_type"], L), r["size_sqft"], r["commute_min"], r["commute_max"],
                   f'=IF(J{i}="","{L["not_measured"]}",IF({sref}!$B$3="","",IF(J{i}<={sref}!$B$3,"{L["yes"]}","{L["no"]}")))',
                   text(r["furnished"], L), text(r["laundry"], L), text(r["parking"], L), text(r["utilities"], L),
                   text(r["move_in"], L), text(r["lease"], L)] + \
                  [text(r["extra"].get(c["key"]), L) for c in extra] + \
                  [L["new"] if r["is_new"] else "", r["source"], L["open"] if r["url"] else "", r["note"] or ""]
            for j, v in enumerate(row, 1):
                c = body(ws, i, j, v)
                if j in (4, 5):
                    c.number_format = money
                if j == 6:
                    c.number_format = '+"$"#,##0;-"$"#,##0;"$"0'
            link = ws.cell(i, len(names) - 1)
            if r["url"]:
                link.hyperlink = r["url"]
                link.font = Font(name=font, size=10, color="0563C1", underline="single")
            if r["is_new"]:
                ws.cell(i, len(names) - 3).font = Font(name=font, size=10, bold=True, color="C00000")
        widths = [5, 32, 11, 11, 13, 12, 14, 9, 10, 10, 11, 20, 16, 18, 18, 14, 14] + [16] * len(extra) + [7, 14, 8, 44]
        for j, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(j)].width = w
        ws.freeze_panes = "C2"
        ws.auto_filter.ref = f"A1:{get_column_letter(len(names))}{max(len(recs), 1) + 1}"

    st = wb.create_sheet(settings_name)
    rows = [(meta.get("title") or "", None),
            (L["settings_budget"], meta.get("budget_target")),
            (L["settings_limit"], meta.get("commute_limit_min")),
            (L["checked"], meta.get("checked_at")),
            (L["move_in"], meta.get("move_in")),
            (L["commute_basis"], meta.get("commute_basis")),
            (L["sites"], ", ".join(meta.get("sites") or [])),
            ("", L["settings_help"])]
    for i, (k, v) in enumerate(rows, 1):
        st.cell(i, 1, k).font = Font(name=font, bold=True, size=14 if i == 1 else 11)
        c = st.cell(i, 2, v)
        c.font = Font(name=font)
        c.alignment = Alignment(wrap_text=True, vertical="top", horizontal="left")
    for r in (2, 3):
        st.cell(r, 2).fill = PatternFill("solid", fgColor="FFFF00")
        st.cell(r, 2).font = Font(name=font, color="0000FF")
    st["B2"].number_format = money
    st.column_dimensions["A"].width = 24
    st.column_dimensions["B"].width = 80
    wb.save(path)
    return True


def write_html(data, L, path):
    tpl = TEMPLATE.read_text(encoding="utf-8")
    meta = data["meta"]
    payload = {"meta": meta, "picks": data["picks"], "listings": data["listings"],
               "budget_cap": budget_cap(meta), "labels": L}
    js = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    title = (meta.get("title") or "Rental search").replace("<", "&lt;").replace(">", "&gt;")
    html = tpl.replace("__TITLE__", title).replace("__LANG__", meta.get("language") or "en").replace("__DATA__", js)
    Path(path).write_text(html, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("listings")
    ap.add_argument("--out", default=".")
    ap.add_argument("--name", default="rentals")
    a = ap.parse_args()
    data = load(a.listings)
    L = labels_for(data["meta"])
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    write_html(data, L, out / f"{a.name}.html")
    write_csv(data, L, out / f"{a.name}.csv")
    made = ["html", "csv"]
    if write_xlsx(data, L, out / f"{a.name}.xlsx"):
        made.append("xlsx")
    print(f"Wrote {', '.join(f'{a.name}.{m}' for m in made)} to {out}")


if __name__ == "__main__":
    main()
