# SYSU-Reimbursement-Handbook

**中大网球队比赛报销手册 · PhSeCl**

[![构建状态](https://github.com/PhSeCl/SYSU-Reimbursement-Handbook/actions/workflows/build-handbook.yml/badge.svg)](https://github.com/PhSeCl/SYSU-Reimbursement-Handbook/actions/workflows/build-handbook.yml)

从发票抬头、凭证留存到材料整理与行程说明，一本写给代表学校参赛的队员的报销手册。把费用、票据和实际行程对应起来，让材料准备更清楚，让反复补交更少一些。

![手册内页预览](docs/preview.png)

## 手册内容

| 章节 | 阅读内容 |
| --- | --- |
| [序章 · 报销主体与凭证要求](latex/chapters/prologue.tex) | 中山大学开票信息；发票、小票、付款记录、行程单与保单的用途和图例 |
| [第一章 · 常规比赛报销](latex/chapters/chapter-1.tex) | 费用分类、票据整理、个人报销汇总表、特殊行程说明与提交前核对 |
| [第二章 · 跨校区训练车费报销](latex/chapters/chapter-2.tex) | 校车发票、费用汇总、单程情况说明与报销进度沟通 |
| [第三章 · 训练费发放](latex/chapters/chapter-3.tex) | 训练费名单、金额与发放时间 |
| [附录 · 开源仓库与模板下载](latex/appendices/appendix-a.tex) | 仓库入口与可填写 PDF 模板 |
| [后记](latex/backmatter/epilogue.tex) | 编写缘起与材料整理的意义 |

书中保留了填写示例；下载包另附**个人报销汇总表及情况说明**、**跨校区训练车费汇总表及情况说明**两份可填写 PDF，包含姓名、学号、邮箱、发票张数、金额明细、总额和情况说明栏。

> 本手册由队员根据实际经历整理。具体费用范围、办理条件和期限，以学校现行规定及经办部门要求为准。

## 下载与使用

[在线阅读完整手册](SYSU-Reimbursement-Handbook.pdf) · [直接下载手册 PDF](https://github.com/PhSeCl/SYSU-Reimbursement-Handbook/raw/refs/heads/main/SYSU-Reimbursement-Handbook.pdf)

两份可填写模板可直接下载：

- [个人报销汇总表及情况说明](https://github.com/PhSeCl/SYSU-Reimbursement-Handbook/releases/latest/download/reimbursement-summary-form.pdf)
- [跨校区训练车费汇总表及情况说明](https://github.com/PhSeCl/SYSU-Reimbursement-Handbook/releases/latest/download/cross-campus-summary-form.pdf)

无需安装 LaTeX 即可取得 PDF：打开 [自动构建页面](https://github.com/PhSeCl/SYSU-Reimbursement-Handbook/actions/workflows/build-handbook.yml)，选择最近一次成功运行，在页面底部的 **Artifacts** 下载 `handbook-pdfs`。压缩包包含手册和两份空白 PDF 表单，保留 14 天；下载构建产物需要登录 GitHub。仓库维护者也可通过 **Run workflow** 重新生成。

表单建议下载后用 Adobe Acrobat Reader 等支持交互表单的阅读器填写，再另存为个人副本。金额明细与总额需自行核对；保存后重新打开并检查打印预览，确认中文和多行说明完整显示。已填写的文件包含个人信息，请通过经办人指定渠道提交。

手册与模板均以 LaTeX 编写，由 GitHub Actions 使用 XeLaTeX 自动构建。正文源码位于 [`latex/chapters/`](latex/chapters/)，模板源码位于 [`latex/forms/`](latex/forms/)。字体采用宋体正文、思源圆体标题；表单内嵌完整中文输入字体。

## 反馈与修订

欢迎通过 [Issues](https://github.com/PhSeCl/SYSU-Reimbursement-Handbook/issues) 提出勘误、补充规则出处或反馈办理经验，也欢迎直接提交 LaTeX 修订。涉及政策变更时，请附适用条件、时间及可核对的来源。

提交图例前，请完整遮盖姓名、证件、联系方式、账号、订单编号、二维码及非必要行程信息，使用不透明色块并导出为新的扁平化图片。

## 许可与致谢

© 2026 **PhSeCl**。手册原创正文、`latex/` 中的文档与排版源码（字体除外）、README 及 `docs/` 中的原创展示内容采用 [CC BY-NC-SA 4.0](LICENSE)（知识共享署名—非商业性使用—相同方式共享 4.0 国际许可协议）。

你可以在非商业用途下分享与改编这些内容；请注明作者 **PhSeCl**、[本仓库](https://github.com/PhSeCl/SYSU-Reimbursement-Handbook)和[许可链接](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans)，说明是否作出修改，并以相同许可分享改编内容。商业使用需另行取得授权。

`scripts/` 中的构建与校验工具继续采用 [MIT License](scripts/LICENSE)。思源圆体采用 SIL OFL 1.1；票据、平台和系统界面中的第三方内容不在上述授权范围内，详见[第三方说明](THIRD_PARTY.md)。此前已按 MIT 发布的版本，其原有授权继续有效。
