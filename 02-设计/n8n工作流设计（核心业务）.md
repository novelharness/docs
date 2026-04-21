# n8n 工作流设计（核心业务，强一致联动版）

## 1. 设计目标（针对你的要求）

你强调的是对的：

- 章节创作不是几个独立 pipeline，而是**一个强一致的联动事务流**。
- 必须把 Agent 参与、审批、落库、状态更新做成**单条主链路**。
- 任一步失败都要可回滚、可恢复、可审计。

因此本设计采用：

> **One Main Workflow + Subflow（子流程）**，由主流程统一状态机驱动，所有最终状态落到 Go 主库。

---

## 2. 总体模式：主流程编排 + 事务状态机

## 2.1 主流程名称

`WF-CHAPTER-ORCHESTRATION-V1`

## 2.2 状态机（强一致）

```text
INIT
  -> CONTEXT_LOCKED
  -> CONTEXT_BUILT
  -> OUTLINE_VALIDATED
  -> DRAFT_GENERATED
  -> CONSISTENCY_CHECKED
  -> QUALITY_REVIEWED
  -> HUMAN_APPROVED(optional)
  -> COMMITTING
  -> COMMITTED
  -> STATE_UPDATED
  -> MEMORY_COMPACTED
  -> DONE

失败分支：
ANY_STEP_FAILED -> COMPENSATING -> FAILED
```

## 2.3 强一致关键点

1. **章节级分布式锁**：`novel_id + chapter_no` 只能单 workflow 持有。
2. **幂等键**：`trace_id + chapter_no + step_name`，防重复执行。
3. **最终提交单点**：只有 `COMMITTING` 节点可写主业务表。
4. **提交后状态联动**：章节正文、伏笔状态、角色状态、动态世界状态在同一事务提交。

---

## 3. 一个章节的工程化联动流程（节点级）

> 这是你要的核心：一个联动过程，不拆成互不相关的独立流水线。

## Step 0：任务创建（Trigger）

- 触发源：前端手动触发 / 定时触发 / API 触发。
- 输入：`novel_id`, `chapter_no`, `writing_goal`, `operator`。
- 动作：写入 `tasks` + `task_runs`，状态 `INIT`。

## Step 1：获取锁 + 校验章节前置状态

- 调 Go API：`POST /api/v1/tasks/{id}/lock`
- 校验：
  - 前一章节是否已 `COMMITTED`
  - 当前章节是否已发布（防重复）
  - 是否存在并发任务
- 成功：状态 `CONTEXT_LOCKED`。

## Step 2：构建上下文包（Context Bundle）

- 调 Go API：`POST /api/v1/runtime/context-bundle`
- 返回：
  - 静态世界观
  - 动态世界状态最新快照
  - 当前卷目标与章节细纲
  - Open 伏笔清单
  - 角色关系与知识差
- 成功：状态 `CONTEXT_BUILT`。

## Step 3：Agent 参与（子流程）

### 3.1 参与 Agent（最小集合）

1. **Outline Guard Agent**：校验细纲目标是否清晰、可执行。
2. **Draft Writer Agent**：生成章节草稿。
3. **Consistency Agent**：检查设定、人设、时间线一致性。
4. **Pace & Hook Agent**：检查节奏与章末钩子。
5. **Foreshadow Agent**：检查伏笔埋设/回收是否符合计划。
6. **Editor Agent**：基于问题清单进行定向修订。

### 3.2 子流程执行顺序

`Outline Guard -> Draft Writer -> Consistency -> Pace&Hook -> Foreshadow -> Editor(optional)`

### 3.3 子流程输出

- `chapter_draft`
- `issues[]`
- `quality_score`
- `state_delta_candidate`
- `foreshadow_delta_candidate`

---

## 4. 审批与门禁（强约束）

## 4.1 自动审批门禁

必须全部通过才可进入提交：

- 一致性分数 >= 阈值
- 关键冲突数 = 0（如战力越级、设定冲突）
- 伏笔违规数 <= 阈值
- 敏感规则命中 = 0

