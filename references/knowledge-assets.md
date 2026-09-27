# 企业知识库与数字资产契约

## 复用 RenWork V4

本包附带上游 `knowledge-card.schema.json` 和 `module-catalog.json` 原文件，来源及 MIT 许可见 sources.json / THIRD_PARTY_NOTICES.md。字段、枚举以 Schema 为准；它包含 `conflicted`，共七种状态，不能沿用旧文案的“六态”遗漏冲突。

每张卡只表达一个可以核对的结论。整段公司简介先存为待拆分资料，不能一次批准后让其中未经证明的宣传语变成事实。保留 `kb_id`、`tenant_id`、revision、entity_id、source_refs、conditions、敏感度、批准状态与时间。

网站映射：

| 模块 | 网站/内部成果 | 公共边界 |
|---|---|---|
| 00 治理 | 覆盖矩阵、负责人、缺口与版本 | 内部 |
| 01 来源权限 | 来源台账、术语、证据许可 | 只公开获准的证据 |
| 02 企业身份 | About、联系信息、Organization | 正式身份与品牌关系一致 |
| 03 品牌口径 | 首页定位、DESIGN.md、内容风格 | 新口号为设计建议，不能暗含虚假优势 |
| 04 产品 | 分类、详情、规格与产品目录 | 仅真实且当前适用产品 |
| 05 制造质量 | 流程、质检、技术能力 | 区分自有、合作与贸易能力 |
| 06 认证合规 | 产品×市场×证据矩阵 | 证书主体、范围、型号、期限须一致 |
| 07 商务交付 | MOQ、样品、交付 FAQ | 按批准的条件公开；底价等受限 |
| 08 市场 | 市场研究、本地化计划 | 研究不等于已出口业绩 |
| 09 ICP | 页面买家路径 | 画像是策略建议 |
| 10 意图 | 内容/询盘需求归因 | 不暴露个人追踪数据 |
| 11 竞争 | 差异化证据链 | 不复制竞品事实给本企业 |
| 12 匹配 | 应用页与选型路径 | 推荐条件写清楚 |
| 13 线索 | 线索研究方法和接入状态 | 联系人及名单留内部 |
| 14 客户 | 客户资产及后续 CRM 映射 | 默认内部/受限，无连接就 NOT_CONNECTED |
| 15 询盘 | RFQ 表单与资格判断 | 公共表单与内部判断规则分离 |
| 16 方案样品 | 技术简报、选型/打样流程 | 不自动承诺价格或免费寄样 |
| 17 谈判 | 异议 FAQ 与内部红线 | 只导出批准的答复 |
| 18 内容 | 网页、邮件签名、社媒/展会派生稿 | 所有渠道复用同一事实版本 |
| 19 交付售后 | 服务范围、维护/售后说明 | 不伪造物流和保修政策 |
| 20 复盘 | 搜索、询盘、样品、成交指标 | 匿名聚合，记录实际数据来源 |

输出 `knowledge-coverage.md` 时每模块写：已有材料、已生成卡数、缺失项、下一步、负责人（未知即未指定）。目录存在不代表建库完成。岗位视图沿用 management、sales_director、junior_sales、senior_sales、marketing、operations_quality；当前无数据的岗位仅列准备路径。

## 公共事实投影

用于事实宣称的卡必须同时满足：同一 tenant；`knowledge_kind=fact`；status 为 verified_fact 或 public_fact；sensitivity 为 public；public_claim_approved 为布尔 true；有可定位且非 AI 推断的来源；无冲突、未过期。行业标准的说明卡不能转换成“本企业通过标准”的结论。

来源是用户提供也可以，但记录谁在何时通过什么文件提供及其授权用途。公开网站声称的关键性能仍需核验；authority 或 confidence 数值不能代替审核。`valid_until` 为空表示未设置期限，不代表永远有效；证书、报价、交期等有明确有效期的材料应填写期限。

公开导出只输出 `kb_id/title/language/conclusion/conditions/updated_at`，不自动附带原始材料、source_refs、邮件、CRM 字段。公开证据下载另经资产台账审核。`sitekit.py export` 只守卫以上局部契约，不是完整 JSON Schema 验证器，也不理解自然语言真伪；用已有 JSON Schema 验证能力再验证完整卡，并人工抽查网页事实关联。导出返回错误时停止构建，不能沿用旧文件当成新验证结果。导出成功也须查看内部 omitted 报告，并检查各页面 claim_ids 全部存在于当前公开投影。

## 来源与事实连接

`page-manifest.json` 每页记录 url、type、language、status、primary_intent、claim_ids、asset_ids、reviewed_at。数值、资质、关系、产能、交付与案例结果均要有 claim_id；主张变化要反查受影响页面。编辑稿可在内部用 `[claim:RW-......]` 标记，公开正文不得泄漏内部定位。

通用选型建议、设计口号和行业介绍另记录来源与策略状态，不硬塞成公司事实。引用行业资料时保留适用条件；有版权的资料优先链接原文，不整篇转载或下载再包装。

## 数字资产台账

使用 JSON 或 CSV，不为台账先部署 DAM 服务。每项至少包含：

```text
asset_id, company_id, file, type, source_uri, captured_at,
rights_status, rights_evidence, visibility, approval,
is_ai_generated, intended_use, claim_ids, derived_from,
version, sha256, language, alt_text, width, height, used_on
```

`rights_status`：owned / licensed / permission_granted / unknown。unknown 不发布。Logo 授权与字体、图库授权分别记录；公开可访问不等于可转载。

存储层分开：`private/raw/` 原件与内部台账；`content/` 可审查内容；网站专用 `public/` 仅放筛选后的发布素材；`builds/site-.../` 或框架构建目录仅生成网站。不要直接把整个企业项目目录当作静态站根目录。

生成资产按实际需要：Logo 原图及派生/favicon、OG 图、真实产品图与裁切版本、参数表、产品目录、能力介绍、公开技术资料、媒体素材包。图片提示词不是成图，PDF 模板不是企业目录；台账分 planned / draft / approved / published，只有实际文件才能标为 generated。

AI 概念图可以表达非事实性的应用气氛，需记录并明确示意用途；真实设备、厂房、认证、人员和案例结果须真实素材。产品结构图若基于经核验规格绘制，记录规格来源，不补画会误导性能/结构的部件。

## 更新与沉淀

每次客户补充材料 → 更新来源和对应卡 revision → 审查受影响页面、翻译、PDF、Schema 和公开投影 → 构建测试 → 按授权发布。保留原件哈希与版本差异；删除或失效材料应撤下对应下载和宣称，不能只改更新时间。

将实际询盘中重复出现的问题归入 15/17/18，新测试资料归入 04/05/06，真实转化数据归入 20。AI 只能提出修订候选，不能从一次对话自动升级企业事实或泄漏客户资料。无需知识图谱服务器即可先用 ID 与 JSON 建立可追溯关系。
