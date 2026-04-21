# Claude Code 复用与双服务拆分设计

## 1. 目标

在不重复造轮子的前提下，把 Claude Code 思路拆成两个服务：

1. **Control Plane（静态配置中心）**
2. **Runtime Plane（Agent 运行时）**

## 2. Control Plane（配置中心）

## 2.1 管理对象

- MCP Server 注册与路由配置
- Skill 包与版本管理
- Agent 模板与 Prompt 契约
- 模型供应商与模型路由策略
- 环境配置（dev/stage/prod）

## 2.2 职责边界

- 提供“配置发布”能力，不参与章节执行。
- 对 Runtime 只暴露“只读发布快照”。

## 2.3 技术建议

- 如果要最大化复用 Claude Code 相关 JS/TS 生态：优先 Node.js。
- 如果团队 Go 能力更强，且接受部分自研适配：可用 Go。

**建议：Control Plane 用 Node，Go 服务做业务主库。**

## 3. Runtime Plane（Agent 执行）

## 3.1 必须复用的运行时能力

- Query Loop
- Tool Router + Permission
- 多层 Memory + Context Compaction
- 子 Agent 调度
- Session Resume
- Hook Pipeline

## 3.2 小说域扩展（放在上层）

- 节奏检查器
- 角色一致性检查器
- 伏笔跟踪器
- 世界观冲突检查器

## 3.3 运行链

1. 拉取配置快照（agent/model/skill）
2. 调用 Go API 拉上下文包
3. 执行多 Agent 生成与审校
4. 输出 `chapter_commit` 给 Go API
5. 回写运行指标给平台

## 4. 双服务协作协议

- `config_version`：Runtime 每次执行必须记录配置版本。
- `trace_id`：贯穿 n8n、Runtime、Go API。
- `task_token`：防重复执行与鉴权。

## 5. 为什么不要做成一个服务

1. 配置变更频繁，执行服务要求稳定，生命周期不同。
2. 控制面和数据面混在一起，事故半径大。
3. 后续接入更多业务（非小说）时难复用。

## 6. 落地策略

- 第一阶段先做“逻辑双服务”（代码可先同仓，进程分离）。
- 稳定后再做物理拆分与独立扩缩容。

