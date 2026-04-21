# Agent 规范与角色库（导演 / 主演 / 配角 / 爽点等）

> 目标：在项目初期把 Agent 的职责、边界、输入输出全部固定，防止写作过程发散。

## 1. Agent 统一规范（所有 Agent 必须遵守）

## 1.1 通用元数据

每个 Agent 必须登记：

- `agent_id`
- `agent_name`
- `agent_type`（planner/writer/reviewer/simulator）
- `owner`（归属服务）
- `version`
- `config_version`

## 1.2 统一输入契约

```json
{
  "trace_id": "string",
  "novel_id": "string",
  "chapter_no": 0,
  "context_bundle": {},
  "task_goal": "string",
  "constraints": {
    "must_follow_world_rules": true,
    "must_follow_character_profile": true,
    "forbidden": []
  }
}
```

## 1.3 统一输出契约

```json
{
  "result": {},
  "decision_log": [],
  "risk_flags": [],
  "suggested_state_delta": {}
}
```

## 1.4 统一行为边界

1. 不得修改世界基础设定（仅建议）。
2. 不得绕过主链路直接提交章节。
3. 必须输出结构化 `risk_flags`。
4. 必须保留“为什么这样决策”的 `decision_log`。

---

## 2. 创作核心 Agent 角色库

## A. 导演 Agent（Director Agent）

- **定位**：总控创作节奏与冲突推进。
- **核心职责**：
  1. 把卷目标拆为章节目标。
  2. 决定“本章冲突类型 + 爽点位置 + 章末钩子”。
  3. 协调主演/配角出场比例。
- **关键输入**：卷纲、章节细纲、当前状态快照。
- **关键输出**：`chapter_directive`（章节导演指令）。
- **硬约束**：不得改变世界规则和角色底层人设。

## B. 爽点设计 Agent（Payoff Designer Agent）

- **定位**：专门负责爽点与情绪释放设计。
- **核心职责**：
  1. 设计小爽点/大爽点。
  2. 校验爽点是否来自有效铺垫（不允许凭空强爽）。
  3. 控制爽点密度（避免连续疲劳）。
- **关键输出**：`payoff_plan`（触发条件、兑现方式、代价与后果）。
- **硬约束**：不能破坏战力与设定边界。

## C. 主演 Agent（Protagonist Agent）

- **定位**：主角视角与行为一致性执行者。
- **核心职责**：
  1. 基于主角档案生成决策与行动。
  2. 保证主角语言风格、动机连续。
  3. 维护主角成长曲线。
- **关键输出**：`protagonist_action_plan`。
- **硬约束**：不得获得其不应知道的信息（信息差约束）。

## D. 配角 Agent（Supporting Cast Agent）

- **定位**：配角群体行为模拟与戏份控制。
- **核心职责**：
  1. 管理配角目标、关系和戏份节奏。
  2. 防止配角喧宾夺主。
  3. 提供支线推动但必须回流主线。
- **关键输出**：`supporting_actions`, `relationship_delta_candidate`。

## E. 世界观守护 Agent（World Guardian Agent）

- **定位**：设定一致性裁判。
- **核心职责**：
  1. 校验世界规则是否被违反。
  2. 校验门派/势力/学校设定是否被错误改写。
- **关键输出**：`world_consistency_report`。
- **硬约束**：该 Agent 只有“驳回/警告权”，无提交权。

## F. 伏笔管理 Agent（Foreshadow Manager Agent）

- **定位**：伏笔生命周期管理。
- **核心职责**：
  1. 追踪 open -> planned -> paid_off。
  2. 防止伏笔过期未回收。
- **关键输出**：`foreshadow_delta_candidate`, `foreshadow_risk_report`。

## G. 文风与对话 Agent（Style & Dialogue Agent）

- **定位**：文风统一与对话风格校正。
- **核心职责**：
  1. 保持文风一致。
  2. 角色说话方式符合人设。
- **关键输出**：`style_review_report`。

## H. 质量守门 Agent（Quality Gate Agent）

- **定位**：最终自动门禁。
- **核心职责**：
  1. 聚合一致性、爽点、伏笔、文风评分。
  2. 输出 PASS/REWRITE/REVIEW_REQUIRED。
- **关键输出**：`quality_gate_result`。

---

## 3. Agent 参与顺序（章节主链路）

`Director -> Payoff Designer -> Protagonist/Supporting -> Draft Writer -> World Guardian -> Foreshadow -> Style -> Quality Gate`

说明：
- 主演与配角可以并行产生候选行为，再由 Director 收敛。
- Quality Gate 永远在提交前最后执行。

---

## 4. Agent 配置模板（建议存 Control Plane）

每个 Agent 配置项：

- `prompt_template_id`
- `model_policy_id`
- `tool_permissions`
- `memory_scope`（world/arc/chapter）
- `output_schema_id`
- `max_retry`
- `timeout_ms`

---

## 5. 防发散机制（你关心的关键）

1. 初期初始化后，世界基础设定锁定（变更需审批）。
2. Agent 只可在指定 `memory_scope` 读取上下文。
3. Agent 输出必须过 schema 校验，不合规直接驳回。
4. 主角/配角行为必须经过导演 Agent 收敛后才能进入正文生成。

