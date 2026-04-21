# ClaudeCode 风格 Runtime 复用与信息差控制设计

## 1. 你的设想是否可行

可行，而且是当前最稳妥路线：
- 把每个 Agent 当成一个“精简版 ClaudeCode runtime 执行单元”；
- 去掉 CLI/交互壳，保留任务执行、工具调用、上下文管理、输出校验能力；
- 用统一协议下发任务卡，保证角色内核、输入结构、输出契约一致。

这比“从零造 Agent 框架”更快落地。

## 2. 单 Agent Runtime 最小内核

每个 Agent 执行时应包含 6 个模块：
1. `Input Assembler`：拼装任务卡 + 最近事件 + 已知事实
2. `Knowledge Filter`：按可见性裁剪信息（信息差）
3. `Role Kernel`：角色核心约束（例如主角必须体现成长/抉择）
4. `Tool Router`：调用检索、规则检查、摘要工具
5. `Output Validator`：校验结构、角色一致性、事实冲突
6. `Patch Generator`：失败时生成最小修复补丁

## 3. 信息差控制模型（关键）

每条事件/事实都带可见性：
- `visible_to`: 事件可见角色列表
- `known_by`: 事实已知角色列表

示例：
- 皇城密令只对导演与守卫可见；
- 主角不知道密令，于是会做“错误但合理”的判断；
- 配角只看到局部信息，形成喜剧误判或戏剧冲突。

这会自然产生“合理/搞笑”的剧情差异。

## 4. 协议建议

Agent 输入包（Task Packet）至少包含：
- `chapter_id`
- `task_goal`
- `recent_events`（已过滤）
- `known_facts`（已过滤）
- `role_core`

Agent 输出包至少包含：
- `draft_patch`
- `fact_deltas`
- `risk_flags`
- `self_check`

## 5. 在当前仓库里的落地

已在 runtime 增加“信息差感知”的上下文策略：
- 基于 `visible_to/known_by` 过滤事件与事实
- 为每个 Agent 构建最小任务包
- 增加 role_core 关键词检查入口

后续只需把 mock 输出替换为真实模型调用即可。
