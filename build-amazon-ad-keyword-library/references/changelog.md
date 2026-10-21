# 变更记录（Changelog）

## 0.1beta（2026-10-21）
首次发布（beta）。

### 新增
- `SKILL.md`：职责边界、调用流程（先问后做）、Step -1（上架前：类目页 + 用户产品事实 + 竞品搜集）、工作流、输出、验收、缺失/冲突处理。
- `references/`：`decision-table.md`(D0–D21)、`matching-types.md`、`negatives-and-conflicts.md`、`lifecycle-playbook.md`、`activity-template.md`、`product-facts.md`、`product-facts-auto.md`、`seller-sprite-workflow.md`、`acceptance-cases.md`、`intake.md`。
- `scripts/`：`read_wordlib.py`、`classify_keywords.py`、`write_sheet_safe.py`。

### 关键规则
- **词库全集不删、活动只筛选**；1:N（词库一词一记录，活动一词可多行）— D0/D15。
- 判定统一用 **ABA 周排名**，月搜索量仅参考 — D14。
- **匹配组合矩阵**：Exact+Phrase 允许（精准否定转交）；Phrase+Broad 非技术禁止、按增量判断 — D10。
- **否定类型**：精准否定=转交已知词；词组否定=挡整段；不得对 Phrase 自身种子做词组否定 — D10。
- **材质三分类**：硬性不符 / 相邻替代 / 待核实；复合材质最长优先（cast iron 不误判 iron）— D4。
- **品牌防御阈值例外** — D3；**竞品三用途**（品牌+品类精准/词组/ASIN）— D7；**竞品名单由用户给** — D16。
- **广泛/词组不卡 ABA 阈值、按词根汇总**；**词组用核心短语 + 必配词组否定异类 + 与精准隔离** — D9/D18。
- **空格写法**：原始词/ABA 始终分开，活动层选代表写法，不承诺完全等价 — D18。
- **阈值未给不默认**，标待确认；**大词标准运营定** — D3/D19。
- **搜索结果反向验证**：纯异类→否定、混合→降级、同类→保留 — D20。
- **阶段可编排但不判当前阶段**、不假定已高转化（缺数据写条件建议）— D21。
- 含 DISPIMG 用 `write_sheet_safe.py`；必出「人工决策记录」— D13。

### 修正
- 规则统一到 **D10 单一规则源**；`matching-types.md`、`negatives-and-conflicts.md` 改为引用，删除"Phrase+Broad 二选一 / 三重自抢 / 不能用否定解决"旧规则。
- `classify_keywords.py` 重写：按列名定位、先资格校验（相关性/ABA）再定活动、ABA 缺失不判达标、复合材质最长匹配、纯品牌→不投/ASIN。
- 验收：脚本行为 10/10 通过；文档旧规则残留复检为 0。

### 已知限制 / 待验证
- 亚马逊反爬：商品页/搜索页可能需用户手动查看或截图。
- 多源 ABA/搜索量的 min/max 合并是启发式，需保留来源与冲突。
- 阶段切换阈值、阈值/大词/竞品名单均为项目参数，由运营按任务给。
