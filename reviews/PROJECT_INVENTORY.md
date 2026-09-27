# PROJECT INVENTORY

盘点日期：2026-09-16  
用途：ByteDance Xpert 专家社区技术作品集的内部选材与真实性审计。  
读取边界：本地 GitHub 项目库中的项目目录；用户指定的公开 GitHub 账号及其公开仓库。未读取浏览器、凭据、`.git` 内部敏感文件、真实 `.env`、支付/身份/聊天资料。

## 筛选档位

- **A — 主作品集候选**：有真实源码、清晰模块、测试/构建/运行证据，能直接证明 Coding、Agent、STEM、QA 或安全评估能力。
- **B — 补充候选**：有可核验代码和明确主题，但存在运行环境限制、公开版不完整或证据深度不足。
- **C — 证据参考**：可用作素材/结构参考，不适合单独作为主项目页面。
- **D — 不选**：重复、纯素材、空壳或当前证据不足。

## 本地授权项目

| 项目 | 类型 / 来源 | 技术栈与核心功能 | 规模 | README | 测试 | Build / 运行 | 发布产物 | 截图 | 文档 / QA | 用户证据 | 档位与理由 | 风险或不足 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 01-mcp-workbench | AI 开发者工具；本地 GitHub 项目库 | Next.js 14、TypeScript、MCP JSON-RPC；Schema 驱动请求构造、工具安全启发式、执行历史、延迟观测 | 中等，全栈 UI + API + demo server | 有 | Vitest、Playwright E2E | 副本 `npm test` 14 passed、build exit 0、E2E 2 passed | 本地 UI 截图 | 4 张 | 架构、Portfolio Notes、E2E | 无；全部为合成 demo | **A**：能证明 Agent 工具检查、Schema 解析和安全意识；作为主项目或强补充 | 安全分类是启发式；计算器在 allowlist 后仍使用 `Function`，需在作品集注明边界 |
| 02-qa-sentinel | Web QA / Agent QA；本地 GitHub 项目库 | Playwright、Next.js、TypeScript；HTTP、console、链接、图片、表单、SEO、响应式溢出检查，多格式报告 | 中等，CLI + dashboard + reporters | 有 | Vitest、Playwright E2E；已有 PASS/FAIL 报告 | 副本 `npm test` 2 passed、build exit 0、E2E 1 passed | HTML/MD/JSON 报告、响应式截图 | 4 张 + 多次报告截图 | Portfolio Notes、测试报告 | 无；fixture 为合成站点 | **A**：最直接证明找 Bug、边界检查、回归与证据交付能力 | 规则为启发式审计，不等同完整可访问性/性能标准 |
| 03-data-cleanroom-studio | 数据质量 / 本地 ETL；本地 GitHub 项目库 | Next.js、React、TypeScript、PapaParse；CSV/JSON profiling、清洗、去重、验证、导出 | 中等，浏览器内数据引擎 + UI | 有 | Vitest、Playwright E2E | 副本测试 9 passed、build exit 0、E2E 1 passed | UI 截图、合成样例数据 | 4 张 | Portfolio Notes、架构说明 | 无；样例均为合成 | **B**：补足数据评估、规则验证和隐私设计 | 规模边界约 50,000 行；仅浏览器内存，非大数据后端 |
| 04-webhook-observatory | API 安全 / Webhook 调试；本地 GitHub 项目库 | Next.js、TypeScript、Node crypto；timing-safe HMAC、契约校验、重放、有限指数退避 | 中等，全栈 API + dashboard | 有 | Vitest 单元/契约、Playwright E2E | `RELEASE_VALIDATION.md` 记录 clean clone、build、16 tests、E2E PASS | 4 张截图、合成事件 | 4 张 | Release Validation、Security Audit | 无；demo secret 明确为合成 | **A**：能证明安全边界、故障注入、重试上限和回归思维 | 默认内存存储；demo secret 只能用于离线演示 |
| 05-browserops-capture | 浏览器自动化 / Extension；本地 GitHub 项目库 | Chrome MV3、React、TypeScript、Vite；activeTab DOM 提取、表格/链接/元数据解析、RFC 4180 导出 | 中等，扩展 UI + 纯函数引擎 | 有 | Vitest DOM、Playwright E2E | `RELEASE_VALIDATION.md` 记录 clean clone、build、10 tests、E2E PASS | 扩展截图、离线 demo site | 4 张 | Release Validation、Security Audit | 无；只处理用户主动点击的活动页 | **B**：作为浏览器自动化与隐私设计补充 | 不覆盖 Canvas/WebGL 表格和无限滚动；未作为主项目页 |
| 06-document-pipeline-studio | 文档处理 / ETL；本地 GitHub 项目库 | FastAPI、Python、Pydantic、pypdf + React/TypeScript；多格式解析、结构切分、实体抽取、溯源、diff、批处理 | 中等偏大，Python backend + frontend + samples | 有 | Pytest、Vitest、Playwright E2E | backend 12 passed、frontend build exit 0、E2E 1 passed；前端有 proxy fallback 日志 | 样例 PDF、4 张 UI 截图、JSON/MD 导出 | 4 张 | Security Audit、Portfolio Notes | 无；样例邮箱使用保留域 | **A**：能证明结构化解析、可追溯性、边界声明和测试验收 | v1 明确不含扫描 PDF OCR；默认内存文档库 |
| `_clean_validation_06` | 文档处理 clean-validation 副本；本地 GitHub 项目库 | 与 06-document-pipeline-studio 内容重复 | 重复副本 | 有 | 有 | 作为验证副本 | 4 张 | 4 张 | 有 | 无 | **D**：不重复纳入；仅作为发现到的重复目录记录 | 若纳入会重复计算同一项目证据 |

