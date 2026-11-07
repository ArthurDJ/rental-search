# 房源网站

各地区平台包让你去搜的那些网站，每个网站怎么用。2026-11-06 在 Kelowna 完整搜索过一次，深入测试了加拿大的网站。2026-11-06 在温哥华、多伦多、西雅图、旧金山湾区、洛杉矶、纽约和奥斯汀各打开过一次下面的搜索页，确认能加载、没有被拦；美国的网站还没有深入测试过。网站的行为会在没有通知的情况下改变：每条规则都写着最后一次确认有效的日期。某条规则不再有效时，想办法绕过去，告诉用户，并把这条规则当作已过时。转述这份文件里的任何内容时，都要说明它来自这些带日期的笔记，不是你今天核实的。

## 所有网站通用的规则

- 在用户自己的浏览器里，按正常人看页面的速度操作。一次开一个页面；不要批量下载房源数据。
- 网站出现验证码、"请证明你是真人"页面或 Cloudflare 验证时，停止搜这个网站，并告诉用户。不要想办法绕过。Castanet（Kelowna 的分类广告网站）在 2026-11-06 就是这样，所以跳过了，并告诉用户可以自己去看。
- 搜索结果只是线索。每个候选都点开看过才算数。
- 标着某个城市的结果，常常包括整个地区（Kijiji 的 Kelowna 区域里有 Penticton、Vernon、Osoyoos 等地）。按房源自己的位置筛选。
- 搜关键词"furnished"会宽松匹配正文，搜出不带家具的房和单间。每套房源都要核实家具情况。

## Kijiji

加拿大。2026-11-06 深入测试过（Kelowna）；2026-11-06 打开过搜索页（温哥华、多伦多）。

- 搜索链接：长租用 `https://www.kijiji.ca/b-apartments-condos/<city>/<keyword>/k0c37l<locationId>`，短租用 `https://www.kijiji.ca/b-short-term-rental/<city>/<keyword>/k0c42l<locationId>`。地区编号：Kelowna `1700228`，温哥华 `1700287`（slug 是 `vancouver`），City of Toronto `1700273`（slug 是 `city-of-toronto`）。加 `?sort=dateDesc` 按最新排序。
- 通用的"For Rent"搜索（`c30349001`）会混进单间和办公室；用上面两个分类。
- 每条结果是一个带 `data-testid="listing-card"` 的元素，里面有价格、标题、区域、发布时长和指向 `/v-...` 的链接。
- 已删除的广告还能打开，标题旁边写着 "No Longer Available"。按已下架处理。

## Craigslist

加拿大和美国。2026-11-06 深入测试过（Kelowna）；2026-11-06 打开过搜索页（温哥华、多伦多、西雅图、旧金山湾区）。

- 搜索：`https://<city>.craigslist.org/search/apa?is_furnished=1&sort=date`（会跳转到 `www.craigslist.org/search/area/<city>?...`）。城市子域名有 `kelowna`、`vancouver`、`toronto`、`seattle`、`sfbay`、`losangeles`、`newyork` 和 `austin` 等。带家具筛选可靠。
- 打开房源用 `https://www.craigslist.org/view/d/<slug>/<id>`。同样的路径换成城市子域名（`<city>.craigslist.org/view/...`）会显示 "Page Not Found"。
- 属性区列出勾选项，比如 "furnished"、"w/d in unit"、"off-street parking"、"available dec 1"。勾选项可能和正文对不上；正文没提家具时，家具标**待核实**。
- 地图元素的 `data-latitude` 和 `data-longitude` 里有大概坐标（还有 `data-accuracy`）。广告没写地址时，用它测通勤。

## Facebook Marketplace

加拿大和美国。2026-11-06 深入测试过（Kelowna）。

- 需要用户自己已登录的账号。不要替用户登录。
- 链接里的城市名（比如 `/marketplace/kelowna/...`）不起作用：结果跟着账号保存的 Marketplace 地点走。要搜别的城市：
  1. 先从地点按钮上记下当前的地点和半径（按钮文字类似"地点：<城市>，<半径>内"）。
  2. 点开，输入城市，选城市那一项，设好半径（10 英里 / 16 公里能覆盖一个中等城市），点应用。
  3. 搜完把地点和半径改回原样，并告诉用户你改回去了。
