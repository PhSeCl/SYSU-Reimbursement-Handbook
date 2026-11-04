# 维护约定

- 正式书稿仅维护 LaTeX：主文件 `latex/main.tex`，正文 `latex/chapters/`，样式 `latex/handbook.sty`。作者固定为 **PhSeCl**。
- 作者当前修订为准，保留原有措辞、段落和语气；只改任务明确要求的部分，不还原旧稿或自行添加正文。
- 延续宋体正文、圆体标题、真实粗体和蓝紫层级；章首使用 `\ChapterOpening` 与 `\ChapterGuide`，序章不加导读框。页眉仅简短节名与页码。
- 正文与图例不得混入对话、计划、占位、草稿或验证记录。未经确认的政策、金额与期限不得编造。
- 图片仅使用 `assets/redacted/` 中经过审查的扁平化素材。姓名、证件、联系方式、账号、单据编号、可读取编码和非必要行程线索必须用不透明实色遮盖。原始材料不得进入仓库、历史或输出。
- 新增或修改图例后，实际查看图片与导出 PDF，检查可复制文字、附件及元数据；审查后更新 `scripts/illustrations.sha256.json`。
- 从仓库根目录运行 `pwsh -NoProfile -File scripts/build-handbook.ps1`；实际通过后再报告结果。Python 使用 uv，新增依赖使用 `uv add`。
- README 面向读者展示手册，避免开发进度、工作区历史和内部核对记录。
- Git 提交采用 Conventional Commits：`<type>(<scope>): <subject>`。
