# Go 后端 API 与数据模型设计（Gin + MySQL）

## 1. 服务职责

Go 服务是小说平台的**业务主服务**，职责：

- 管理小说全生命周期（项目、卷、章、角色、世界观、伏笔）。
- 提供 Runtime 与 n8n 调用的标准 API。
- 提供审计、版本、回滚能力。

## 2. 业务域拆分（建议）

1. `novel-domain`：小说、卷、章节。
2. `world-domain`：静态世界观、动态世界状态。
3. `character-domain`：角色档案、关系、知识差。
4. `foreshadow-domain`：伏笔埋设、状态、回收。
5. `workflow-domain`：任务、执行记录、人工审核节点。
6. `platform-domain`：Agent 绑定、模型策略引用、MCP 绑定关系。

## 3. API 分组（REST）

## 3.1 小说与章节

- `POST /api/v1/novels` 创建小说
- `GET /api/v1/novels/{id}` 查询小说
- `POST /api/v1/novels/{id}/volumes` 创建卷
- `POST /api/v1/chapters` 创建章节草稿
- `POST /api/v1/chapters/{id}/publish` 发布章节
- `POST /api/v1/chapters/{id}/rollback` 回滚章节

## 3.2 世界观

- `POST /api/v1/world/static` 新增静态设定
- `PUT /api/v1/world/static/{id}` 更新静态设定
- `POST /api/v1/world/dynamic/snapshots` 写入动态快照
- `GET /api/v1/world/dynamic/current?novel_id=` 查询当前动态状态

## 3.3 伏笔与任务

- `POST /api/v1/foreshadows` 创建伏笔
- `PUT /api/v1/foreshadows/{id}/status` 更新伏笔状态（open/paidoff/cancelled）
- `GET /api/v1/foreshadows?novel_id=&status=` 伏笔检索
- `POST /api/v1/tasks` 创建创作任务
- `PUT /api/v1/tasks/{id}/status` 更新任务状态
- `POST /api/v1/tasks/{id}/lock` 章节级互斥锁（novel_id + chapter_no）
- `POST /api/v1/tasks/{id}/unlock` 释放互斥锁

## 3.4 Runtime 回写接口（重点）

- `POST /api/v1/runtime/chapter-commit`
  - 入参：`chapter_text`, `state_delta`, `quality_report`, `trace_id`
  - 行为：事务提交章节 + 状态变更 + 审计日志
- `POST /api/v1/runtime/context-bundle`
  - 入参：`novel_id`, `chapter_no`, `intent`
  - 出参：`world + arc + chapter_memory + open_foreshadows`

## 4. MySQL 核心表（最小集）

- `novels`
- `volumes`
- `chapters`
- `chapter_versions`
- `world_static_items`
- `world_dynamic_snapshots`
- `characters`
- `character_relations`
- `foreshadows`
- `tasks`
- `task_runs`
- `audit_logs`

## 5. 数据一致性策略

1. **章节发布事务**：`chapters + chapter_versions + world_dynamic_snapshots + foreshadows + audit_logs` 同事务。
2. **幂等键**：`trace_id + action_type + step_name` 防止重复执行。
3. **乐观锁**：动态世界状态使用 `version` 字段避免并发覆盖。
4. **章节互斥锁**：同一 `novel_id + chapter_no` 只允许一个 workflow 实例进入提交阶段。

## 6. 安全与权限

- JWT + RBAC：作者、编辑、运营、管理员、系统账号。
- Runtime 使用服务账号 + 签名请求。
- 关键接口（publish/rollback/commit）必须写审计日志。

## 7. 实现顺序（不写代码版）

1. 先冻结 API 契约（OpenAPI）。
2. 再冻结表结构（DDL + 迁移规范）。
3. 最后接入 n8n 和 Runtime。

