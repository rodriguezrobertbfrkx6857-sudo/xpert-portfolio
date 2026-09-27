# EVIDENCE MAP

最终版预计 10 页 A4。页面只引用本目录 `assets/` 的合成截图、授权副本源码、公开 GitHub README/源码和本次复核结果。

| 页码 | 主题 | 主要证据 | 交付能力 |
|---|---|---|---|
| 01 | Evidence first engineering | 7 个主项目的能力范围；事实边界 | 证据优先的工程叙事 |
| 02 | Capability map | 需求到验收的统一方法链 | 规格化、实现、测试、回归 |
| 03 | Algorithm / STEM | GPU Kernel Lab 源码结构、非规则尺寸、CPU-only table；Repro Kit 校验 | 算法、内存、科学证据 |
| 04 | Agent engineering | Optimizer pipeline、8 tests、transpose `INCONCLUSIVE`、reduction `REJECT` | Agent 闭环、门禁、诚实决策 |
| 05 | AI safety | RAG detector/scorer/conflict/self-purify、risk/evidence formula、6 backend tests | 投毒检测、溯源、隔离 |
| 06 | QA Sentinel | `assets/qa-hero.png`、`assets/qa-findings.png`、副本 2 tests/build/E2E | 多视口 QA、缺陷发现、报告 |
| 07 | Webhook Observatory | `assets/webhook-dashboard.png`、`assets/webhook-retry.png`、HMAC/retry facts | API 安全、故障注入、重试 |
| 08 | Document Pipeline | `assets/doc-workspace.png`、`assets/doc-extraction.png`、backend 12 tests | 多格式解析、抽取、溯源、diff |
| 09 | Additional work | `assets/mcp-hero.png`、`assets/browserops-table.png`；Data Cleanroom summary | MCP、浏览器自动化、数据质量 |
| 10 | Evidence / privacy audit | source map、限制、未声明项、公开链接 | 可复核、可交接、隐私边界 |

## 证据分层

1. **运行证据**：本次在 `extracted/` 副本中完成的测试、构建、E2E、demo 和结果文件。
2. **源码证据**：模块名、函数逻辑、测试用例和配置文件；用于证明实现边界。
3. **项目自带证据**：README、报告、截图和实验 JSON；只在和源码一致时引用。
4. **背景证据**：公开 GitHub 页面；不把 Star/Fork 或未核验的自述当作工程成果。

## 复核原则

任何无法映射到源码路径、测试输出、结果 JSON、合成截图或公开页面的数字都不进入最终页面。缺失的 CUDA、frontend source、真实用户指标和游戏/Mod 目录均在作品集内显式标注为边界。
