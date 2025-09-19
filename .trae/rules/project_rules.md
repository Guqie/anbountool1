# 项目工程规则与工具调用范式（Trae MCP 版）

> 目的：统一多智能体在本仓库的工作方式，确保“先规划（Sequential Thinking）→ 再执行（工具编排）→ 验证（测试/校验）→ 沉淀（Memory）”的工程闭环，提升协作效率与产出可复用性。

---

## 0. 统一工作流与输出规范
- 输出结构：必须使用“四段式”——【情景回顾与问题确认】【核心回答】【深度解析与知识科普】【完整可执行答案】。
- 先思考后执行：任何任务前，先使用 Sequential Thinking 明确目标、工具链路、输入/输出、成功判据、回滚策略。
- 环境约束（Windows + PowerShell + .venv）：执行命令前务必检查并激活 .venv；命令以 PowerShell 语法描述。
- 代码规范：函数级中文注释；避免“魔法数字”，关键参数需解释。
- 知识扩展：涉及知识性/理论性问题，优先 Context7/Exa/Fetch 动态补充，源可疑需标注不确定性与求证方式。
- 任务闭环：将 ToolCall 摘要、关键 Decision、Error 根因、Artifact 路径回写 Memory。

---

## 1) 关键工具“调用范式蓝本” 

### 1.1 Sequential Thinking（动态思考→决定后续工具）
```json
{
  "nextThoughtNeeded": true,
  "thoughtNumber": 1,
  "totalThoughts": 3,
  "thought": "描述任务目标、子任务、所需工具（顺序）、输入输出、成功判据、回滚策略",
  "isRevision": false
}
```

### 1.2 Context7（定位库文档→获取 API/版本差异）
```json
{
  "resolve-library-id": { "libraryName": "python-docx" },
  "get-library-docs": {
    "context7CompatibleLibraryID": "/org/project-or-resolved-id",
    "tokens": 4000,
    "topic": "api"
  }
}
```

### 1.3 Exa Search 与 Fetch（外部检索→精准核对）
```json
{
  "exa-search": { "query": "python-docx hyperlink add example", "numResults": 5 },
  "fetch": { "url": "https://example.com/precise-doc", "max_length": 4000 }
}
```

### 1.4 Memory（沉淀任务/证据/错误/产物）
```json
{
  "create_entities": {
    "entities": [
      { "entityType": "Task", "name": "TASK:20250917-GenerateWord-0001", "observations": ["目标: 生成并校验 Word 报告", "开始时间: 2025-09-17 10:00"] },
      { "entityType": "Artifact", "name": "ART:outputs/generated_report.docx", "observations": ["类型: Word 文档", "来源: Doc-tools 流水"] },
      { "entityType": "Decision", "name": "DEC:UseDocToolsPipeline", "observations": ["理由: 稳定API, 便于自动化", "替代: 直接python-docx"] }
    ]
  },
  "create_relations": {
    "relations": [
      {"from": "TASK:20250917-GenerateWord-0001", "relationType": "justified_by", "to": "DEC:UseDocToolsPipeline"},
      {"from": "TASK:20250917-GenerateWord-0001", "relationType": "produces", "to": "ART:outputs/generated_report.docx"}
    ]
  }
}
```

### 1.5 Excel（读写/格式/截图）
```json
{
  "excel_write_to_sheet": {
    "fileAbsolutePath": "D:\\桌面\\clientab-main\\web_url.xlsx",
    "newSheet": false,
    "sheetName": "Sheet1",
    "range": "A1:C2",
    "values": [["Title","URL","Note"],["Home","https://example.com","ok"]]
  },
  "excel_read_sheet": {
    "fileAbsolutePath": "D:\\桌面\\clientab-main\\web_url.xlsx",
    "sheetName": "Sheet1",
    "range": "A1:C2",
    "showFormula": false
  }
}
```

### 1.6 Doc-tools（生成 Word→写段落/表→查询信息）
```json
{
  "create_document": { "filePath": "D:\\桌面\\clientab-main\\outputs\\sample.docx", "title": "Auto Report", "author": "Bot" },
  "add_paragraph": { "filePath": "D:\\桌面\\clientab-main\\outputs\\sample.docx", "text": "这是自动生成的测试段落。", "style": "Normal", "alignment": "start" },
  "add_table": { "filePath": "D:\\桌面\\clientab-main\\outputs\\sample.docx", "headers": ["字段","值"], "rows": 2, "cols": 2, "data": [["版本","v1"],["状态","通过"]] },
  "set_page_margins": { "filePath": "D:\\桌面\\clientab-main\\outputs\\sample.docx", "top": 72, "bottom": 72, "left": 72, "right": 72 },
  "get_document_info": { "filePath": "D:\\桌面\\clientab-main\\outputs\\sample.docx" }
}
```

### 1.7 文件系统（最小化变更优先）
```json
{
  "update_file": { "file_path": "D:\\桌面\\clientab-main\\utils\\doc_utils.py", "old_str": "def old_func(", "new_str": "def new_func(" },
  "write_to_file": { "file_path": "D:\\桌面\\clientab-main\\scripts\\smoke_doc_test.py", "rewrite": false, "content": "# 新文件内容（含函数级注释）" }
}
```