## 4.2 人工审批节点（可配置）

以下场景强制人工审批：

- 新卷开篇
- 重大转折章
- 新主角色首次高权重登场
- 自动质检低于灰度阈值

人工审批结果：
- `APPROVE` -> 进入 `COMMITTING`
- `REJECT` -> 回到 `Editor Agent` 修订（最多 N 轮）

---

## 5. 提交与状态联动更新（事务核心）

## 5.1 提交接口（单入口）

- `POST /api/v1/runtime/chapter-commit`

## 5.2 提交内容

- 最终章节正文
- 章节版本信息
- 角色状态变化 `character_delta`
- 动态世界变化 `world_delta`
- 伏笔状态变化 `foreshadow_delta`
- 质量报告与审批记录
- `trace_id`, `config_version`

## 5.3 数据库事务范围（必须同事务）

1. `chapters` / `chapter_versions`
2. `world_dynamic_snapshots`
3. `characters` / `character_relations`
4. `foreshadows`
5. `task_runs` / `audit_logs`

成功后：状态 `COMMITTED -> STATE_UPDATED`。

---

## 6. 提交后处理（非阻塞但可追踪）

## Step A：记忆压缩与向量索引

- 生成章节摘要（事实/情绪双摘要）
- 更新检索索引
- 标记 `MEMORY_COMPACTED`

## Step B：指标回写

- 成本、时延、重试次数、人工介入次数
- 回写监控与报表系统

> 注意：后处理失败不影响主事务提交结果，但必须生成补偿任务。

---

## 7. 回滚与补偿机制

## 7.1 失败分类

- **执行失败**：Agent 调用失败、超时
- **门禁失败**：质检不通过
- **提交失败**：数据库事务失败
- **后处理失败**：摘要/索引失败

## 7.2 补偿策略

- 执行失败：指数退避重试 + 切换备用模型。
- 门禁失败：自动修订，不超过 `max_revision_round`。
- 提交失败：事务自动回滚，任务状态 `FAILED`。
- 后处理失败：异步补偿队列，不回滚已提交章节。

---

## 8. n8n 工作流编排建议（可直接配置）

## 8.1 主流程节点组

1. Trigger Node
2. Lock & Preconditions Node（HTTP -> Go API）
3. Context Build Node（HTTP -> Go API）
4. Agent Runtime Node（HTTP -> Runtime）
5. Auto-Gate Node（Function）
6. Human Approval Node（Webhook/Manual）
7. Commit Node（HTTP -> Go API）
8. Post-Process Node（Runtime/Indexer）
9. Metrics & Notify Node
10. Unlock & Finish Node

## 8.2 必配 n8n 控制参数

- 每节点超时
- 最大重试次数
- 重试退避策略
- 失败通知渠道（飞书/钉钉/邮件）
- 死信队列处理策略

---

## 9. 章节工程化验收标准（Workflow 级）

1. 同一章节并发触发时，只有一个实例可提交成功。
2. 任意步骤失败可恢复，且不出现“正文提交成功但状态未更新”。
3. 提交记录可追溯到完整 Agent 输入输出与审批记录。
4. 章节从触发到提交全链路有统一 `trace_id`。

---

## 9.5 Phase-0 初始化前置工作流（必须先完成）

在 `WF-CHAPTER-ORCHESTRATION-V1` 之前，必须先执行：

- `WF-BOOTSTRAP-NOVEL-V1`（初始化世界/势力/角色/伏笔并冻结快照）

前置校验：
- 存在 `bootstrap_snapshot_version`
- 主角与核心配角档案完整
- 势力卡片与主线骨架完整

---

## 10. 与其他 workflow 的关系

你关心“不要拆散”：

- 主链路只保留一个：`WF-CHAPTER-ORCHESTRATION-V1`。
- 其他流程（运营优化、模型治理）是**旁路支持流程**，不直接改章节主状态。
- 主状态写入权限只在主链路 `Commit Node`。

