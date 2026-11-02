# 公开范围与隐私审查

## 发布的文件

标准库工具：`repair_runtime.py`、`evidence.py`。测试：`tests/test_repair_runtime.py`、`tests/test_evidence.py`。离线演示：`demo/index.html`、`demo/candidate.patch`、`demo/case_evidence.json`、`demo/FastAPI-MIT.txt`。说明：本 README 和本清单。

## 故意没有发布

原私有仓库的 Git 历史、任何 Kaggle 原始任务全文与隐藏测试、参考答案/Golden Patch、Notebook/Kaggle 输入数据、GPU 运行私有日志/模型轨迹、模型权重、官方 wheel、V8/V10/G10/G11 提交 ZIP、账户凭据与本机绝对路径、未经处理的论文研究语料、确认集全量登记表。

## 技术与许可限制

此次公开工具不等于可以独立复现 Kaggle 官方得分的完整系统。原始代码在私有工程中配合官方工具链使用；这里是可执行的局部组件和合成测试。GitHub Public 不意味着第三方内容自动获得宽松许可。本展示未附独立项目开源许可证，FastAPI 代码片段遵循所附 MIT 许可。

本目录未改变原私有仓库的可见性。不得将简历中的 Kaggle 得分 0.17 与 G11 的实际实验效果混淆，亦不得声称已完成 LoRA 训练或论文录用。
