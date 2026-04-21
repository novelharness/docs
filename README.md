# Novel Agent Monorepo (Runtime + MCP + Skills + n8n)

这是一个先跑通流程的单仓 MVP：
- `agents/`：已有 Agent 定义资产
- `runtime/`：Agent Runtime（FastAPI）
- `mcp/`：MCP 适配服务（工具列表、技能加载）
- `skills/`：可加载的技能包
- `n8n/workflows/`：可导入的 n8n 工作流

## 1. 启动

```bash
docker compose up -d
```

服务端口：
- runtime: `http://localhost:8100`
- mcp: `http://localhost:8200`
- n8n: `http://localhost:5678`

## 2. 在 n8n 里导入流程

1. 打开 n8n UI，导入 `n8n/workflows/chapter-runtime-demo.json`
2. 激活 workflow
3. 调用 Webhook：

```bash
curl -X POST http://localhost:5678/webhook/chapter-run \
  -H 'Content-Type: application/json' \
  -d '{"chapter_id":"ch001","brief":"主角首次觉醒","target_words":2000}'
```

## 3. 直连 runtime 调试

```bash
curl -X POST http://localhost:8100/api/v1/chapters/run \
  -H 'Content-Type: application/json' \
  -d '{"chapter_id":"ch001","brief":"主角首次觉醒","target_words":2000}'
```

## 4. 验证

```bash
./scripts/smoke_test.sh
```


## 5. 架构设计补充

- 参考：`02-设计/n8n-FastGPT-ClaudeCode协同架构设计.md`（回答“平台内 Agent 与自研 Runtime 如何协同”）。
- 参考：`02-设计/初始化流程-回环重写-长篇状态同步方案.md`（回答 loop、审核打回、200万字状态同步）。
