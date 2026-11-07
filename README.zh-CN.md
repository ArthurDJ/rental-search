[English](README.md) | 简体中文

> **说明：** 这个仓库是一个给 Claude 用的 skill。关于 Agent Skills 标准，见 [agentskills.io](https://agentskills.io)。

# rental-search

一个帮 Claude 找住处、并判断**应该先联系哪几套房源**的 skill。它在你自己的浏览器里搜索租房网站，逐个打开房源，实测早高峰通勤时间，算出实际月花费，核实每套房源是否还在租、是不是诈骗，最后用你的语言交付排好序的表格、Excel 和网页。它会起草给房东的消息，但从不发送、不提交申请、不付款。

仓库里同一个 skill 有两种语言：`skills/rental-search`（英文指令）和 `skills/rental-search-zh`（中文指令），装其中一个即可。两个都会用你写消息的语言回答。

## 这个 skill 做什么

| 问题 | skill 怎么处理 |
|---|---|
| 同一套房在好几个网站上价格不同，还混着单间、办公室和别的城市 | 逐个打开候选，合并重复，一套房只留一行、保留所有链接 |
| 房源会过期，上周的短名单一半都没了 | 每次汇报前重新核对每套房源，列出已下架的并附证据 |
| "带家具""水电全包""含车位"在页面不同地方意思不一样 | 读这套房自己的页面，标出矛盾，没写的一律标"未写" |
| 房源页上的通勤时间是猜的 | 按你出门的时间用 Google Maps 实测，拿区间最慢的那头和你的上限比 |
| 只看房租会误判 | 把水电、车位、宠物费和一次性费用加进实际月花费 |
| 诈骗房源看起来最划算 | 用清单排查（价格远低于市价、要求离开平台联系、看房前要钱、房东在国外） |

三种模式：**快速**（给你贴的房源排序）、**标准**（搜一个城市）和**盯盘**（报告和上次相比的变化）。

## 它不会做的事

- 联系房东、预约看房、提交申请或付款。它只起草，由你发送。
- 替你登录或注册账号。需要登录的网站（Facebook Marketplace）用你浏览器里已经登录的账号。
- 绕过验证码或机器人检测，或批量下载房源数据。它按正常人的速度浏览，遇到挡自动浏览的网站就跳过。
- 买房、商业或办公室租赁、按晚计费的度假住宿、租赁纠纷。

## 地区

| 地区 | 状态 |
|---|---|
| 加拿大 BC 省（Kelowna、温哥华） | 2026-11-06 在 Kelowna 完整搜索过：Kijiji、Craigslist、Facebook Marketplace、liv.rent、Zumper / PadMapper、rentals.ca，每条规则都标了日期。温哥华的搜索页 2026-11-06 粗测过。 |
| 加拿大安省（多伦多） | 搜索页 2026-11-06 粗测过。安省租赁规定（只能收租金押金、不能收损坏押金和宠物押金、标准租约）来自官方页面。 |
| 美国（西雅图、旧金山湾区、洛杉矶、纽约市、奥斯汀） | Zillow、HotPads、Apartments.com、StreetEasy、Furnished Finder、Zumper 和 Craigslist 的搜索页 2026-11-06 粗测过。各州和城市的规定（押金上限、费用、纽约 FARE Act、西雅图入住费用上限、短租规定）来自官方页面。 |
| 其他地方 | 没有平台包。skill 会先找出当地的网站，请你确认名单，在官方页面上查当地规定，给结果加标注，事后可以帮你写一个新的平台包。 |

除 Kelowna 外，其他平台包都是粗测（确认搜索页能打开、规定来自官方来源），没有做完整搜索。

## 需求模块

除了基础问题（城市、通勤、预算、入住、租期、几个人住、房型），你的需求涉及时，skill 会打开对应的模块：

| 模块 | 增加的内容 |
|---|---|
| 宠物 | 每套房源的宠物政策、体重和品种限制、宠物押金和费用 |
| 出差或工作调动 | 报销用的收据或发票、公司付款、最短租期、网络和书桌 |
| 带家具 | 家具到底有哪些（厨具、床品） |
| 停车和电车 | 车位是否包含、电车充电 |
| 家庭和孩子 | 卧室数、学区、公园 |
| 无障碍 | 电梯、一楼、无台阶入口 |
| 合租 | 独立卫生间、还有谁住、转租 |
| 中短租 | 具体日期、能否转租、原租约何时结束 |

## 输出

`scripts/build_outputs.py` 把房源记录生成：

- `.xlsx` Excel：每个分组一张表（预算内、超预算、已下架和排除），另有一张设置表，里面的预算和通勤上限驱动公式；
- 包含所有房源的 `.csv`；
- 一个网页：跟随浅色或深色模式，手机上也能看，可以发布成 Claude artifact，也可以在本地打开。

界面文字内置英文和中文；其他语言在数据文件里提供译文即可。用虚构的示例数据试一下：

```
python skills/rental-search/scripts/build_outputs.py examples/sample-listings.json --out examples/out
```

## 安装

- **Claude Code**：`/plugin marketplace add ArthurDJ/rental-search`，然后 `/plugin install rental-search@rental-search`（或 `rental-search-zh@rental-search`）。
- **Claude.ai**：把一个 skill 文件夹打包成 zip，在 Settings → Capabilities → Skills 里上传。
- **其他支持 Agent Skills 的 agent**：从 `skills/` 复制一个文件夹。

配合浏览器工具（Claude in Chrome 或类似的浏览器扩展）效果最好；生成 Excel 需要 Python 和 `openpyxl`。没有浏览器时，它会用你贴过来的房源工作，并标注"未重新核对"。

## 仓库结构

```
skills/rental-search/          英文 skill（SKILL.md、references/、scripts/、assets/）
skills/rental-search-zh/       中文 skill，结构相同
evals/                         14 个行为测试用例和 24 条触发测试
examples/sample-listings.json  给输出脚本用的虚构示例数据
scripts/                       仓库检查脚本（中英对照、格式校验）
```

## 参与贡献

- 网站规则会过时。平台包里某条规则不再有效时，开一个 "Rule out of date" issue，写明网站、规则和你核实的日期。
- 欢迎新的地区平台包。按 `references/regions-other.md` → 写新的平台包 来写，不要写进任何人的个人信息，并且中英文 skill 一起改。
- 提交 pull request 之前，运行 `python scripts/check_parity.py` 和 `python scripts/validate_skills.py`。

## 许可证

MIT。见 [LICENSE](LICENSE)。
