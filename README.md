# Amazon Ad Keyword Library Skill（v0.1beta）

亚马逊 SP 关键词词库搭建 Skill：把零散关键词变成「词库 + 匹配方式 + 广告活动」的可执行方案。
**广告上架前使用**：产品事实由运营提供，类目页用于了解品类/找竞品，不依赖本产品 listing。

---

## 目录结构

```
build-amazon-ad-keyword-library/
├── SKILL.md                      # 技能主文件（流程/职责/验收）
├── references/
│   ├── decision-table.md         # D0–D21 决策表（唯一规则源）
│   ├── matching-types.md         # 三种匹配触发面（规则见 D10）
│   ├── negatives-and-conflicts.md# 否定来源/作用域（规则见 D10）
│   ├── activity-template.md      # 广告活动最终版结构模板
│   ├── lifecycle-playbook.md     # 三阶段参考（skill 不判阶段）
│   ├── product-facts.md          # 产品事实核实
│   ├── product-facts-auto.md     # 类目页→事实+竞品搜集
│   ├── seller-sprite-workflow.md # 卖家精灵取数/导出
│   ├── intake.md                 # 调用前问询清单
│   ├── acceptance-cases.md       # 验收/回归案例
│   └── changelog.md              # 版本与变更记录
└── scripts/
    ├── read_wordlib.py           # 读词库/校验
    ├── classify_keywords.py      # 资格判断+匹配建议
    └── write_sheet_safe.py       # WPS DISPIMG 安全写 sheet
```

---

## 安装

1. 把 `build-amazon-ad-keyword-library/` 整个目录放到 Qoder 的 skills 目录：
   - 用户级：`C:\Users\<你>\.qoder-cn\skills\`
   - 项目级：`<项目>/.qoder/skills/`
2. 在 Qoder 里执行 `/skills reload`（或重启会话）。
3. 调用：`/build-amazon-ad-keyword-library`，或在对话里说"用这个 skill 搭词库"。

---

## 快速开始（SOP）

### 第 1 步：准备输入（先问后做）
Skill 会先按 `references/intake.md` 问你，最少需要：
1. **产品事实**（8 项）：材质 / 形态类型 / 规格 / 是否含杆配件 / 是否可调 / 硬或软 / 自有品牌 / 是否卖套装
2. **ABA 阈值**（精准）与 **大词阈值**（运营按产品定）
3. **竞品名单**（打哪些品牌/ASIN、哪些不投）
4. **数据源**：卖家精灵导出的 xlsx（关键词挖掘 / 反查 / 拓展流量词）
5. 可选：类目商品页链接（用于了解品类 + 自动找竞品）

### 第 2 步：执行
```
核实产品事实 → 读词库/按列名定位 → 复核相关性(搜索验证) 
→ 资格判断(相关性+ABA) → 分配匹配方式 → 活动编排 → 否定隔离 → 验收
```
产物：一个 xlsx，含 4 个 sheet：
- **词库**（全集，不删；含分层/相关性/ABA/匹配建议/活动入选）
- **广告活动**（新品/成长/成熟 + 分区块 + 逐词 + 4 列：关键词｜匹配方式｜关键词类型｜备注）
- **否定包**（按活动各挂）
- **人工决策记录**（日期/项目/动作/理由/影响）

### 第 3 步：脚本（可选，批量处理）
```bash
# 读词库/校验
py scripts/read_wordlib.py --xlsx 词库.xlsx --sheet 词库

# 资格判断 + 匹配建议（按列名定位，不硬编码列）
py scripts/classify_keywords.py --xlsx 词库.xlsx --sheet 词库 \
   --material "rubber" --threshold 350000 --big-threshold 110000 \
   --own-brand "mikolo" --competitors "yes4all,ritfit" --out 结果.csv

# 安全写 sheet（含 WPS DISPIMG 图片时必用，禁止 openpyxl 保存）
py scripts/write_sheet_safe.py --xlsx 词库.xlsx --sheet 新Sheet --csv data.csv --mode new
```

### 第 4 步：验收
按 `references/acceptance-cases.md` 检查：
- 精准词达标或有例外记录；ABA 缺失不判达标
- 匹配组合符合 D10；无同根自抢
- 材质/形态不符已否定；材质相符但量低标低优先
- 竞品按三用途；品牌防御阈值例外
- 否定按活动各挂；人工决策记录已出

---

## 核心规则速查（详见 `references/decision-table.md`）

| 规则 | 位置 |
|---|---|
| 词库全集不删、活动只筛选；1:N（词库一词一记录，活动一词多行） | D0 / D15 |
| 判定统一用 ABA 周排名，月量仅参考 | D14 |
| 匹配组合矩阵（Exact+Phrase 允许；Phrase+Broad 非技术禁止） | D10 |
| 否定类型（精准=转交已知词；词组=挡整段；不否自身种子） | D10 |
| 材质三分类（硬性不符/相邻替代/待核实，复合材质最长优先） | D4 |
| 品牌防御阈值例外 | D3 |
| 竞品三用途（品牌+品类精准/词组/ASIN） | D7 |
| 广泛/词组不卡阈值、按词根汇总；词组用核心短语+必配否定 | D9 / D18 |
| 阈值未给不默认；大词标准运营定 | D3 / D19 |
| 搜索结果反向验证（纯异类→否定/混合→降级/同类→保留） | D20 |
| 阶段可编排但不判当前阶段/不假定高转化 | D21 |

---

## 常见问题
- **亚马逊反爬/验证码**：商品页/搜索页抓不到 → 请用户手动查看或截图；不硬爬。
- **WPS 文件被占用（`~$` 锁）**：先关闭 WPS/Excel 再写。
- **含 DISPIMG 图片**：只读不重存；编辑用 `write_sheet_safe.py`（zip+XML，保图）。
- **列顺序不同**：按列名/别名定位，不靠列号。
- **25lb / 25 lb / 单复数 / 词序**：是不同记录，ABA 不互换。

---

## 版本
当前 **0.1beta**（2026-10-21）。变更记录见 `references/changelog.md`。
