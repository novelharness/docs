# Claude Code Runtime 复用策略（面向小说创作系统）

## 1. 调研目标

基于你给的 `liuup/claude-code-analysis` 分析视角，抽取 Claude Code Runtime 中对“小说多 Agent 系统”最有价值的可复用能力，并映射为可落地组件。

## 2. 复用原则

1. **先复用运行时，不先复用 UI**：优先拿执行内核、记忆、权限、持久化。
2. **先单主控，再多 Agent 扩展**：先稳态产出，再追求并发复杂度。
3. **小说域特化在上层做，不污染 Runtime 核心**：Runtime 保持通用，业务规则放在 Novel Domain Layer。

## 3. 能力映射表（Claude Code → 小说系统）

| Claude Code Runtime 能力 | 小说系统复用目标 | 实施方式 |
|---|---|---|
| Query Loop（统一主循环） | 统一章节任务执行生命周期 | 建立 `ChapterQueryLoop`：读取上下文→规划子任务→调用工具/Agent→合并结果→提交状态 |
| Tool Router + Tool Permission | 工具调用可控、可审计 | 建立写作工具白名单（检索、摘要、状态更新、风格检查）+ deny-by-default |
| 多层 Memory（长期/项目/动态） | 世界观、卷纲、章节状态分层记忆 | 固化为 WorldMemory / ArcMemory / ChapterMemory 三层存储 |
| Context Compaction | 降低 token 成本，防止长文漂移 | 每章结束自动做摘要压缩 + 伏笔索引 + 检索重建 |
| Session Storage / Resume | 断点续写与任务恢复 | 每个章节任务有 `session_id`，支持失败重试与恢复 |
| Hooks/Event Pipeline | 关键节点自动质检 | 在 pre-generate/post-generate/post-review 挂钩执行质量规则 |
| 子 Agent 机制 | 分工协作（设定/大纲/正文/审校） | 主控 Agent 调用专职子 Agent，统一汇总输出 |
| 安全沙箱思路 | 防止工具误操作 | 写操作分级，核心资产（设定库/已发布章节）默认只读 |

## 4. MVP 必须复用的 6 个 Runtime 能力

1. **统一 Query Loop**：没有主循环就无法稳定编排。
2. **分层 Memory**：没有分层就会“写着写着人设崩”。
3. **Context Compaction**：没有压缩会快速超窗、变贵、变乱。
4. **Session 持久化**：没有恢复能力就无法稳定长跑。
5. **Tool Permission**：没有权限就难以工程化托管。
6. **Hooks 质检链**：没有门禁会导致质量波动巨大。

## 5. 不建议直接照搬的部分

- **面向编码任务的工具集**：小说任务需要替换成剧情工具（伏笔、节奏、角色一致性）。
- **终端交互优先的 UX 假设**：小说创作更偏“编辑器 + 看板 + 审核流”。
- **以代码 diff 为核心的反馈机制**：应切到“章节差异 + 状态差异 + 设定冲突差异”。

## 6. 风险与对策

- **风险 A：复用过度，导致写作体验像 DevOps。**
  - 对策：Runtime 内核保留工程性，前台交互保持创作感（章节卡片、角色卡、剧情脉络图）。
- **风险 B：多 Agent 并行导致设定冲突。**
  - 对策：主控串行提交状态，任何写入都经过一致性校验器。
- **风险 C：压缩摘要丢失情绪细节。**
  - 对策：摘要拆分为“剧情事实摘要 + 文风情绪摘要”双通道。

## 7. 调研结论

你现在最应该做的不是“再加新 Agent”，而是先把 Runtime 复用骨架搭好：

- 先落 `QueryLoop + Memory + Persistence + Hooks + Permission`，
- 再逐步扩 `多角色协作 + 自动运营优化`。

这样能把“泛想法”变成“连续可交付系统”。

