# 小说 Agent 系统总体架构（复用 Claude Code Runtime 思路）

## 1. 架构目标

- **稳定产出**：持续生成章节，不因上下文膨胀失控。
- **质量可控**：每章都可过“节奏、人设、设定一致性”门禁。
- **可追溯可恢复**：任意章节可回放生成链路并断点恢复。

## 2. 分层架构

```text
[创作交互层]
  - 需求输入 / 章节看板 / 人工审核

[编排控制层]
  - Orchestrator（主控）
  - Chapter Query Loop
  - Hook Pipeline（前后置质检）

[领域能力层]
  - 设定架构师 Agent
  - 大纲规划 Agent
  - 正文生成 Agent
  - 节奏分析 Agent
  - 质量守门 Agent

[运行时基础层]
  - Memory Manager（World/Arc/Chapter）
  - Tool Router + Permission
  - Session Storage + Resume
  - Event Bus

[数据持久层]
  - 设定库 / 大纲库 / 章节库
  - 角色状态库 / 关系库 / 伏笔索引库
  - 日志与评估指标库
```

## 3. 核心执行链（章节级）

1. `load_context`: 读取世界设定 + 卷纲 + 最近章节摘要 + 当前角色状态。
2. `plan_chapter`: 生成本章目标、冲突、节奏计划。
3. `draft_chapter`: 生成正文草稿。
4. `run_hooks_pre_publish`: 触发一致性与质量检查。
5. `revise_if_needed`: 不通过则局部重写。
6. `commit_state`: 写入章节正文与状态更新。
7. `compact_memory`: 摘要压缩并更新检索索引。

> 这就是小说版的 query loop：每章一个可回放事务。

## 4. 模块清单（最小可行）

### 4.1 Orchestrator（主控编排）

- 职责：调度各 Agent、控制重试、收敛输出。
- 输入：章节任务请求。
- 输出：章节结果 + 状态变更包。

### 4.2 Consistency Checker（一致性校验）

- 校验项：
  - 人设一致（角色口吻/动机不突变）
  - 设定一致（力量体系、规则不越界）
  - 时间线一致（事件先后正确）

### 4.3 Pace & Hook Analyzer（节奏与钩子检查）

- 校验“三章一小爽，十章一大爽”是否偏离。
- 检查章末钩子强度与信息密度。

### 4.4 Memory Manager（分层记忆）

- WorldMemory：静态设定
- ArcMemory：卷级策略与伏笔计划
- ChapterMemory：最近章节事实与情绪轨迹

## 5. 数据模型建议（先文档契约，后实现）

- `chapter_task`
  - `task_id`, `chapter_no`, `target`, `status`
- `chapter_artifact`
  - `draft_text`, `final_text`, `quality_report`, `revision_round`
- `state_delta`
  - `character_delta`, `relationship_delta`, `task_delta`, `foreshadow_delta`
- `memory_snapshot`
  - `world_ref`, `arc_summary`, `chapter_summary`, `embedding_keys`

## 6. 技术策略

- **先单线程串行提交**：确保状态一致。
- **并行只发生在候选草稿生成**：并行出多个版本，再由主控合并。
- **所有写操作都带审计日志**：章节生成必须可追溯。

## 7. 设计完成定义（DoD）

架构阶段完成的标准：

1. 每个模块有“职责/输入/输出/失败处理”定义。
2. 每条章节执行链有“触发条件/重试策略/终止条件”。
3. 数据模型可支持“回滚到任意章节并重跑”。

