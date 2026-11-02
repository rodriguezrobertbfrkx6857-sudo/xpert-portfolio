# Gemma 4 Coding Agent — Repository Repair & Evidence Validation

本目录是从私人科研/竞赛仓库中**人工筛选的公开技术展示**，不是完整的 Kaggle 提交、比赛数据镜像或独立训练的基础模型。

## 能看什么

- [核心编辑组件](repair_runtime.py)：Git 仓库内有界定位、源码 SHA 乐观锁、多文件写前预检、Python AST 检查、进程内失败回滚、补丁审计。只能保证进程内可恢复写失败，不承诺机器崩溃原子性或强安全沙箱。
- [证据校验组件](evidence.py)：验证补丁/评测日志/实验身份绑定，要求外部独立控制器账本，不把普通 JSON 哈希当作可信来源。
- [合成测试](tests/)：临时 Git 仓库中验证编辑安全边界及可信回执拒绝逻辑；测试不是模型的真实修复任务。
- [历史真实案例回放](demo/index.html)：一个已知 FastAPI 开发任务，Gemma 4 12B 生成候选，独立评分记录为 11 项测试通过。此页面只重播经脱敏的历史证据，不会运行模型。相关 [候选 Patch](demo/candidate.patch)、[证据说明](demo/case_evidence.json) 与 [FastAPI MIT 许可](demo/FastAPI-MIT.txt) 已附带。

## 技术流程

任务/仓库状态 → Agent 定位与工具调用 → 文件版本检查与编辑 → Patch 审查与正式评测 → 结果/来源绑定。

公开的是两个可复用的 Python 标准库工具与合成测试，**不是可直接连接 Kaggle 评分环境的一键提交 Agent**。实际模型、官方评测器、任务快照和推理服务需要另行按许可配置。

## 本地检查

需要 Python 3.11+、Git、pytest。请在本目录运行：

```bash
python -m pip install pytest
python -m pytest tests/test_repair_runtime.py tests/test_evidence.py -q
python repair_runtime.py --help
python evidence.py --help
```

发布前已做静态来源、敏感信息与路径检查；公开版本增加了硬链接写入拒绝测试并将测试临时目录移至系统临时区。**新公开版本的完整测试尚未在本次公开流程中实际执行，不能把私有仓库先前的 134/136 通过直接当作本目录测试结果。**

## 记录与局限

- 历史个人 Kaggle V8 Public Score **0.17**，不属于 G11 的实测收益。
- V10 是外部社区基线，公开页面显示的 0.22 不等于本项目同一候选的已证实分数。
- 私有项目 G11 在 31B GPU 试验中存在 Skill 参数格式错误、校准失败及服务超时；**没有证明 G11 超过 V10，也没有完成 LoRA 提分**。
- 历史 FastAPI 案例只有 **1 个已知任务、11 项测试通过**，不能写成 11 个任务或未知任务成功率。
- 本目录不包含私有比赛任务、参考答案、测试集、GPU 日志、原模型权重、账户信息、私有仓库历史或凭据。

## 来源与许可

Gemma 模型与 Google 官方 ADK / 赛事评测框架属于各自权利人。社区参考：Igor Zharov / flexonafft（预算感知 Agent）、Hanh Tran / honghanhhh（公开 Notebook）、Ryan Holbrook（官方 Getting Started 相关示例），均不属于本目录从零原创成果。本目录**没有分发这些第三方完整 Notebook 或模型**。FastAPI 上下文来自其 MIT 授权项目，并附原许可文本。

本公开展示代码为项目的选定 Python 工具组件，借助 AI 编程工具完成实现与测试，由项目组织者进行研究设计、工程验收和证据审查。代码不附加一个未获确认的完整项目开源许可证；引用、复用或衍生使用前请检查各文件及第三方许可。展示不代表 Google 雇佣、官方合作、Kaggle 获奖或论文录用。