- 城市名按界面语言匹配。2026-11-06 中文界面里输入英文"Kelowna"，没有出现这个城市；输入中文名"基隆拿"才找到。英文名只搜出街区时，试试界面语言里的名字。
- 搜索：`https://www.facebook.com/marketplace/category/search/?query=furnished&category_id=propertyrentals&sortBy=creation_time_descend`。往下滚几次加载更多。卡片上只有价格、标题和城市，所以每条都要点开。
- 每个房源页有描述、"房屋信息"区（房型、洗衣、车位、宠物），有时有地址。"我们只提供大概位置"表示没有确切地址。
- 出现"再次发消息"按钮，表示用户的账号已经给这个卖家发过消息。告诉用户；在任何人再写信之前，这一点很重要。
- Marketplace 页面截图有时会超时；读页面文字可以正常用。

## liv.rent

加拿大，温哥华最强。2026-11-06 深入测试过（Kelowna）；2026-11-06 打开过城市页（温哥华房源很多，多伦多很少）。

- 城市页：`https://liv.rent/rental-listings/city/<city>`。查询参数 `furnished=true` 不起筛选作用：要看每套房源自己的字段，写的是 "Furnished"、"Unfurnished" 或 "Furnish Available"。
- 房源页有固定的信息区：Move-In Date、Lease Type、Max. Occupancy、Minimum Lease、Parking；降过价的会显示划掉的旧价格。
- 顶部写着 "This listing has been marked as rented" 就是已下架，即使正文还写着 "available immediately"。
- 房东旁边的 "ID Unverified"，和其他迹象一起出现时，是诈骗信号（`references/verification.md` → 诈骗迹象）。

## Zumper 和 PadMapper

加拿大和美国。2026-11-06 深入测试过（Kelowna）；2026-11-06 打开过温哥华、多伦多、西雅图、洛杉矶、纽约和奥斯汀的带家具专页。

- Zumper 带家具专页：`https://www.zumper.com/apartments-for-rent/<city>-<province or state>/furnished`，比如 `kelowna-bc`、`toronto-on`、`seattle-wa`、`los-angeles-ca`、`new-york-ny`、`austin-tx`。往下滚，把所有卡片都加载出来；标题里的数字数的是房间数，不是卡片数。
- 楼盘卡片（"Central Kelowna, Studio–3 beds, $1,400–$2,657"）带的是整栋楼的标签。楼盘上的 "Furnished" 标签不代表你要的那套带家具；要向楼盘确认，或看单元页。
- 地址页显示 "Monthly rent –"、只有一个 "Notify me" 按钮的，是已下架。
- PadMapper 显示的是同一份数据。它的 `/apartments/<city>/furnished` 路径在 2026-11-06 会跳转到没筛选的列表，所以用 Zumper 的带家具专页。

## rentals.ca

加拿大。2026-11-06 深入测试过（Kelowna）；2026-11-06 打开过城市页（多伦多）。

- 城市页：`https://rentals.ca/<city>`。楼盘页（比如 `https://rentals.ca/<city>/<building>`）列出每种房型的价格、面积和 "Available"，详情区有 "Furnished: Yes/No"、租期和车位费。
- rentals.ca 和 Zumper 对家具的说法不一致时，两个都别信：这套房源算**待核实**，直到楼盘给出答复。

## Zillow、HotPads 和 Trulia

美国，同一家公司。2026-11-06 打开过搜索页（西雅图），没有遇到人机验证；没有深入测试过。

- Zillow 租房：`https://www.zillow.com/<city>-<state>/rentals/`，比如 `seattle-wa`。HotPads：`https://hotpads.com/<city>-<state>/apartments-for-rent`。
- Zillow 常出"按住不放"的人机验证；2026-11-06 没有出现。出现的话，和别的人机验证一样处理。
- 家具情况一般写在正文里，筛选靠不住：每套房源都要点开。

## Apartments.com

美国。2026-11-06 打开过带家具专页（西雅图）；没有深入测试过。

- 带家具专页：`https://www.apartments.com/<city>-<state>/furnished/`，比如 `seattle-wa`。页面加载慢，加载完还会再跳一次；等一下再读。
- 大多是物业管理的楼：价格常写成各单元的一个区间，从多少"起"。要确认具体那套的价格和家具情况。

## StreetEasy

纽约市。2026-11-06 打开过带家具搜索；没有深入测试过。

- 带家具搜索：`https://streeteasy.com/for-rent/nyc/amenities:furnished`。
- 房源会写要不要付中介费；对照纽约的规定看：`references/regions-us.md` → 纽约市。

## Furnished Finder

美国，带家具的按月短住（旅行护士常用）。2026-11-06 打开过城市页（西雅图）；没有深入测试过。

- 城市页：`https://www.furnishedfinder.com/housing/us--<state>--<city>`，比如 `us--wa--seattle`。
- 一般住 30 天或更久。很多房东是个人：照常排查诈骗迹象。
