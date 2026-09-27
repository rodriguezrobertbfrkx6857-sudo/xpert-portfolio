# DESIGN REVIEW V1

复核对象：`output/v1-pages/page-01.png` ... `page-10.png`。复核方式：Chromium 生成 PDF 后使用 Poppler 实际渲染 PNG，逐页人工检查。以下是 V1 中真实观察到的改进点；V2 只做对应的可读性、事实和版式修正。

| # | 页面 | V1 观察到的问题 | V2 修正 |
|---:|---|---|---|
| 1 | P01 | 封面右侧竖排 source/build/run/acceptance 标签阅读方向不够自然。 | 改为更清晰的横向小标签并保留装饰作用。 |
| 2 | P01 | 封面指标写成 `5 local UI systems re-run`，与实际复核的 6 个本地项目不一致。 | 改为 `6 local systems re-run in copies`。 |
| 3 | P02 | 8 步流程条横向过挤，Implementation 的尾部接近连接箭头。 | 缩小流程条字距、固定连接器宽度并允许步骤文本更稳妥换行。 |
| 4 | P02 | Code review 在流程条中换成两行，和其他步骤的垂直节奏不统一。 | 使用较短的 `Review` 标签并保留页内解释。 |
| 5 | P02 | capability map 的项目证据列较窄，长项目名产生不必要的断行。 | 微调三列比例，给项目证据列增加宽度。 |
| 6 | P03 | CPU reference 表的列标题和数字字号偏小，首次阅读需要放大。 | 提高表头/表体字号并减少不必要的列间空隙。 |
| 7 | P03 | GEMM 的红色 0.094x 是重要反例，但与黄色 measurement note 的视觉层级略接近。 | 加强反例标签和说明的层次区分。 |
| 8 | P03 | code sample 与下方 boundary callout 的视觉间隔略大。 | 收紧 code block 与 note 之间的垂直间距。 |
| 9 | P04 | 两个案例名称的 `<small>` 文字与粗体标题粘连为 `transposepadded...` / `reductionprecision...`。 | 将案例副标题设为块级并加上间距。 |
| 10 | P04 | decision.py 片段在窄列中把布尔条件从中间折行，阅读成本较高。 | 改成等价但更短的三态决策伪代码。 |
| 11 | P04 | Agent flow 的 `accept / reject / inconclusive` 在末节点内折行，节点高度观感不齐。 | 缩短辅助说明为 `three-state outcome`。 |
| 12 | P04 | 主内容集中在上半页，底部有较大的无信息空区。 | 增加简洁的 `what this proves / does not prove` 边界条。 |
| 13 | P05 | PoisonRisk 公式在右栏换行后，运算符和项的节奏不够像一个公式。 | 改成两行固定的等宽公式文本。 |
| 14 | P05 | 左侧 self-purify 状态文字折成两行，和五层流程的结束关系不够明确。 | 改为单行 `QUARANTINE / SELF-PURIFY / REPORT`，并收紧字号。 |
| 15 | P06 | 两张 QA 截图在 A4 版面上保留了大量浏览器 UI 细节，核心 finding 的文字偏小。 | 提高截图显示高度并补充更清晰的 findings 标签。 |
| 16 | P06 | QA 的 inspection surface 文本是长串斜杠清单，阅读节奏偏密。 | 将清单拆成两行语义组。 |
| 17 | P06 | 页面下半部留白较多，callout 与 footer 之间纵向距离偏大。 | 增加 `clean run / defect run / artifact` 三项证据条。 |
| 18 | P07 | 两张 webhook 截图高度不同，页面中的视觉节奏略不一致。 | 统一图片框高，使用 contain/背景色保留完整界面。 |
| 19 | P07 | retry 证据中的数字与说明较密，`3 default max retries` 和 `5 hard cap` 需要更明确的标签。 | 改为 `default retries` / `absolute cap`。 |
| 20 | P08 | 文档截图细节偏小，底部三列又叠加了较长说明，页面信息密度不均。 | 略缩短 lede，统一截图框高并提升三列行距。 |
| 21 | P08 | scope boundary 文本中 `Scanned-image PDF OCR` 的断行不够平滑。 | 改为短句并使用强调标签。 |
| 22 | P09 | additional table 的长项目名断成 `05-browserops- / capture`，列宽显得拥挤。 | 扩大项目列，压缩限制作列，并使用更短展示名。 |
| 23 | P09 | 两张补充截图下的 caption 线长不一致，造成轻微跳动。 | 统一 caption 最小高度。 |
| 24 | P10 | source map 用 `{detector,consistency,...}` 的 shell 风格缩写，对非作者读者不够直观。 | 展开为文件名列表。 |
| 25 | P10 | 三个 public source 链接在同一行挤在一起，难以扫读。 | 改为四列网格，短化显示标签并允许换行。 |

V2 复核目标：10 页仍为 A4 portrait；没有文本越过内容边界；截图不发生关键区域裁切；公共链接可点击；最终 PDF 文本不包含本机路径、用户名或敏感标记。
