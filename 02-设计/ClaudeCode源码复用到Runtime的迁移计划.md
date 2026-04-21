# ClaudeCode 源码复用到 Runtime 的迁移计划

## 背景

你给的仓库：`https://github.com/oboard/claude-code-rev`。

当前容器网络对 GitHub 访问返回 `403 CONNECT tunnel failed`，所以这版先按“ClaudeCode-style 内核”完成可运行改造；
后续你本地可拉源码后，按本计划逐步做等价迁移。

## 已完成的 Runtime 改造（本仓）

- 增加 `ClaudeCodeLikeRuntime` 内核（run/task/events in-memory state center）
- 增加 `create_run -> execute_all -> get_run` 生命周期
- 保留信息差输入包（`visible_to` / `known_by`）
- 增加 `/api/v1/runs`、`/api/v1/runs/{id}/execute`、`/api/v1/runs/{id}` API

## 与 ClaudeCode 对齐的迁移步骤（建议）

1. **Session 层迁移**
   - 把 claude-code 的会话对象映射到 `Run + AgentTask`
2. **Tool 执行层迁移**
   - 接入真实 tool router，替换当前 mock summary
3. **Prompt/Policy 层迁移**
   - 把角色内核/信息差策略注入 system/user prompt builder
4. **输出校验层迁移**
   - 用结构化 schema + quality gate 替换关键词检查
5. **持久化层迁移**
   - 从 in-memory 改成 PostgreSQL（runs/tasks/events/facts）
6. **编排层迁移**
   - n8n 只保留流程控制，语义回环由 runtime 返回 reason codes

## 目标接口兼容

- `POST /api/v1/runs` 创建运行
- `POST /api/v1/runs/{run_id}/execute` 执行
- `GET /api/v1/runs/{run_id}` 查询
- `POST /api/v1/chapters/run` 一步执行（兼容旧调用）

这样你后续换掉内核实现，不需要改 n8n 工作流。
