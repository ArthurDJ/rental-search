# 输出

## 语言

给用户的所有东西（总结、表格、Excel、网页）都用用户写消息时用的语言，除非用户要求别的语言。专有名词、地址和网站名保持房源上原来的写法。给房东的消息默认用房源的语言（北美大多数房源是英文），不管用户跟你说什么语言；需要时在草稿旁边附上译文，方便用户核对。

## 交付什么

按这个顺序：

1. **两行说明有什么变化**，如果这是对之前找房结果的更新：哪些下架了、哪些是新的、哪些调价了、对之前名单的更正。
2. **前 3 名**，每套写月租和实际月花费、实测通勤、两三条理由，以及要问房东的第一件事。如果没有一套满足所有硬性条件，就直接说，改为展示最好的几套**待核实**房源。
3. **完整表格**，列出在租的房源，按状态或预算分组，带链接。
4. **已下架和排除**，每条附证据（"Kijiji：No Longer Available""车程 18–35 min""疑似诈骗：……"）。
5. **怎么查的**，简短说明：搜了哪些网站、跳过了哪些及原因、通勤怎么测的、核实的日期和时间、改过并已改回的设置。
6. **文件**：`scripts/build_outputs.py` 生成的 Excel、CSV 和网页。

有文件时，聊天里的回答要简短：前 3 名、变化，以及文件在哪。

## 房源记录

`scripts/build_outputs.py` 读取一个 JSON 文件。边搜边写，每套房源一条记录。页面没写的用 `null`；输出里会按用户的语言显示成"未写"。

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

- `status`：`meets`（符合）、`confirm`（待核实）、`fails`（不符合）、`gone`（已下架）或 `excluded`（已排除）。`fails`、`gone`、`excluded` 必须填 `reason`。
- `bedrooms`：studio 填 `0`，不知道填 `null`。网页用它做房型筛选。
- `commute_min` 和 `commute_max`：分钟数，最快那条路线的区间；Maps 只给一个数时两个相等；没测时填 `null`，并在 `note` 里写原因。
- `true_cost`：计算方法见 `references/scoring.md` → 实际月花费；未知太多时宁可填 `null`，不要猜。
- `extra`：`meta.extra_columns` 对应的值，由模块添加（宠物、收据、最短租期等）。
- `is_new`：上次核对之后新出现的（或者是用户带来的名单里没有的）。

运行：

```
python scripts/build_outputs.py listings.json --out <folder> [--name rentals]
```

它会生成 `<name>.xlsx`（需要 `openpyxl`；没装就跳过并提示）、`<name>.csv` 和 `<name>.html`。Excel 每个分组一张表，另有一张设置表，里面的预算和通勤上限决定"比预算多/少"和"车程是否达标"两列公式。网页用 `assets/page_template.html`，跟随浏览者的浅色或深色主题，手机宽度也能正常看。

## 给房东的消息

只在用户要求时写，而且只写草稿。

- 每套房源一条，简短，用房源的语言。
- 写明谁在问（不要写用户没同意分享的细节）、入住日期、租期、几个人住，以及决定这套房行不行的两三个问题（常见的有：还在租吗、确切地址、包含哪些费用、家具清单、宠物、车位）。
- 不替用户做没做过的承诺（收入、信用、推荐人），不要求保留房子，不谈付款。
- 结尾写怎么联系用户，用 `[你的电话或邮箱]` 这样的占位符，除非用户给了你可以用的联系方式。

例子：

> Hi, is the furnished 1-bedroom on [street] still available for a December 1 move-in? We are two working adults, non-smokers, looking for a 12-month lease. Could you tell me the exact address, which utilities are included, and whether a parking stall comes with it? We would like to arrange a viewing. Thanks, [name], [your phone or email]
