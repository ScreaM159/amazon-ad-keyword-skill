# 匹配方式与触发面（参考）

> **单一规则源**：匹配组合与否定规则以 `decision-table.md` 的 **D10** 为准。本文只讲"三种匹配各自的触发面"示例，不重复定义规则。

## 三种匹配的触发面（从窄到宽：Exact < Phrase < Broad）
以投放 `olympic weight plates` 为例：

| 搜索词 | Exact | Phrase | Broad |
|---|---|---|---|
| olympic weight plates | ✓ | ✓ | ✓ |
| olympic weight plate（单数） | ✓(close变体) | ✓ | ✓ |
| 45 lb olympic weight plates（前加词） | ✗ | ✓ | ✓ |
| olympic weight plates set（后加词） | ✗ | ✓ | ✓ |
| weight plates olympic（词序反） | ✗ | ✗ | ✓ |
| olympic plates（丢词） | ✗ | ✗ | ✓ |
| olympic bumper plates（语义近） | ✗ | ✗ | 可能✓ |

要点：
- Exact：完全一致＋close variants（单复数/拼写/空格/连字符）。
- Phrase：必须按顺序连续包含短语，可前后加词；不做语义扩展。
- Broad：不限顺序、可丢词/加词、含同义/语义/拼写错误 → 最宽最易跑偏。

## 组合与否定
- **组合矩阵（Exact+Phrase 允许、Phrase+Broad 非技术禁止、三层按增量判断）** → 见 D10。
- **精准否定 = 转交已知确切词；词组否定 = 排除整段短语；不得对 Phrase 自身种子做词组否定** → 见 D10。
- 不把跨活动重叠写成"必然自抬竞价"；上线用搜索词报告核验。

## 输出记录
每个宽匹配活动必须列出：该活动内**精准否定**了哪些精准词、**词组否定**了哪些品类/异类词。