### 1.8 命令行（PowerShell + venv 检查与激活 + 测试）
```powershell
# 工作目录: D:\桌面\clientab-main
if (-Not (Test-Path ".\.venv\Scripts\Activate.ps1")) { python -m venv .venv }
. .\.venv\Scripts\Activate.ps1
pip install -r .\requirements.txt
pytest -q
```

### 1.9 代码搜索（先语义，后正则精准）
```json
{
  "search_codebase": { "information_request": "查找生成Word文档的核心流程或python-docx使用位置" },
  "search_by_regex": { "query": "python-docx|Document\\(", "search_directory": "D:\\桌面\\clientab-main" }
}
```

### 1.10 run_command 异步 + 轮询 + 停止
```json
{
  "run_command": { "command": "pytest -q", "blocking": false, "cwd": "D:\\桌面\\clientab-main" },
  "check_command_status": { "command_id": "<prev-id>", "wait_ms_before_check": 1500 },
  "stop_command": { "command_id": "<prev-id>" }
}
```

---

## 2) Memory 固定实体命名规范（建议）
- Task: `TASK:YYYYMMDD-<短slug>-NNNN` 例：`TASK:20250917-GenerateWord-0001`
- Artifact: `ART:<相对路径或外部URL>` 例：`ART:outputs/generated_20250917_131432.docx`
- Decision: `DEC:<简短决策点>` 例：`DEC:UseDocToolsPipeline`
- Error: `ERR:<模块/文件>#<错误摘要>` 例：`ERR:doc_utils#ValueError-Hyperlink`
- ToolCall: `CALL:<工具名>#<时间戳或序号>` 例：`CALL:doc-tools#20250917-101530`
- Evidence(Exa/Fetch/Context7): `EVD:<来源>#<主题>` 例：`EVD:Context7#python-docx-api`
- 观测写入要点：仅保留必要入参摘要与产物路径/URL；避免敏感信息；任务开始与结束各写一条观测。

---

## 3) Context7 快速入口模板
- 场景：需要精准获取某库 API、版本差异、官方最佳实践时使用。
- 步骤：resolve-library-id → get-library-docs。
- 模板：
```json
{
  "resolve-library-id": { "libraryName": "pandas" },
  "get-library-docs": {
    "context7CompatibleLibraryID": "/org/project-or-resolved-id",
    "tokens": 5000,
    "topic": "io|api|whatsnew|best-practice"
  }
}
```
- 选型建议：
  - 已知库 → 直接 Context7；
  - 问题模糊/需要对比 → 先 Exa Search 汇总，再用 Context7 精读权威文档；
  - 已有具体 URL → Fetch 精读并抽取要点。

---

## 4) 工作区动态上下文工程（索引/忽略/文档集）

### 4.1 代码索引管理与 #Workspace 问答
- 目标：针对跨文件、跨模块问题，自动检索与问题高度相关的上下文，减少幻觉与错位答案。
- 提示词约定：当识别到用户发起“#Workspace”类提问时，优先调用 `search_codebase` 定位候选，再用 `view_files` 拉取关键片段核对，必要时 `search_by_regex` 精准定位函数/类名。
- 回答规范：在【完整可执行答案】中给出涉及文件与符号清单，必要时附补丁策略（update_file 优先）。

### 4.2 忽略文件（附 .trae/.ignore 规则）
- 目的：降低无关/二进制大文件对索引质量的影响。
- 建议规则（已同步到 .trae/.ignore）：
  - `.venv/`
  - `**/node_modules/`, `frontend/node_modules/`, `frontend/dist/`, `frontend/.vercel/`
  - `__pycache__/`, `*.pyc`, `.pytest_cache/`
  - `outputs/*.docx`, `outputs/*_backup.docx`
  - `ab_doc_temps/*.docx`, `ab_response_formats/*.docx`
  - `uploads/`
  - `.streamlit/`, `.git/`

### 4.3 文档集（示例清单与提示）
- 可配置的常用文档作为外部上下文：
  - 提示词工程2 | 更新时间 2025/08/26 13:08
  - 提示词工程 | 更新时间 2025/08/25 10:37
  - langgraph
- 使用建议：当问题涉及提示词工程/Agent编排/langgraph 流程时，在 Sequential Thinking 的“知识补充”步骤显式声明：先查文档集摘要（若可用），再结合 Exa/Context7 校验。

---

## 5) 错误处理、验证与回滚
- 捕获错误后：在下一轮 Sequential Thinking 中追加“错误诊断与恢复计划”；将 Error 与 ToolCall、Task 建立关系写入 Memory；附最小可复现实验。
- 验证优先级：能写测试就写测试（pytest）；否则使用 Doc-tools `get_document_info`、Excel `read_sheet` 做数据/文档双向校验。
- 回滚：文件改动优先差异化补丁；必要时保留 `.bak` 文件并在 Memory 中记录映射关系。

---

## 6) 常用 PowerShell（环境与测试）
```powershell
# 进入工作目录
Set-Location "D:\桌面\clientab-main"
# 准备与激活虚拟环境
if (-Not (Test-Path ".\.venv\Scripts\Activate.ps1")) { python -m venv .venv }
. .\.venv\Scripts\Activate.ps1
pip install -r .\requirements.txt
# 运行测试
pytest -q
```