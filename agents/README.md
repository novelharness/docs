# Agent Assets（MVP）

本目录是可执行资产层（不是纯说明文档），用于让 Runtime / Control Plane 直接加载 Agent 定义。

## 目录结构

- `_schema/agent.schema.json`：Agent 清单结构约束。
- `<agent_name>/agent.yaml`：Agent 元数据、I/O、模型策略、权限与运行参数。
- `<agent_name>/prompt.md`：系统提示词模板（可版本化）。
- `<agent_name>/output.schema.json`：输出结构校验。

## 当前已实现的关键 Agent

1. `director`
2. `payoff_designer`
3. `protagonist`
4. `supporting_cast`
5. `world_guardian`
6. `quality_gate`

## 运行约束

- 所有 agent 都必须声明：`agent_id / version / config_version / output_schema`。
- 默认不允许写主库（`db_write=false`）。
- 只有 `quality_gate` 可以输出 `PASS/REWRITE/REVIEW_REQUIRED` 门禁结论。

