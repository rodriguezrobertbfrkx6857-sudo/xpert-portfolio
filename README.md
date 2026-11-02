# ByteDance Xpert 技术作品集

本目录保存用于 ByteDance Xpert 专家社区申请的最终技术作品集，以及可复核的选材、事实和隐私审计记录。

## 交付物

- `FINAL/Xpert_Portfolio_FINAL.pdf`：10 页 A4 主作品集。
- `FINAL/Xpert_Portfolio_Page_01.png` ... `FINAL/Xpert_Portfolio_Page_10.png`：最终 PDF 的逐页 PNG 预览。
- `reviews/`：项目盘点、事实核验、证据映射、隐私审计和视觉复核记录。
- `assets/`：从授权本地项目复制的合成 UI 截图；只在本目录内使用。
- `extracted/`：本地复核时使用的项目副本与临时环境；体积较大且可重新取得，因此不纳入 Git 仓库。
- `source/`：HTML/CSS 渲染源和复核脚本。

## 选材原则

主作品集选择 7 个项目，覆盖 Agent 工程、AI 安全、STEM/CUDA、QA、安全 API、文档 ETL 与 MCP 工具开发。选材依据是源码结构、测试、构建/运行结果和可展示的合成证据，不使用 Star、Fork、访问量或未经核验的用户指标。

本轮授权可见目录没有发现明确的 itch 游戏项目或 Minecraft Fabric/Forge Mod 项目，所以最终作品集不包含游戏/Mod 页面，也不声称完成了相关运行验收。当前主机没有 CUDA，GPU 项目只展示源码、CPU fallback 和真实的 CPU-only/INCONCLUSIVE/REJECT 边界，不把 CPU 计时包装成 GPU 性能。

## 来源与隐私

读取范围仅为用户指定的本地项目根目录和公开 GitHub 账号 `rodriguezrobertbfrkx6857-sudo`。未读取浏览器配置、凭据、`.git` 内部、真实 `.env`、密钥、Token、Cookie、支付或身份资料；未登录 GitHub，未 push、建 Issue 或建 PR。截图和样例数据均为合成内容，作品集中不展示真实用户数据。

## 复核与再生成

HTML 使用 Chromium 生成 PDF；依赖路径、测试命令和本次结果记录在 `reviews/VALIDATION_LOG.md`。重新生成时应在本目录内运行（首次复核需按 `reviews/` 中记录重新准备本地证据目录）：

```powershell
& 'C:\Users\PUBLIC_USER\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' '.\source\render.js'
```

渲染前请先执行 PDF skill 要求的 artifact-operation 标记命令；最终交付前还应重新运行页数、文本、元数据、文件大小和逐页 PNG 检查。原项目目录保持只读。

## Gemma 4 编程智能体 · 仓库修复与可信评测

- [公开展示与源码](projects/gemma4-coding-agent/README.md)：事务式代码编辑、源码版本校验、补丁/独立回执校验的选定工具与合成测试。
- [历史 FastAPI 修复案例](projects/gemma4-coding-agent/demo/index.html)：一个已知任务、11 项测试通过的离线记录复播；不是当前 G11 的成功率或实时模型演示。

此展示来自独立私有研究项目的脱敏筛选版本；未公开任务数据、模型权重或完整实验轨迹。私有项目仓库仍保持私有。