本地盘点中没有发现显式命名或结构明确的 itch 游戏项目目录，也没有 Minecraft Fabric/Forge Mod 项目目录。该结论只针对本次授权可见的本地 GitHub 项目库根目录；因此最终作品集不虚构游戏或 Mod 页面，也不声称已完成游戏运行验收。

## 公开 GitHub 项目

来源账号：<https://github.com/rodriguezrobertbfrkx6857-sudo>。仅通过匿名 HTTPS 读取公开页面 / README / 公开源码 / 公开实验文件；不登录、不使用 Token、不 push、不创建 Issue/PR。Star、Fork、访问量不作为选材依据。

| 项目 | 类型 / 技术栈 | 代码与结构证据 | 测试 / 运行 / 产物证据 | 截图 / 文档 | 用户证据 | 档位与理由 | 风险或不足 |
|---|---|---|---|---|---|---|---|
| [agentic-gpu-optimizer](https://github.com/rodriguezrobertbfrkx6857-sudo/agentic-gpu-optimizer) | Agent 工程、GPU 优化；Python、NumPy、PyYAML，保留 CUDA workload | `optimizer/orchestrator.py` 串起 build、correctness、benchmark、profiler、patch、decision；`evaluator/` 与 `runner/` 模块真实存在 | 3 个 pytest 文件；transpose 实验有完整 JSON bundle；真实结果为 CPU-only，transpose `INCONCLUSIVE`、reduction `REJECT` | README、实验 summary / decision JSON | 无 | **A**：最强的证据优先 Agent 评估项目，能展示接受/拒绝/不确定三态 | 当前机器无 CUDA；CPU 时间不能形成 CUDA 结论；需保留该限制 |
| [rag-poisoning-detection-trusted-provenance](https://github.com/rodriguezrobertbfrkx6857-sudo/rag-poisoning-detection-trusted-provenance) | AI 安全 / RAG 可信溯源；FastAPI、Python、SQLite、本地前端 dist | backend 真实包含 detector、scorer、consistency、conflict graph、evidence、retrieval、RAG、redteam、self-purify | 后端 3 个测试入口；demo / blind / poison / conflict 数据集；公开版 CI 覆盖后端与前端预览 | README、实验明细、预构建 frontend/dist | 无；数据声明为合成 | **A**：直接覆盖投毒检测、冲突裁决、隔离、自净化和证据链 | 前端源代码未随公开版提供；定位为本机/可信局域网原型，不是公网部署方案 |
| [gpu-kernel-performance-lab](https://github.com/rodriguezrobertbfrkx6857-sudo/gpu-kernel-performance-lab) | CUDA / STEM；C++17、CUDA、CMake、NumPy fallback | vector add、transpose、reduction、GEMM CUDA kernels；shared memory、padding、warp shuffle、tiled GEMM | CMake 注册 4 个 CUDA tests；无 CUDA 时有 CPU smoke；公开报告记录 CPU-only 参考测量与边界案例 | README、结果 JSON/MD、执行模型与内存文档 | 无 | **A**：最清晰的算法/内核/边界测试项目 | 当前公开结果没有 GPU 实测；CPU fallback 的速度不能写成 GPU 加速 |
| [spectral-operator-gpu-lab](https://github.com/rodriguezrobertbfrkx6857-sudo/spectral-operator-gpu-lab) | 频谱算子 / FNO；Python、PyTorch、CUDA extension | reference / improved / custom complex64 CUDA / fused kernel；3 个测试文件 | 结果 JSON/MD；5 组 operator shape、complex multiply、Mini-FNO；CUDA unavailable 时显式 skip | README、`docs/`、profiling README | 无 | **B**：技术深度很高，可作为 GPU/STEM 补充证据 | 当前报告为 CPU-only；仓库需在 CUDA host 重测；不作为主页核心性能结论 |
| [scientific-reproducibility-kit](https://github.com/rodriguezrobertbfrkx6857-sudo/scientific-reproducibility-kit) | 科学证据验证；Python、SHA-256 manifest、JSON contract | `bundle.py`、`validate.py` 与 demo bundle；校验环境、benchmark、decision、source hashes | 2 个 pytest 文件；可生成确定性 demo bundle；拒绝 CPU-only 冒充 CUDA | README、`SKILL.md`、validation JSON | 无 | **B**：适合作品集证据层与方法页 | 不是 kernel、不是 Web 产品；功能范围是 bundle 完整性与语义校验 |
| [quantum-statevector-gpu-lab](https://github.com/rodriguezrobertbfrkx6857-sudo/quantum-statevector-gpu-lab) | 量子态矢量 / CUDA；Python、NumPy、CMake、CUDA | 小端序布局、单比特 gate pair update、CPU reference/vectorized candidate/CUDA kernel | 2 个 pytest 文件；CPU demo 可运行；CUDA 结果要求硬件门禁 | README、results、SKILL.md | 无 | **B**：算法与科学计算补充候选 | 明确不是完整量子 SDK；当前主机无 CUDA |
| [ai4s-scientific-operator-agent](https://github.com/rodriguezrobertbfrkx6857-sudo/ai4s-scientific-operator-agent) | AI4S / Poisson-Jacobi；Python、NumPy、CMake、CUDA | ground truth、向量化 CPU、naive/tiled CUDA stencil、误差指标、三态决策 | pytest、demo、报告生成；CUDA unavailable 时保持 `INCONCLUSIVE` | README、docs、SKILL contract | 无 | **B**：适合作为科学 Agent 支线补充 | 当前未以主项目页呈现，CUDA 需在目标硬件验证 |
| [contract-lens-ai](https://github.com/rodriguezrobertbfrkx6857-sudo/contract-lens-ai) | 合同审阅 UI；Next.js 16、React 19、TypeScript | 队列、条款风险、证据进度、人工批准、REST API、WebMCP-compatible tools | 1 个 `portfolio-qa.mjs`；有 build/dev 配置与合成数据 | `docs/screenshots/hero.png`、README | 无 | **B**：产品 UI 完整，但相对其他项目工程证据较薄 | AI 结果是展示型 synthetic workflow，不应写成真实法律系统 |
| [revops-pulse](https://github.com/rodriguezrobertbfrkx6857-sudo/revops-pulse) | 运营分析 UI；Next.js、React、TypeScript、Tailwind | pipeline health、weighted forecast、risk signals、owner actions、API state | README 说明 browser acceptance testing；需要更多源码/测试证据才适合作品集主项 | `docs/screenshots/hero.png`、README | 无；全为 synthetic | **B**：可作为业务 dashboard 补充 | 与已有 QA/数据项目相比差异化较弱，未纳入主项目页 |
| [support-pilot-ai](https://github.com/rodriguezrobertbfrkx6857-sudo/support-pilot-ai) | 支持运营 UI；Next.js、React、TypeScript、Tailwind | triage、incident clustering、SLA、routing、人工批准 | README 说明 browser acceptance testing；公开摘要证据有限 | `docs/screenshots/hero.png`、README | 无；全为 synthetic | **B**：可做补充，但不进入主选择 | 与 ContractLens / RevOps Pulse 同属产品展示型项目，避免堆数量 |
| contra-portfolio-assets | 作品集素材仓库；公开账号仓库 | 通过匿名 raw README 未发现 README；未作为工程项目使用 | 无足够源码/测试证据 | 可能是素材，不作为产品证据 | 无 | **C/D**：只作来源盘点，不纳入 | 不能用素材仓库证明工程能力 |

## 初步主作品集选择

主作品集计划使用 7 个项目，按能力覆盖而非数量堆叠：

1. **agentic-gpu-optimizer** — Agent 实现、隔离 patch、正确性/性能门禁、三态决策。
2. **rag-poisoning-detection-trusted-provenance** — RAG 投毒、可信来源、冲突检测、红队、自净化。
3. **gpu-kernel-performance-lab** — CUDA 内核、内存/warp/分块、非规则尺寸测试与诚实 benchmark。
4. **02-qa-sentinel** — Playwright 多视口 QA、Bug 发现、报告和视觉证据。
5. **04-webhook-observatory** — HMAC、契约校验、重放、有限重试和故障注入。
6. **06-document-pipeline-studio** — 多格式解析、实体溯源、diff、批处理、Python/React 分层。
7. **01-mcp-workbench** — MCP Schema 检查、工具执行、风险启发式和执行历史。

补充材料候选：05-browserops-capture、03-data-cleanroom-studio、spectral-operator-gpu-lab、scientific-reproducibility-kit、quantum-statevector-gpu-lab。游戏、Minecraft Mod 与公开素材仓库不进入最终主作品集。

## 真实性结论

- README 与源码总体一致，但任何“production-grade / battle-tested / 100%”措辞不直接作为作品集事实。
- 所有 GPU 相关项目均按当前公开结果标注 `CPU-only`、`CUDA unavailable` 或 `NOT BENCHMARKED ON CURRENT HARDWARE`；不从 CPU 计时推断 GPU 性能。
- RAG 公开版明确存在“前端源代码缺失、只有构建产物”的边界，作品集将写成“backend + previewable frontend prototype”。
- 本地项目的 `RELEASE_VALIDATION.md` 作为已有证据，但最终事实核验会区分“项目自带报告”与“本次在 extracted 副本中的复核”。
- 对安全相关实现按代码事实描述，不将启发式分类、合成 secret 或本地 demo 误写成生产授权系统。
