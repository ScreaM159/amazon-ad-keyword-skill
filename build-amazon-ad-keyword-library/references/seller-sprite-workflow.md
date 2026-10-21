# 卖家精灵取数与导出（实盘经验）

## 可用入口（美国站 marketId=1）
- 关键词挖掘：`https://www.sellersprite.com/v3/keyword-miner/?q=<kw>&marketId=1`
- 关键词反查：`https://www.sellersprite.com/v3/keyword-reverse`（输入单 ASIN）
- 拓展流量词：`https://www.sellersprite.com/v3/traffic/extend`
- 批量分析关键词：关键词挖掘页内的 tab（元素结构特殊，脚本常点不到，优先用导出）

## 能否脚本抓取
- **关键词挖掘页可抓**：用 browser-use `evaluate_script` 读表格。
  - 表头定位：列5 = `ABA月排名\n周排名`；列6 = `月搜索量\n增长率`。
  - 提取：`kw = td[1].split('\n')[0].replace(/\s*AC$/,'')`；`abaWeek = td[5].split('\n')[1]`；`volMonth = td[6].split('\n')[0]`。
  - 注意：该页常只返回 ~20 条、无分页。
- **反查 / 拓展流量词 抓不到数据行**：是会员虚拟表格，脚本只读到表头（tbody 无行）。→ **让用户手动导出 CSV**。
- 导出文件列索引（不同文件不同，务必核对表头）：
  - ReverseASIN：`ABA周排名=15`，`月搜索量=16`，`流量占比=2`
  - ExpandKeywords：`ABA周排名=8`，`月搜索量=9`，`流量占比=3`
  - KeywordMining：`ABA月=3`，`ABA周=4`，`月搜索量=5`

## 反查可拿到的产品事实
- 反查页会显示 ASIN 的标题/卖家/价格/评分/评论/BSR/上架时间 → 用于**确认竞品材质/形态**（例：Yes4All = Powder Coated Cast Iron；PAETA = Soft Kettlebell）。

## 多源合并口径
- 同词多源：ABA 周排名取**最小**（最靠前）、月搜索量取**最大**；记录来源。
- 判定只用 ABA 周排名（见决策表 D14）；月量仅参考。

## 卡住时
- 虚拟表格抓不到、批量 tab 点不到、导航超时：**停止硬磨，给用户 3 步手动导出**（反查/拓展/批量分析各自"导出 CSV"），拿到 CSV 再合并。
