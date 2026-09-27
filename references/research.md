# 第一阶段研究与融合依据

研究日期：2026-09-27。本文保留第一阶段的18行业研究范围；V2已扩展为20行业，实际实现与新增来源以 [V2融合差异](fusion-v2.md) 和 [最新平台核验](search-current.md) 为准。仓库锁定版本及来源清单见 [sources.json](sources.json)。结论来自本次仓库文件审读、官方文档、学术原文摘要与真实厂商网站结构观察；不是宣称穷尽互联网或已在 18 个行业验证转化收益。

## 核心判断

“简单 Logo + 简介”足以启动完整品牌/内容/网站生产流程，却不足以证明企业的工厂规模、证书、技术性能和交付能力。专业度来自行业采购逻辑、事实结构、证据和良好体验。新 Skill 允许资料不全时继续产出可运行草稿，把缺口留在内部，不用虚构资料填满专业模板。

## 三个指定仓库的融合

| 来源 | 本次核对 | 采用 | 调整 |
|---|---|---|---|
| [brand-visual-system-master](https://github.com/cnproduct/brand-visual-system-master) | SKILL、README、脚本目录与品牌产物结构，commit `10908551ccb4a439615d806a68761d2a081661ca`，MIT | Logo→视觉规则→Web Tokens→品牌触点→一致性审核 | 不把所有线下导视作为建站必需品；安全区、字体和取色是设计提案，不冒充原始商标工程标准；不以概念空间渲染冒充真实工厂 |
| [renwork-export-kb-suite](https://github.com/cnproduct/renwork-export-kb-suite) | orchestrator、governance auditor、知识卡 Schema、模块目录，commit `f0d524815db52283044f3e5a988c037ccb8d79ff`，MIT | 00–20 模块、统一知识卡、敏感度、公开批准、来源、岗位视图 | 保留 Schema 的七状态，包括 conflicted；未接 CRM 不写已接入；只导出允许公开的字段，不把企业完整知识库作为网站目录 |
| [renwork-seo-geo-optimizer](https://github.com/cnproduct/renwork-seo-geo-optimizer) | SKILL、文件目录、geo_audit_runner.py，commit `f1e40f72171fd70833f4afffcd07ee66a9c14e6a`；本次未检出仓库许可证 | 事实与网页映射、链接清理、语义 HTML、Schema、技术参数、部署后核验 | 不复制源码；取消固定密度/字数/5000词门槛、“满分=引用”及强制 WebMCP；不自动添加作者、实体档案、退货/运输政策 |

旧 SEO 工具的 `geo_audit_runner.py` 调用外部 `geo audit`，展示其规则评分；不能据此判定搜索平台真实引用或询盘增长。本次只审读，未对真实网站运行该审计或部署脚本。

## 补充 Skill 与方法

审读了 [coreyhaines31/marketingskills](https://github.com/coreyhaines31/marketingskills) 的 `site-architecture`、`cro`、`programmatic-seo`、`ai-seo`，锁定 `5b2c0007766c6a1cf1d53fd8fc73e979e0821022`。吸收采购路径、CTA、页面意图、表单阻力及每页独立价值；不继承未在本次核验的收益倍数、平台来源偏好或固定回答长度。未整包复制或自动安装它。

本地参考 `frontend-design-deslop` 的定位→视觉→组件思路、`industry-brand-adapt` 的行业差异，以及 `footwear-export-site-builder` 的鞋类参数/打样/移动端询盘经验。重新编写行业配置，舍弃默认500双MOQ/固定交期、全部删除.html、GPTBot直通Google AI Overviews等不可推广规则。没有把这些本地 Skill 作为使用本包的硬依赖。

## 以官方资料校正 SEO/GEO

- Google 2026 AI 指南将原创、独特且对人有用的信息列为重点，否定专用 AI 文件、固定切片和特殊 Schema 是必要条件的说法。新模板优先真实产品数据、适用条件和工程知识。[官方 AI 优化指南](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- Google 更新记录明确 FAQ rich results 从 2026-05-07 起停止显示，6 月移除文档。因此 FAQ 保留采购问答用途，不承诺搜索特殊展现。[官方变更记录](https://developers.google.com/search/updates)
- 新 GSC 帮助页介绍生成式 AI 曝光报告，含 AI Overviews/AI Mode，并写明 2026-08-31 全球上线；同页仍列出账号可见性/曝光不足等条件。旧文档与新文档存在口径差异，实施时以账号与最新帮助页核验。[GSC 生成式 AI 报告](https://support.google.com/webmasters/answer/16984139)
- Bing AI Performance 提供其支持的 AI 场景下被引用 URL 等信息。它是 Microsoft 场景数据，不是全网统一 GEO 分数。[Bing 官方说明](https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/)
- OpenAI 搜索与训练爬虫分开配置，支持选择允许搜索而不允许训练；不一律放行全部机器人。[OpenAI 爬虫文档](https://developers.openai.com/api/docs/bots)
- `llms.txt` 目前是提案，2026-08 v2 强调简洁索引和按需读取。只作为可选信息导航，不为凑分复制整个内部知识库。[提案原文](https://llmstxt.org/)
- WebMCP 本次读取为 2026-09-26 Draft Community Group Report，原文明示不是 W3C Standard。仅按需求及兼容性选择，不强制给营销站开放自动业务操作。[规范草案](https://webmachinelearning.github.io/webmcp/)
- GEO 原始论文的实验表明领域差异，不能把其中 benchmark 的最高提升直接作为企业项目收益。新 Skill 用固定采购问题集和真实搜索/询盘数据建立基线。[GEO 论文](https://arxiv.org/abs/2311.09735)

## 行业模板如何形成

18 类配置是按采购决策重写的可扩展蓝图，而不是 18 套简单换肤。重点是产品字段、证据资料、询盘信息和内容顺序。

观察 [TI 产品入口](https://www.ti.com/product-category/overview.html) 与 [封装查询](https://www.ti.com/packaging/docs/searchproductbypackage.tsp)，提炼型号/参数/封装/资料入口；观察 [Protolabs 服务](https://www.protolabs.com/Services/)，提炼材料、数量、工艺和设计资料驱动的询盘；观察 [恒安质量体系](https://en.hengan.com/column/78/) 与 [Portwest 产品页面](https://www.portwest.com/products/view/DX420/ABR)，提炼质量证据和技术详情的呈现。以上仅为各公司的公开网站观察，不构成客户关系，也不把其能力转移给目标企业。

其它行业字段为采购工作流设计建议，并未逐行业完成市场/法规实证。实际公司项目仍需检索同行、目的市场、SKU和官方标准。建材、食品、医疗、化学品中的标准名称只作为待研究方向；无证据不发布合规结论。

## 实施依据与可维护性

可访问性以 [WCAG 2.2](https://www.w3.org/TR/WCAG22/) 为基础；性能区分 [Core Web Vitals](https://web.dev/articles/vitals) 现场与实验室数据；多语言参考 [Google hreflang 指南](https://developers.google.com/search/docs/specialty/international/localized-versions)；Schema 参考 [Product 官方文档](https://developers.google.com/search/docs/appearance/structured-data/product-snippet)；批量内容遵循 [搜索垃圾政策](https://developers.google.com/search/docs/essentials/spam-policies)。

静态/局部交互建站参考 [Astro Islands](https://docs.astro.build/en/concepts/islands/)，跨工具 token 参考 [DTCG](https://www.designtokens.org/tr/drafts/format/)，站点更新通知参考 [IndexNow](https://www.indexnow.org/documentation)。这些都是条件性选项，不要求新增框架/服务，也不把提交 URL 当作保证收录。

## 研究覆盖与限制

GitHub 通过 agent-reach 的 gh CLI 读取并克隆；Exa 未配置，通用检索采用现有网页搜索能力。Twitter 搜索两次返回 API 404；B站 OpenCLI 返回 Browser Bridge 未连接，未获得这两路有效材料，未为此改动账号配置或升级工具。搜索返回的社区讨论只作为线索，不作为技术规则依据。Agent Reach 检查结果为 v1.5.0 已是最新。

本包已完成结构与辅助脚本验证，但没有声称已替任何真实公司建设/发布网站、已在18行业运行用户测试、已提升排名或获取询盘。后续以真实公司试建补充行为验证和模板改进。
