# universal_csv_to_word 模块说明文档

更新时间：自动生成于当前重构批次

## 1. 模块目的与定位
- 以统一的“模板 + 数据”范式生成 Word 文档，支持多行业模板（国资委、新能源、房地产、科技与产业、电力等）。
- 通过 TemplateFactory 从 templates_config.yaml 读取模板元信息，实例化具体模板（ConfigBasedTemplate）。
- 由 UniversalDocumentGenerator 负责数据到文档的转换与后处理（标题/正文/图片/来源/日期/返回目录占位符等）。

## 2. 关键类与职责
- TemplateFactory
  - 加载并校验模板配置；
  - create_template(template_type) 生成具体模板；
  - get_available_templates() 列出可用模板。
- ConfigBasedTemplate（实现 DocumentTemplate 抽象）
  - 提供模板路径、样式配置（含 title_mapping、return_link、target_bookmark、styles 等）；
  - 可对输入 item 进行模板级预处理（如标题格式化）。
- UniversalDocumentGenerator
  - 组合模板与样式，遍历数据，生成段落结构；
  - 处理 heading_1/2/3 与 title 的映射与样式；
  - 解析正文中 URL 并就地下载/插入图片；
  - 生成来源与日期行；
  - 执行文档级后处理与合并结尾模板。

## 3. 数据输入与字段约定（CSV/JSON）
- 支持字段：heading_1、heading_2、heading_3、title、content、source、date；
- 空值/NaN 将被安全跳过；
- 图片 URL 允许出现在 content 中，会被下载并内联插入；
- 每条有效内容后会追加“返回目录占位符”。

## 4. 与配置（templates_config.yaml）的契约
- start_template：起始模板（必填）
- end_template：结尾模板（可选）
- styles：段落/标题/图片等样式字典（可为空对象或缺省）
- title_mapping：将 heading_1/2/3/title 映射到具体 Word 级别
- return_link：返回目录锚点相关配置（target_bookmark 等）

## 5. 重构与耦合治理（本次变更）
- 新增 utils 包，新增 utils/doc_utils.py：
  - 封装并转发 csv_to_word 中的通用处理函数；
  - 统一在 universal_csv_to_word 中从 utils.doc_utils 导入，隔离对 csv_to_word 的直接依赖；
  - 后续如替换底层实现，仅需调整 utils/doc_utils.py。
- 现状：业务类（UniversalDocumentGenerator）仍保留其内部私有方法（如段落样式应用、返回目录占位符等），后续可分阶段抽取到 utils 中（需参数化 logger 与 style_config）。

## 6. 典型使用流程
1) 选择模板类型（例如 "guoziwei"）。
2) 读取 CSV/JSON 并转为 List[dict] 数据。
3) 创建 UniversalDocumentGenerator(template_type)；
4) 调用 generate_document(data) 生成 .docx。

## 7. 异常与容错
- 配置缺失或 YAML 解析失败时抛出友好错误；
- 单条内容处理异常会记录日志并跳过；
- 图片下载具备重试与格式转换（优先 PNG/JPEG，必要时转 RGB/RGBA）。

## 8. 未来优化建议
- 分离更多与样式/段落/链接相关的通用私有方法到 utils；
- 在 utils 层引入策略模式，按模板特性组合处理链；
- 为关键路径增加单测与集成测试；
- 对图片缓存与失败回退策略做参数化配置。

以上为模块说明与本次重构的要点总结。