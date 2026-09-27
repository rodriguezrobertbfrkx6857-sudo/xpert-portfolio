# FACT CHECK

核验日期：2026-09-16。核验对象：最终作品集中的项目、能力和边界表述。`Verified` 只表示在授权副本、公开源码或本次副本运行中找到对应证据；不表示生产环境认证。

| 作品集表述 | Verified | 证据 | 边界 / 写法 |
|---|---|---|---|
| 主作品集包含 7 个项目 | YES | `reviews/PROJECT_INVENTORY.md` 的主选择；`source/index.html` 逐页映射 | 这是编辑选择，不是项目总数 |
| Agentic GPU Optimizer 有 build/correctness/benchmark/decision 闭环 | YES | `extracted/public/agentic-gpu-optimizer/optimizer/orchestrator.py`、`runner/`、`evaluator/` | 描述为代码闭环，不称为生产 Agent |
| Agentic GPU Optimizer 本次测试 8 项通过 | YES | 副本运行 `python -m pytest -q`：8 passed | 测试通过不等于 CUDA 性能已验证 |
| Agentic transpose 的 CPU candidate 快于 baseline | YES | `extracted/public/agentic-gpu-optimizer/experiments/transpose/` 的 JSON bundle；约 4.3958 ms 对 0.0452 ms | 只写 CPU-only observation；决策为 `INCONCLUSIVE` |
| Agentic reduction 没有被性能门禁接受 | YES | `experiments/reduction/` JSON；correctness PASS、decision `REJECT` | 不把失败隐藏为成功案例 |
| GPU Kernel Lab 包含 transpose/reduction/GEMM 等内核 | YES | `extracted/public/gpu-kernel-performance-lab/README.md`、`src/`、`tests/` | 当前环境没有 CUDA/CMake build；不写本次 GPU 构建通过 |
| GPU Kernel Lab 有非规则尺寸测试 | YES | `tests/` 中 65x97、65x65 transpose，31/1003 等 reduction，非方阵 GEMM | 这是源码测试覆盖，不是大规模性能承诺 |
| 当前公开 GPU 结果是 CPU-only | YES | 两个 GPU 项目 README、results/summary；本次环境 CUDA unavailable | 所有速度数字必须标注 CPU reference/fallback |
| Scientific Reproducibility Kit demo 可复现并通过校验 | YES | 副本运行 `pytest`：4 passed；`run_demo.py`、`validate_bundle.py` exit 0；validation JSON `valid: true` | 作为证据层补充，不写成科研平台 |
| RAG 投毒项目包含检测、评分、冲突和 self-purify | YES | `extracted/public/rag-poisoning-detection-trusted-provenance/backend/` 下 `detector.py`、`scorer.py`、`consistency.py`、`conflict_graph.py`、`self_purify.py` | 定位为本机/可信局域网原型；公开版 frontend 只有 dist |
| RAG backend 本次 6 项测试通过 | YES | 副本运行 `backend/tests`：6 passed，2 warnings | 不扩展为公网安全保证 |
| QA Sentinel 能检查多视口和常见 Web QA 项 | YES | `extracted/local/02-qa-sentinel/` runner、reporters、fixtures | 规则是启发式审计，不等同完整 WCAG 或性能认证 |
| QA Sentinel 本次测试通过 | YES | 副本 `npm test`：2 passed；build exit 0；E2E 1 passed | E2E 使用受控 fixture；报告输出是合成证据 |
| Webhook Observatory 使用 timing-safe HMAC 和有限重试 | YES | `extracted/local/04-webhook-observatory/src/lib/hmac.ts`、`src/lib/retry.ts` | 默认内存存储；demo secret 仅离线演示 |
| Webhook Observatory 本次测试通过 | YES | 副本 4 个测试文件、16 passed；build exit 0；E2E 1 passed | 不写成真实生产 webhook 网关 |
| Document Pipeline 支持多格式结构解析、抽取和 diff | YES | `extracted/local/06-document-pipeline-studio/backend/` parsers/extractor/diff_engine；frontend UI | v1 不含扫描 PDF OCR；默认内存文档库 |
| Document Pipeline backend/frontend 本次复核通过 | YES | backend pytest 12 passed；frontend build exit 0、E2E 1 passed；前端复核有 proxy fallback | 前后端分开复核；不能暗示一次端到端 backend-connected 通过 |
| MCP Workbench 包含 schema 驱动请求构造和风险启发式 | YES | `extracted/local/01-mcp-workbench/src/lib/mcp/`、API route、测试 | safety 是启发式；calculator 的 demo `Function` 执行边界需保留 |
| MCP Workbench 本次测试通过 | YES | 2 test files、14 passed；build exit 0；E2E 2 passed | demo server 与合成数据，不是任意远程工具执行承诺 |
| 本地授权目录没有发现 itch 游戏或 Minecraft Mod | YES | 只盘点用户指定本地项目库根目录；详见 inventory | 结论范围限定为本轮授权可见目录，不推断其他磁盘 |
| 项目没有真实用户指标或真实个人数据 | YES | README/源码审计；截图人工检查；样例为 synthetic | 作品集不使用 stars、forks、访问量、客户名或真实账号数据 |

## 明确不写入作品集的表述

- “GPU 已在本机跑通”或任何未经当前 CUDA 主机验证的 GPU speedup。
- “production-grade / battle-tested / 100% secure / 完整量子 SDK”等无直接证据的结论。
- 真实用户数、客户名称、商业收入、增长率、线上 SLA、Star/Fork 等指标。
- itch 游戏、Minecraft Mod 或对应验收结果。
